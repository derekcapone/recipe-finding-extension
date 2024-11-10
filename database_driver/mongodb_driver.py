from pymongo import MongoClient

# Connect to MongoDB (use the default host and port)
client = MongoClient('mongodb://localhost:27017/')

# Select the database
db = client['RecipeDB']

print("Database driver connected to database and collection")

def insert_pantry_essentials(ingredient_item):
    try:
        # Select the collection (create if it doesn't exist)
        collection = db['pantryEssentials']

        # Insert a single document into the collection
        result = collection.insert_one(ingredient_item)
        print(f"Inserted item with ID: {result.inserted_id}")
    except Exception as e:
        # Print the type of the exception and the exception message
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")


if __name__ == "__main__":
    print("Hello world from database land")

    # 2. **Insert a Single Item (Document)**
    ingredient_item = {
        "name": "Apple",
        "quantity": 10,
        "unit": "pieces"
    }

    # 4. **Retrieve All Items**
    # Retrieve all documents from the collection
    all_items = collection.find()

    # Print each document
    for item in all_items:
        print(item)

    # 5. **Retrieve a Specific Item**
    # Find a document where the name is 'Apple'
    apple_item = collection.find_one({"name": "Apple"})
    print(f"Found apple item: {apple_item}")

    # 6. **Query with Filters**
    # Retrieve items with a quantity greater than 5
    items_above_5 = collection.find({"quantity": {"$gt": 5}})

    # Print these items
    print("Items with quantity greater than 5:")
    for item in items_above_5:
        print(item)

    # 7. **Update an Item**
    # Update the quantity of the 'Apple' item
    update_result = collection.update_one(
        {"name": "Apple"},  # Find the document with name "Apple"
        {"$set": {"quantity": 15}}  # Set the new quantity
    )

    print(f"Matched {update_result.matched_count} document(s) and modified {update_result.modified_count} document(s).")

    # 8. **Delete an Item**
    # Delete the 'Eggs' item
    delete_result = collection.delete_one({"name": "Eggs"})
    print(f"Deleted {delete_result.deleted_count} document(s).")
