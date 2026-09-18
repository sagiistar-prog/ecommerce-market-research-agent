"""Descriptive, paired-task checks against an explicit, evidence-bound plan."""
import csv
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import io
import json
from pathlib import Path
from statistics import median

from jsonschema import Draft202012Validator
from hypothesis_review import export_review, decisions_id

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return 'sha256:' + sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def plan_test(analysis, decisions, review, fields):
    export_review(analysis, decisions, review)
    schema = json.loads((ROOT / 'schemas/test-plan.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(schema).validate(fields)
    # jsonschema accepts NaN as a Python number; explicit finite checks cover CLI calls too.
    for name in ('min_improvement', 'max_guardrail_rate'):
        if not Decimal(str(fields[name])).is_finite():
            raise ValueError('Plan thresholds must be finite.')
    fields = {**fields, 'min_improvement': float(fields['min_improvement']),
              'max_guardrail_rate': float(fields['max_guardrail_rate']), 'min_pairs': int(fields['min_pairs'])}
    entry = next((row for row in review['entries'] if row['proposal_id'] == fields['proposal_id']), None)
    if not entry or entry['choice'] != 'test':
        raise ValueError('Record Plan a test for this hypothesis before defining a test.')
    payload = {'schema_version': '1.0', 'kind': 'market-test-plan',
        'analysis_id': analysis['analysis_id'], 'decisions_id': decisions_id(decisions), 'fields': fields}
    return {**payload, 'plan_id': digest(payload)}


def check_plan(analysis, decisions, review, plan):
    if not isinstance(plan, dict) or set(plan) != {'schema_version', 'kind', 'analysis_id', 'decisions_id', 'fields', 'plan_id'}:
        raise ValueError('Import a complete version 1.0 test plan.')
    expected = plan_test(analysis, decisions, review, plan['fields'])
    if plan != expected:
        raise ValueError('Test plan or its evidence changed. Use the matching plan and inputs.')
    return expected


def read_pairs(contents):
    if not isinstance(contents, str) or not contents.strip() or len(contents) > 200_000:
        raise ValueError('Provide observation CSV, up to 200000 characters.')
    required = ['pair_id', 'baseline', 'candidate', 'guardrail_failed', 'source_ref']
    try:
        reader = csv.DictReader(io.StringIO(contents.lstrip('\ufeff')), strict=True)
        if reader.fieldnames is None or len(reader.fieldnames) != len(required) or set(reader.fieldnames) != set(required):
            raise ValueError('CSV needs pair_id, baseline, candidate, guardrail_failed, source_ref exactly once.')
        rows, ids = [], set()
        for line, raw in enumerate(reader, 2):
            if len(rows) >= 1000:
                raise ValueError('Keep this paired task study within 1000 observations.')
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError(f'CSV row {line}: missing or extra cells.')
            row = {key: value.strip() for key, value in raw.items()}
            if not row['pair_id'] or len(row['pair_id']) > 80 or row['pair_id'] in ids:
                raise ValueError(f'CSV row {line}: use a unique, nonempty pair_id, up to 80 characters.')
            if not row['source_ref'] or len(row['source_ref']) > 500:
                raise ValueError(f'CSV row {line}: add an observation source reference, up to 500 characters.')
            ids.add(row['pair_id'])
            for key in ('baseline', 'candidate'):
                try:
                    value = Decimal(row[key])
                except InvalidOperation:
                    raise ValueError(f'CSV row {line}: {key} must be numeric; missing values are not zero.') from None
                if not value.is_finite() or not 0 <= value <= 1_000_000_000:
                    raise ValueError(f'CSV row {line}: {key} must be finite and between 0 and 1000000000.')
                row[key] = value
            if row['guardrail_failed'] not in ('0', '1'):
                raise ValueError(f'CSV row {line}: guardrail_failed must be 0 or 1.')
            row['guardrail_failed'] = int(row['guardrail_failed'])
            rows.append(row)
    except csv.Error as error:
        raise ValueError('CSV could not be parsed. Check quoted fields.') from error
    if not rows:
        raise ValueError('CSV needs at least one paired observation.')
    return rows


def evaluate_test(analysis, decisions, review, plan, observations_csv):
    plan = check_plan(analysis, decisions, review, plan)
    rows = read_pairs(observations_csv)
    fields = plan['fields']
    sign = Decimal(1 if fields['direction'] == 'lower' else -1)
    improvements = [(row['baseline'] - row['candidate']) * sign for row in rows]
    observed = median(improvements)
    failures = sum(row['guardrail_failed'] for row in rows)
    n = len(rows)
    enough = n >= fields['min_pairs']
    primary = observed >= Decimal(str(fields['min_improvement']))
    guardrail = Decimal(failures) <= Decimal(str(fields['max_guardrail_rate'])) * n
    status = ('guardrail_exceeded' if not guardrail else 'need_more_pairs' if not enough else
              'criteria_met' if primary else 'improvement_below_target')
    result = {'pair_count': n, 'median_improvement': float(observed),
        'baseline_median': float(median(row['baseline'] for row in rows)),
        'candidate_median': float(median(row['candidate'] for row in rows)),
        'guardrail_failures': failures, 'guardrail_rate': failures / n,
        'enough_pairs': enough, 'primary_met': primary, 'guardrail_met': guardrail,
        'criteria_status': status,
        'evidence_status': 'synthetic_exercise' if fields['data_kind'] == 'synthetic' else 'provided_unverified',
        'inference': 'descriptive_only', 'business_effect': 'not_established'}
    package = {'schema_version': '1.0', 'kind': 'market-test-result', 'plan': plan,
        'observations_csv': observations_csv,
        'observations_id': 'sha256:' + sha256(observations_csv.encode()).hexdigest(), 'result': result}
    lines = ['# Paired task review', '', fields['metric_label'], '',
        f"Plan: {plan['plan_id']}", f"Hypothesis: {fields['proposal_id']}",
        f"Data: {result['evidence_status']}", f"Observation source: {fields['collection_method']}", '',
        f"Pairs: {n} / minimum {fields['min_pairs']}",
        f"Median within-pair improvement: {observed} {fields['unit']}",
        f"Required improvement: {fields['min_improvement']} {fields['unit']}",
        f"Guardrail: {fields['guardrail_label']}",
        f"Guardrail failures: {failures}/{n}; maximum rate {fields['max_guardrail_rate']}",
        f"Criteria status: {status}", '',
        'Descriptive check only. No statistical significance, causal effect, verified source or launch recommendation is established.',
        'The plan hash checks integrity; it does not prove when the plan was created.', '']
    return {'package': package, 'markdown': '\n'.join(lines)}
