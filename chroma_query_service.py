"""
ChromaDB Recipe Query Service
Serves queries against a persistent ChromaDB collection
Returns only recipe names for integration with existing API
"""

import chromadb
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

class PersistentRecipeSearcher:
    """ChromaDB-based recipe searcher using persistent storage"""
    
    def __init__(self, chroma_db_path: str = "./chroma_db"):
        self.chroma_db_path = chroma_db_path
        self.client: Optional[Any] = None  # Using Any to avoid complex type issues
        self.collection: Optional[Any] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to persistent ChromaDB collection"""
        if not os.path.exists(self.chroma_db_path):
            raise FileNotFoundError(
                f"ChromaDB database not found at {self.chroma_db_path}. "
                "Please run load_recipes_to_chroma.py first to create the database."
            )
        
        print(f"Connecting to ChromaDB at: {self.chroma_db_path}")
        self.client = chromadb.PersistentClient(path=self.chroma_db_path)
        
        try:
            self.collection = self.client.get_collection(name="recipes")
            if self.collection:
                count = self.collection.count()
                print(f"Connected to recipes collection with {count} documents")
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to recipes collection: {e}. "
                "Please run load_recipes_to_chroma.py first."
            )
    
    def search_by_text(self, query_text: str, n_results: int = 10) -> List[str]:
        """
        Semantic search by text query
        Returns: List of recipe names
        """
        if not self.collection:
            return []
            
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        recipe_names = []
        if results['metadatas']:
            for metadata in results['metadatas'][0]:
                recipe_names.append(metadata.get('name', ''))
        
        return recipe_names
    
    def search_by_ingredient(self, ingredient_name: str, n_results: int = 10) -> List[str]:
        """
        Search recipes containing a specific ingredient
        Returns: List of recipe names
        """
        if not self.collection:
            return []
            
        results = self.collection.query(
            query_texts=[f"recipe with {ingredient_name}"],
            where_document={"$contains": ingredient_name},
            n_results=n_results
        )
        
        recipe_names = []
        if results['metadatas']:
            for metadata in results['metadatas'][0]:
                recipe_names.append(metadata.get('name', ''))
        
        return recipe_names
    
    def search_by_diet(self, diet_type: str, n_results: int = 10) -> List[str]:
        """
        Filter recipes by diet type
        Returns: List of recipe names
        """
        if not self.collection:
            return []
            
        results = self.collection.get(
            where={"primary_diet": diet_type},
            limit=n_results
        )
        
        recipe_names = []
        if results['metadatas']:
            for metadata in results['metadatas']:
                recipe_names.append(metadata.get('name', ''))
        
        return recipe_names
    
    def search_by_meal_type(self, meal_type: str, n_results: int = 10) -> List[str]:
        """
        Filter recipes by meal type
        Returns: List of recipe names
        """
        if not self.collection:
            return []
            
        results = self.collection.get(
            where={"primary_meal_type": meal_type},
            limit=n_results
        )
        
        recipe_names = []
        if results['metadatas']:
            for metadata in results['metadatas']:
                recipe_names.append(metadata.get('name', ''))
        
        return recipe_names

# Global instance for easy use
_searcher: Optional[PersistentRecipeSearcher] = None

def get_recipe_searcher(chroma_db_path: str = "./chroma_db") -> PersistentRecipeSearcher:
    """Get or create the global PersistentRecipeSearcher instance"""
    global _searcher
    if _searcher is None:
        _searcher = PersistentRecipeSearcher(chroma_db_path)
    return _searcher

# Convenience functions for direct use
def semantic_search(query_text: str, n_results: int = 10, chroma_db_path: str = "./chroma_db") -> List[str]:
    """Semantic search returning recipe names only"""
    searcher = get_recipe_searcher(chroma_db_path)
    return searcher.search_by_text(query_text, n_results)

def ingredient_search(ingredient_name: str, n_results: int = 10, chroma_db_path: str = "./chroma_db") -> List[str]:
    """Ingredient search returning recipe names only"""
    searcher = get_recipe_searcher(chroma_db_path)
    return searcher.search_by_ingredient(ingredient_name, n_results)

def diet_search(diet_type: str, n_results: int = 10, chroma_db_path: str = "./chroma_db") -> List[str]:
    """Diet filter returning recipe names only"""
    searcher = get_recipe_searcher(chroma_db_path)
    return searcher.search_by_diet(diet_type, n_results)

def meal_type_search(meal_type: str, n_results: int = 10, chroma_db_path: str = "./chroma_db") -> List[str]:
    """Meal type filter returning recipe names only"""
    searcher = get_recipe_searcher(chroma_db_path)
    return searcher.search_by_meal_type(meal_type, n_results)

def test_queries():
    """Test function to demonstrate query capabilities"""
    print("=== ChromaDB Persistent Query Service Test ===\n")
    
    try:
        searcher = get_recipe_searcher()
        
        if not searcher.collection:
            print("❌ No collection available")
            return
            
        print(f"📊 Collection Info:")
        print(f"  Total recipes: {searcher.collection.count()}")
        print(f"  Database path: {os.path.abspath(searcher.chroma_db_path)}")
        print()
        
        # Test different search types
        print("🔍 Test Queries (returning recipe names only):\n")
        
        # 1. Semantic search
        print("1. Semantic search for 'chicken soup':")
        chicken_results = searcher.search_by_text("chicken soup", n_results=3)
        for i, name in enumerate(chicken_results, 1):
            print(f"   {i}. {name}")
        print()
        
        # 2. Ingredient search
        print("2. Recipes with 'Brambory' (potatoes):")
        potato_results = searcher.search_by_ingredient("Brambory", n_results=3)
        for i, name in enumerate(potato_results, 1):
            print(f"   {i}. {name}")
        print()
        
        # 3. Diet filter
        print("3. Vegetarian recipes:")
        veggie_results = searcher.search_by_diet("vegetarian", n_results=3)
        for i, name in enumerate(veggie_results, 1):
            print(f"   {i}. {name}")
        print()
        
        # 4. Meal type filter
        print("4. Main courses:")
        main_results = searcher.search_by_meal_type("hlavní chod", n_results=3)
        for i, name in enumerate(main_results, 1):
            print(f"   {i}. {name}")
        print()
        
        print("✅ All tests completed successfully!")
        print("🚀 Ready to integrate with your Flask API!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Make sure you've run load_recipes_to_chroma.py first.")

def main():
    """Main function to test the query service"""
    test_queries()

if __name__ == "__main__":
    main()
