import unittest
from app.pipeline_runner import PipelineRunner

class TestPipelineRunner(unittest.TestCase):
    """
    Deterministic Regression Tests for the PipelineRunner.
    Validates the orchestration, dependency injection, and adherence to Architecture Rules.
    """

    def setUp(self):
        self.runner = PipelineRunner()
        
        # We bypass the JsonNormalizer here to test the Runner's orchestration logic directly.
        # This represents a perfectly normalized payload ready for the calculation engines.
        self.mock_normalized_payload = {
            "metadata": {
                "name": "integration test native",
                "ascendant_sign": "aries",
            },
            "planets": {
                "sun": {
                    "name": "sun",
                    "sign": "aries",
                    "house_type": "kendra",
                    "dignity": "exalted",     # D1 Exalted (35) + Kendra (20) = 55 Base Score
                    "is_combust": False,
                    "is_retrograde": False,
                },
                "mars": {
                    "name": "mars",
                    "sign": "scorpio",
                    "house_type": "dusthana",
                    "dignity": "own_sign",    # D1 Own Sign (25) + Dusthana (-10) = 15 Base Score
                    "is_combust": False,
                    "is_retrograde": False,
                }
            },
            "houses": {
                "1": {
                    "house": 1,
                    "house_type": "kendra",   # Kendra = 20 Base Score
                    "lord": "mars",           # Dependency: Needs Mars' score (15 * 0.25 = 3.75)
                    "occupants": [],
                    "aspected_by": []
                }
            },
            "vargas": {
                "D9": {
                    "planets": {
                        "sun": {
                            "sign": "libra",  # D1 Aries -> D9 Libra = Contradicted (Debilitated)
                            "dignity": "debilitated",
                            "is_vargottama": False
                        },
                        "mars": {
                            "sign": "scorpio", # D1 Scorpio -> D9 Scorpio = Vargottama
                            "dignity": "own_house",
                            "is_vargottama": True
                        }
                    }
                }
            }
        }
        
        # Monkey-patch the normalizer to inject our perfectly structured test data
        self.runner.normalizer.normalize = lambda raw: self.mock_normalized_payload

        # Execute the pipeline once for all tests to use
        self.results = self.runner.process({})

    def test_schema_consistency(self):
        """Ensure the final output contains all mandated top-level JSON Contract keys."""
        self.assertIn("metadata", self.results)
        self.assertIn("engine_outputs", self.results)
        
        engine_outputs = self.results["engine_outputs"]
        self.assertIn("planets", engine_outputs)
        self.assertIn("houses", engine_outputs)
        self.assertIn("vargas", engine_outputs)

    def test_immutable_d1_rule(self):
        """Architecture Rule 1: Vargas MUST NOT overwrite the D1 final_score."""
        d1_sun_score = self.results["engine_outputs"]["planets"]["sun"]["final_score"]
        varga_sun_score = self.results["engine_outputs"]["vargas"]["sun"]["final_score"]
        
        # Both should equal 55 (Exalted 35 + Kendra 20)
        self.assertEqual(d1_sun_score, 55)
        self.assertEqual(d1_sun_score, varga_sun_score, "Varga Engine illegally modified the D1 final_score!")

    def test_safe_dependency_flow(self):
        """Ensure the PipelineRunner successfully passes the Mars D1 score into House 1."""
        house_1 = self.results["engine_outputs"]["houses"]["1"]
        
        # Mars D1 score is 15. The house lord weight multiplier is 0.25. (15 * 0.25 = 3.75)
        self.assertEqual(house_1["breakdown"]["lord_contribution"], 3.75)
        self.assertEqual(house_1["final_score"], 23) # Kendra (20) + Lord (3.75) = 23.75 -> Clamped to 23

    def test_varga_confidence_flags_and_modifiers(self):
        """Ensure the Varga Engine correctly calculates structural modifiers and string flags."""
        varga_sun = self.results["engine_outputs"]["vargas"]["sun"]
        varga_mars = self.results["engine_outputs"]["vargas"]["mars"]

        self.assertIn("varga_contradicted", varga_sun["confidence_flags"])
        self.assertIn("D9_vargottama", varga_mars["confidence_flags"])
        self.assertEqual(varga_mars["modifiers"]["D9_vargottama_bonus"], 15.0)