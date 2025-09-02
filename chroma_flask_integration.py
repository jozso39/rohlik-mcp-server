"""
Flask integration module for ChromaDB semantic search
Easy integration with your existing Flask recipe API
"""

from chroma_query_service import PersistentRecipeSearcher
import os
from typing import List, Dict, Any, Optional

class ChromaIntegration:
    """Integration layer between Flask API and ChromaDB"""
    
    def __init__(self, chroma_db_path: str = "./chroma_db"):
        self.searcher: Optional[PersistentRecipeSearcher] = None
        self.chroma_db_path = chroma_db_path
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize ChromaDB connection"""
        try:
            self.searcher = PersistentRecipeSearcher(self.chroma_db_path)
            if self.searcher.collection:
                print(f"ChromaDB integration initialized with {self.searcher.collection.count()} recipes")
        except Exception as e:
            print(f"Warning: ChromaDB not available: {e}")
            print("Run 'python load_recipes_to_chroma.py' to initialize the database")
            self.searcher = None
    
    def is_available(self) -> bool:
        """Check if ChromaDB is available"""
        return self.searcher is not None and self.searcher.collection is not None
    
    def semantic_search(self, query: str, limit: int = 10) -> List[str]:
        """
        Semantic search returning recipe names only
        Returns empty list if ChromaDB not available
        """
        if not self.is_available() or not self.searcher:
            return []
        
        try:
            return self.searcher.search_by_text(query, n_results=limit)
        except Exception as e:
            print(f"ChromaDB search error: {e}")
            return []
    
    def search_by_ingredient(self, ingredient: str, limit: int = 10) -> List[str]:
        """
        Search by ingredient returning recipe names only
        Returns empty list if ChromaDB not available
        """
        if not self.is_available() or not self.searcher:
            return []
        
        try:
            return self.searcher.search_by_ingredient(ingredient, n_results=limit)
        except Exception as e:
            print(f"ChromaDB ingredient search error: {e}")
            return []
    
    def search_by_filters(self, diet: Optional[str] = None, meal_type: Optional[str] = None, limit: int = 10) -> List[str]:
        """
        Search by diet/meal type filters returning recipe names only
        Returns empty list if ChromaDB not available
        """
        if not self.is_available() or not self.searcher:
            return []
        
        try:
            if diet:
                return self.searcher.search_by_diet(diet, n_results=limit)
            elif meal_type:
                return self.searcher.search_by_meal_type(meal_type, n_results=limit)
            else:
                return []
        except Exception as e:
            print(f"ChromaDB filter search error: {e}")
            return []
    
    def advanced_search(self, query: Optional[str] = None, diet: Optional[str] = None, 
        meal_type: Optional[str] = None, ingredient: Optional[str] = None, 
        limit: int = 10) -> List[str]:
        """
        Advanced search with multiple parameters returning recipe names only
        Returns empty list if ChromaDB not available
        """
        if not self.is_available() or not self.searcher:
            return []
        
        try:
            # Simple approach: use text search if query provided
            if query:
                return self.searcher.search_by_text(query, n_results=limit)
            elif ingredient:
                return self.searcher.search_by_ingredient(ingredient, n_results=limit)
            elif diet:
                return self.searcher.search_by_diet(diet, n_results=limit)
            elif meal_type:
                return self.searcher.search_by_meal_type(meal_type, n_results=limit)
            else:
                return []
        except Exception as e:
            print(f"ChromaDB advanced search error: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get ChromaDB status information"""
        if not self.is_available() or not self.searcher:
            return {
                "available": False,
                "message": "ChromaDB not initialized. Run load_recipes_to_chroma.py",
                "total_recipes": 0
            }
        
        try:
            total_recipes = self.searcher.collection.count() if self.searcher.collection else 0
            return {
                "available": True,
                "message": "ChromaDB operational",
                "total_recipes": total_recipes,
                "database_path": os.path.abspath(self.searcher.chroma_db_path)
            }
        except Exception as e:
            return {
                "available": False,
                "message": f"ChromaDB error: {e}",
                "total_recipes": 0
            }

# Global instance - initialize once
chroma_integration = ChromaIntegration()

# Convenience functions for direct use in Flask routes
def semantic_search(query: str, limit: int = 10) -> List[str]:
    """Global semantic search function"""
    return chroma_integration.semantic_search(query, limit)

def ingredient_search(ingredient: str, limit: int = 10) -> List[str]:
    """Global ingredient search function"""
    return chroma_integration.search_by_ingredient(ingredient, limit)

def filter_search(diet: Optional[str] = None, meal_type: Optional[str] = None, limit: int = 10) -> List[str]:
    """Global filter search function"""
    return chroma_integration.search_by_filters(diet, meal_type, limit)

def advanced_search(query: Optional[str] = None, diet: Optional[str] = None, 
    meal_type: Optional[str] = None, ingredient: Optional[str] = None, 
    limit: int = 10) -> List[str]:
    """Global advanced search function"""
    return chroma_integration.advanced_search(query, diet, meal_type, ingredient, limit)

def get_chroma_status() -> Dict[str, Any]:
    """Global function to get ChromaDB status"""
    return chroma_integration.get_status()

def is_chroma_available() -> bool:
    """Global function to check if ChromaDB is available"""
    return chroma_integration.is_available()

if __name__ == "__main__":
    # Test the integration
    print("=== ChromaDB Flask Integration Test ===")
    
    status = get_chroma_status()
    print(f"Status: {status}")
    
    if is_chroma_available():
        print("\nTesting searches:")
        
        # Test semantic search
        results = semantic_search("chicken", 3)
        print(f"Semantic search for 'chicken': {results}")
        
        # Test ingredient search
        results = ingredient_search("Brambory", 3)
        print(f"Ingredient search for 'Brambory': {results}")
        
        print("\n✅ ChromaDB integration ready for Flask!")
    else:
        print("\n❌ ChromaDB not available. Run load_recipes_to_chroma.py first.")
