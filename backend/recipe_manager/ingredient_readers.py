from abc import ABC, abstractmethod

class IngredientReaderInterface(ABC):
    @abstractmethod
    def get_and_unroll_ingredients(self):
        """
        Retrieves all existing ingredients and their aliases, unrolls them into a single list
        Used for direct string matching
        """
        pass

    @abstractmethod
    def get_all_ingredients(self):
        """
        Retrieves all ingredients but keeps them in format of:
        { "name": "ingredient_name", "alias": [] }
        """
        pass