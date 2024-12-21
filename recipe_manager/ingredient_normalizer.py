import spacy
from rapidfuzz import process, fuzz
import logging_config, logging
import database_driver


# Load the pre-trained spacy model
nlp = spacy.load("en_core_web_lg")

# Get logger instance
logger = logging.getLogger(__name__)

# Retrieve the normalized ingredient list from MongoDB and convert it to list of strings
norm_ingredients_list = database_driver.get_normalized_ingredients()
normalized_ingredients_strings = sorted([ingredient["normalized_name"] for ingredient in norm_ingredients_list])


def match_normalized_ingredients(ingredient_to_check):
    # Try a fuzzy string match, return ingredient if only one match is hit
    sublist = process.extractOne(ingredient_to_check, normalized_ingredients_strings, score_cutoff=80)
    if sublist is None:
        logger.info(f"{ingredient_to_check} was not found in database")
        # Add to database and return ingredient as written
        # TODO: Implement Recipe Scraping better so that we can actually continually scrape and insert
        # normalized_ingredients_strings.append(ingredient_to_check)
        # database_driver.insert_normalized_ingredient(ingredient_to_check)
        return ingredient_to_check
    elif sublist[0] != ingredient_to_check:
        logger.info(f"Non-exact match between {ingredient_to_check}-{sublist[0]}")
        return sublist[0]
    else:
        logger.info(f"Exact match for {ingredient_to_check}")
        return ingredient_to_check

    ### Then do an NLP check
    # TODO: Make this function better for finding accurate ingredient matches
    # highest_similarity = 0.0
    # matching_ingredient = ""
    # for ingredient in sub_ingredient_list:
    #     if ingredient == ingredient_to_check:
    #         # Exact match found, return with exact match
    #         return ingredient
    #     isSimilar, similarity = nlp_similarity_check(ingredient, ingredient_to_check)
    #     logger.debug(f"NLP: {ingredient} vs {ingredient_to_check}: Similarity={similarity:.2f}, isSimilar={isSimilar}")
    #     if isSimilar and similarity > highest_similarity:
    #         matching_ingredient = ingredient
    #         highest_similarity = similarity
    # return matching_ingredient if highest_similarity != 0 else matching_ingredient


def nlp_similarity_check(ingredient1, ingredient2, threshold=0.85):
    """
    Compare two ingredient names for similarity.
    :param ingredient1: First ingredient name (string)
    :param ingredient2: Second ingredient name (string)
    :param threshold: Similarity threshold (default is 0.85)
    :return: (True/False for match, similarity score)
    """
    doc1 = nlp(ingredient1)
    doc2 = nlp(ingredient2)
    similarity = doc1.similarity(doc2)
    isSimilar = similarity >= threshold
    return isSimilar, similarity


if __name__ == "__main__":
    ingredient_list = ["reduced fat cheddar cheese", "Big fat cheesy guy"]
    ingredient = "cheese"

    # matchFound, ingredient_name = find_ingredient_from_list(ingredient_list, ingredient)
    # logger.warning(f"Ingredient match: {matchFound} for {ingredient_name}")
