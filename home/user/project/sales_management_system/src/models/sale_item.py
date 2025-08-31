
"""
Sale item model for the sales management system
"""

from dataclasses import dataclass

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
