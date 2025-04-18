from fastapi import FastAPI, Request
import logging_config, logging
import database_driver
import recipe_manager
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow only your React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Route to handle GET requests for "get_recipes"
@app.get('/get_recipes')
async def get_recipes():
    return "These are recipes!"


# Route to handle POST requests for "set_pantry_essentials"
@app.post('/set_pantry_essentials')
async def set_pantry_essentials(request: Request):
    # Get JSON data from the request body
    ingredient_data = await request.json()

    database_driver.insert_pantry_essentials(ingredient_data)
    return "Setting pantry essentials..."


# Route to handle GET requests for "get_recipe_links"
@app.get('/get_recipe_links')
async def get_recipe_links(request: Request):
    request_object = await request.json()

    matching_recipe = recipe_manager.find_similar_recipe(request_object)
    return json.dumps(matching_recipe)
