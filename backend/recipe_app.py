from flask import Flask, request, jsonify
import logging_config, logging
import database_driver
import recipe_manager
import json

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Route to handle GET requests for "get_recipes"
@app.route('/get_recipes', methods=['GET'])
def get_recipes():
    return "These are recipes!"


# Route to handle POST requests for "set_pantry_essentials"
@app.route('/set_pantry_essentials', methods=['POST'])
def set_pantry_essentials():
    # Get JSON data from the request body
    ingredient_data = request.get_json()

    database_driver.insert_pantry_essentials(ingredient_data)
    return "Setting pantry essentials..."


# Route to handle GET requests for "get_recipe_links"
@app.route('/get_recipe_links', methods=['GET'])
def get_recipe_links():
    request_object = request.get_json()
    matching_recipe = recipe_manager.find_similar_recipe(request_object)

    return json.dumps(matching_recipe)


if __name__ == '__main__':
    app.run(debug=True)