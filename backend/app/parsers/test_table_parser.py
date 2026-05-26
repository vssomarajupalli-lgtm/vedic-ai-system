import unittest
from app.parsers.table_parser import TableParser

class TestTableParser(unittest.TestCase):

    def setUp(self):
        self.parser = TableParser()

    def test_comprehensive_parsing_scenario(self):
        """
        Tests a realistic grid with clean data, dirty data, malformed rows,
        and non-planet rows to ensure robust, deterministic parsing.
        """
        raw_input_grid = [
            ["Planet", "Sign", "Longitude", "Nakshatra", "Pada", "R/D"],  # 0: Header
            ["Sun", " Aries ", " 14°25'12\" ", "Ashwini", "1", " D "],     # 1: Valid with whitespace
            ["Moon", "Taurus", "05°12'00\"", "Krittika", "3", "D"],       # 2: Clean valid
            [" Mars ", "Gemini", "28°45'11\"", "Punarvasu", "3", " R"],      # 3: Valid with planet whitespace
            ["Jupiter"],                                                  # 4: Malformed (not enough columns)
            ["Saturn", "Aquarius", "12°11'00\"", "Shatabhisha", "2", ""],  # 5: Valid with empty R/D
            ["Ascendant", "Cancer", "01°01'01\"", "Punarvasu", "4", "D"], # 6: Non-planet row
            ["Rahu", "Pisces", "19°19'19\"", "Revati", "1", "D"],         # 7: Valid
            ["", "", "", "", "", ""],                                     # 8: Empty row
            ["Ketu", "Virgo", "19°19'19\"", "Hasta", "3", "D"]            # 9: Valid
        ]

        # This test will fail until the parser is implemented correctly
        result = self.parser.parse(raw_input_grid)

        # Sort rejected rows by index for deterministic comparison
        if "rejected_rows" in result.get("extraction_metadata", {}):
            result["extraction_metadata"]["rejected_rows"].sort(key=lambda x: x['row_index'])

        # Assertions for parsed planets
        self.assertEqual(len(result.get("planets", {})), 6)
        self.assertIn("Sun", result["planets"])
        self.assertIn("Mars", result["planets"]) # Check that " Mars " was cleaned
        self.assertEqual(result["planets"]["Sun"]["sign"], "Aries")
        self.assertEqual(result["planets"]["Sun"]["is_retrograde"], False)
        self.assertEqual(result["planets"]["Mars"]["is_retrograde"], True)
        self.assertEqual(result["planets"]["Saturn"]["is_retrograde"], False)

        # Assertions for metadata and rejected rows
        metadata = result.get("extraction_metadata", {})
        self.assertEqual(metadata.get("status"), "partial_success")
        self.assertEqual(metadata.get("total_parsed"), 6)
        self.assertEqual(len(metadata.get("rejected_rows", [])), 4)

        # Check rejected rows content
        rejected_reasons = [r['reason'] for r in metadata['rejected_rows']]
        self.assertIn("header_row_ignored", rejected_reasons)
        self.assertIn("column_count_mismatch", rejected_reasons)
        self.assertIn("not_a_planet_row", rejected_reasons)
        self.assertIn("empty_or_invalid_planet", rejected_reasons)

        # Check specific rejected rows
        self.assertEqual(metadata["rejected_rows"][0]["row_index"], 0)
        self.assertEqual(metadata["rejected_rows"][1]["row_index"], 4)
        self.assertEqual(metadata["rejected_rows"][2]["row_index"], 6)
        self.assertEqual(metadata["rejected_rows"][3]["row_index"], 8)

    def test_empty_input_grid(self):
        """
        Tests that the parser handles an empty list gracefully.
        """
        result = self.parser.parse([])
        expected = {
            "planets": {},
            "extraction_metadata": {
                "status": "success",
                "total_parsed": 0,
                "rejected_rows": []
            }
        }
        self.assertEqual(result, expected)

    def test_no_valid_planet_rows(self):
        """
        Tests that a grid with only headers and junk is handled correctly.
        """
        raw_input_grid = [
            ["Planet", "Sign", "Longitude", "Nakshatra", "Pada", "R/D"],
            ["Ascendant", "Cancer", "01°01'01\"", "Punarvasu", "4", "D"]
        ]
        result = self.parser.parse(raw_input_grid)
        
        if "rejected_rows" in result.get("extraction_metadata", {}):
            result["extraction_metadata"]["rejected_rows"].sort(key=lambda x: x['row_index'])

        expected = {
            "planets": {},
            "extraction_metadata": {
                "status": "success",
                "total_parsed": 0,
                "rejected_rows": [
                    {
                        "row_index": 0,
                        "raw_data": ["Planet", "Sign", "Longitude", "Nakshatra", "Pada", "R/D"],
                        "reason": "header_row_ignored"
                    },
                    {
                        "row_index": 1,
                        "raw_data": ["Ascendant", "Cancer", "01°01'01\"", "Punarvasu", "4", "D"],
                        "reason": "not_a_planet_row"
                    }
                ]
            }
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()