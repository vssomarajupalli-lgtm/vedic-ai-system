class JsonNormalizer:
    """
    Transforms raw, unformatted extraction data into the stable, 
    deterministic JSON schema required by the astrology engines.
    Acts as a firewall preventing parser bugs from crashing calculations.
    """
    
    def __init__(self):
        # Dictionaries to map common PDF variations to standard system keys
        self.planet_map = {
            "su": "sun", "surya": "sun", 
            "mo": "moon", "chandra": "moon",
            "ma": "mars", "mangala": "mars", "kuja": "mars",
            "me": "mercury", "budha": "mercury",
            "ju": "jupiter", "guru": "jupiter",
            "ve": "venus", "shukra": "venus",
            "sa": "saturn", "shani": "saturn",
            "ra": "rahu",
            "ke": "ketu"
        }
        
        self.sign_map = {
            # --- Aries ---
            "ar": "aries", "ari": "aries", "mesha": "aries", "mesh": "aries",

            # --- Taurus ---
            "ta": "taurus", "tau": "taurus",
            "vrishabha": "taurus", "vrishaba": "taurus", "vrushabha": "taurus",

            # --- Gemini ---
            "ge": "gemini", "gem": "gemini",
            "mithuna": "gemini", "mithun": "gemini", "mithunam": "gemini",

            # --- Cancer ---
            "ca": "cancer", "can": "cancer",
            "kataka": "cancer", "karka": "cancer", "karkataka": "cancer",
            "katakam": "cancer",

            # --- Leo ---
            "le": "leo",
            "simha": "leo", "singh": "leo", "simham": "leo",

            # --- Virgo ---
            "vi": "virgo", "vir": "virgo",
            "kanya": "virgo", "kani": "virgo", "kanyam": "virgo",

            # --- Libra ---
            "li": "libra", "lib": "libra",
            "tula": "libra", "thula": "libra", "tulam": "libra",

            # --- Scorpio ---
            "sc": "scorpio", "sco": "scorpio",
            "vrishchika": "scorpio", "vrischika": "scorpio", "vrischikam": "scorpio",
            "vruschika": "scorpio", "scorpius": "scorpio",

            # --- Sagittarius ---
            "sa": "sagittarius", "sag": "sagittarius",
            "dhanu": "sagittarius", "dhanus": "sagittarius", "dhanush": "sagittarius",
            "dhanussu": "sagittarius",

            # --- Capricorn ---
            "cp": "capricorn", "cap": "capricorn",
            "makara": "capricorn", "makar": "capricorn", "makaram": "capricorn",

            # --- Aquarius ---
            "aq": "aquarius", "aqu": "aquarius",
            "kumbha": "aquarius", "kumbam": "aquarius",

            # --- Pisces ---
            "pi": "pisces", "pis": "pisces",
            "meena": "pisces", "meen": "pisces", "meenam": "pisces",
            "meena rasi": "pisces",
        }

    def normalize(self, raw_data: dict) -> dict:
        """Main entry point to normalize a complete raw extraction dictionary."""
        print("====== DEBUG START ======")
        print("JsonNormalizer received keys:", list(raw_data.keys()))
        normalized_planets = self._normalize_planets(raw_data.get("raw_planets") or raw_data.get("planets", {}))
        print("Normalized Planets Count:", len(normalized_planets))
        return {
            "metadata": self._normalize_metadata(raw_data.get("raw_metadata") or raw_data.get("metadata") or raw_data.get("birth_data", {})),
            "planets": normalized_planets,
            "houses": self._normalize_houses(raw_data.get("raw_houses") or raw_data.get("houses", {})),
            "vargas": self._normalize_vargas(raw_data.get("raw_vargas") or raw_data.get("vargas", {}), normalized_planets),
            "ashtakavarga": self._normalize_ashtakavarga(raw_data.get("raw_ashtakavarga") or raw_data.get("ashtakavarga", {})),
            "dashas": self._normalize_dashas(raw_data.get("raw_dashas") or raw_data.get("dashas", {})),
            "transits": {         # Placeholder for Phase 7 Transit Engine
                "active_modifiers": []
            }
        }

    def _normalize_metadata(self, raw_metadata: dict) -> dict:
        return {
            "name": self._clean_string(raw_metadata.get("name", "Unknown")),
            "ascendant_sign": self._clean_name(raw_metadata.get("lagna", ""), self.sign_map) or "aries",
            "ascendant_degree": self._extract_float(raw_metadata.get("lagna_degree", 0.0))
        }

    def _normalize_planets(self, raw_planets: dict) -> dict:
        normalized = {}
        for raw_name, p_data in raw_planets.items():
            std_name = self._clean_name(raw_name, self.planet_map)
            if not std_name:
                continue  # Skip junk rows that aren't planets
                
            normalized[std_name] = {
                "name": std_name,
                "sign": self._clean_name(p_data.get("sign", ""), self.sign_map),
                "degree": self._extract_float(p_data.get("degree", 0.0)),
                "nakshatra": self._clean_string(p_data.get("nakshatra", "")),
                "house": self._extract_int(p_data.get("house", 0)),
                "house_type": self._clean_string(p_data.get("house_type", "neutral")),
                "dignity": self._clean_string(p_data.get("dignity", "neutral")),
                "is_retrograde": self._extract_boolean(p_data.get("retrograde")),
                "is_combust": self._extract_boolean(p_data.get("combust")),
                "conjunctions": [self._clean_name(c, self.planet_map) for c in p_data.get("conjunctions", []) if self._clean_name(c, self.planet_map)],
                "benefic_aspects_count": self._extract_int(p_data.get("benefic_aspects", 0)),
                "malefic_aspects_count": self._extract_int(p_data.get("malefic_aspects", 0)),
                "aspected_by": [self._clean_name(a, self.planet_map) for a in p_data.get("aspected_by", []) if self._clean_name(a, self.planet_map)],
                "varga_data": {},
                "bav_points": self._extract_int(p_data.get("bav", 0))
            }
        return normalized

    def _normalize_vargas(self, raw_vargas: dict, d1_planets: dict) -> dict:
        """Structures Varga data and automatically detects Vargottama alignments."""
        normalized = {}
        for varga_id, varga_data in raw_vargas.items():
            v_id = varga_id.upper() # e.g., "D9", "D10"
            normalized[v_id] = {"planets": {}}
            
            for raw_name, p_data in varga_data.get("planets", {}).items():
                std_name = self._clean_name(raw_name, self.planet_map)
                if not std_name:
                    continue # Skip junk
                    
                varga_sign = self._clean_name(p_data.get("sign", ""), self.sign_map)
                d1_sign = d1_planets.get(std_name, {}).get("sign", "")
                
                normalized[v_id]["planets"][std_name] = {
                    "sign": varga_sign,
                    "dignity": self._clean_string(p_data.get("dignity", "neutral")),
                    "is_vargottama": bool(varga_sign and d1_sign and varga_sign == d1_sign)
                }
        return normalized

    def _normalize_dashas(self, raw_dashas: dict) -> dict:
        """Structures the active time periods extracted from the PDF timeline."""
        return {
            "mahadasha": {
                "lord": self._clean_name(raw_dashas.get("mahadasha", ""), self.planet_map)
            },
            "antardasha": {
                "lord": self._clean_name(raw_dashas.get("antardasha", ""), self.planet_map)
            },
            "pratyantardasha": {
                "lord": self._clean_name(raw_dashas.get("pratyantardasha", ""), self.planet_map)
            }
        }

    def _normalize_houses(self, raw_houses: dict) -> dict:
        """
        Normalizes raw house data for all 12 bhavas.

        Accepts the raw_houses dict passed through by HoroscopeSourceLoader.
        Each key is a house number string ("1"–"12").

        Normalized fields per house:
            house        (int)  : House number 1–12
            house_type   (str)  : Kendra / Trikona / Dusthana / Upachaya / Neutral
            sign         (str)  : Zodiac sign of the house (normalized via sign_map)
            lord         (str)  : Ruling planet (normalized via planet_map)
            occupants    (list) : Planets present in the house (planet_map normalized)
            aspected_by  (list) : Planets aspecting the house (planet_map normalized)
            sav_points   (int)  : Sarvashtakavarga bindus (0 if absent)

        Houses with missing or unparseable keys receive safe neutral defaults.
        Houses beyond 1–12 range are silently rejected.
        """
        normalized = {}

        for raw_key, h_data in raw_houses.items():
            # --- Validate and extract house number ---
            house_num = self._extract_int(raw_key)
            if house_num < 1 or house_num > 12:
                continue  # Reject out-of-range keys defensively

            if not isinstance(h_data, dict):
                continue  # Reject malformed entries

            # --- Normalize occupants: raw planet names → standard system names ---
            raw_occupants = h_data.get("occupants", [])
            occupants = [
                self._clean_name(p, self.planet_map)
                for p in raw_occupants
                if self._clean_name(p, self.planet_map)
            ]

            # --- Normalize aspected_by: same planet_map pass-through ---
            raw_aspects = h_data.get("aspected_by", [])
            aspected_by = [
                self._clean_name(p, self.planet_map)
                for p in raw_aspects
                if self._clean_name(p, self.planet_map)
            ]

            # --- Assemble normalized house record ---
            normalized[str(house_num)] = {
                "house":       house_num,
                "house_type":  self._clean_string(h_data.get("house_type", "neutral")),
                "sign":        self._clean_name(h_data.get("sign", ""), self.sign_map),
                "lord":        self._clean_name(h_data.get("lord", ""), self.planet_map),
                "occupants":   occupants,
                "aspected_by": aspected_by,
                "sav_points":  self._extract_int(h_data.get("sav_points", 0))
            }

        return normalized

    def _normalize_ashtakavarga(self, raw_av: dict) -> dict:
        """
        Normalizes the raw Ashtakavarga data extracted by HoroscopeSourceLoader.

        SAV Chart normalization:
            - Keys normalized to str(1)–str(12)
            - Bindu values coerced to int via _extract_int()

        BAV Charts normalization:
            - Planet name keys normalized through planet_map
            - House keys normalized to str(1)–str(12)
            - Bindu values coerced to int via _extract_int()
            - Rahu and Ketu are excluded (no BAV charts in classical Parashari AV)
            - Out-of-range house keys (< 1 or > 12) silently rejected

        Returns safe empty dicts on missing or malformed input.
        """
        if not raw_av or not isinstance(raw_av, dict):
            return {"sav_chart": {}, "bav_charts": {}}

        # --- Normalize SAV chart ---
        sav_normalized = {}
        for raw_house, bindus in raw_av.get("sav_chart", {}).items():
            house_num = self._extract_int(raw_house)
            if 1 <= house_num <= 12:
                sav_normalized[str(house_num)] = self._extract_int(bindus)

        # --- Normalize BAV charts ---
        # Classical Parashari AV includes 7 planets (excludes Rahu/Ketu)
        excluded_planets = {"rahu", "ketu"}
        bav_normalized = {}

        for raw_planet, house_bindus in raw_av.get("bav_charts", {}).items():
            std_planet = self._clean_name(raw_planet, self.planet_map)
            if not std_planet or std_planet in excluded_planets:
                continue
            if not isinstance(house_bindus, dict):
                continue

            planet_bav = {}
            for raw_house, bindus in house_bindus.items():
                house_num = self._extract_int(raw_house)
                if 1 <= house_num <= 12:
                    planet_bav[str(house_num)] = self._extract_int(bindus)

            if planet_bav:
                bav_normalized[std_planet] = planet_bav

        return {
            "sav_chart":  sav_normalized,
            "bav_charts": bav_normalized
        }

    # --- Isolated Helper Methods ---

    def _clean_string(self, val: any) -> str:
        return str(val).strip().lower() if val else ""

    def _clean_name(self, val: str, mapping_dict: dict) -> str:
        cleaned = self._clean_string(val)
        return mapping_dict.get(cleaned, cleaned)

    def _extract_float(self, val: any) -> float:
        try: return float(val)
        except (ValueError, TypeError): return 0.0

    def _extract_int(self, val: any) -> int:
        try: return int(float(val)) # float cast first handles strings like "14.0"
        except (ValueError, TypeError): return 0

    def _extract_boolean(self, val: any) -> bool:
        if isinstance(val, bool): return val
        return str(val).strip().lower() in ["true", "yes", "y", "1", "r", "retrograde", "c", "combust"]