import recipe_manager

def test_find_ingredient_from_list():
    ingredient_to_check = "spaghetti squash"

    match_found, ingredient_name = recipe_manager.match_normalized_single_ingredient(ingredient_to_check)
    print(f"Matched ingredients: {ingredient_to_check} - {ingredient_name}")
