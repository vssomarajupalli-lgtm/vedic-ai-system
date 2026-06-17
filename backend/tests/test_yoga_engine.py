import unittest
from app.engines.yoga_engine import YogaEngine

class TestYogaEngine(unittest.TestCase):
    def setUp(self):
        self.engine = YogaEngine()

    def test_pancha_mahapurusha_yoga(self):
        # Mars in 10th house, exalted
        payload = {"planets": {"mars": {"house": 10, "dignity": "exalted"}}, "houses": {}}
        p_res = {"mars": {"final_score": 80.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        yogas = res["active_yogas"]
        self.assertEqual(len(yogas), 1)
        self.assertEqual(yogas[0]["yoga_name"], "Ruchaka Yoga")
        self.assertEqual(yogas[0]["strength"], 80.0)

    def test_gaja_kesari_yoga(self):
        # Jupiter in 4th from Moon
        payload = {"planets": {"jupiter": {"house": 4, "dignity": "neutral"}, "moon": {"house": 1, "dignity": "neutral"}}, "houses": {}}
        p_res = {"jupiter": {"final_score": 75.0}, "moon": {"final_score": 65.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        gk = [y for y in res["active_yogas"] if y["category"] == "Gaja Kesari Yoga"]
        self.assertEqual(len(gk), 1)
        self.assertEqual(gk[0]["strength"], 70.0) # (75 + 65) / 2

    def test_vipareeta_raja_yoga(self):
        # 6th lord in 8th house
        payload = {
            "planets": {"mars": {"house": 8}}, 
            "houses": {"6": {"lord": "mars"}}
        }
        p_res = {"mars": {"final_score": 50.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        vr = [y for y in res["active_yogas"] if y["yoga_name"] == "Harsha Yoga"]
        self.assertEqual(len(vr), 1)
        self.assertEqual(vr[0]["category"], "Vipareeta Raja Yoga")

    def test_dhana_yoga_conjunction(self):
        # 2nd lord and 5th lord conjunct in house 1
        payload = {
            "planets": {"venus": {"house": 1}, "mercury": {"house": 1}},
            "houses": {"2": {"lord": "venus"}, "5": {"lord": "mercury"}}
        }
        p_res = {"venus": {"final_score": 60.0}, "mercury": {"final_score": 70.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        dy = [y for y in res["active_yogas"] if y["category"] == "Dhana Yoga"]
        self.assertEqual(len(dy), 1)
        self.assertIn("conjunction", dy[0]["yoga_name"])
        self.assertEqual(dy[0]["strength"], 65.0)

    def test_raja_yoga_aspect(self):
        # 4th lord and 9th lord aspecting (dist 7)
        payload = {
            "planets": {"moon": {"house": 1}, "sun": {"house": 7}},
            "houses": {"4": {"lord": "moon"}, "9": {"lord": "sun"}}
        }
        p_res = {"moon": {"final_score": 80.0}, "sun": {"final_score": 80.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        ry = [y for y in res["active_yogas"] if y["category"] == "Raja Yoga"]
        self.assertEqual(len(ry), 1)
        self.assertIn("mutual_aspect", ry[0]["yoga_name"])

    def test_neecha_bhanga_raja_yoga(self):
        # Mars debilitated in 4, Dispositor Moon in 1 (Kendra)
        payload = {
            "planets": {"mars": {"house": 4, "dignity": "debilitated"}, "moon": {"house": 1}},
            "houses": {"4": {"lord": "moon"}}
        }
        p_res = {"mars": {"final_score": 50.0}, "moon": {"final_score": 90.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        nb = [y for y in res["active_yogas"] if y["category"] == "Neecha Bhanga Raja Yoga"]
        self.assertEqual(len(nb), 1)
        self.assertEqual(nb[0]["strength"], 90.0)

    def test_arishta_yoga_kemadruma(self):
        # Moon with no planets in 2nd or 12th from it
        payload = {"planets": {"moon": {"house": 5}, "jupiter": {"house": 8}}, "houses": {}}
        p_res = {"moon": {"final_score": 40.0}}
        res = self.engine.evaluate(payload, p_res, {})
        
        ay = [y for y in res["active_yogas"] if y["yoga_name"] == "Kemadruma Yoga"]
        self.assertEqual(len(ay), 1)
        self.assertEqual(ay[0]["strength"], 60.0) # 100 - 40

if __name__ == '__main__':
    unittest.main()
