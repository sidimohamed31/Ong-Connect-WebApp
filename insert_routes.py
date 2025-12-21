#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script to insert new routes into app.py

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('temp_routes.py', 'r', encoding='utf-8') as f:
    new_routes = f.read()

# Find line with @app.route('/admin/dashboard')
insert_line = None
for i, line in enumerate(lines):
    if '@app.route(\'/admin/dashboard\')' in line:
        insert_line = i
        break

if insert_line:
    # Insert new routes before admin dashboard
    lines.insert(insert_line, new_routes + '\n')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Successfully inserted routes at line {insert_line}")
else:
    print("Could not find insertion point")
