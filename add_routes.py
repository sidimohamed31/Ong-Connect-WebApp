# coding: utf-8
import codecs

# Read the main app file
with codecs.open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Read the new routes
with codecs.open('temp_routes.py', 'r', encoding='utf-8') as f:
    routes = f.read()

# Find the insertion point
marker = "@app.route('/admin/dashboard')"
insert_index = content.find(marker)

if insert_index != -1:
    # Insert the routes
    new_content = content[:insert_index] + routes + "\n" + content[insert_index:]
    
    # Write back
    with codecs.open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Successfully added routes!")
else:
    print("Could not find insertion point")
