from recipe_manager.ingredient_normalizer import IngredientNormalizer
from recipe_manager.mongodb_driver import DatabaseDriver
from tests.ingredient_testing.raw_json_ingredient_reader import RawJsonIngredientReader


class RecipeManager:
    def __init__(self):
        raw_ingredient_reader = RawJsonIngredientReader()
        self.ingredient_normalizer = IngredientNormalizer(raw_ingredient_reader)

        self.database_driver = DatabaseDriver()

    def find_similar_recipe(self, ingredient_request: dict):
        """
        Searches saved recipes to find the recipe(s) that most closely match the requested ingredients
        :param ingredient_request: Ingredient request dict from the Request Handler in the format below
        {
            "num_missing_ingredients_allowed": integer,
            "ingredients_list": list[string]
        }
        :return: Response object in the format below
        {
            "recipe": recipe_dict,
            "num_missing_ingredients": integer,
            "missing_ingredients": list[string],
            "success": True/False
        }
        """
        normalized_ingredient_list, _ = self.ingredient_normalizer.generate_normalized_ingredients(ingredient_request["ingredients_list"])
        smallest_difference = self.database_driver.get_ingredient_set_difference(normalized_ingredient_list)
        resulting_dict = smallest_difference[0]

        if ingredient_request["num_missing_ingredients_allowed"] < resulting_dict["difference_count"]:
            # Not allowed this many differences, return None
            return {"success": False}

        # Generate the response dict to the Request Handler
        recipe_dict = {
            "recipe": {
                "recipe_name": resulting_dict["recipe_name"],
                "source_url": resulting_dict["source_url"],
                "ingredients": resulting_dict["ingredients"]
            },
            "number_missing_ingredients": resulting_dict["difference_count"],
            "missing_ingredients": resulting_dict["difference_ingredients"],
            "success": True
        }
        return recipe_dict



if __name__ == "__main__":
    ingredient_request = {
        "num_missing_ingredients_allowed": 0,
        "ingredients_list": [
            "broccoli",
            "cheddar cheese",
            "chives",
            "cream",
            "egg",
            "pepper",
            "salt",
            "tomato"
        ]
    }

    recipe_manager = RecipeManager()
    print(recipe_manager)
