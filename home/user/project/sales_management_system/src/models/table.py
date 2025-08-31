
"""
Table model for the sales management system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class SaleItem:
    """Represents an item in a sale"""
    name: str
    price: float
    quantity: int
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if not self.name.strip():
            raise ValueError("Item name cannot be empty")
    
    @property
    def total(self) -> float:
        """Calculate total price for this item"""
        return self.price * self.quantity
    
    def to_dict(self) -> dict:
        """Convert sale item to dictionary"""
        return {
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "total": self.total
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SaleItem':
        """Create sale item from dictionary"""
        return cls(
            name=data["name"],
            price=data["price"],
            quantity=data["quantity"]
        )

@dataclass
class Table:
    """Represents a table in the restaurant"""
    table_number: int
    items: List[SaleItem] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    finalized_at: Optional[datetime] = None
    
    def add_item(self, item_name: str, price: float, quantity: int) -> None:
        """Add an item to the table or update quantity if exists"""
        if not self.is_active:
            raise ValueError("Cannot add items to a finalized table")
        
        # Check if item already exists
        for item in self.items:
            if item.name == item_name:
                item.quantity += quantity
                return
        
        # Add new item
        self.items.append(SaleItem(item_name, price, quantity))
    
    def remove_item(self, index: int) -> None:
        """Remove an item from the table"""
        if not self.is_active:
            raise ValueError("Cannot remove items from a finalized table")
        
        if 0 <= index < len(self.items):
            self.items.pop(index)
        else:
            raise IndexError("Invalid item index")
    
    def update_item_quantity(self, index: int, new_quantity: int) -> None:
        """Update the quantity of an item"""
        if not self.is_active:
            raise ValueError("Cannot update items in a finalized table")
        
        if 0 <= index < len(self.items):
            if new_quantity <= 0:
                self.remove_item(index)
            else:
                self.items[index].quantity = new_quantity
        else:
            raise IndexError("Invalid item index")
    
    def update_item_price(self, index: int, new_price: float) -> None:
        """Update the price of an item"""
        if not self.is_active:
            raise ValueError("Cannot update items in a finalized table")
        
        if 0 <= index < len(self.items):
            if new_price < 0:
                raise ValueError("Price cannot be negative")
            self.items[index].price = new_price
        else:
            raise IndexError("Invalid item index")
    
    def get_total(self) -> float:
        """Calculate total amount for the table"""
        return sum(item.total for item in self.items)
    
    def get_item_count(self) -> int:
        """Get total number of items"""
        return sum(item.quantity for item in self.items)
    
    def finalize(self) -> None:
        """Finalize the table bill"""
        if not self.items:
            raise ValueError("Cannot finalize an empty table")
        
        self.is_active = False
        self.finalized_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert table to dictionary"""
        return {
            "table_number": self.table_number,
            "items": [item.to_dict() for item in self.items],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "finalized_at": self.finalized_at.isoformat() if self.finalized_at else None,
            "total": self.get_total(),
            "item_count": self.get_item_count()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Table':
        """Create table from dictionary"""
        table = cls(
            table_number=data["table_number"],
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
        
        if data.get("finalized_at"):
            table.finalized_at = datetime.fromisoformat(data["finalized_at"])
        
        table.items = [SaleItem.from_dict(item_data) for item_data in data["items"]]
        
        return table
