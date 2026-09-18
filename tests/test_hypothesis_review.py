import copy
import json
from pathlib import Path
import sys
import unittest
from jsonschema import ValidationError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from plugin_run import run
from hypothesis_review import prepare_review,export_review


class HypothesisReviewTests(unittest.TestCase):
    def setUp(self):
        self.analysis=run(json.loads((ROOT/'examples/commuter-mug-input.json').read_text(encoding='utf-8')))['result']['analysis']
        self.decisions=json.loads((ROOT/'examples/commuter-mug-decisions.json').read_text(encoding='utf-8'))
        self.review=prepare_review(self.analysis,self.decisions)

    def test_nothing_is_approved_by_default_and_partial_review_has_correct_denominator(self):
        initial=export_review(self.analysis,self.decisions,self.review)['package']
        self.assertEqual(initial['summary']['reviewed_count'],0)
        self.review['entries'][0].update(choice='test',reason='Fictional exercise: compare the proposed opening task.')
        output=export_review(self.analysis,self.decisions,self.review)
        summary=output['package']['summary']
        self.assertEqual((summary['proposal_count'],summary['reviewed_count']),(2,1))
        self.assertEqual(summary['choices'],{'unreviewed':1,'test':1,'defer':0,'reject':0})
        self.assertEqual(summary['validation_status'],'not_measured')
        self.assertEqual(summary['review_status'],'in_progress')
        self.assertIn('Proposed validation',output['markdown'])
        self.assertEqual(output['package']['analysis'],self.analysis)

    def test_changed_hypothesis_cannot_inherit_a_previous_vote(self):
        changed=copy.deepcopy(self.decisions)
        changed['proposals'][0]['proposed_change']='A materially different fictional change'
        with self.assertRaisesRegex(ValueError,'Hypotheses changed'):
            export_review(self.analysis,changed,self.review)

    def test_swapped_proposals_cannot_reassign_votes(self):
        changed=copy.deepcopy(self.decisions);changed['proposals'].reverse()
        with self.assertRaises(ValueError):export_review(self.analysis,changed,self.review)

    def test_missing_duplicate_unknown_and_invented_outcome_rejected(self):
        invalid=[]
        for choice in ('approved','validated','launched'):
            row=copy.deepcopy(self.review);row['entries'][0]['choice']=choice;invalid.append(row)
        row=copy.deepcopy(self.review);row['entries'].pop();invalid.append(row)
        row=copy.deepcopy(self.review);row['entries'][1]=row['entries'][0];invalid.append(row)
        row=copy.deepcopy(self.review);row['entries'][0]['proposal_id']='P999';invalid.append(row)
        for row in invalid:
            with self.assertRaises((ValueError,ValidationError)):export_review(self.analysis,self.decisions,row)

    def test_reviewed_choice_requires_reason_and_unreviewed_cannot_hide_a_reason(self):
        for choice,reason in [('test',''),('defer','  '),('reject','\n'),('unreviewed','Secretly approved')]:
            row=copy.deepcopy(self.review);row['entries'][0].update(choice=choice,reason=reason)
            with self.assertRaises(ValidationError):export_review(self.analysis,self.decisions,row)

    def test_restore_checks_references_again_even_if_review_hash_matches(self):
        self.decisions['proposals'][0]['evidence'][0]['quote']='Invented source text'
        with self.assertRaisesRegex(ValueError,'quoted text'):
            prepare_review(self.analysis,self.decisions)

    def test_roundtrip_is_deterministic_with_unicode_and_reason_preserved(self):
        for row in self.review['entries']:row.update(choice='defer',reason='虚构练习：先核对反例 🧪\n不能把计划当成结果。')
        first=export_review(self.analysis,self.decisions,self.review)
        restored=json.loads(json.dumps(first['package'],ensure_ascii=False))
        second=export_review(self.analysis,restored['decisions'],restored['review'])
        self.assertEqual(first,second)
        self.assertEqual(first['package']['summary']['review_status'],'complete')
        self.assertEqual(first['package']['summary']['validation_status'],'not_measured')


if __name__=='__main__':unittest.main()
