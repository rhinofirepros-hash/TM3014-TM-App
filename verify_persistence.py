#!/usr/bin/env python3
"""
Verify data persistence in MongoDB
"""

import requests
import json

# Test data persistence by retrieving stored data
backend_url = 'https://project-inspect-app.preview.emergentagent.com/api'

print('=== Verifying Data Persistence ===')

# Check T&M tags
tm_response = requests.get(f'{backend_url}/tm-tags')
if tm_response.status_code == 200:
    tm_tags = tm_response.json()
    print(f'✅ T&M Tags in database: {len(tm_tags)}')
    if tm_tags:
        latest_tag = tm_tags[-1]
        print(f'   Latest tag: {latest_tag["project_name"]} - {latest_tag["tm_tag_title"]}')
        print(f'   Labor entries: {len(latest_tag.get("labor_entries", []))}')
        print(f'   Material entries: {len(latest_tag.get("material_entries", []))}')
        print(f'   Equipment entries: {len(latest_tag.get("equipment_entries", []))}')
        print(f'   Other entries: {len(latest_tag.get("other_entries", []))}')
else:
    print(f'❌ Failed to retrieve T&M tags: {tm_response.status_code}')

# Check workers
worker_response = requests.get(f'{backend_url}/workers')
if worker_response.status_code == 200:
    workers = worker_response.json()
    print(f'✅ Workers in database: {len(workers)}')
    for worker in workers[-3:]:  # Show last 3 workers
        print(f'   Worker: {worker["name"]} - {worker["position"]} (${worker["rate"]}/hr)')
else:
    print(f'❌ Failed to retrieve workers: {worker_response.status_code}')