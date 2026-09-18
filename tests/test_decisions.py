import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from plugin_run import run
from validate_decisions import validate


class DecisionReferences(unittest.TestCase):
    def setUp(self):
        self.analysis = run(json.loads((ROOT / "examples/pet-bowl-input.json").read_text(encoding="utf-8")))["result"]["analysis"]
        self.decisions = json.loads((ROOT / "examples/pet-bowl-decisions.json").read_text(encoding="utf-8"))

    def test_example_proposal_references_resolve(self):
        result = validate(self.analysis, self.decisions)
        self.assertEqual(result["scope"], "reference_validation_only")
        self.assertEqual(result["proposal_count"], 1)
        self.assertTrue(result["manual_review_required"])

    def test_made_up_quote_and_source_rejected(self):
        for changes in [{"quote": "Independently tested conversion uplift"}, {"id": "E099"}, {"field": "original_brief"}]:
            candidate = copy.deepcopy(self.decisions)
            candidate["proposals"][0]["evidence"][0].update(changes)
            with self.assertRaises(ValueError): validate(self.analysis, candidate)

    def test_new_input_invalidates_old_plan_even_with_same_row_ids(self):
        data = json.loads((ROOT / "examples/pet-bowl-input.json").read_text(encoding="utf-8"))
        data["brief"] += "\nAdditional requirement: Only disposable packaging can be tested."
        changed = run(data)["result"]["analysis"]
        with self.assertRaisesRegex(ValueError, "different analysis"):
            validate(changed, self.decisions)

    def test_edited_analysis_rejected(self):
        self.analysis["evidence"][0]["key_feature"] = "Invented performance"
        with self.assertRaisesRegex(ValueError, "changed after analysis"):
            validate(self.analysis, self.decisions)

    def test_empty_and_overconfident_proposals_rejected(self):
        for changes in [{"evidence": []}, {"status": "validated"}]:
            candidate = copy.deepcopy(self.decisions)
            candidate["proposals"][0].update(changes)
            with self.assertRaises(Exception): validate(self.analysis, candidate)


if __name__ == "__main__":
    unittest.main()
