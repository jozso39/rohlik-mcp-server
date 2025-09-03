# Shopping List MCP Server

This project implements a **Model Context Protocol (MCP) server** that provides AI assistants with tools for managing shopping lists and searching recipes. The server follows the MCP specification 2025-06-18 and uses JSON-RPC 2.0 for communication.

The server provides both:
1. **MCP Server** (recommended) - Full MCP-compliant server with proper JSON-RPC 2.0 protocol
2. **Legacy REST API** - Simple Flask REST endpoints for backwards compatibility

It was created to serve a [Rohlík AI ReAct Agent](https://github.com/jozso39/rohlik-agent-js). Both projects are created as an interview assignment to [Rohlík](https://www.rohlik.cz/) company. There is no intention to deploy this code or use it in production.

## Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python mcp_server.py
```

The MCP server communicates via **stdio** using **JSON-RPC 2.0** protocol. It's designed to be integrated with MCP-compatible AI assistants.

### Legacy REST API
```bash
# Activate virtual environment first
source venv/bin/activate

# Run the Flask REST API server
python shopping_list_mcp_server/server.py
```

## MCP Server Features

### Tools Available
The MCP server provides 9 tools:

1. **`search_recipes`** - Search recipes by diet, meal type, ingredients, or name
2. **`get_shopping_list`** - Get the current shopping list
3. **`add_ingredients_to_shopping_list`** - Add ingredients to shopping list  
4. **`remove_ingredients_from_shopping_list`** - Remove ingredients from shopping list
5. **`clear_shopping_list`** - Clear all ingredients from shopping list
6. **`get_recipe_details`** - Get detailed information about a specific recipe
7. **`get_all_ingredients`** - Get all available ingredients from database
8. **`get_all_diet_types`** - Get all available diet types from database
9. **`get_all_meal_types`** - Get all available meal types from database

### Protocol Support
- **Protocol Version**: 2025-06-18
- **Transport**: stdio (stdin/stdout)
- **Message Format**: JSON-RPC 2.0
- **Capabilities**: Tools only (no prompts, resources, or completions)

### Database Content
- **Total Recipes**: 100 Czech recipes
- **Diet Types**: 8 available (vegetarian, vegan, high-protein, low-carb, masité, tučné, bezlepkové, bez laktozy)
- **Meal Types**: Multiple categories (polévka, hlavní chod, desert, příloha, etc.)
- **Ingredients**: 125+ unique ingredients in Czech language
- **Recipe Examples**: Bábovka s ořechy, Bramboračka, Hovězí guláš, etc.

### Example MCP Interaction
```bash
# Activate virtual environment first
source venv/bin/activate

# Initialize the server
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "clientInfo": {"name": "test-client", "version": "1.0.0"}, "capabilities": {}}}' | python mcp_server.py

# List available tools  
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | python mcp_server.py

# Search for vegetarian recipes
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_recipes", "arguments": {"diet": "vegetarian", "limit": 3}}}' | python mcp_server.py
```

## Testing

### Test MCP Server
```bash
# Activate virtual environment first
source venv/bin/activate

# Run comprehensive MCP tests
python test_mcp_client.py
```

### Test Legacy REST API
```bash
# Activate virtual environment first  
source venv/bin/activate

# Run REST API tests
python -m unittest tests/test_api.py
```

## Endpoints

### Get Shopping List
- **URL**: `/get_shopping_list`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "shopping_list": ["Mléko", "Cibule", "Chléb"]
    }
    ```

### Search Recipes
- **URL**: `/search_recipes`
- **Method**: `GET`
- **Query Parameters**:
  - `diet` (optional): Search recipes by diet category (e.g., "vegetarian", "vegan", "high-protein")
  - `meal_type` (optional): Search recipes by meal type (e.g., "polévka", "hlavní chod", "desert")
  - `name` (optional): Search recipes by name
  - `includes_ingredients` (optional): Comma-separated list of ingredients that must be present in the recipe (e.g., "Cibule,Máslo")
  - `excludes_ingredients` (optional): Comma-separated list of ingredients that must NOT be present in the recipe (e.g., "Mléko,Vejce")
  - `page` (optional): Page number for pagination (default: 1)
- **Note**: Results are limited to 10 recipes per page
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "recipes": [
            {
                "id": "12",
                "ingredients": ["Cibule", "Cukr krupice", "..."],
                "name": "Hrášková krémová polévka",
                "steps": "...",
                "diet": ["vegetarian"],
                "meal_type": ["polévka"]
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 25,
            "total_pages": 3,
            "has_next": true,
            "has_prev": false
        }
    }
    ```

### Get All Recipes
- **URL**: `/get_recipes`
- **Method**: `GET`
- **Query Parameters**:
  - `page` (optional): Page number for pagination (default: 1)
- **Note**: Results are limited to 10 recipes per page
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "recipes": [
            {
            "id": "10",
            "ingredients": [
                "Bobkový list",
                "Drcený kmín"
            ],
            "name": "Hovězí guláš s karlovarským knedlíkem",
            "steps": "...",
            "diet": ["masité", "high-protein"],
            "meal_type": ["hlavní chod"]
        }
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 100,
            "total_pages": 10,
            "has_next": true,
            "has_prev": false
        }
    }
    ```

### Get All Ingredients
- **URL**: `/get_all_ingredients`
- **Method**: `GET`
- **Description**: Get all unique ingredients from all recipes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "count": 125,
        "ingredients": ["Badyán", "Bobkový list", "Cibule", "Citron", "Cukr krupice", "..."]
    }
    ```

### Get All Diets
- **URL**: `/get_all_diets`
- **Method**: `GET`
- **Description**: Get all unique diet types from all recipes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "count": 8,
        "diets": ["bezlepkové", "high-protein", "low-carb", "masité", "tučné", "vegan", "vegetarian", "bez laktozy"]
    }
    ```

### Get Recipe Names
- **URL**: `/get_recipe_names`
- **Method**: `GET`
- **Description**: Get all recipe names from all recipes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "count": 100,
        "recipe_names": ["Alaskaská pizza", "Asijský burger", "Bramboračka", "Karbanátky", "..."]
    }
    ```

### Add Multiple Ingredients to Shopping List
- **URL**: `/add_ingredients`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
      "ingredients": ["Mléko", "Cibule", "Chléb"]
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "message": "3 ingredients added",
        "shopping_list": ["Mléko", "Cibule", "Chléb"]
    }
    ```

### Remove Ingredients from Shopping List
- **URL**: `/remove_ingredients`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
      "ingredients": ["Cibule", "Máslo", "Neexistuje"]
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "shopping_list": ["Mléko", "Chléb"]
    }
    ```

#### Clear Shopping List
- **URL**: `/clear_shopping_list`
- **Method**: `POST`
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "message": "Shopping list cleared"
    }
    ```

## TODO: Future Enhancements

- integrating a more robust database solution (e.g., SQLite or PostgreSQL) for better data management as the project scales.
- user authentication
