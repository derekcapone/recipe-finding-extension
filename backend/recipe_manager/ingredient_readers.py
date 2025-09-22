from abc import ABC, abstractmethod
from typing import List, Dict

class IngredientReaderInterface(ABC):
    @abstractmethod
    def get_and_unroll_ingredients(self) -> List[str]:
        """
        Retrieves all existing ingredients and their aliases, unrolls them into a single list
        Used for direct string matching
        """
        pass

    @abstractmethod
    def get_all_ingredients(self) -> List[Dict]:
        """
        Retrieves all ingredients but keeps them in format of:
        { "name": "ingredient_name", "alias": [] }
        """
        pass