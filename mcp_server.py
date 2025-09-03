#!/usr/bin/env python3
"""
MCP Server Implementation for Recipe and Shopping List Management
Uses the official Model Context Protocol Python SDK
"""

import asyncio
import json
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    ServerCapabilities,
    ToolsCapability
)

# Import our existing business logic
from shopping_list_mcp_server.shopping_list_manager import ShoppingListManager
from shopping_list_mcp_server.recipe_loader import load_recipes

# Initialize business logic
shopping_list_manager = ShoppingListManager()
recipes = load_recipes('data/Recipes.csv')

# Cache ingredients and diets for quick lookup
all_ingredients = set()
all_diet_types = set()
all_meal_types = set()

for recipe in recipes:
    if recipe.get('ingredients'):
        all_ingredients.update(recipe['ingredients'])
    if recipe.get('diet'):
        all_diet_types.update(recipe['diet'])
    if recipe.get('meal_type'):
        all_meal_types.update(recipe['meal_type'])

# Create the MCP server
server = Server("rohlik-recipe-shopping-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="search_recipes",
            description="Search for recipes based on various criteria including diet, meal type, ingredients, and name",
            inputSchema={
                "type": "object",
                "properties": {
                    "diet": {
                        "type": "string",
                        "description": "Filter by diet type (e.g., 'vegetarian', 'vegan', 'high-protein')"
                    },
                    "meal_type": {
                        "type": "string", 
                        "description": "Filter by meal type (e.g., 'polévka', 'hlavní chod', 'desert')"
                    },
                    "name": {
                        "type": "string",
                        "description": "Search recipes by name (partial match)"
                    },
                    "includes_ingredients": {
                        "type": "string",
                        "description": "Comma-separated list of ingredients that must be present"
                    },
                    "excludes_ingredients": {
                        "type": "string", 
                        "description": "Comma-separated list of ingredients that must NOT be present"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recipes to return (default: 10, max: 50)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_shopping_list", 
            description="Get the current shopping list",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="add_ingredients_to_shopping_list",
            description="Add ingredients to the shopping list",
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ingredients to add to shopping list"
                    }
                },
                "required": ["ingredients"]
            }
        ),
        Tool(
            name="remove_ingredients_from_shopping_list",
            description="Remove ingredients from the shopping list", 
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ingredients to remove from shopping list"
                    }
                },
                "required": ["ingredients"]
            }
        ),
        Tool(
            name="clear_shopping_list",
            description="Clear all ingredients from the shopping list",
            inputSchema={
                "type": "object", 
                "properties": {}
            }
        ),
        Tool(
            name="get_recipe_details",
            description="Get detailed information about a specific recipe by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_name": {
                        "type": "string",
                        "description": "Exact name of the recipe to get details for"
                    }
                },
                "required": ["recipe_name"]
            }
        ),
        Tool(
            name="get_all_ingredients",
            description="Get all available ingredients from the recipe database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_all_diet_types", 
            description="Get all available diet types from the recipe database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_all_meal_types", 
            description="Get all available meal types from the recipe database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution"""
    
    if name == "search_recipes":
        result = search_recipes(arguments)
    elif name == "get_shopping_list":
        result = get_shopping_list()
    elif name == "add_ingredients_to_shopping_list":
        result = add_ingredients_to_shopping_list(arguments)
    elif name == "remove_ingredients_from_shopping_list": 
        result = remove_ingredients_from_shopping_list(arguments)
    elif name == "clear_shopping_list":
        result = clear_shopping_list()
    elif name == "get_recipe_details":
        result = get_recipe_details(arguments)
    elif name == "get_all_ingredients":
        result = get_all_ingredients()
    elif name == "get_all_diet_types":
        result = get_all_diet_types()
    elif name == "get_all_meal_types":
        result = get_all_meal_types()
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [
        TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )
    ]

