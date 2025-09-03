# Shopping List MCP Server

This project implements a **Model Context Protocol (MCP) server** that provides AI assistants with tools for managing shopping lists and searching recipes. The server follows the MCP specification 2025-06-18 and uses JSON-RPC 2.0 for communication.

It was created to serve a [Rohlík AI ReAct Agent](https://github.com/jozso39/rohlik-agent-js). Both projects are created as an interview assignment to [Rohlík](https://www.rohlik.cz/) company. There is no intention to deploy this code or use it in production.

## Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python run_mcp_server.py
```

The MCP server communicates via **stdio** using **JSON-RPC 2.0** protocol. It's designed to be integrated with MCP-compatible AI assistants.

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
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "clientInfo": {"name": "test-client", "version": "1.0.0"}, "capabilities": {}}}' | python run_mcp_server.py

# List available tools  
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | python run_mcp_server.py

# Search for vegetarian recipes
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_recipes", "arguments": {"diet": "vegetarian", "limit": 3}}}' | python run_mcp_server.py
```

## Testing

```bash
# Activate virtual environment first
source venv/bin/activate

# Run comprehensive MCP tests
python test_mcp_client.py
```

## TODO: Future Enhancements

- integrating a more robust database solution (e.g., SQLite or PostgreSQL) for better data management as the project scales.
- user authentication
