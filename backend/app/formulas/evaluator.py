from typing import Dict, Any, List
from app.formulas.schema import FormulaSchema, FormulaEvaluationResult

class FormulaEvaluator:
    @staticmethod
    def extract_signals(payload: Dict[str, Any], required_signals: List[str]) -> Dict[str, Any]:
        """
        Plucks only the specific variables defined in a formula's required_signals.
        """
        isolated = {}
        
        def find_keys(d: Dict[str, Any], keys_to_find: set) -> Dict[str, Any]:
            found = {}
            for k, v in d.items():
                if k in keys_to_find:
                    found[k] = v
                elif isinstance(v, dict):
                    found.update(find_keys(v, keys_to_find))
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            found.update(find_keys(item, keys_to_find))
            return found

        isolated = find_keys(payload, set(required_signals))
        return isolated

    @staticmethod
    def check_engine_degradation(formula: FormulaSchema, payload: Dict[str, Any]) -> List[str]:
        """
        Checks if required engines actually populated data.
        """
        warnings = []
        for engine in formula.required_engines:
            engine_key = engine.replace("Engine", "").lower()
            if engine_key == "natalpromise":
                engine_key = "natal_promise"
                
            # Allow flexible matching for engine keys
            found = False
            for k in payload.keys():
                if engine_key in k.lower():
                    found = True
                    break
                    
            if not found:
                warnings.append(f"Engine Degradation: {engine} output is missing.")
        return warnings

    @staticmethod
    def evaluate(formula: FormulaSchema, chart_response: Any) -> FormulaEvaluationResult:
        # Convert response to dict for extraction
        if isinstance(chart_response, dict):
            payload = chart_response
        else:
            try:
                payload = chart_response.model_dump()
            except AttributeError:
                payload = dict(chart_response)
            
        system_warnings = FormulaEvaluator.check_engine_degradation(formula, payload)
        
        # Missing payload handling (Risk-FR-05)
        isolated_signals = FormulaEvaluator.extract_signals(payload, formula.required_signals)
        for sig in formula.required_signals:
            if sig not in isolated_signals:
                system_warnings.append(f"Missing Payload: requested signal '{sig}' not found.")
        
        # Boolean condition evaluation
        fulfilled_layers = 0
        total_layers = len(formula.required_confidence_layers)
        
        for layer in formula.required_confidence_layers:
            is_fulfilled = True
            
            # Simulated boolean mapping: if degradation impacts the layer, mark False
            if "dasha" in layer.lower() and any("DashaEngine" in w for w in system_warnings):
                is_fulfilled = False
                
            if is_fulfilled:
                fulfilled_layers += 1
                
        # Confidence layer evaluation & Matrix Resolution (Pure Boolean Gating)
        final_state = "MIXED"
        is_degraded = len(system_warnings) > 0
        
        if total_layers > 0:
            if is_degraded:
                final_state = "MIXED"  # Force neutral if degraded
            elif fulfilled_layers == total_layers:
                final_state = "FAVORABLE"
            elif fulfilled_layers == 0:
                final_state = "UNFAVORABLE"
            else:
                final_state = "MIXED"
        
        return FormulaEvaluationResult(
            final_state=final_state,
            isolated_signals=isolated_signals,
            answer_template_key=formula.answer_template_key,
            system_warnings=system_warnings
        )
