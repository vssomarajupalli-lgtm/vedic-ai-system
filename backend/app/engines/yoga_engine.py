from app.config.yoga_registry import YOGA_REGISTRY

class YogaEngine:
    """
    Yoga Engine for detection and classification only.
    No scores, probabilities, or mathematical weights are applied.
    """
    
    def __init__(self):
        self.registry = YOGA_REGISTRY

    def evaluate(self, chart_data: dict, planet_results: dict = None, house_results: dict = None) -> dict:
        """
        Detects yogas present in the chart and categorizes them by house.
        """
        results = {f"house_{i}_yogas": [] for i in range(1, 13)}
        results["universal_yogas"] = []
        
        # Helper to add yoga to results based on registry mapping
        def add_yoga(name: str):
            info = self.registry.get(name)
            if not info: return
            houses = info.get("houses", [])
            for h in houses:
                if h == "universal":
                    if name not in results["universal_yogas"]:
                        results["universal_yogas"].append(name)
                else:
                    h_key = f"house_{h}_yogas"
                    if h_key in results and name not in results[h_key]:
                        results[h_key].append(name)

        # --- UNIVERSAL YOGAS ---
        if self._detect_gaja_kesari_yoga(chart_data): add_yoga("Gaja Kesari Yoga")
        if self._detect_neecha_bhanga_raja_yoga(chart_data): add_yoga("Neecha Bhanga Raja Yoga")
        if self._detect_adhi_yoga(chart_data): add_yoga("Adhi Yoga")

        # --- PANCHA MAHAPURUSHA YOGAS ---
        if self._detect_ruchaka_yoga(chart_data): add_yoga("Ruchaka Yoga")
        if self._detect_bhadra_yoga(chart_data): add_yoga("Bhadra Yoga")
        if self._detect_hamsa_yoga(chart_data): add_yoga("Hamsa Yoga")
        if self._detect_malavya_yoga(chart_data): add_yoga("Malavya Yoga")
        if self._detect_sasa_yoga(chart_data): add_yoga("Sasa Yoga")

        # --- WEALTH YOGAS ---
        if self._detect_dhana_yoga(chart_data): add_yoga("Dhana Yoga")
        if self._detect_lakshmi_yoga(chart_data): add_yoga("Lakshmi Yoga")
        if self._detect_vasumathi_yoga(chart_data): add_yoga("Vasumathi Yoga")

        # --- CAREER YOGAS ---
        if self._detect_raja_yoga(chart_data): add_yoga("Raja Yoga")
        if self._detect_dharma_karma_adhipati_yoga(chart_data): add_yoga("Dharma Karma Adhipati Yoga")
        if self._detect_amala_yoga(chart_data): add_yoga("Amala Yoga")

        # --- EDUCATION YOGAS ---
        if self._detect_saraswati_yoga(chart_data): add_yoga("Saraswati Yoga")
        if self._detect_vidya_yoga(chart_data): add_yoga("Vidya Yoga")

        # --- MARRIAGE YOGAS ---
        if self._detect_kalatra_yoga(chart_data): add_yoga("Kalatra Yoga")
        if self._detect_saubhagya_yoga(chart_data): add_yoga("Saubhagya Yoga")

        # --- CHILDREN YOGAS ---
        if self._detect_putra_yoga(chart_data): add_yoga("Putra Yoga")
        if self._detect_santana_yoga(chart_data): add_yoga("Santana Yoga")

        # --- SPIRITUAL YOGAS ---
        if self._detect_moksha_yoga(chart_data): add_yoga("Moksha Yoga")
        if self._detect_sanyasa_yoga(chart_data): add_yoga("Sanyasa Yoga")
        if self._detect_parivraja_yoga(chart_data): add_yoga("Parivraja Yoga")

        return results

    # -------------------------------------------------------------------------
    # Detection Stubs
    # -------------------------------------------------------------------------

    def _get_planet_house(self, chart_data: dict, planet: str) -> int:
        return chart_data.get("planets", {}).get(planet, {}).get("house", -1)

    def _get_planet_dignity(self, chart_data: dict, planet: str) -> str:
        return chart_data.get("planets", {}).get(planet, {}).get("dignity", "neutral")

    def _get_lord_of_house(self, chart_data: dict, house: int) -> str:
        return chart_data.get("houses", {}).get(str(house), {}).get("lord", "")

    def _is_kendra(self, house: int) -> bool:
        return house in [1, 4, 7, 10]

    def _is_trikona(self, house: int) -> bool:
        return house in [1, 5, 9]

    # --- UNIVERSAL ---
    def _detect_gaja_kesari_yoga(self, chart_data: dict) -> bool:
        jup_house = self._get_planet_house(chart_data, "jupiter")
        moon_house = self._get_planet_house(chart_data, "moon")
        if jup_house == -1 or moon_house == -1: return False
        # Jupiter in kendra from Moon
        diff = (jup_house - moon_house) % 12
        if diff < 0: diff += 12
        relative_house = diff + 1
        return self._is_kendra(relative_house)

    def _detect_neecha_bhanga_raja_yoga(self, chart_data: dict) -> bool:
        for p, data in chart_data.get("planets", {}).items():
            if data.get("dignity") == "debilitated":
                # Very basic stub: if debilitated planet's dispositor is in kendra
                dispositor = chart_data.get("houses", {}).get(str(data.get("house")), {}).get("lord")
                if dispositor:
                    disp_house = self._get_planet_house(chart_data, dispositor)
                    if self._is_kendra(disp_house):
                        return True
        return False

    def _detect_adhi_yoga(self, chart_data: dict) -> bool:
        # Benefics in 6, 7, 8 from Moon
        moon_house = self._get_planet_house(chart_data, "moon")
        if moon_house == -1: return False
        benefics = ["mercury", "jupiter", "venus"]
        count = 0
        for b in benefics:
            h = self._get_planet_house(chart_data, b)
            if h != -1:
                rel = ((h - moon_house) % 12) + 1
                if rel in [6, 7, 8]:
                    count += 1
        return count >= 2

    # --- PANCHA MAHAPURUSHA ---
    def _check_mahapurusha(self, chart_data: dict, planet: str) -> bool:
        h = self._get_planet_house(chart_data, planet)
        d = self._get_planet_dignity(chart_data, planet)
        return self._is_kendra(h) and d in ["own_sign", "exalted", "moolatrikona"]

    def _detect_ruchaka_yoga(self, chart_data: dict) -> bool:
        return self._check_mahapurusha(chart_data, "mars")

    def _detect_bhadra_yoga(self, chart_data: dict) -> bool:
        return self._check_mahapurusha(chart_data, "mercury")

    def _detect_hamsa_yoga(self, chart_data: dict) -> bool:
        return self._check_mahapurusha(chart_data, "jupiter")

    def _detect_malavya_yoga(self, chart_data: dict) -> bool:
        return self._check_mahapurusha(chart_data, "venus")

    def _detect_sasa_yoga(self, chart_data: dict) -> bool:
        return self._check_mahapurusha(chart_data, "saturn")

    # --- WEALTH ---
    def _detect_dhana_yoga(self, chart_data: dict) -> bool:
        l2 = self._get_lord_of_house(chart_data, 2)
        l11 = self._get_lord_of_house(chart_data, 11)
        if not l2 or not l11: return False
        h2 = self._get_planet_house(chart_data, l2)
        h11 = self._get_planet_house(chart_data, l11)
        return h2 == h11 and h2 != -1

    def _detect_lakshmi_yoga(self, chart_data: dict) -> bool:
        l9 = self._get_lord_of_house(chart_data, 9)
        if not l9: return False
        h9 = self._get_planet_house(chart_data, l9)
        d9 = self._get_planet_dignity(chart_data, l9)
        l1 = self._get_lord_of_house(chart_data, 1)
        d1 = self._get_planet_dignity(chart_data, l1)
        return self._is_kendra(h9) and d9 in ["own_sign", "exalted"] and d1 not in ["debilitated"]

    def _detect_vasumathi_yoga(self, chart_data: dict) -> bool:
        benefics = ["jupiter", "venus", "mercury"]
        count = 0
        for b in benefics:
            h = self._get_planet_house(chart_data, b)
            if h in [3, 6, 10, 11]:
                count += 1
        return count >= 2

    # --- CAREER ---
    def _detect_raja_yoga(self, chart_data: dict) -> bool:
        l9 = self._get_lord_of_house(chart_data, 9)
        l10 = self._get_lord_of_house(chart_data, 10)
        l4 = self._get_lord_of_house(chart_data, 4)
        l5 = self._get_lord_of_house(chart_data, 5)
        # Any Kendra lord conjunct any Trikona lord
        pairs = [(l9, l10), (l4, l5), (l5, l10), (l4, l9)]
        for p1, p2 in pairs:
            if p1 and p2:
                h1 = self._get_planet_house(chart_data, p1)
                h2 = self._get_planet_house(chart_data, p2)
                if h1 == h2 and h1 != -1: return True
        return False

    def _detect_dharma_karma_adhipati_yoga(self, chart_data: dict) -> bool:
        l9 = self._get_lord_of_house(chart_data, 9)
        l10 = self._get_lord_of_house(chart_data, 10)
        if not l9 or not l10: return False
        h9 = self._get_planet_house(chart_data, l9)
        h10 = self._get_planet_house(chart_data, l10)
        return h9 == h10 and h9 != -1

    def _detect_amala_yoga(self, chart_data: dict) -> bool:
        # Benefic in 10th from Lagna
        for b in ["jupiter", "venus", "mercury", "moon"]:
            if self._get_planet_house(chart_data, b) == 10:
                return True
        return False

    # --- EDUCATION ---
    def _detect_saraswati_yoga(self, chart_data: dict) -> bool:
        for b in ["jupiter", "venus", "mercury"]:
            h = self._get_planet_house(chart_data, b)
            if not (self._is_kendra(h) or self._is_trikona(h) or h == 2):
                return False
        return self._get_planet_dignity(chart_data, "jupiter") in ["own_sign", "exalted"]

    def _detect_vidya_yoga(self, chart_data: dict) -> bool:
        # Benefics in 5th house
        for b in ["jupiter", "venus", "mercury"]:
            if self._get_planet_house(chart_data, b) == 5:
                return True
        return False

    # --- MARRIAGE ---
    def _detect_kalatra_yoga(self, chart_data: dict) -> bool:
        d_ven = self._get_planet_dignity(chart_data, "venus")
        l7 = self._get_lord_of_house(chart_data, 7)
        d_l7 = self._get_planet_dignity(chart_data, l7) if l7 else "neutral"
        return d_ven in ["own_sign", "exalted"] and d_l7 in ["own_sign", "exalted"]

    def _detect_saubhagya_yoga(self, chart_data: dict) -> bool:
        l7 = self._get_lord_of_house(chart_data, 7)
        l9 = self._get_lord_of_house(chart_data, 9)
        if not l7 or not l9: return False
        return self._get_planet_house(chart_data, l7) == self._get_planet_house(chart_data, l9) and self._get_planet_house(chart_data, l7) != -1

    # --- CHILDREN ---
    def _detect_putra_yoga(self, chart_data: dict) -> bool:
        l5 = self._get_lord_of_house(chart_data, 5)
        if not l5: return False
        h5 = self._get_planet_house(chart_data, l5)
        d5 = self._get_planet_dignity(chart_data, l5)
        # Simply checking if 5th lord is strong for stub
        return d5 in ["own_sign", "exalted"] and h5 in [1, 5, 9, 10, 11]

    def _detect_santana_yoga(self, chart_data: dict) -> bool:
        l5 = self._get_lord_of_house(chart_data, 5)
        if not l5: return False
        h5 = self._get_planet_house(chart_data, l5)
        hj = self._get_planet_house(chart_data, "jupiter")
        return h5 == hj and h5 != -1

    # --- SPIRITUAL ---
    def _detect_moksha_yoga(self, chart_data: dict) -> bool:
        return self._get_planet_house(chart_data, "ketu") == 12

    def _detect_sanyasa_yoga(self, chart_data: dict) -> bool:
        houses = {}
        for p, data in chart_data.get("planets", {}).items():
            if p not in ["rahu", "ketu"]:
                h = data.get("house")
                houses[h] = houses.get(h, 0) + 1
        return any(v >= 4 for v in houses.values())

    def _detect_parivraja_yoga(self, chart_data: dict) -> bool:
        # Moon aspected by Saturn (simplification: moon and saturn same house or opposite)
        h_moon = self._get_planet_house(chart_data, "moon")
        h_sat = self._get_planet_house(chart_data, "saturn")
        if h_moon == -1 or h_sat == -1: return False
        diff = abs(h_moon - h_sat)
        return diff == 0 or diff == 6
