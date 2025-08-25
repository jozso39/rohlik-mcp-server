# Shopping List MCP Server

This project implements a simple MCP (Meal Planning) server that serves as a database for managing shopping lists based on recipes. The server is built using Flask and interacts with a dataset of recipes stored in a CSV file.

## Project Structure

```
shopping-list-mcp-server
├── src
│   ├── server.py               # Main entry point for the MCP server
│   ├── shopping_list_manager.py # Logic for managing the shopping list
│   ├── recipe_loader.py         # Loads recipes from the CSV file
│   └── utils.py                 # Utility functions for the project
├── data
│   └── Recipes.csv              # Dataset of recipes
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd shopping-list-mcp-server
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the server:**
   Start the MCP server by running:
   ```
   python src/server.py
   ```

## Usage

Once the server is running, you can interact with it through HTTP requests. The server provides the following endpoints to manage the shopping list and recipes:

### API Endpoints

#### Get All Recipes
- **URL**: `/get_recipes`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "recipes": [
             {
            "author_note": "...",
            "id": "10",
            "ingredients": [
                "Bobkový list",
                "Drcený kmín"
            ],
            "name": "Roman Vaněk",
            "steps": "..."
        },
        ]
    }
    ```

#### Add Ingredient to Shopping List
- **URL**: `/add_ingredient`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
      "ingredient": "Mléko"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
        "message": "Ingredient added",
        "shopping_list": ["Mléko"]
    }
    ```
- **Error Responses**:
  - **Code**: 400
  - **Content**:
    ```json
    {"error": "Request must be JSON"}
    ```
    or
    ```json
    {"error": "Invalid JSON"}
    ```
    or
    ```json
    {"error": "No ingredient provided"}
    ```

#### Get Shopping List
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



### Example Usage with cURL

1. Add an ingredient:
```bash
curl -X POST http://localhost:5000/add_ingredient \
  -H "Content-Type: application/json" \
  -d '{"ingredient": "Mléko"}'
```

2. Get the shopping list:
```bash
curl http://localhost:5000/get_shopping_list
```

3. Clear the shopping list:
```bash
curl -X POST http://localhost:5000/clear_shopping_list
```

4. Get all recipes:
```bash
curl http://localhost:5000/get_recipes
```

## TODO: Future Enhancements

- integrating a more robust database solution (e.g., SQLite or PostgreSQL) for better data management as the project scales.
- user authentication
- recipe search
- meal planning
- recipe tags, like vegan, keto...
