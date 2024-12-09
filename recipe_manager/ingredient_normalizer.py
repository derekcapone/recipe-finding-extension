import spacy
import logging_config, logging

# Load the pre-trained spacy model
nlp = spacy.load("en_core_web_md")
logger = logging.getLogger(__name__)


def find_ingredient_from_list(ingredient_list, ingredient_to_check) -> (bool, str):
    """
    Uses NLP to determine if the ingredient exists in the ingredient list
    TODO: Make this more robust so that we ensure we are correlating the correct ingredient names
    """
    highest_similarity = 0.0
    matching_ingredient = ""
    for ingredient in ingredient_list:
        isSimilar, similarity = nlp_similarity_check(ingredient, ingredient_to_check)
        logger.debug(f"NLP: {ingredient} vs {ingredient_to_check}: Similarity={similarity:.2f}, isSimilar={isSimilar}")
        if isSimilar and similarity > highest_similarity:
            matching_ingredient = ingredient
            highest_similarity = similarity
    # Return (True, ingredient name) with the highest similarity score, or (False, "") if similarity threshold not reached
    return (True, matching_ingredient) if highest_similarity != 0 else (False, matching_ingredient)


def nlp_similarity_check(ingredient1, ingredient2, threshold=0.85):
    """
    Compare two ingredient names for similarity.

    :param ingredient1: First ingredient name (string)
    :param ingredient2: Second ingredient name (string)
    :param threshold: Similarity threshold (default is 0.85)
    :return: True if ingredients are similar, False otherwise
    """
    doc1 = nlp(ingredient1)
    doc2 = nlp(ingredient2)
    similarity = doc1.similarity(doc2)
    isSimilar = similarity >= threshold
    return isSimilar, similarity


if __name__ == "__main__":
    ingredient_list = ["jasdfa", "asdfht"]
    ingredient = "lemon juice"

    matchFound, ingredient_name = find_ingredient_from_list(ingredient_list, ingredient)
    logger.warning(f"Ingredient match: {matchFound} for {ingredient}")
