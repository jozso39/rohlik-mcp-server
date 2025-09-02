"""
Script to load recipes from CSV into a persistent ChromaDB collection
This script creates a local ChromaDB database that persists to disk
"""

import chromadb
import csv
import os
from pathlib import Path

def load_recipes_to_persistent_chroma(csv_path="data/Recipes.csv", chroma_db_path="./chroma_db"):
    """Load recipes from CSV into persistent ChromaDB collection"""
    
    # Create the database directory if it doesn't exist
    Path(chroma_db_path).mkdir(exist_ok=True)
    
    # Initialize persistent ChromaDB client
    print(f"Initializing ChromaDB client with persistent storage at: {chroma_db_path}")
    chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    
    # Try to delete existing collection if it exists
    try:
        existing_collection = chroma_client.get_collection(name="recipes")
        chroma_client.delete_collection(name="recipes")
        print("Deleted existing recipes collection")
    except Exception:
        print("No existing collection found - creating new one")
    
    # Create new collection with embedding function
    print("Creating new recipes collection...")
    collection = chroma_client.create_collection(
        name="recipes",
        metadata={"description": "Recipe collection with semantic search capabilities"}
    )
    
    # Load recipes from CSV
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    recipes = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipes.append(row)
    
    print(f"Loaded {len(recipes)} recipes from CSV: {csv_path}")
    
    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []
    
    for recipe in recipes:
        # Use recipe ID as the document ID
        recipe_id = str(recipe['id'])
        ids.append(recipe_id)
        
        # Create a comprehensive document text for semantic search
        # Combine name, ingredients, and cooking steps
        document_text = f"""
        Recipe: {recipe['name']}
        Ingredients: {recipe['ingredients']}
        Diet: {recipe['diet']}
        Meal Type: {recipe['meal_type']}
        Cooking Steps: {recipe['steps']}
        """.strip()
        documents.append(document_text)
        
        # Store structured metadata for filtering
        # ChromaDB only supports str, int, float, bool, None for metadata values
        metadata = {
            'name': recipe['name'],
            'diet_string': recipe['diet'] if recipe['diet'] else '',
            'meal_type_string': recipe['meal_type'] if recipe['meal_type'] else '',
            'ingredients_string': recipe['ingredients'] if recipe['ingredients'] else '',
            'steps_preview': recipe['steps'][:200] if recipe['steps'] else '',
            # Store primary categories for filtering
            'primary_diet': recipe['diet'].split(',')[0].strip() if recipe['diet'] else '',
            'primary_meal_type': recipe['meal_type'].split(',')[0].strip() if recipe['meal_type'] else '',
            'ingredient_count': len([i.strip() for i in recipe['ingredients'].split(',')]) if recipe['ingredients'] else 0,
        }
        metadatas.append(metadata)
    
    # Add all recipes to the collection in batches
    batch_size = 50
    total_batches = (len(recipes) + batch_size - 1) // batch_size
    
    for i in range(0, len(recipes), batch_size):
        batch_end = min(i + batch_size, len(recipes))
        batch_num = (i // batch_size) + 1
        
        print(f"Adding batch {batch_num}/{total_batches} (recipes {i+1}-{batch_end})...")
        
        collection.add(
            ids=ids[i:batch_end],
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end]
        )
    
    print(f"Successfully added {len(recipes)} recipes to persistent ChromaDB collection")
    
    # Verify the collection
    count = collection.count()
    print(f"Collection verification: {count} documents stored")
    
    # Show some statistics
    print("\n=== Collection Statistics ===")
    
    # Get available diet types
    all_results = collection.get()
    diet_types = set()
    meal_types = set()
    
    if all_results['metadatas']:
        for metadata in all_results['metadatas']:
            if metadata.get('primary_diet'):
                diet_types.add(metadata['primary_diet'])
            if metadata.get('primary_meal_type'):
                meal_types.add(metadata['primary_meal_type'])
    
    print(f"Available diet types: {sorted(list(diet_types))}")
    print(f"Available meal types: {sorted(list(meal_types))}")
    print(f"Database location: {os.path.abspath(chroma_db_path)}")
    
    return collection, chroma_client

def main():
    """Main function to load recipes into persistent ChromaDB"""
    
    try:
        collection, client = load_recipes_to_persistent_chroma()
        
        print(f"\n✅ ChromaDB collection created successfully!")
        print(f"📁 Database location: {os.path.abspath('./chroma_db')}")
        print(f"🔢 Total recipes: {collection.count()}")
        print(f"🚀 Ready to use with query script!")
        
    except Exception as e:
        print(f"❌ Error loading recipes: {e}")
        raise

if __name__ == "__main__":
    main()
