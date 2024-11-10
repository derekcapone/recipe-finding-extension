from flask import Flask, request, jsonify
import request_handler

app = Flask(__name__)


# Route to handle GET requests for "get_recipes"
@app.route('/get_recipes', methods=['GET'])
def get_recipes():
    request_handler.external_function()
    return "These are recipes!"


# Route to handle POST requests for "set_pantry_essentials"
@app.route('/set_pantry_essentials', methods=['POST'])
def set_pantry_essentials():
    return "Setting pantry essentials..."


# Route to handle GET requests for "get_recipe_links"
@app.route('/get_recipe_links', methods=['GET'])
def get_recipe_links():
    return "Getting recipe links..."


if __name__ == '__main__':
    app.run(debug=True)