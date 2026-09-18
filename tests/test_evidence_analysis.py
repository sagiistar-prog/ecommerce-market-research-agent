import csv
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evidence_analysis import analyze, load_rows, parse_brief
from plugin_run import run

HEADERS = ["brand", "price_usd", "channel", "positioning_claim", "key_feature", "content_hook", "evidence_level", "notes", "comparison_group", "data_kind", "source_url", "observed_at"]


def csv_text(prices=("19.95", "29.95", "39.95"), **fields):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=HEADERS)
    writer.writeheader()
    for index, price in enumerate(prices):
        writer.writerow({**dict.fromkeys(HEADERS, ""), "brand": f"Fictional offer {index}", "price_usd": price,
                         "channel": "Fictional shop", "key_feature": "Washable cover", "evidence_level": "E0",
                         "comparison_group": "one unit excluding shipping", "notes": "Synthetic test fixture", **fields})
    return stream.getvalue()


def review(text=None, **fields):
    rows = load_rows(text if text is not None else csv_text(**fields))
    return analyze(parse_brief("Category: Travel carrier\nTarget market: Fictional market\nAudience hypothesis: Train travelers\nResearch goal: Should we test a washable cover?"), rows)


class EvidenceAnalysisTests(unittest.TestCase):
    def test_prices_preserve_cents_and_scientific_notation(self):
        a = review(csv_text(("1e2", "19.95", "29.95")))
        self.assertEqual([r["price_usd"] for r in a["evidence"]], [100, 19.95, 29.95])
        group = a["sample"]["price_groups"][0]
        self.assertEqual(group["median_usd"], 29.95)
        self.assertEqual(group["mean_usd"], 49.97)

    def test_missing_prices_are_null_and_zero_is_real(self):
        a = review(csv_text(("", "0", "10.50")))
        self.assertIsNone(a["evidence"][0]["price_usd"])
        self.assertEqual(a["sample"]["missing_price_count"], 1)
        self.assertEqual(a["sample"]["price_groups"][0]["median_usd"], 5.25)

    def test_all_missing_is_not_a_zero_price_market(self):
        a = review(csv_text(("", "", "")))
        self.assertIsNone(a["sample"]["price_groups"][0]["mean_usd"])
        self.assertFalse(any(o["kind"] == "sample_price" for o in a["observations"]))

    def test_ungrouped_prices_do_not_produce_benchmarks(self):
        a = review(comparison_group="")
        self.assertEqual(a["sample"]["price_groups"], [])
        self.assertEqual(a["sample"]["ungrouped_count"], 3)

    def test_different_pack_sizes_are_separate(self):
        rows = load_rows(csv_text())
        rows[2]["comparison_group"] = "six pack"
        a = analyze(parse_brief("Compare package offers"), rows)
        self.assertEqual(len(a["sample"]["price_groups"]), 2)
        self.assertEqual(sorted(g["priced_count"] for g in a["sample"]["price_groups"]), [1, 2])

    def test_synthetic_and_provided_prices_never_mix(self):
        rows = load_rows(csv_text())
        rows[2].update(evidence_level="E2", data_kind="provided", source_url="https://example.org/fixture", observed_at="2025-01-01")
        a = analyze(parse_brief("Compare offers"), rows)
        self.assertEqual(len(a["sample"]["price_groups"]), 2)
        provided = next(g for g in a["sample"]["price_groups"] if g["data_kind"] == "provided")
        self.assertEqual(provided["evidence_ids"], ["E003"])

    def test_plain_brief_preserved_without_invented_audience(self):
        a = analyze(parse_brief("我想研究宠物碗退货的原因"), load_rows(csv_text()))
        self.assertEqual(a["original_brief"], "我想研究宠物碗退货的原因")
        self.assertIsNone(a["brief"]["audience_hypothesis"])
        self.assertEqual(a["decision_status"], "needs_input")

    def test_chinese_and_bold_labels(self):
        brief = parse_brief("- **品类：** 宠物碗\n目标市场：日本\n**目标用户**：养猫家庭\n研究问题：清洗是否费时")
        self.assertEqual(brief["category"], "宠物碗")
        self.assertEqual(brief["target_country"], "日本")
        self.assertEqual(brief["audience_hypothesis"], "养猫家庭")

    def test_conflicting_brief_labels_rejected(self):
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            parse_brief("Category: Shoes\n品类：Books")

    def test_cross_category_output_has_no_desk_personas(self):
        for category in ["Child car seat", "Pet feeding bowl", "Reusable food wrap"]:
            with self.subTest(category=category):
                result = run({"brief": f"Category: {category}\nTarget market: Fictional market\nAudience hypothesis: Supplied audience\nResearch goal: Compare cleaning effort", "competitors_csv": csv_text(key_feature="Washable material")})
                report = result["result"]["markdown"]
                self.assertIn(category, report)
                for invented in ["desk", "gift buyer", "Student creator", "lighting", "Compact transformation"]:
                    self.assertNotIn(invented, report)

    def test_every_observation_and_task_reference_resolves(self):
        a = review(positioning_claim="Easy to wash")
        ids = {row["id"] for row in a["evidence"]}
        for record in a["observations"] + a["research_tasks"]:
            self.assertTrue(set(record["evidence_ids"]) <= ids)
        repeated = [row for row in a["observations"] if row["kind"] == "repeated_claim"]
        self.assertEqual(len(repeated), 2)
        self.assertEqual(repeated[0]["evidence_ids"], ["E001", "E002", "E003"])

    def test_source_label_never_implies_verification(self):
        a = review(data_kind="provided", evidence_level="E3", source_url="https://example.org/fixture", observed_at="2025-01-01")
        self.assertEqual(a["decision_status"], "research_only")
        self.assertIn("not independently verified", a["limitations"][0])

    def test_no_network_for_analysis(self):
        with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")):
            result = run({"brief": "A fictional concept", "competitors_csv": csv_text(source_url="https://example.org/never-fetch")})
        self.assertEqual(result["status"], "ok")

    def test_markdown_escapes_supplied_markup(self):
        result = run({"brief": "Category: <script>alert(1)</script> | **new**", "competitors_csv": csv_text(brand="A | <img src=x>\nHeading")})
        report = result["result"]["markdown"]
        self.assertNotIn("<script>", report)
        self.assertNotIn("<img", report)
        self.assertIn("&#124;", report)
        self.assertIn("&lt;script&gt;", report)

    def test_bad_values_rejected(self):
        for overrides in [dict(evidence_level="verified"), dict(observed_at="2099-01-01"), dict(observed_at="2025-02-30"), dict(source_url="javascript:alert(1)"), dict(source_url="https://user:pass@localhost"), dict(data_kind="provided")]:
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                load_rows(csv_text(**overrides))
        for price in ["nan", "inf", "-1", "$20", "1,000", "1e999"]:
            with self.subTest(price=price), self.assertRaises(ValueError):
                load_rows(csv_text((price,)))

    def test_duplicate_headers_and_rows_rejected(self):
        content = csv_text(("1",))
        with self.assertRaisesRegex(ValueError, "Duplicate CSV"):
            load_rows(content.replace("price_usd", "brand", 1))
        with self.assertRaisesRegex(ValueError, "duplicate observation"):
            load_rows(content + content.splitlines()[-1] + "\n")

    def test_unknown_columns_and_oversized_rows_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            load_rows(csv_text().replace("notes,comparison_group", "notes,unused,comparison_group"))
        with self.assertRaises(ValueError):
            load_rows(csv_text(tuple("10" for _ in range(251))))

    def test_error_contract_version_and_output_size(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/plugin_run.py")], input='{"brief":NaN}', text=True, capture_output=True, encoding="utf-8")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], "2.0")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
