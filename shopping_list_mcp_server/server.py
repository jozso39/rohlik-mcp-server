from flask import Flask, request, jsonify
from shopping_list_manager import ShoppingListManager
from recipe_loader import load_recipes

app = Flask(__name__)

# Initialize the shopping list manager and load recipes
shopping_list_manager = ShoppingListManager()
recipes = load_recipes('data/Recipes.csv')

# Cache all unique ingredients for fast lookup
all_ingredients = set()
for recipe in recipes:
    if recipe.get('ingredients'):
        all_ingredients.update(recipe['ingredients'])

# Cache all unique diet types for fast lookup
all_diet_types = set()
for recipe in recipes:
    if recipe.get('diet'):
        all_diet_types.update(recipe['diet'])

@app.route('/get_all_ingredients', methods=['GET'])
def get_all_ingredients():
    """Get all unique ingredients from all recipes."""
    return jsonify({
        "count": len(all_ingredients),
        "ingredients": sorted(all_ingredients)
    }), 200

@app.route('/get_all_diets', methods=['GET'])
def get_all_diets():
    """Get all unique diet types from all recipes."""
    return jsonify({
        "count": len(all_diet_types),
        "diets": sorted(all_diet_types)
    }), 200

@app.route('/get_shopping_list', methods=['GET'])
def get_shopping_list():
    return jsonify({"shopping_list": shopping_list_manager.get_list()}), 200

@app.route('/get_recipes', methods=['GET'])
def get_recipes_route():
    return jsonify({"recipes": recipes}), 200

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

@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    diet = request.args.get('diet')
    meal_type = request.args.get('meal_type')
    name = request.args.get('name')
    includes_ingredients = request.args.get('includes_ingredients')
    excludes_ingredients = request.args.get('excludes_ingredients')
    
    if not any([diet, meal_type, name, includes_ingredients, excludes_ingredients]):
        return jsonify({"error": "Please provide at least one search parameter: 'diet', 'meal_type', 'name', 'includes_ingredients', or 'excludes_ingredients'"}), 400
    
    filtered_recipes = recipes.copy()
    
    if diet:
        filtered_recipes = [
            recipe for recipe in filtered_recipes 
            if recipe.get('diet') and any(d.lower() == diet.lower() for d in recipe['diet'])
        ]
    
    if meal_type:
        filtered_recipes = [
            recipe for recipe in filtered_recipes 
            if recipe.get('meal_type') and any(m.lower() == meal_type.lower() for m in recipe['meal_type'])
        ]
    
    if name:
        filtered_recipes = [
            recipe for recipe in filtered_recipes 
            if 'name' in recipe and recipe['name'] and name.lower() in recipe['name'].lower()
        ]
    
    if includes_ingredients:
        # Parse comma-separated ingredients and normalize case
        required_ingredients = [ing.strip().lower() for ing in includes_ingredients.split(',') if ing.strip()]
        filtered_recipes = [
            recipe for recipe in filtered_recipes
            if recipe.get('ingredients') and all(
                any(req_ing in recipe_ing.lower() for recipe_ing in recipe['ingredients'])
                for req_ing in required_ingredients
            )
        ]
    
    if excludes_ingredients:
        # Parse comma-separated ingredients and normalize case
        excluded_ingredients = [ing.strip().lower() for ing in excludes_ingredients.split(',') if ing.strip()]
        filtered_recipes = [
            recipe for recipe in filtered_recipes
            if recipe.get('ingredients') and not any(
                any(excl_ing in recipe_ing.lower() for recipe_ing in recipe['ingredients'])
                for excl_ing in excluded_ingredients
            )
        ]
    
    return jsonify({
        "count": len(filtered_recipes),
        "recipes": filtered_recipes
    }), 200

@app.route('/clear_shopping_list', methods=['POST'])
def clear_shopping_list():
    shopping_list_manager.clear_list()
    return jsonify({"message": "Shopping list cleared"}), 200

# New endpoint to remove ingredients from the shopping list
@app.route('/remove_ingredients', methods=['POST'])
def remove_ingredients():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    ingredients = data.get('ingredients')
    if ingredients is None:
        return jsonify({"error": "No ingredients provided"}), 400

    if not isinstance(ingredients, list):
        return jsonify({"error": "Ingredients must be an array"}), 400

    if not ingredients:
        return jsonify({"error": "Ingredients array is empty"}), 400

    shopping_list_manager.remove_ingredients(ingredients)

    return jsonify({
        "shopping_list": shopping_list_manager.get_list()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=8001)