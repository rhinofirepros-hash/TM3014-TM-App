#!/usr/bin/env python3
"""
Debug GC Login 400 Error
"""

import requests
import json

BACKEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com/api"
FRONTEND_URL = "https://gc-sprinkler-app.preview.emergentagent.com"

def debug_gc_login():
    session = requests.Session()
    
    # First get a project with PIN
    print("Getting projects...")
    projects_response = session.get(f"{BACKEND_URL}/projects")
    if projects_response.status_code == 200:
        projects = projects_response.json()
        if projects:
            project = projects[0]
            project_id = project.get("id")
            project_pin = project.get("gc_pin")
            project_name = project.get("name")
            
            print(f"Testing with Project: {project_name}")
            print(f"Project ID: {project_id}")
            print(f"Project PIN: {project_pin}")
            
            # Test the login endpoint
            login_data = {
                "project_id": project_id,
                "pin": project_pin
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Origin': FRONTEND_URL
            }
            
            print(f"\nSending login request to: {BACKEND_URL}/gc/login-simple")
            print(f"Login data: {login_data}")
            print(f"Headers: {headers}")
            
            response = session.post(
                f"{BACKEND_URL}/gc/login-simple",
                json=login_data,
                headers=headers,
                timeout=10
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")
            
            # Try to parse as JSON
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                print("Response is not valid JSON")
                
        else:
            print("No projects found")
    else:
        print(f"Failed to get projects: {projects_response.status_code}")

if __name__ == "__main__":
    debug_gc_login()