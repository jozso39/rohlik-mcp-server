import unittest
import requests
import time
import subprocess
import sys
from pathlib import Path

class TestMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask server
        server_path = Path(__file__).parent.parent / 'src' / 'server.py'
        cls.server_process = subprocess.Popen([sys.executable, str(server_path)])
        # Wait for server to start
        time.sleep(2)
        cls.base_url = 'http://localhost:5000'

    @classmethod
    def tearDownClass(cls):
        # Stop the Flask server
        cls.server_process.terminate()
        cls.server_process.wait()

    def setUp(self):
        # Clear shopping list before each test
        requests.post(f"{self.base_url}/clear_shopping_list")

    def test_add_ingredients(self):
        """Test adding ingredients to shopping list"""
        # Test data
        ingredients = ["Mléko", "Cibule", "Chléb"]
        
        # Make request
        response = requests.post(
            f"{self.base_url}/add_ingredients",
            json={"ingredients": ingredients}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "3 ingredients added")
        self.assertEqual(set(data["shopping_list"]), set(ingredients))

    def test_get_shopping_list(self):
        """Test getting shopping list"""
        # Add some ingredients first
        ingredients = ["Mléko", "Cibule"]
        requests.post(
            f"{self.base_url}/add_ingredients",
            json={"ingredients": ingredients}
        )
        
        # Get shopping list
        response = requests.get(f"{self.base_url}/get_shopping_list")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data["shopping_list"]), set(ingredients))

    def test_clear_shopping_list(self):
        """Test clearing shopping list"""
        # Add some ingredients first
        ingredients = ["Mléko", "Cibule"]
        requests.post(
            f"{self.base_url}/add_ingredients",
            json={"ingredients": ingredients}
        )
        
        # Clear shopping list
        response = requests.post(f"{self.base_url}/clear_shopping_list")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Shopping list cleared")
        
        # Verify list is empty
        response = requests.get(f"{self.base_url}/get_shopping_list")
        self.assertEqual(response.json()["shopping_list"], [])

    def test_search_recipes_by_tag(self):
        """Test searching recipes by tag"""
        response = requests.get(f"{self.base_url}/search_recipes", params={"tag": "polévka"})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("recipes", data)
        # Verify all returned recipes have the polévka tag
        for recipe in data["recipes"]:
            self.assertTrue(any(tag.lower() == "polévka" for tag in recipe["tags"]))

    def test_search_recipes_by_name(self):
        """Test searching recipes by name"""
        search_term = "guláš"
        response = requests.get(f"{self.base_url}/search_recipes", params={"name": search_term})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("recipes", data)
        # Verify all returned recipes have guláš in their name
        for recipe in data["recipes"]:
            self.assertIn(search_term.lower(), recipe["name"].lower())

    def test_search_recipes_invalid_request(self):
        """Test search recipes with missing parameters"""
        response = requests.get(f"{self.base_url}/search_recipes")
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

if __name__ == '__main__':
    unittest.main()
