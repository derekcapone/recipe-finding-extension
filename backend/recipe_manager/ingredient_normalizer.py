from ingredient_parser import parse_ingredient, parse_multiple_ingredients

class IngredientNormalizer:
    @staticmethod
    def trim_ingredient_string(ingredient_string: str) -> str | None:
        # Use foundation foods for extra trimming
        parsed_ingredient = parse_ingredient(ingredient_string, foundation_foods=True)

        ingredient_text = ""
        # Grab the foundation food if it exists
        if parsed_ingredient.foundation_foods:
            ingredient_text = parsed_ingredient.foundation_foods[0].text
            print(f"Foundation food: {ingredient_text}")

        # If regular ingredient does not exist, return None
        if not parsed_ingredient.name:
            print(f"Could not find ingredient name in ingredient string: {ingredient_string}")
            return None
        elif ingredient_text == "":
            ingredient_text = parsed_ingredient.name[0].text
            print(f"Regular ingredient: {ingredient_text}")

        return ingredient_text




if __name__ == "__main__":
    ingredient_strings = [
        "1 teaspoon Mexican oregano",
        "2 tablespoons packed light brown sugar",
        "cooking spray",
        "2 pounds ground chuck",
        "1 cup flour",
        "butter or olive oil, 1 tbsp",
        "chicken thigh",
        "1 (16 ounce) package pasta",
        "2 tablespoons olive oil",
        "½ cup chopped onion",
        "2 ½ tablespoons pesto",
        "salt to taste",
        "ground black pepper to taste",
        "2 tablespoons grated Parmesan cheese",
        "1 large organic cucumber",
        "2 pounds 85% lean ground beef",
        "1 (12-ounce) package frozen mixed vegetables",
        "1 1/2 cups lower-sodium beef broth",
    ]

    for ingredient in ingredient_strings:
        IngredientNormalizer.trim_ingredient_string(ingredient)