from typing import List, Dict, Optional
from app.formulas.schema import FormulaSchema
from app.formulas.registry_data import get_seed_registry
from app.formulas.validator import FormulaValidator

class FormulaNotFoundError(Exception):
    pass

class FormulaRepositoryLoader:
    def __init__(self):
        self._formulas: Dict[str, FormulaSchema] = {}
        self._load_registry()

    def _load_registry(self):
        """
        Loads the formula definitions and validates them.
        """
        # Load the seed data
        formulas_list = get_seed_registry()
        
        # Validate all formulas (checks for duplicates, invalid engines, etc)
        FormulaValidator.validate_all(formulas_list)
        
        # Cache them internally
        for f in formulas_list:
            self._formulas[f.formula_key] = f

    def get_formula(self, formula_key: str) -> FormulaSchema:
        """
        Retrieve a formula by key.
        Raises FormulaNotFoundError if the key does not exist.
        """
        formula = self._formulas.get(formula_key)
        if not formula:
            raise FormulaNotFoundError(f"Formula with key '{formula_key}' not found in repository.")
        return formula

    def list_formulas(self) -> List[FormulaSchema]:
        """
        Return all loaded formulas.
        """
        return list(self._formulas.values())

# Global instance for app usage
formula_repository_loader = FormulaRepositoryLoader()
