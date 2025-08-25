from flask import Flask, request, jsonify
from shopping_list_manager import ShoppingListManager
from recipe_loader import load_recipes

app = Flask(__name__)

# Initialize the shopping list manager and load recipes
shopping_list_manager = ShoppingListManager()
recipes = load_recipes('data/Recipes.csv')

@app.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    ingredient = data.get('ingredient')
    if not ingredient:
        return jsonify({"error": "No ingredient provided"}), 400
        
    shopping_list_manager.add_ingredient(ingredient)
    return jsonify({
        "message": "Ingredient added",
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)