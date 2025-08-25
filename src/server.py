from flask import Flask, request, jsonify
from shopping_list_manager import ShoppingListManager
from recipe_loader import load_recipes

app = Flask(__name__)

# Initialize the shopping list manager and load recipes
shopping_list_manager = ShoppingListManager()
recipes = load_recipes('data/Recipes.csv')

@app.route('/add_ingredients', methods=['POST'])
def add_ingredients():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    ingredients = data.get('ingredients')
    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400
    
    if not isinstance(ingredients, list):
        return jsonify({"error": "Ingredients must be an array"}), 400
    
    if not ingredients:
        return jsonify({"error": "Ingredients array is empty"}), 400
    
    for ingredient in ingredients:
        shopping_list_manager.add_ingredient(ingredient)
    
    return jsonify({
        "message": f"{len(ingredients)} ingredients added",
        "shopping_list": shopping_list_manager.get_list()
    }), 200

@app.route('/get_shopping_list', methods=['GET'])
def get_shopping_list():
    return jsonify({"shopping_list": shopping_list_manager.get_list()}), 200

@app.route('/clear_shopping_list', methods=['POST'])
def clear_shopping_list():
    shopping_list_manager.clear_list()
    return jsonify({"message": "Shopping list cleared"}), 200

@app.route('/get_recipes', methods=['GET'])
def get_recipes_route():
    return jsonify({"recipes": recipes}), 200

@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    tag = request.args.get('tag')
    name = request.args.get('name')
    
    if not tag and not name:
        return jsonify({"error": "Please provide either 'tag' or 'name' parameter"}), 400
    
    filtered_recipes = recipes.copy()
    
    if tag:
        filtered_recipes = [
            recipe for recipe in filtered_recipes 
            if tag.lower() in [t.lower() for t in recipe['tags']]
        ]
    
    if name:
        filtered_recipes = [
            recipe for recipe in filtered_recipes 
            if name.lower() in recipe['name'].lower()
        ]
    
    return jsonify({
        "count": len(filtered_recipes),
        "recipes": filtered_recipes
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)