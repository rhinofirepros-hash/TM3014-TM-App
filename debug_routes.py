#!/usr/bin/env python3
"""
Debug script to check what routes are registered in the unified server
"""

import sys
import os
sys.path.append('/app/backend')

from server_unified import app

def debug_routes():
    print("🔍 Debugging FastAPI Routes in server_unified.py")
    print("=" * 60)
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods) if route.methods else [],
                'name': getattr(route, 'name', 'Unknown')
            })
    
    # Filter for GC-related routes
    gc_routes = [r for r in routes if 'gc' in r['path'].lower()]
    
    print(f"Total routes registered: {len(routes)}")
    print(f"GC-related routes found: {len(gc_routes)}")
    print()
    
    if gc_routes:
        print("🎯 GC ROUTES FOUND:")
        for route in gc_routes:
            print(f"  {route['methods']} {route['path']} ({route['name']})")
    else:
        print("❌ NO GC ROUTES FOUND!")
        print("\n🔍 All registered routes:")
        for route in sorted(routes, key=lambda x: x['path']):
            print(f"  {route['methods']} {route['path']} ({route['name']})")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    debug_routes()