
#!/bin/bash

# Create the project directory structure
mkdir -p sales_management_system/{src/{models,views,controllers,utils},data,config,tests}

# Create __init__.py files for Python packages
touch sales_management_system/src/__init__.py
touch sales_management_system/src/models/__init__.py
touch sales_management_system/src/views/__init__.py
touch sales_management_system/src/controllers/__init__.py
touch sales_management_system/src/utils/__init__.py

echo "Project structure created successfully!"
