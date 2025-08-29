class ShoppingListManager:
    def __init__(self):
        self.shopping_list = set()

    def add_ingredient(self, ingredient):
        """Add an ingredient to the shopping list. No duplicates allowed."""
        if ingredient and isinstance(ingredient, str):
            self.shopping_list.add(ingredient.strip())
            return True
        return False

    def get_list(self):
        """Get the current shopping list as a sorted list."""
        return sorted(self.shopping_list)

    def clear_list(self):
        """Clear the shopping list."""
        self.shopping_list = set()

    def remove_ingredients(self, ingredients):
        """Remove specified ingredients from the shopping list. Ignore any not present."""
        if not isinstance(ingredients, list):
            return False
        for ingredient in ingredients:
            self.shopping_list.discard(ingredient)
        return True