import ingredient_normalizer
import database_driver

def find_similar_recipe(ingredient_request: dict):
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
    normalized_ingredient_list = ingredient_normalizer.normalize_ingredient_list(ingredient_request["ingredients_list"])
    smallest_difference = database_driver.get_ingredient_set_difference(normalized_ingredient_list)
    resulting_dict = smallest_difference[0]

    if ingredient_request["num_missing_ingredients_allowed"] > resulting_dict["difference_count"]:
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

    returned_object = find_similar_recipe(ingredient_request)
    print(returned_object)



    # Large list of integers
    # list1_int = list(range(100000))
    # list2_int = list(range(50000, 150000))
    #
    # # Large list of strings
    # list1_str = [str(i) for i in list1_int]
    # list2_str = [str(i) for i in list2_int]
    #
    # # Measure time for integers
    # start = time.time()
    # diff_int = set(list1_int) ^ set(list2_int)
    # end = time.time()
    # print(f"Time for integers: {end - start:.5f} seconds")
    #
    # # Measure time for strings
    # start = time.time()
    # diff_str = set(list1_str) ^ set(list2_str)
    # end = time.time()
    # print(f"Time for strings: {end - start:.5f} seconds")