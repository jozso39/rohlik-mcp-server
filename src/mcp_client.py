import requests
from typing import List, Optional, Dict, Union, TypedDict

class Recipe(TypedDict):
    id: str
    name: str
    ingredients: List[str]
    steps: str
    diet: List[str]
    meal_type: List[str]

class RecipeSearchResponse(TypedDict):
    count: int
    recipes: List[Recipe]

class ShoppingListResponse(TypedDict):
    shopping_list: List[str]

class MessageResponse(TypedDict):
    message: str

class RecipesResponse(TypedDict):
    recipes: List[Recipe]

class ShoppingListMessageResponse(TypedDict):
    message: str
    shopping_list: List[str]

class ShoppingListMCPClient:
    """Client for interacting with the Shopping List MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url.rstrip('/')

    def get_all_recipes(self) -> RecipesResponse:
        """Get all available recipes.
        
        Returns:
            Dict containing a list of recipes
        """
        response = requests.get(f"{self.base_url}/get_recipes")
        response.raise_for_status()
        return response.json()

    def search_recipes(self, 
                      diet: Optional[str] = None, 
                      meal_type: Optional[str] = None, 
                      name: Optional[str] = None) -> RecipeSearchResponse:
        """Search for recipes using various criteria.
        
        Args:
            diet: Filter by diet category (e.g., "vegetarian", "vegan", "high-protein")
            meal_type: Filter by meal type (e.g., "polévka", "hlavní chod", "desert")
            name: Search by recipe name (partial match)
            
        Returns:
            Dict containing count and list of matching recipes
            
        Raises:
            ValueError: If no search parameters are provided
            requests.HTTPError: If the server returns an error
        """
        if not any([diet, meal_type, name]):
            raise ValueError("At least one search parameter (diet, meal_type, or name) must be provided")
        
        params = {}
        if diet:
            params['diet'] = diet
        if meal_type:
            params['meal_type'] = meal_type
        if name:
            params['name'] = name
            
        response = requests.get(f"{self.base_url}/search_recipes", params=params)
        response.raise_for_status()
        return response.json()

    def add_ingredients(self, ingredients: List[str]) -> ShoppingListMessageResponse:
        """Add ingredients to the shopping list.
        
        Args:
            ingredients: List of ingredients to add
            
        Returns:
            Dict containing success message and current shopping list
            
        Raises:
            ValueError: If ingredients list is empty
            requests.HTTPError: If the server returns an error
        """
        if not ingredients:
            raise ValueError("Ingredients list cannot be empty")
            
        response = requests.post(
            f"{self.base_url}/add_ingredients",
            json={"ingredients": ingredients}
        )
        response.raise_for_status()
        return response.json()

    def get_shopping_list(self) -> ShoppingListResponse:
        """Get the current shopping list.
        
        Returns:
            Dict containing the current shopping list
        """
        response = requests.get(f"{self.base_url}/get_shopping_list")
        response.raise_for_status()
        return response.json()

    def clear_shopping_list(self) -> MessageResponse:
        """Clear all items from the shopping list.
        
        Returns:
            Dict containing success message
        """
        response = requests.post(f"{self.base_url}/clear_shopping_list")
        response.raise_for_status()
        return response.json()

# Example usage:
if __name__ == "__main__":
    # Create client
    client = ShoppingListMCPClient()
    
    # Example: Search for vegetarian desserts
    results = client.search_recipes(diet="vegetarian", meal_type="desert")
    print(f"Found {results['count']} vegetarian desserts:")
    for recipe in results['recipes']:
        print(f"- {recipe['name']}")
    
    # Example: Add ingredients from first recipe to shopping list
    if results['recipes']:
        recipe = results['recipes'][0]
        client.add_ingredients(recipe['ingredients'])
        print(f"\nAdded ingredients for {recipe['name']} to shopping list:")
        shopping_list = client.get_shopping_list()
        for item in shopping_list['shopping_list']:
            print(f"- {item}")
