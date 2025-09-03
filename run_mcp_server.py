#!/usr/bin/env python3
"""
MCP Server Runner - for easier integration with MCP clients
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the MCP server"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Path to the MCP server
    mcp_server_path = script_dir / "mcp_server.py"
    
    if not mcp_server_path.exists():
        print(f"Error: MCP server not found at {mcp_server_path}", file=sys.stderr)
        sys.exit(1)
    
    # Check if we're in a virtual environment or if required modules are available
    try:
        from shopping_list_mcp_server.shopping_list_manager import ShoppingListManager
        from shopping_list_mcp_server.recipe_loader import load_recipes
    except ImportError as e:
        print(f"Error: Required modules not found. Please install dependencies: {e}", file=sys.stderr)
        print("Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)
    
    # Check if data file exists
    data_file = script_dir / "data" / "Recipes.csv"
    if not data_file.exists():
        print(f"Error: Recipe data file not found at {data_file}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Starting MCP Recipe & Shopping List Server...", file=sys.stderr)
    print(f"Data file: {data_file}", file=sys.stderr)
    print(f"Protocol: Model Context Protocol 2025-06-18", file=sys.stderr)
    print(f"Transport: stdio (JSON-RPC 2.0)", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Run the MCP server
    try:
        subprocess.run([sys.executable, str(mcp_server_path)], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Server exited with error code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
