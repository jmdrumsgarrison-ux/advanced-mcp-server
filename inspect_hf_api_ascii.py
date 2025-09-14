#!/usr/bin/env python3
"""
Inspect HuggingFace Hub API to discover all available methods and operations
ASCII-only version for Windows console compatibility
"""

import os
import json
import inspect
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def inspect_hf_api():
    """Inspect HfApi class to discover all available methods"""
    
    try:
        from huggingface_hub import HfApi
        print("=== HUGGINGFACE HUB API INSPECTION ===")
        print(f"Timestamp: {datetime.now()}")
        
        # Create API instance
        api = HfApi()
        
        # Get all methods from HfApi class
        methods = []
        for name in dir(api):
            if not name.startswith('_'):  # Skip private methods
                attr = getattr(api, name)
                if callable(attr):
                    # Get method signature
                    try:
                        sig = inspect.signature(attr)
                        doc = inspect.getdoc(attr)
                        
                        methods.append({
                            "name": name,
                            "signature": str(sig),
                            "doc": doc[:200] + "..." if doc and len(doc) > 200 else doc,
                            "parameters": list(sig.parameters.keys()) if sig else []
                        })
                    except (ValueError, TypeError):
                        # Some methods might not have inspectable signatures
                        methods.append({
                            "name": name,
                            "signature": "N/A",
                            "doc": "N/A",
                            "parameters": []
                        })
        
        # Sort methods alphabetically
        methods.sort(key=lambda x: x["name"])
        
        print(f"\n=== DISCOVERED {len(methods)} METHODS ===\n")
        
        # Categorize methods by function
        categories = {
            "Repository Management": [],
            "Model Operations": [],
            "Dataset Operations": [],
            "Space Operations": [],
            "File Operations": [],
            "Search & Discovery": [],
            "Authentication": [],
            "Other": []
        }
        
        for method in methods:
            name = method["name"]
            if any(keyword in name for keyword in ["repo", "create_repo", "delete_repo"]):
                categories["Repository Management"].append(method)
            elif any(keyword in name for keyword in ["model", "pipeline"]):
                categories["Model Operations"].append(method)
            elif "dataset" in name:
                categories["Dataset Operations"].append(method)
            elif "space" in name:
                categories["Space Operations"].append(method)
            elif any(keyword in name for keyword in ["file", "upload", "download"]):
                categories["File Operations"].append(method)
            elif any(keyword in name for keyword in ["search", "list", "get", "info"]):
                categories["Search & Discovery"].append(method)
            elif any(keyword in name for keyword in ["auth", "login", "token", "whoami"]):
                categories["Authentication"].append(method)
            else:
                categories["Other"].append(method)
        
        # Print categorized results - ASCII only
        for category, methods_list in categories.items():
            if methods_list:
                print(f"=== {category.upper()} ({len(methods_list)} methods) ===")
                for method in methods_list:
                    print(f"  * {method['name']}{method['signature']}")
                    if method['doc'] and method['doc'] != 'N/A':
                        print(f"    -> {method['doc']}")
                print()
        
        # Save detailed results to file
        with open("hf_api_inspection_results.json", "w", encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_methods": len(methods),
                "categories": categories,
                "all_methods": methods
            }, f, indent=2)
        
        print(f"[SUCCESS] Complete inspection saved to: hf_api_inspection_results.json")
        print(f"[INFO] Total methods discovered: {len(methods)}")
        
        # Test authentication
        print("\n=== AUTHENTICATION TEST ===")
        try:
            user_info = api.whoami()
            print(f"[SUCCESS] Authenticated as: {user_info}")
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
        
        return methods
        
    except ImportError as e:
        print(f"[ERROR] HuggingFace Hub not available: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Inspection failed: {e}")
        return []

if __name__ == "__main__":
    methods = inspect_hf_api()
    print(f"\n[COMPLETE] HuggingFace Hub API Inspection Complete!")
