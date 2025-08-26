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
                # Convert ingredients string to list if it exists and is not None
                if 'ingredients' in row and row['ingredients']:
                    row['ingredients'] = [i.strip() for i in row['ingredients'].split(',')]
                # Convert diet and meal_type to lists if they exist and are not None
                if 'diet' in row and row['diet']:
                    row['diet'] = [t.strip() for t in row['diet'].split(',')]
                # Ensure diet exists even if empty
                if 'diet' not in row or not row['diet']:
                    row['diet'] = []
                    
                if 'meal_type' in row and row['meal_type']:
                    row['meal_type'] = [t.strip() for t in row['meal_type'].split(',')]
                # Ensure meal_type exists even if empty
                if 'meal_type' not in row or not row['meal_type']:
                    row['meal_type'] = []
                recipes.append(row)
        return recipes
    except Exception as e:
        print(f"Error loading recipes: {e}")
        return []