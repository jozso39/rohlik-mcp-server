class ShoppingListManager:
    def __init__(self):
        self.shopping_list = []

    def add_ingredient(self, ingredient):
        """Add an ingredient to the shopping list."""
        if ingredient and isinstance(ingredient, str):
            self.shopping_list.append(ingredient.strip())
            return True
        return False

    def get_list(self):
        """Get the current shopping list."""
        return self.shopping_list

    def clear_list(self):
        """Clear the shopping list."""
        self.shopping_list = []

    def remove_ingredients(self, ingredients):
        """Remove specified ingredients from the shopping list. Ignore any not present."""
        if not isinstance(ingredients, list):
            return False
        # Remove each ingredient if present
        for ingredient in ingredients:
            if ingredient in self.shopping_list:
                self.shopping_list = [item for item in self.shopping_list if item != ingredient]
        return True