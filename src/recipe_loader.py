import csv
import os

def load_recipes(csv_path):
    """Load recipes from a CSV file."""
    recipes = []
    try:
        # Get absolute path relative to the script location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, csv_path)
        
        with open(full_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert ingredients string to list
                if 'ingredients' in row:
                    row['ingredients'] = [i.strip() for i in row['ingredients'].split(',')]
                recipes.append(row)
        return recipes
    except Exception as e:
        print(f"Error loading recipes: {e}")
        return []