import unittest
from app.parsers.json_normalizer import JsonNormalizer

class TestJsonNormalizer(unittest.unittest.TestCase):
    def setUp(self):
        self.normalizer = JsonNormalizer()

    def test_normalize_clean_data(self):
        """Tests that perfectly extracted data passes through correctly."""
        raw_data = {
            "raw_metadata": {"name": "Test Native", "lagna": "Mesha", "lagna_degree": "14.5"},
            "raw_planets": {
                "Surya": {
                    "sign": "Mesha",
                    "degree": "10.0",
                    "house": "1",
                    "house_type": "Kendra",
                    "dignity": "Exalted",
                    "combust": "False",
                    "conjunctions": ["Budha"]
                }
            }
        }
        
        result = self.normalizer.normalize(raw_data)
        
        # Assertions
        self.assertEqual(result["metadata"]["name"], "test native")
        self.assertEqual(result["metadata"]["ascendant_sign"], "aries")
        self.assertEqual(result["metadata"]["ascendant_degree"], 14.5)
        
        sun = result["planets"]["sun"]
        self.assertEqual(sun["sign"], "aries")
        self.assertEqual(sun["degree"], 10.0)
        self.assertEqual(sun["house"], 1)
        self.assertEqual(sun["house_type"], "kendra")
        self.assertEqual(sun["dignity"], "exalted")
        self.assertFalse(sun["is_combust"])
        self.assertEqual(sun["conjunctions"], ["mercury"])

    def test_normalize_edge_cases_and_missing_fields(self):
        """
        Tests that missing fields receive safe defaults and 
        bad types (e.g., strings where floats are expected) don't crash the system.
        """
        raw_data = {
            "raw_planets": {
                "JunkData": {"degree": "invalid_number"}, # Should be ignored (not in planet map)
                "Mo": { # Shortname mapping
                    # Missing sign, house, degree, etc.
                    "retrograde": "y", # Truthy check
                    "combust": "yes",  # Truthy check
                    "bav": "GARBAGE_TEXT"
                }
            }
        }
        
        result = self.normalizer.normalize(raw_data)
        
        # 'JunkData' should be safely ignored
        self.assertNotIn("junkdata", result["planets"])
        
        # 'Mo' should map to 'moon' and apply defaults
        moon = result["planets"]["moon"]
        self.assertEqual(moon["degree"], 0.0) # Fallback for missing
        self.assertEqual(moon["house"], 0)    # Fallback for missing
        self.assertTrue(moon["is_retrograde"]) # 'y' -> True
        self.assertTrue(moon["is_combust"])    # 'yes' -> True
        self.assertEqual(moon["bav_points"], 0) # Fallback for bad string cast
        self.assertEqual(moon["dignity"], "neutral") # Safe default

    def test_normalize_vargas_and_vargottama(self):
        """
        Tests that Varga data is normalized and Vargottama is correctly calculated
        by comparing against D1 planet placements.
        """
        raw_data = {
            "raw_planets": {
                "Su": {"sign": "Mesha"}, # D1 Aries
                "Mo": {"sign": "Karka"}  # D1 Cancer
            },
            "raw_vargas": {
                "D9": {
                    "planets": {
                        "Su": {"sign": "Mesha", "dignity": "Exalted"}, # Matches D1 (Vargottama)
                        "Mo": {"sign": "Tula", "dignity": "Enemy"}     # Different from D1
                    }
                }
            }
        }
        
        result = self.normalizer.normalize(raw_data)
        
        d9_planets = result["vargas"]["D9"]["planets"]
        
        # Sun should be Vargottama
        self.assertEqual(d9_planets["sun"]["sign"], "aries")
        self.assertTrue(d9_planets["sun"]["is_vargottama"])
        
        # Moon should NOT be Vargottama
        self.assertFalse(d9_planets["moon"]["is_vargottama"])

    def test_schema_stability(self):
        """Ensure the top-level keys always exist for the engines to access."""
        result = self.normalizer.normalize({})
        expected_keys = ["metadata", "planets", "houses", "vargas", "ashtakavarga", "dashas", "transits"]
        for key in expected_keys:
            self.assertIn(key, result)

if __name__ == '__main__':
    unittest.main()