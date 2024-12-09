import recipe_scraper

def test_check_recipe_links():
    """
    Basic test to ensure pytest is working
    """
    recipe_list = []
    checked_list = recipe_scraper.check_and_normalize_recipes(recipe_list)
    assert checked_list == recipe_list