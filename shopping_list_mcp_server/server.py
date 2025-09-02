from flask import Flask, request, jsonify
from .shopping_list_manager import ShoppingListManager
from .recipe_loader import load_recipes
# Import ChromaDB integration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chroma_flask_integration import semantic_search, ingredient_search, filter_search, is_chroma_available

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

@app.route('/get_recipe_names', methods=['GET'])
def get_recipe_names():
    """Get all recipe names from all recipes."""
    recipe_names = [recipe['name'] for recipe in recipes if recipe.get('name')]
    return jsonify({
        "count": len(recipe_names),
        "recipe_names": sorted(recipe_names)
    }), 200

@app.route('/get_shopping_list', methods=['GET'])
def get_shopping_list():
    return jsonify({"shopping_list": shopping_list_manager.get_list()}), 200

@app.route('/get_recipes', methods=['GET'])
def get_recipes_route():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Fixed limit of 10 recipes per page
    
    # Calculate pagination
    total_recipes = len(recipes)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    # Get paginated recipes
    paginated_recipes = recipes[start_index:end_index]
    
    # Calculate pagination info
    total_pages = (total_recipes + per_page - 1) // per_page  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return jsonify({
        "recipes": paginated_recipes,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_recipes,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    }), 200

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
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Fixed limit of 10 recipes per page
    
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
    
    # Apply pagination to filtered results
    total_filtered = len(filtered_recipes)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_recipes = filtered_recipes[start_index:end_index]
    
    # Calculate pagination info
    total_pages = (total_filtered + per_page - 1) // per_page  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return jsonify({
        "recipes": paginated_recipes,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_filtered,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
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

# ChromaDB Semantic Search Routes
@app.route('/semantic_search_by_text', methods=['GET'])
def semantic_search_by_text():
    """Semantic search by text query"""
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    limit = min(int(request.args.get('limit', 10)), 50)
    
    recipe_names = semantic_search(query, limit)
    
    return jsonify({
        'query': query,
        'recipe_names': recipe_names,
        'count': len(recipe_names),
        'chroma_available': is_chroma_available(),
        'message': 'Use /search_recipes?name=<recipe_name> for full details'
    })

@app.route('/semantic_search_by_ingredient', methods=['GET'])
def semantic_search_by_ingredient():
    """Semantic search by ingredient"""
    ingredient = request.args.get('ingredient')
    if not ingredient:
        return jsonify({'error': 'Ingredient parameter required'}), 400
    
    limit = min(int(request.args.get('limit', 10)), 50)
    
    recipe_names = ingredient_search(ingredient, limit)
    
    return jsonify({
        'ingredient': ingredient,
        'recipe_names': recipe_names,
        'count': len(recipe_names),
        'chroma_available': is_chroma_available(),
        'message': 'Use /search_recipes?includes_ingredients=<ingredient> for full details'
    })

@app.route('/semantic_search_by_diet', methods=['GET'])
def semantic_search_by_diet():
    """Semantic search by diet type"""
    diet = request.args.get('diet')
    if not diet:
        return jsonify({'error': 'Diet parameter required'}), 400
    
    limit = min(int(request.args.get('limit', 10)), 50)
    
    recipe_names = filter_search(diet=diet, limit=limit)
    
    return jsonify({
        'diet': diet,
        'recipe_names': recipe_names,
        'count': len(recipe_names),
        'chroma_available': is_chroma_available(),
        'message': 'Use /search_recipes?diet=<diet> for full details'
    })

@app.route('/semantic_search_by_meal_type', methods=['GET'])
def semantic_search_by_meal_type():
    """Semantic search by meal type"""
    meal_type = request.args.get('meal_type')
    if not meal_type:
        return jsonify({'error': 'Meal type parameter required'}), 400
    
    limit = min(int(request.args.get('limit', 10)), 50)
    
    recipe_names = filter_search(meal_type=meal_type, limit=limit)
    
    return jsonify({
        'meal_type': meal_type,
        'recipe_names': recipe_names,
        'count': len(recipe_names),
        'chroma_available': is_chroma_available(),
        'message': 'Use /search_recipes?meal_type=<meal_type> for full details'
    })

@app.route('/semantic_search_by_name', methods=['GET'])
def semantic_search_by_name():
    """Semantic search by recipe name (alias for text search)"""
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name parameter required'}), 400
    
    limit = min(int(request.args.get('limit', 10)), 50)
    
    recipe_names = semantic_search(name, limit)
    
    return jsonify({
        'name': name,
        'recipe_names': recipe_names,
        'count': len(recipe_names),
        'chroma_available': is_chroma_available(),
        'message': 'Use /search_recipes?name=<recipe_name> for full details'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8001)