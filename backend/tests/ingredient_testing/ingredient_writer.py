import json
from collections import defaultdict
import os

# Path to your JSON file
json_file = "baseline_ingredient_list.json"


def append_ingredient(ingredient_to_add):
    # Ensure the file exists; create it with an empty list if not
    if not os.path.exists(json_file):
        with open(json_file, 'w') as f:
            json.dump([], f, indent=2)

    # Load the current data
    with open(json_file, 'r') as f:
        data = json.load(f)

    for ingredient in data:
        if ingredient_to_add["name"] == ingredient["name"]:
            print(f"Ingredient already exists: {ingredient_to_add['name']}")
            return

    # Append the new ingredient to the list
    data.append(new_ingredient)

    # Write the updated list back to the file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Added: {new_ingredient}")


def append_aliases(ingredient_name, new_aliases):
    # Ensure the file exists and initialize with empty list if not
    if not os.path.exists(json_file):
        with open(json_file, 'w') as f:
            json.dump([], f, indent=2)

    # Load existing data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Normalize aliases to avoid duplicates and preserve casing
    ingredient_found = False
    for item in data:
        if item["name"] == ingredient_name:
            current_aliases = set(item.get("alias", []))
            item["alias"] = list(current_aliases.union(new_aliases))
            ingredient_found = True
            break

    if not ingredient_found:
        print(f"Ingredient '{ingredient_name}' not found.")
        return

    # Write the updated data back
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"[+] Appended aliases to '{ingredient_name}': {new_aliases}")


def print_baseline_ingredients():
    # Ensure the file exists and initialize with empty list if not
    if not os.path.exists(json_file):
        with open(json_file, 'w') as f:
            json.dump([], f, indent=2)

    # Load existing data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Normalize aliases to avoid duplicates and preserve casing
    ingredient_found = False
    for item in data:
        print(item["name"])

def find_duplicate_ingredients():
    with open(json_file, 'r') as f:
        data = json.load(f)

    name_map = defaultdict(list)

    # Map each name to a list of its indices in the file
    for idx, item in enumerate(data):
        name = item.get("name")
        if name:
            name_map[name].append(idx)

    # Filter only those with more than one occurrence
    duplicates = {name: indices for name, indices in name_map.items() if len(indices) > 1}

    if duplicates:
        print("[!] Duplicate ingredients found:")
        for name, indices in duplicates.items():
            print(f" - '{name}' at indices {indices}")
    else:
        print("[✓] No duplicates found.")

    return duplicates

def get_and_unroll_ingredients():
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Initialize the final list of ingredients
    ingredient_list = []

    # Loop through each ingredient in the JSON
    for item in data:
        # Add the ingredient name itself
        ingredient_list.append(item["name"])

        # Add all aliases associated with the ingredient
        ingredient_list.extend(item.get("alias", []))

    return ingredient_list

if __name__ == "__main__":
    ingredients = get_and_unroll_ingredients()
    for ing in ingredients:
        print(ing)

    # ### Create Ingredient ###
    # new_ingredient = {
    #     "name": "olive oil",
    #     "alias": ["extra virgin olive oil"]
    # }
    #
    # append_ingredient(new_ingredient)
    # exit()
    #
    #
    # ### Append alias ###
    # ingredient_to_append_alias = "olive oil"
    # aliases = [
    #     "salted butter",
    #     "margarine"
    # ]
    #
    # append_aliases(ingredient_to_append_alias, aliases)