# Tool implementations
def search_recipes(args: dict) -> dict:
    """Search recipes with various filters"""
    diet = args.get('diet')
    meal_type = args.get('meal_type')
    name = args.get('name')
    includes_ingredients = args.get('includes_ingredients')
    excludes_ingredients = args.get('excludes_ingredients')
    limit = min(args.get('limit', 10), 50)
    
    filtered_recipes = recipes.copy()
    
    # Apply filters (same logic as REST API)
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
        required_ingredients = [ing.strip().lower() for ing in includes_ingredients.split(',') if ing.strip()]
        filtered_recipes = [
            recipe for recipe in filtered_recipes
            if recipe.get('ingredients') and all(
                any(req_ing in recipe_ing.lower() for recipe_ing in recipe['ingredients'])
                for req_ing in required_ingredients
            )
        ]
    
    if excludes_ingredients:
        excluded_ingredients = [ing.strip().lower() for ing in excludes_ingredients.split(',') if ing.strip()]
        filtered_recipes = [
            recipe for recipe in filtered_recipes
            if recipe.get('ingredients') and not any(
                any(excl_ing in recipe_ing.lower() for recipe_ing in recipe['ingredients'])
                for excl_ing in excluded_ingredients
            )
        ]
    
    # Apply limit and pagination
    limited_recipes = filtered_recipes[:limit]
    
    return {
        "recipes": limited_recipes,
        "total_found": len(filtered_recipes),
        "returned": len(limited_recipes),
        "filters_applied": {
            "diet": diet,
            "meal_type": meal_type,
            "name": name,
            "includes_ingredients": includes_ingredients,
            "excludes_ingredients": excludes_ingredients,
            "limit": limit
        }
    }

def get_shopping_list() -> dict:
    """Get current shopping list"""
    return {
        "shopping_list": shopping_list_manager.get_list(),
        "count": len(shopping_list_manager.get_list())
    }

def add_ingredients_to_shopping_list(args: dict) -> dict:
    """Add ingredients to shopping list"""
    ingredients = args.get('ingredients', [])
    if not isinstance(ingredients, list):
        raise ValueError("Ingredients must be an array")
    
    for ingredient in ingredients:
        shopping_list_manager.add_ingredient(ingredient)
    
    return {
        "message": f"{len(ingredients)} ingredients processed",
        "shopping_list": shopping_list_manager.get_list(),
        "count": len(shopping_list_manager.get_list())
    }

def remove_ingredients_from_shopping_list(args: dict) -> dict:
    """Remove ingredients from shopping list"""
    ingredients = args.get('ingredients', [])
    if not isinstance(ingredients, list):
        raise ValueError("Ingredients must be an array")
    
    shopping_list_manager.remove_ingredients(ingredients)
    
    return {
        "message": f"Removal of {len(ingredients)} ingredients attempted",
        "shopping_list": shopping_list_manager.get_list(),
        "count": len(shopping_list_manager.get_list())
    }

def clear_shopping_list() -> dict:
    """Clear shopping list"""
    shopping_list_manager.clear_list()
    return {
        "message": "Shopping list cleared",
        "shopping_list": [],
        "count": 0
    }

def get_recipe_details(args: dict) -> dict:
    """Get details for a specific recipe"""
    recipe_name = args.get('recipe_name')
    if not recipe_name:
        raise ValueError("Recipe name is required")
    
    # Find recipe by exact name match
    recipe = next((r for r in recipes if r.get('name') == recipe_name), None)
    if not recipe:
        return {
            "found": False,
            "message": f"Recipe '{recipe_name}' not found",
            "suggestion": "Use search_recipes to find similar recipes"
        }
    
    return {
        "found": True,
        "recipe": recipe
    }

def get_all_ingredients() -> dict:
    """Get all available ingredients"""
    return {
        "count": len(all_ingredients),
        "ingredients": sorted(list(all_ingredients))
    }

def get_all_diet_types() -> dict:
    """Get all available diet types"""
    return {
        "count": len(all_diet_types),
        "diet_types": sorted(list(all_diet_types))
    }

def get_all_meal_types() -> dict:
    """Get all available meal types"""
    return {
        "count": len(all_meal_types),
        "meal_types": sorted(list(all_meal_types))
    }

async def main():
    """Run the MCP server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rohlik-recipe-shopping-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(listChanged=False)
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
