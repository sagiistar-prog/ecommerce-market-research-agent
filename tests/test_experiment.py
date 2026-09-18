import copy
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from jsonschema import ValidationError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from plugin_run import run
from hypothesis_review import prepare_review, export_review
from experiment import plan_test, check_plan, evaluate_test, read_pairs

HEADER='pair_id,baseline,candidate,guardrail_failed,source_ref\n'


class PairedTests(unittest.TestCase):
    def setUp(self):
        self.analysis=run(json.loads((ROOT/'examples/pet-bowl-input.json').read_text(encoding='utf-8')))['result']['analysis']
        self.decisions=json.loads((ROOT/'examples/pet-bowl-decisions.json').read_text(encoding='utf-8'))
        self.review=prepare_review(self.analysis,self.decisions)
        self.review['entries'][0].update(choice='test',reason='Fictional exercise: compare the same cleaning task.')
        self.fields=dict(proposal_id='P001',metric_label='Cleaning time',unit='seconds',collection_method='Fictional paired task sheets; identical residue and capacity, alternate order.',
            direction='lower',min_improvement=10,min_pairs=3,guardrail_label='Assembly or cleaning failure',max_guardrail_rate=0,data_kind='synthetic')
        self.args=[self.analysis,self.decisions,self.review]
        self.plan=plan_test(*self.args,self.fields)
        self.csv=HEADER+'A,100,80,0,fictional sheet A\nB,80,60,0,fictional sheet B\nC,60,50,0,fictional sheet C\n'

    def evaluate(self,csv=None,plan=None):
        return evaluate_test(*self.args,plan or self.plan,self.csv if csv is None else csv)

    def test_met_conditions_remain_descriptive_and_synthetic(self):
        result=self.evaluate()['package']['result']
        self.assertEqual(result['criteria_status'],'criteria_met')
        self.assertEqual(result['median_improvement'],20)
        self.assertEqual(result['pair_count'],3)
        self.assertEqual(result['evidence_status'],'synthetic_exercise')
        self.assertEqual(result['business_effect'],'not_established')
        self.assertEqual(result['inference'],'descriptive_only')

    def test_median_is_within_pair_not_difference_of_medians(self):
        csv=HEADER+'A,100,99,0,sheet A\nB,10,0,0,sheet B\nC,20,1,0,sheet C\n'
        result=self.evaluate(csv)['package']['result']
        self.assertEqual(result['median_improvement'],10)
        self.assertNotEqual(result['baseline_median']-result['candidate_median'],result['median_improvement'])

    def test_guardrail_failure_has_priority_over_favorable_primary_or_small_sample(self):
        result=self.evaluate(HEADER+'A,100,10,1,sheet A\n')['package']['result']
        self.assertTrue(result['primary_met'])
        self.assertFalse(result['enough_pairs'])
        self.assertEqual(result['criteria_status'],'guardrail_exceeded')

    def test_insufficient_pairs_and_insufficient_improvement_differ(self):
        self.assertEqual(self.evaluate(HEADER+'A,100,80,0,sheet A\n')['package']['result']['criteria_status'],'need_more_pairs')
        self.assertEqual(self.evaluate(self.csv.replace('100,80','100,99').replace('80,60','80,79'))['package']['result']['criteria_status'],'improvement_below_target')

    def test_higher_direction_threshold_equality_and_decimal_guardrail(self):
        fields={**self.fields,'direction':'higher','min_improvement':0.1,'min_pairs':10,'max_guardrail_rate':0.1,'data_kind':'provided'}
        plan=plan_test(*self.args,fields)
        csv=HEADER+''.join(f'P{i},0.1,0.2,{int(i==0)},sheet {i}\n' for i in range(10))
        result=self.evaluate(csv,plan)['package']['result']
        self.assertEqual(result['criteria_status'],'criteria_met')
        self.assertEqual(result['evidence_status'],'provided_unverified')
        self.assertEqual(result['median_improvement'],0.1)

    def test_changed_plan_input_hypothesis_or_review_cannot_inherit_result(self):
        plan=copy.deepcopy(self.plan);plan['fields']['min_improvement']=1
        with self.assertRaises(ValueError):self.evaluate(plan=plan)
        changed=copy.deepcopy(self.decisions);changed['proposals'][0]['title']='Different question'
        with self.assertRaises(ValueError):evaluate_test(self.analysis,changed,self.review,self.plan,self.csv)
        changed=copy.deepcopy(self.analysis);changed['original_brief']+='changed'
        with self.assertRaises(ValueError):evaluate_test(changed,self.decisions,self.review,self.plan,self.csv)
        self.review['entries'][0].update(choice='defer',reason='Wait')
        with self.assertRaises(ValueError):self.evaluate()

    def test_non_finite_empty_boolean_or_impossible_thresholds_rejected(self):
        for fields in [{**self.fields,'min_improvement':float('nan')},{**self.fields,'max_guardrail_rate':float('inf')},
                       {**self.fields,'min_pairs':True},{**self.fields,'min_pairs':1},
                       {**self.fields,'min_improvement':0},{**self.fields,'max_guardrail_rate':1.1},
                       {**self.fields,'collection_method':'  '}]:
            with self.subTest(fields=fields),self.assertRaises((ValueError,ValidationError)):plan_test(*self.args,fields)

    def test_csv_missing_values_duplicates_and_infinities_never_silently_drop(self):
        for csv in [HEADER,HEADER+'A,,10,0,s\n',HEADER+'A,NaN,10,0,s\n',HEADER+'A,1,Infinity,0,s\n',
                    HEADER+'A,-1,10,0,s\n',HEADER+'A,1,10,true,s\n',HEADER+'A,1,10,0,\n',
                    HEADER+'A,1,10,0,s\nA,1,10,0,s\n',HEADER+'A,1,10,0\n',
                    HEADER+'A,1,10,0,s,extra\n',HEADER.replace('candidate','baseline')+'A,1,10,0,s\n']:
            with self.subTest(csv=csv),self.assertRaises(ValueError):read_pairs(csv)

    def test_decimal_scientific_notation_bom_and_quoted_source(self):
        rows=read_pairs('\ufeff'+HEADER+'A,1e2,90.25,0,"fictional sheet, row 1"\n')
        self.assertEqual(str(rows[0]['baseline']),'1E+2')
        self.assertEqual(rows[0]['source_ref'],'fictional sheet, row 1')

    def test_browser_numeric_roundtrip_and_result_recomputation(self):
        plan=json.loads(json.dumps(self.plan))
        plan['fields']['min_improvement']=10.0
        self.assertEqual(check_plan(*self.args,plan),self.plan)
        original=copy.deepcopy(self.plan)
        saved=self.evaluate()['package'];saved['result']['median_improvement']=999999
        restored=evaluate_test(*self.args,saved['plan'],saved['observations_csv'])
        self.assertEqual(restored['package']['result']['median_improvement'],20)
        self.assertEqual(self.plan,original)
        self.assertEqual(saved['observations_id'],restored['package']['observations_id'])

    def test_cli_exports_same_result_and_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'review.json').write_text(json.dumps(export_review(*self.args)['package']),encoding='utf-8')
            (root/'plan.json').write_text(json.dumps(self.plan),encoding='utf-8')
            (root/'observations.csv').write_text(self.csv,encoding='utf-8')
            command=[sys.executable,str(ROOT/'scripts/review_test.py'),'--review',str(root/'review.json'),
                '--plan',str(root/'plan.json'),'--observations',str(root/'observations.csv'),'--output-dir',str(root/'run')]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            actual=json.loads((root/'run/result.json').read_text(encoding='utf-8'))
            self.assertEqual(actual,self.evaluate()['package'])
            before=(root/'run/result.json').read_bytes()
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,2)
            self.assertEqual((root/'run/result.json').read_bytes(),before)


if __name__=='__main__':unittest.main()
