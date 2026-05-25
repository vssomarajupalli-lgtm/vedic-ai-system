from app.parsers.json_normalizer import JsonNormalizer
from app.engines.planet_strength_engine import PlanetStrengthEngine
from app.engines.house_strength_engine import HouseStrengthEngine
from app.engines.varga_engine import VargaEngine

class PipelineRunner:
    """
    Lightweight deterministic execution pipeline prototype.
    Connects the extraction normalizer and calculation engines 
    into a predictable, stateless execution flow.
    """

    def __init__(self):
        # Initialize the stateless modules
        self.normalizer = JsonNormalizer()
        self.planet_engine = PlanetStrengthEngine()
        self.house_engine = HouseStrengthEngine()
        self.varga_engine = VargaEngine()

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
            
        # 4. Varga Engine Execution (Phase 5 Refinement)
        # Safely pass the D1 planet scores as read-only dependencies
        varga_results = self.varga_engine.evaluate(normalized_payload, dependency_scores=planet_results)
            
        # 5. Combine and Return Standardized Outputs
        return {
            "metadata": normalized_payload.get("metadata", {}),
            "engine_outputs": {
                "planets": planet_results,
                "houses": house_results,
                "vargas": varga_results
            }
        }

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