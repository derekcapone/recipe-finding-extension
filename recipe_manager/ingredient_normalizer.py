import spacy

# Load the pre-trained spacy model
nlp = spacy.load("en_core_web_md")


def find_ingredient_from_list(ingredient_list, ingredient_to_check):
    for ingredient in ingredient_list:
        print(ingredient)


def are_ingredients_similar(ingredient1, ingredient2, threshold=0.85):
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
    print(f"Are ingredients similar? {isSimilar} (Similarity Score: {similarity:.2f})")
    return isSimilar, similarity


if __name__ == "__main__":
    ingredient_list = ["olive oil", "chicken breast", "butter", "margarine"]
    ingredient = "extra virgin olive oil"

    find_ingredient_from_list(ingredient_list, ingredient)
