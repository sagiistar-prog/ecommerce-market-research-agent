"""User-authored choices bound to an exact evidence and hypothesis snapshot."""
from hashlib import sha256
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from validate_decisions import validate

ROOT=Path(__file__).resolve().parents[1]


def decisions_id(decisions):
    return 'sha256:'+sha256(json.dumps(decisions,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def prepare_review(analysis,decisions):
    validate(analysis,decisions)
    return {'decisions_id':decisions_id(decisions),'entries':[
        {'proposal_id':f'P{i:03d}','choice':'unreviewed','reason':''}
        for i in range(1,len(decisions['proposals'])+1)]}


def export_review(analysis,decisions,review):
    expected=prepare_review(analysis,decisions)
    schema=json.loads((ROOT/'schemas/review.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(schema).validate(review)
    if review['decisions_id']!=expected['decisions_id']:
        raise ValueError('Hypotheses changed. Review the new proposal package before reusing choices.')
    ids=[row['proposal_id'] for row in review['entries']]
    if len(set(ids))!=len(ids) or set(ids)!={row['proposal_id'] for row in expected['entries']}:
        raise ValueError('Review must include each proposal exactly once.')
    entries=sorted(review['entries'],key=lambda row:row['proposal_id'])
    counts={choice:sum(row['choice']==choice for row in entries) for choice in ('unreviewed','test','defer','reject')}
    package={'schema_version':'1.0','kind':'market-hypothesis-review','analysis':analysis,'decisions':decisions,
        'review':{'decisions_id':expected['decisions_id'],'entries':entries},
        'summary':{'proposal_count':len(entries),'reviewed_count':len(entries)-counts['unreviewed'],
            'choices':counts,'review_status':'complete' if not counts['unreviewed'] else 'in_progress',
            'validation_status':'not_measured'}}
    lines=['# Product hypothesis review','','These are reviewer choices, not measured product outcomes.','',
        f"Evidence snapshot: {analysis['analysis_id']}",f"Hypothesis snapshot: {expected['decisions_id']}",'']
    for row,proposal in zip(entries,decisions['proposals']):
        lines.extend([f"## {row['proposal_id']} / {proposal['title']}",'',f"Choice: {row['choice']}",
            f"Reason: {row['reason'] or 'Not reviewed'}",'',f"User: {proposal['target_user']}",
            f"Problem: {proposal['problem_statement']}",f"Change: {proposal['proposed_change']}",'',
            '### Evidence',''])
        for ref in proposal['evidence']:
            lines.extend([f"{ref['id']} / {ref['field']}",ref['quote'],''])
        lines.extend(['### Assumptions','',*['- '+a for a in proposal['assumptions']],'','### Proposed validation',''])
        for key,value in proposal['validation'].items():lines.extend([key.replace('_',' ').capitalize()+': '+value,''])
    return {'package':package,'markdown':'\n'.join(lines)}
