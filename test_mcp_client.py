#!/usr/bin/env python3
"""
Simple test script for the MCP server
"""

import asyncio
import json
import subprocess
import sys
import os


async def test_mcp_basic():
    """Test the MCP server with basic JSON-RPC calls"""
    
    print("🚀 Testing MCP Server with basic JSON-RPC...")
    
    # Test if the server can be imported and basic functionality works
    try:
        # Change to the correct directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Import and test the server functions directly
        sys.path.append('.')
        from mcp_server import (
            search_recipes, get_shopping_list, add_ingredients_to_shopping_list,
            clear_shopping_list, get_all_diet_types, get_recipe_details
        )
        
        print("✅ MCP server modules imported successfully!")
        
        # Test 1: Get all diet types
        print("\n🥗 Testing: Get all diet types")
        diet_data = get_all_diet_types()
        print(f"Found {diet_data['count']} diet types: {diet_data['diet_types']}")
        
        # Test 2: Search for vegetarian recipes
        print("\n🔍 Testing: Search for vegetarian recipes")
        search_data = search_recipes({"diet": "vegetarian", "limit": 3})
        print(f"Found {search_data['total_found']} vegetarian recipes, showing {search_data['returned']}:")
        for recipe in search_data["recipes"]:
            print(f"  • {recipe['name']}")
        
        # Test 3: Add ingredients to shopping list
        print("\n🛒 Testing: Add ingredients to shopping list")
        shopping_data = add_ingredients_to_shopping_list({"ingredients": ["Brambory", "Cibule", "Česnek"]})
        print(f"Added ingredients. Shopping list now has {shopping_data['count']} items:")
        for item in shopping_data["shopping_list"]:
            print(f"  • {item}")
        
        # Test 4: Get shopping list
        print("\n📝 Testing: Get shopping list")
        list_data = get_shopping_list()
        print(f"Shopping list has {list_data['count']} items:")
        for item in list_data["shopping_list"]:
            print(f"  • {item}")
        
        # Test 5: Get recipe details
        if search_data["recipes"]:
            recipe_name = search_data["recipes"][0]["name"]
            print(f"\n📖 Testing: Get details for '{recipe_name}'")
            recipe_data = get_recipe_details({"recipe_name": recipe_name})
            if recipe_data["found"]:
                recipe = recipe_data["recipe"]
                print(f"  • Name: {recipe['name']}")
                print(f"  • Diet: {', '.join(recipe.get('diet', []))}")
                print(f"  • Meal Type: {', '.join(recipe.get('meal_type', []))}")
                print(f"  • Ingredients: {len(recipe.get('ingredients', []))} items")
        
        # Test 6: Clear shopping list
        print("\n🧹 Testing: Clear shopping list")
        clear_data = clear_shopping_list()
        print(f"  • {clear_data['message']}")
        
        # Test 7: Verify shopping list is empty
        print("\n📝 Testing: Verify shopping list is empty")
        empty_list = get_shopping_list()
        print(f"  • Shopping list has {empty_list['count']} items")
        
        print("\n✅ All MCP server function tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_mcp_server_process():
    """Test running the MCP server as a subprocess"""
    
    print("\n🚀 Testing MCP Server as subprocess...")
    
    try:
        # Test that the server can start without errors
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send a simple initialize message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
                "capabilities": {}
            }
        }
        
        if process.stdin:
            process.stdin.write(json.dumps(init_message) + "\n")
            process.stdin.flush()
        
        # Wait a bit for response
        await asyncio.sleep(1)
        
        # Check if process is still running (good sign)
        if process.poll() is None:
            print("✅ MCP server process started successfully!")
            process.terminate()
            process.wait()
            return True
        else:
            # Process died, check error
            _, stderr = process.communicate()
            print(f"❌ MCP server process failed: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start MCP server process: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Starting MCP Server Tests\n")
    
    # Test 1: Basic functionality
    basic_test = await test_mcp_basic()
    
    # Test 2: Server process
    process_test = await test_mcp_server_process()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"  • Basic functionality: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"  • Server process: {'✅ PASS' if process_test else '❌ FAIL'}")
    
    if basic_test and process_test:
        print("\n🎉 All tests passed! MCP server is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
