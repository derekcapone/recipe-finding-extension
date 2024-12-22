import spacy
from rapidfuzz import process, fuzz
import logging_config, logging
import database_driver

# Get logger instance
logger = logging.getLogger(__name__)

# Retrieve the normalized ingredient list from MongoDB and convert it to list of strings
norm_ingredients_list = database_driver.get_normalized_ingredients()
normalized_ingredients_strings = sorted([ingredient["normalized_name"] for ingredient in norm_ingredients_list])


def normalize_ingredient_list(ingredients_to_normalize):
    """
    Generates new sorted list of normalized ingredient names
    :param ingredients_to_normalize: list of ingredient name strings to normalize
    :return: list[string] containing normalized ingredient names
    """
    normalized_list = []
    for ingredient in ingredients_to_normalize:
        new_ingredient_name = match_normalized_single_ingredient(ingredient)
        normalized_list.append(new_ingredient_name)

    return sorted(normalized_list)


def match_normalized_single_ingredient(ingredient_to_check):
    # TODO: Make this function better for finding accurate ingredient matches
    # Try a fuzzy string match, return ingredient if only one match is hit
    sublist = process.extractOne(ingredient_to_check, normalized_ingredients_strings, score_cutoff=70, scorer=fuzz.ratio)
    if sublist is None:
        logger.info(f"{ingredient_to_check} was not found in database")
        # Add to database and return ingredient as written
        # TODO: Implement Recipe Scraping better so that we can actually continually scrape and insert
        # normalized_ingredients_strings.append(ingredient_to_check)
        # database_driver.insert_normalized_ingredient(ingredient_to_check)
        return ingredient_to_check
    elif sublist[0] != ingredient_to_check:
        logger.info(f"Non-exact match between {ingredient_to_check}-{sublist[0]} with score ")
        return sublist[0]
    else:
        logger.info(f"Exact match for {ingredient_to_check}")
        return ingredient_to_check


def check_ingredient_name_similarity(ing1, ing2):
    """
    Helper function to manually check similarity values
    """
    result = fuzz.ratio(ing1, ing2)
    print(f"Similarity between {ing1} - {ing2}: {result}")


if __name__ == "__main__":
    ingredient = "smooth peanut butter"

    match_normalized_single_ingredient(ingredient)


