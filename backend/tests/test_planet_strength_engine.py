import unittest
from app.engines.planet_strength_engine import PlanetStrengthEngine

class TestPlanetStrengthEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PlanetStrengthEngine()

    def test_calculate_strong_planet(self):
        """
        Test a very strong planet.
        Exalted (35) + Kendra (20) + 1 Benefic Aspect (10) = 65
        """
        planet_data = {
            "name": "sun",
            "dignity": "exalted",
            "house_type": "kendra",
            "is_combust": False,
            "is_retrograde": False,
            "benefic_aspects_count": 1,
            "malefic_aspects_count": 0
        }
        
        result = self.engine.calculate_strength(planet_data)
        
        self.assertEqual(result["metadata"]["entity_id"], "sun")
        self.assertEqual(result["metadata"]["entity_type"], "planet")
        self.assertEqual(result["raw_score"], 65.0)
        self.assertEqual(result["final_score"], 65)
        self.assertEqual(result["breakdown"]["dignity"], 35)
        self.assertEqual(result["breakdown"]["house_placement"], 20)
        self.assertEqual(result["breakdown"]["aspects"], 10)

    def test_calculate_weak_planet_with_clamping(self):
        """
        Test a very weak planet to ensure the score doesn't drop below 0.
        Debilitated (0) + Dusthana (-10) + Combust (-15) + 1 Malefic Aspect (-10) = -35
        Should clamp to 0.
        """
        planet_data = {
            "name": "saturn",
            "dignity": "debilitated",
            "house_type": "dusthana",
            "is_combust": True,
            "is_retrograde": False,
            "benefic_aspects_count": 0,
            "malefic_aspects_count": 1
        }
        
        result = self.engine.calculate_strength(planet_data)
        
        self.assertEqual(result["metadata"]["entity_id"], "saturn")
        self.assertEqual(result["raw_score"], -35.0)
        self.assertIn("clamped_to_zero", result["confidence_flags"])
        self.assertEqual(result["final_score"], 0) # Clamped
        self.assertEqual(result["breakdown"]["dignity"], 0)
        self.assertEqual(result["breakdown"]["house_placement"], -10)
        self.assertEqual(result["breakdown"]["state_modifiers"], -15)
        self.assertEqual(result["breakdown"]["aspects"], -10)

    def test_missing_data_uses_neutral_defaults(self):
        """
        Test that if input data is completely bare/missing, the engine
        gracefully processes neutral strength.
        Neutral Dignity (10) + Neutral House (10) = 20.
        """
        planet_data = {
            "name": "mars"
        }
        
        result = self.engine.calculate_strength(planet_data)
        
        self.assertEqual(result["final_score"], 20)

if __name__ == '__main__':
    unittest.main()