import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from generate_market_report import load_competitors_text
class CSVValidation(unittest.TestCase):
    def test_missing_headers_rejected(self):
        with self.assertRaises(ValueError):load_competitors_text('brand,price\nDemo,20')
    def test_nan_price_rejected(self):
        text='brand,price_usd,channel,positioning_claim,key_feature,content_hook,evidence_level,notes\nDemo,NaN,shop,test,test,test,fictional,test'
        with self.assertRaises(ValueError):load_competitors_text(text)
    def test_extra_columns_rejected(self):
        text='brand,price_usd,channel,positioning_claim,key_feature,content_hook,evidence_level,notes\nDemo,20,shop,test,test,test,fictional,test,extra'
        with self.assertRaises(ValueError):load_competitors_text(text)
if __name__=='__main__':unittest.main()
