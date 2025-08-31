
"""
Data management utilities for the sales management system
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime
from ..models.table import Table

class DataManager:
    """Handles data persistence and retrieval"""
    
    def __init__(self):
        # Create data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.database_file = os.path.join(self.data_dir, "sales_data.json")
        self._ensure_data_file()
    
    def _ensure_data_file(self) -> None:
        """Ensure the data file exists with default structure"""
        if not os.path.exists(self.database_file):
            default_data = {
                "tables": {},
                "settings": {
                    "last_table_number": 0,
                    "created_at": datetime.now().isoformat()
                }
            }
            self.save_data(default_data)
    
    def load_data(self) -> dict:
        """Load data from the database file"""
        try:
            with open(self.database_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            return {"tables": {}, "settings": {}}
    
    def save_data(self, data: dict) -> None:
        """Save data to the database file"""
        try:
            with open(self.database_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_tables(self) -> Dict[str, Table]:
        """Load all tables from the database"""
        data = self.load_data()
        tables = {}
        
        for table_name, table_data in data.get("tables", {}).items():
            try:
                tables[table_name] = Table.from_dict(table_data)
            except Exception as e:
                print(f"Error loading table {table_name}: {e}")
        
        return tables
    
    def save_tables(self, tables: Dict[str, Table]) -> None:
        """Save all tables to the database"""
        data = self.load_data()
        data["tables"] = {name: table.to_dict() for name, table in tables.items()}
        self.save_data(data)
    
    def get_next_table_number(self) -> int:
        """Get the next available table number"""
        data = self.load_data()
        last_number = data.get("settings", {}).get("last_table_number", 0)
        next_number = last_number + 1
        
        # Update the last table number
        data.setdefault("settings", {})["last_table_number"] = next_number
        self.save_data(data)
        
        return next_number
    
    def backup_data(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the current data"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.data_dir, f"backup_{timestamp}.json")
        
        data = self.load_data()
        with open(backup_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        return backup_path
