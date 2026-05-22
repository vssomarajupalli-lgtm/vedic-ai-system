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
            "ar": "aries", "mesha": "aries",
            "ta": "taurus", "vrishabha": "taurus",
            # ... other signs will be added here
        }

    def normalize(self, raw_data: dict) -> dict:
        """Main entry point to normalize a complete raw extraction dictionary."""
        return {
            "metadata": self._normalize_metadata(raw_data.get("raw_metadata", {})),
            "planets": self._normalize_planets(raw_data.get("raw_planets", {})),
            "houses": {},         # Placeholder for House Engine extraction mapping
            "vargas": {},         # Placeholder for Phase 5 Varga Engine
            "ashtakavarga": {     # Placeholder for Phase 3/4 integration
                "sav_chart": {},
                "bav_charts": {}
            },
            "dashas": {           # Placeholder for Phase 6 Dasha Engine
                "current_mahadasha": None,
                "current_antardasha": None
            },
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
                "aspects_received": {
                    "benefic_aspects_count": self._extract_int(p_data.get("benefic_aspects", 0)),
                    "malefic_aspects_count": self._extract_int(p_data.get("malefic_aspects", 0)),
                    "aspected_by": [self._clean_name(a, self.planet_map) for a in p_data.get("aspected_by", []) if self._clean_name(a, self.planet_map)]
                },
                "varga_data": {},
                "bav_points": self._extract_int(p_data.get("bav", 0))
            }
        return normalized

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