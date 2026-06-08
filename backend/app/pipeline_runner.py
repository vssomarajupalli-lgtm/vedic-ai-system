from app.parsers.json_normalizer import JsonNormalizer
from app.engines.planet_strength_engine import PlanetStrengthEngine
from app.engines.house_strength_engine import HouseStrengthEngine
from app.engines.varga_engine import VargaEngine
from app.engines.dasha_engine import DashaEngine
from app.engines.rasi_strength_engine import RasiStrengthEngine
from app.engines.ashtakavarga_engine import AshtakavargaEngine
from app.engines.master_probability_engine import MasterProbabilityEngine
from app.engines.natal_promise_engine import NatalPromiseEngine
from app.engines.transit_engine import TransitEngine
from app.engines.yoga_engine import YogaEngine
from app.utils.ephemeris_service import EphemerisService
from app.config.astrology_constants import SIGNS_IN_ORDER

class PipelineRunner:
    """
    Lightweight deterministic execution pipeline prototype.
    Connects the extraction normalizer and calculation engines 
    into a predictable, stateless execution flow.
    """

    def __init__(self):
        # Initialize the stateless modules
        self.normalizer      = JsonNormalizer()
        self.planet_engine   = PlanetStrengthEngine()
        self.house_engine    = HouseStrengthEngine()
        self.varga_engine    = VargaEngine()
        self.dasha_engine    = DashaEngine()
        self.rasi_engine     = RasiStrengthEngine()
        self.av_engine       = AshtakavargaEngine()
        self.natal_engine    = NatalPromiseEngine()
        self.transit_engine  = TransitEngine()
        self.yoga_engine     = YogaEngine()
        self.master_engine   = MasterProbabilityEngine()
        self.ephemeris       = EphemerisService()

    def process(self, raw_input_data: dict) -> dict:
        """
        Executes the strict calculation pipeline sequentially.
        
        Args:
            raw_input_data (dict): The messy, unformatted dictionary scraped from the PDF.
            
        Returns:
            dict: The unified deterministic output payload containing all engine results.
        """
        # 1. Normalize the raw data into our strict deterministic schema
        normalized_payload = self.normalizer.normalize(raw_input_data)
        
        # 2. Planet Engine Execution (Foundation Layer)
        planet_results = {}
        for planet_id, planet_data in normalized_payload.get("planets", {}).items():
            planet_results[planet_id] = self.planet_engine.calculate_strength(planet_data)
            
        # 3. Safe Dependency Passing & House Engine Execution
        house_results = {}
        for house_id, house_data in normalized_payload.get("houses", {}).items():
            
            # Result-passing strategy: Extract the lord's name (e.g., "mars", "sun")
            lord_name = house_data.get("lord", "unknown")
            
            # Fetch the previously calculated lord score safely.
            # If the lord is missing due to a parser error, fallback to a neutral 50.
            lord_score = 50
            if lord_name in planet_results:
                lord_score = planet_results[lord_name].get("final_score", 50)
            
            # Create a shallow copy to preserve D1 immutability
            house_eval_payload = dict(house_data)
            house_eval_payload["lord_strength_score"] = lord_score

            # Calculate house strength using copied payload
            house_results[str(house_id)] = self.house_engine.calculate_strength(
            house_eval_payload
)

        # 3.5. Yoga Engine Execution
        # Requires pre-computed planet results to calculate true yoga potency
        yoga_results = self.yoga_engine.evaluate(normalized_payload, planet_results, house_results)
            
        # 4. Varga Engine Execution (Phase 5 Refinement)
        # Safely pass the D1 planet scores as read-only dependencies
        varga_results = self.varga_engine.evaluate(normalized_payload, dependency_scores=planet_results)

        # 5. Dasha Engine Execution (Temporal Activation Layer)
        # Passes normalized dasha data and D1 planet scores as read-only dependencies.
        # DashaEngine evaluates MD/AD relationship and timing multipliers only.
        dasha_results = self.dasha_engine.evaluate(normalized_payload, dependency_scores=planet_results)

        # 6. Rasi Strength Engine (Sign Environment Layer)
        # Passes planet scores and varga outputs as read-only dependencies.
        # RasiStrengthEngine never re-calculates planets — reads pre-computed scores only.
        rasi_results = self.rasi_engine.evaluate(
            normalized_payload,
            dependency_scores=planet_results,
            varga_outputs=varga_results
        )

        # 7. Ashtakavarga Engine (Bindu Validation Layer)
        # Processes extracted SAV/BAV data. Produces planet modifiers,
        # dasha BAV confidence, SAV house analysis, and consistency audit.
        av_results = self.av_engine.evaluate(
            normalized_payload,
            dependency_scores=planet_results
        )

        # 7.5 BAV Modifier Injection (Environmental Layer)
        # Applies AshtakavargaEngine modifiers to final planet scores and
        # dasha timing multipliers. This is the ONLY place BAV modifiers are
        # consumed. All upstream engines (House, Rasi, Dasha) correctly used
        # the unmodified D1 structural scores — BAV is an environmental weight
        # layer applied to the reported output, not to intermediate calculations.
        # Source: VEDIC_AI_MASTER_ARCHITECTURE.md — "Dasha uses Ashtakavarga Support"
        self._apply_bav_modifiers(planet_results, dasha_results, av_results)

        # 8. Master Probability Engine (Synthesis Layer)
        # Combines all engine outputs into a single weighted probability score.
        # Weights: Natal Promise 40% | Planet 15% | House 10% | Rasi 10%
        #          Varga 10% | Dasha 10% | Transit 5%
        # Transit is the only remaining stub — returns neutral 50 until TransitEngine is built.
        engine_outputs = {
            "planets":      planet_results,
            "houses":       house_results,
            "vargas":       varga_results,
            "dashas":       dasha_results,
            "rasis":        rasi_results,
            "ashtakavarga": av_results
        }

        # 8. Natal Promise Engine (Domain Promise Layer)
        # Evaluates birth chart promise for 8 life domains using 6-factor formula.
        # Reads normalized_payload["houses"] directly for occupant/lord detection.
        natal_results = self.natal_engine.evaluate(
            planet_results    = planet_results,
            house_results     = house_results,
            rasi_results      = rasi_results,
            varga_results     = varga_results,
            av_results        = av_results,
            yoga_results      = yoga_results,
            normalized_houses = normalized_payload.get("houses", {})
        )
        engine_outputs["natal_promise"] = natal_results

        # 7.75 Transit Engine (Timing Layer)
        # 1. Fetch stateless sidereal planet transits for "right now"
        raw_transits = self.ephemeris.generate_transit_snapshot()
        
        # 2. Contextualize transits using the native's D1 Lagna
        # Formula: house = ((transit_sign - lagna_sign + 12) % 12) + 1
        asc_sign = normalized_payload.get("metadata", {}).get("ascendant_sign", "aries").lower()
        try:
            lagna_idx = SIGNS_IN_ORDER.index(asc_sign)
        except ValueError:
            lagna_idx = 0
            
        contextual_transits = {"planets": {}}
        for p, data in raw_transits.get("planets", {}).items():
            try:
                t_sign_idx = SIGNS_IN_ORDER.index(data["sign"])
                house = ((t_sign_idx - lagna_idx + 12) % 12) + 1
            except ValueError:
                house = 1
            # Merge with raw ephemeris data
            contextual_transits["planets"][p] = {**data, "house": house}

        # 3. Evaluate transit impact using pre-computed natal + timing scores
        transit_results = self.transit_engine.evaluate(
            transit_payload       = contextual_transits,
            natal_payload         = normalized_payload,
            dasha_results         = dasha_results,
            av_results            = av_results,
            natal_promise_results = natal_results,
        )
        engine_outputs["transit"] = transit_results
        
        # Add yoga results to outputs for the master engine
        engine_outputs["yogas"] = yoga_results

        # 9. Master Probability Engine (Synthesis Layer)
        # Combines all engine outputs into a single weighted probability score.
        # natal_promise factor now uses real domain scores (stub replaced).
        master_result = self.master_engine.evaluate(engine_outputs)

        # 9. Combine and Return Standardized Outputs
        final_output = {
            "metadata":           normalized_payload.get("metadata", {}),
            "master_probability": master_result,
            "engine_outputs":     engine_outputs
        }
        print("PipelineRunner Final Output Score:", final_output["master_probability"]["final_score"])
        return final_output

    # -------------------------------------------------------------------------
    # Step 7.5 — BAV Modifier Injection
    # -------------------------------------------------------------------------

    def _apply_bav_modifiers(
        self,
        planet_results: dict,
        dasha_results:  dict,
        av_results:     dict
    ) -> None:
        """
        Applies AshtakavargaEngine engine_modifiers to planet final_scores
        and dasha timing_multipliers. Mutates both dicts in-place.

        Planet BAV — three fields written atomically per planet:
            base_score   = original D1 structural score (preserved, never lost)
            bav_modifier = signed BAV adjustment (+5 / 0 / -5)
            final_score  = clamp(base_score + bav_modifier, 0, 100)

        All three fields are always written together so the score is fully
        explainable at every layer: D1 structural → BAV environment → final.

        Dasha BAV Multiplier:
            timing_multiplier      = base_timing_multiplier × bav_multiplier
            base_timing_multiplier = pre-BAV relationship multiplier (preserved)
            bav_multiplier         = AV timing confidence scalar

        Architecture Rule: This method contains zero astrological logic.
        It is pure orchestration — reading AV outputs and writing to other
        engine result dicts. All calculation is done inside the engines.
        """
        modifiers = av_results.get("engine_modifiers", {})

        # --- Planet BAV score adjustments ---
        bav_adjustments = modifiers.get("planet_score_adjustments", {})
        for planet, bav_modifier in bav_adjustments.items():
            if planet not in planet_results:
                continue
            base_score  = planet_results[planet].get("final_score", 0)
            final_score = max(0, min(100, base_score + bav_modifier))
            # Write all three fields atomically — full explainability preserved
            planet_results[planet]["base_score"]  = base_score    # original D1 score
            planet_results[planet]["bav_modifier"] = bav_modifier  # environmental layer
            planet_results[planet]["final_score"]  = final_score   # combined output

        # --- Dasha BAV confidence multiplier ---
        bav_mult = modifiers.get("dasha_bav_confidence_multiplier", 1.0)
        for lord, lord_data in dasha_results.items():
            temporal = lord_data.get("temporal_activation", {})
            if "timing_multiplier" not in temporal:
                continue
            base_mult  = temporal["timing_multiplier"]
            adj_mult   = round(base_mult * bav_mult, 4)
            temporal["timing_multiplier"]      = adj_mult
            temporal["base_timing_multiplier"] = base_mult
            temporal["bav_multiplier"]         = bav_mult

# --- Sample Execution Example ---
if __name__ == "__main__":
    import json
    
    # Simulated raw extraction payload (Before Phase 1 PDF integration)
    sample_raw_pdf_data = {
        "raw_metadata": {
            "name": "Pipeline Test Native",
            "lagna": "Mesha"
        },
        "raw_planets": {
            "Surya": {
                "sign": "Mesha",
                "house": "1",
                "house_type": "kendra",
                "dignity": "exalted"
            },
            "Kuja": { # Mars
                "sign": "Vrishchika",
                "house": "8",
                "house_type": "dusthana",
                "dignity": "own_sign"
            }
        },
        "raw_vargas": {
            "D9": {
                "planets": {
                    "Surya": {
                        "sign": "Tula",          # D1 Aries -> D9 Libra (Debilitated) = Contradicted
                        "dignity": "debilitated"
                    },
                    "Kuja": {
                        "sign": "Vrishchika",    # D1 Scorpio -> D9 Scorpio = Vargottama
                        "dignity": "own_house"
                    }
                }
            }
        }
    }
    
    runner = PipelineRunner()
    unified_output = runner.process(sample_raw_pdf_data)
    
    print(json.dumps(unified_output, indent=2))