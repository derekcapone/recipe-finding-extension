import spacy
from rapidfuzz import fuzz

# Load the pre-trained spacy model
nlp = spacy.load("en_core_web_md")


def find_ingredient_from_list(ingredient_list, ingredient_to_check) -> (bool, str):
    """
    Uses fuzz matching and NLP to determine if the ingredient exists in the ingredient list
    """
    possible_matches = []
    # First get possible matches from NLP model
    for ingredient in ingredient_list:
        isSimilar, similarity = nlp_similarity_check(ingredient, ingredient_to_check)
        print(f"NLP: {ingredient} vs {ingredient_to_check}: Similarity={similarity:.2f}, isSimilar={isSimilar}")
        if isSimilar:
            possible_matches.append(ingredient)

    # If no matches were found then return False because no ingredients matched the threshold
    if len(possible_matches) == 0:
        return False, ""
    # If one match found, return that match
    elif len(possible_matches) == 1:
        return True, possible_matches[0]

    # Then go back through the list and get the highest fuzz match
    match_value = 0
    final_ingredient = ""
    for possible_match in possible_matches:
        new_match_value = fuzz.ratio(possible_match, ingredient_to_check)
        if new_match_value > match_value:
            final_ingredient = possible_match
            match_value = new_match_value



def nlp_similarity_check(ingredient1, ingredient2, threshold=0.8):
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
    ingredient_list = ["juice of lemon", "lime juice"]
    ingredient = "lemon juice"

    matchFound, ingredient_name = find_ingredient_from_list(ingredient_list, ingredient)
