
"""
Sales controller for managing business logic
"""

from typing import Dict, Optional, Callable, List
from ..models.table import Table
from ..utils.data_manager import DataManager

class SalesController:
    """Controller for managing sales operations"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.tables: Dict[str, Table] = {}
        self.observers: List[Callable] = []
        
        self.load_data()
    
    def add_observer(self, callback: Callable) -> None:
        """Add an observer for data changes"""
        self.observers.append(callback)
    
    def notify_observers(self) -> None:
        """Notify all observers of data changes"""
        for callback in self.observers:
            try:
                callback()
            except Exception as e:
                print(f"Error notifying observer: {e}")
    
    def load_data(self) -> None:
        """Load data from storage"""
        self.tables = self.data_manager.load_tables()
        self.notify_observers()
    
    def save_data(self) -> None:
        """Save data to storage"""
        self.data_manager.save_tables(self.tables)
    
    def create_table(self) -> str:
        """Create a new table and return its name"""
        table_number = self.data_manager.get_next_table_number()
        table_name = f"Table {table_number}"
        
        # Ensure unique table name
        while table_name in self.tables:
            table_number = self.data_manager.get_next_table_number()
            table_name = f"Table {table_number}"
        
        self.tables[table_name] = Table(table_number)
        self.save_data()
        self.notify_observers()
        
        return table_name
    
    def delete_table(self, table_name: str) -> bool:
        """Delete a table"""
        if table_name in self.tables:
            del self.tables[table_name]
            self.save_data()
            self.notify_observers()
            return True
        return False
    
    def add_item_to_table(self, table_name: str, item_name: str, price: float, quantity: int) -> bool:
        """Add an item to a table"""
        if table_name not in self.tables:
            return False
        
        try:
            self.tables[table_name].add_item(item_name, price, quantity)
            self.save_data()
            self.notify_observers()
            return True
        except ValueError:
            return False
    
    def remove_item_from_table(self, table_name: str, item_index: int) -> bool:
        """Remove an item from a table"""
        if table_name not in self.tables:
            return False
        
        try:
            self.tables[table_name].remove_item(item_index)
            self.save_data()
            self.notify_observers()
            return True
        except (ValueError, IndexError):
            return False
    
    def update_item_quantity(self, table_name: str, item_index: int, new_quantity: int) -> bool:
        """Update item quantity in a table"""
        if table_name not in self.tables:
            return False
        
        try:
            self.tables[table_name].update_item_quantity(item_index, new_quantity)
            self.save_data()
            self.notify_observers()
            return True
        except (ValueError, IndexError):
            return False
    
    def update_item_price(self, table_name: str, item_index: int, new_price: float) -> bool:
        """Update item price in a table"""
        if table_name not in self.tables:
            return False
        
        try:
            self.tables[table_name].update_item_price(item_index, new_price)
            self.save_data()
            self.notify_observers()
            return True
        except (ValueError, IndexError):
            return False
    
    def finalize_table(self, table_name: str) -> bool:
        """Finalize a table's bill"""
        if table_name not in self.tables:
            return False
        
        try:
            self.tables[table_name].finalize()
            self.save_data()
            self.notify_observers()
            return True
        except ValueError:
            return False
    
    def get_table(self, table_name: str) -> Optional[Table]:
        """Get a table by name"""
        return self.tables.get(table_name)
    
    def get_all_tables(self) -> Dict[str, Table]:
        """Get all tables"""
        return self.tables.copy()
    
    def get_sales_summary(self) -> dict:
        """Get sales summary statistics"""
        total_sales = 0
        total_items = 0
        active_tables = 0
        finalized_tables = 0
        
        for table in self.tables.values():
            if table.is_active:
                active_tables += 1
            else:
                finalized_tables += 1
                total_sales += table.get_total()
                total_items += table.get_item_count()
        
        return {
            "total_sales": total_sales,
            "total_items": total_items,
            "active_tables": active_tables,
            "finalized_tables": finalized_tables,
            "total_tables": len(self.tables)
        }

    def get_tables(self) -> List[Table]:
        """Get all tables as a list"""
        return list(self.tables.values())
    
    def create_table_with_name(self, table_name: str, table_number: int) -> bool:
        """Create a new table with a specific name and number"""
        try:
            from ..models.table import Table
            
            # Create new table with specific number
            new_table = Table(table_number)
            
            # Add to tables dictionary with the specific name
            self.tables[table_name] = new_table
            
            # Notify observers
            self.notify_observers()
            
            return True
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
            return False

    def get_or_create_table(self, table_name: str, table_number: int):
        """Get existing table or create new one if it doesn't exist"""
        table = self.get_table(table_name)
        if not table:
            self.create_table_with_name(table_name, table_number)
            table = self.get_table(table_name)
        return table
