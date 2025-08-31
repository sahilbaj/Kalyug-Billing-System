
"""
Main window for the sales management system
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from typing import Optional
from ..controllers.sales_controller import SalesController
from config.settings import APP_SETTINGS
import json
from pathlib import Path
from ..utils.receipt_manager import ReceiptManager

class MainWindow:
    """Main application window with modern dark theme"""

# Update the __init__ method to include receipt manager
    def __init__(self):
        self.root = tk.Tk()
        self.controller = SalesController()
        self.current_table_name: Optional[str] = None
        self.receipt_manager = ReceiptManager()  # Add this line

        self.setup_window()
        self.setup_dark_theme()
        self.setup_ui()
        self.setup_bindings()

        # Register as observer for data changes
        self.controller.add_observer(self.on_data_changed)

        # Initial data load
        self.refresh_all_data()

    def setup_window(self) -> None:
        """Configure the main window with responsive sizing"""
        self.root.title(APP_SETTINGS["title"])

        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate optimal window size based on screen resolution
        if screen_width >= 1920 and screen_height >= 1080:  # 1080p and above
            window_width = 1600
            window_height = 1000
            min_width = 1400
            min_height = 900
        elif screen_width >= 1366 and screen_height >= 768:  # 720p
            window_width = 1300
            window_height = 850
            min_width = 1200
            min_height = 800
        else:  # Smaller screens
            window_width = int(screen_width * 0.9)
            window_height = int(screen_height * 0.85)
            min_width = 1000
            min_height = 700

        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(min_width, min_height)
        self.root.configure(bg='#1e1e1e')

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def setup_dark_theme(self) -> None:
        """Setup modern dark theme"""
        style = ttk.Style()

        # Use default theme as base
        style.theme_use('clam')

        # Configure styles for different widgets
        style.configure('TFrame', background='#2d2d2d', relief='flat')
        style.configure('TLabelFrame', background='#2d2d2d', foreground='#ffffff',
                        relief='solid', borderwidth=1)
        style.configure('TLabelFrame.Label', background='#2d2d2d', foreground='#00d4ff',
                        font=('Segoe UI', 10, 'bold'))

        style.configure('TLabel', background='#2d2d2d', foreground='#ffffff',
                        font=('Segoe UI', 9))
        style.configure('Title.TLabel', background='#2d2d2d', foreground='#00d4ff',
                        font=('Segoe UI', 12, 'bold'))
        style.configure('Total.TLabel', background='#2d2d2d', foreground='#00ff88',
                        font=('Segoe UI', 14, 'bold'))

        style.configure('TButton', background='#404040', foreground='#ffffff',
                        font=('Segoe UI', 8), relief='flat', borderwidth=1)
        style.map('TButton',
                  background=[('active', '#505050'), ('pressed', '#303030')])

        style.configure('Primary.TButton', background='#0078d4', foreground='#ffffff',
                        font=('Segoe UI', 8, 'bold'), relief='flat', borderwidth=1)
        style.map('Primary.TButton',
                  background=[('active', '#106ebe'), ('pressed', '#005a9e')])

        style.configure('Success.TButton', background='#107c10', foreground='#ffffff',
                        font=('Segoe UI', 8, 'bold'), relief='flat', borderwidth=1)
        style.map('Success.TButton',
                  background=[('active', '#0e6e0e'), ('pressed', '#0c5d0c')])

        style.configure('Danger.TButton', background='#d13438', foreground='#ffffff',
                        font=('Segoe UI', 8, 'bold'), relief='flat', borderwidth=1)
        style.map('Danger.TButton',
                  background=[('active', '#b92b2f'), ('pressed', '#a02327')])

        style.configure('Warning.TButton', background='#ff8c00', foreground='#ffffff',
                        font=('Segoe UI', 8, 'bold'), relief='flat', borderwidth=1)
        style.map('Warning.TButton',
                  background=[('active', '#e67e00'), ('pressed', '#cc7000')])

        style.configure('TEntry', fieldbackground='#404040', foreground='#ffffff',
                        borderwidth=1, relief='solid', insertcolor='#ffffff')
        style.configure('TSpinbox', fieldbackground='#404040', foreground='#ffffff',
                        borderwidth=1, relief='solid', insertcolor='#ffffff')

        style.configure('Treeview', background='#353535', foreground='#ffffff',
                        fieldbackground='#353535', borderwidth=1, relief='solid')
        style.configure('Treeview.Heading', background='#404040', foreground='#00d4ff',
                        font=('Segoe UI', 9, 'bold'), relief='flat')
        style.map('Treeview', background=[('selected', '#0078d4')])

        style.configure('Vertical.TScrollbar', background='#404040', troughcolor='#2d2d2d',
                        borderwidth=0, arrowcolor='#ffffff')

    def setup_ui(self) -> None:
        """Setup the user interface"""
        # Add menu bar
        self.setup_menu_bar()

        # Main container with gradient effect
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)  # Only menu items panel gets weight
        main_frame.rowconfigure(0, weight=1)

        # Setup panels - only tables and menu items
        self.setup_tables_panel(main_frame)
        self.setup_items_panel(main_frame)
        self.setup_status_bar()

    def setup_menu_bar(self) -> None:
        """Setup the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Data", command=self.controller.save_data, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Sales Reports", command=self.view_sales_reports)
        reports_menu.add_command(label="Today's Summary", command=self.show_daily_sales_report)
        reports_menu.add_separator()
        reports_menu.add_command(label="🔍 Removal Audit Log", command=self.view_removal_audit_log)

        # Tables menu
        tables_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tables", menu=tables_menu)
        tables_menu.add_command(label="New Table", command=self.create_new_table, accelerator="Ctrl+N")
        tables_menu.add_command(label="Clear All Finalized", command=self.clear_all_finalized)
        tables_menu.add_separator()
        tables_menu.add_command(label="Refresh", command=self.refresh_all_data, accelerator="F5")

    def setup_tables_panel(self, parent: ttk.Frame) -> None:
        """Setup the tables management panel with fixed 15 tables"""
        tables_frame = ttk.LabelFrame(parent, text="🍽️ Tables (15 Available)", padding="10")
        tables_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        tables_frame.rowconfigure(2, weight=1)

        # Quick table buttons grid (3x5 = 15 tables)
        quick_tables_frame = ttk.LabelFrame(tables_frame, text="Quick Table Access", padding="8")
        quick_tables_frame.pack(fill=tk.X, pady=(0, 10))

        # Create 15 table buttons in a 3x5 grid
        self.table_buttons = {}
        for i in range(15):
            table_num = i + 1
            row = i // 5
            col = i % 5

            btn = ttk.Button(quick_tables_frame, text=f"T{table_num}", width=8,
                             command=lambda t=table_num: self.select_table(t))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky=(tk.W, tk.E))
            self.table_buttons[table_num] = btn

            # Configure column weights
            quick_tables_frame.columnconfigure(col, weight=1)

        # Table details section
        details_section = ttk.LabelFrame(tables_frame, text="📋 Selected Table Details", padding="8")
        details_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        details_section.columnconfigure(0, weight=1)
        details_section.rowconfigure(1, weight=1)

        # Table info with modern styling
        info_frame = ttk.Frame(details_section)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.table_info_label = ttk.Label(info_frame, text="No table selected", style='Title.TLabel')
        self.table_info_label.pack(side=tk.LEFT)

        # Items treeview (compact version)
        items_container = ttk.Frame(details_section)
        items_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        items_container.columnconfigure(0, weight=1)
        items_container.rowconfigure(0, weight=1)

        columns = ("Item", "Qty", "Price", "Total")
        self.items_tree = ttk.Treeview(items_container, columns=columns, show="headings", height=8)

        column_widths = {"Item": 100, "Qty": 40, "Price": 60, "Total": 70}
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=column_widths[col], minwidth=40)

        self.items_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add this line to make the tree focusable
        self.items_tree.bind('<Button-1>', lambda e: self.items_tree.focus_set())

        # Scrollbar for items
        items_scrollbar = ttk.Scrollbar(items_container, orient=tk.VERTICAL, command=self.items_tree.yview)
        items_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)

        # Total display
        total_frame = ttk.Frame(details_section)
        total_frame.pack(fill=tk.X, pady=(0, 10))

        self.total_label = ttk.Label(total_frame, text="Total: ₹0.00", style='Total.TLabel')
        self.total_label.pack(side=tk.RIGHT)

        # Control buttons with modern styling
        controls_frame = ttk.Frame(tables_frame)
        controls_frame.pack(fill=tk.X)

        ttk.Button(controls_frame, text="✅ Finalize Bill", style='Success.TButton',
                   command=self.finalize_selected_table).pack(fill=tk.X, pady=(0, 4))
        ttk.Button(controls_frame, text="🗑️ Clear Table", style='Danger.TButton',
                   command=self.clear_selected_table).pack(fill=tk.X, pady=(0, 4))
        ttk.Button(controls_frame, text="🧹 Clear All Finalized", style='Warning.TButton',
                   command=self.clear_all_finalized).pack(fill=tk.X)

    def clear_all_finalized(self) -> None:
        """Clear all finalized tables to make them available for reuse"""
        if messagebox.askyesno("Confirm", "Clear all finalized tables? This will make them available for new orders."):
            cleared_count = 0
            tables = self.controller.get_tables()

            for table in tables:
                if not table.is_active:  # Finalized table
                    # Save to daily sales before clearing
                    if table.items:
                        self.save_to_daily_sales(table)

                    table_name = f"Table {table.table_number}"
                    if hasattr(self.controller, 'clear_table'):
                        if self.controller.clear_table(table_name):
                            cleared_count += 1
                    else:
                        # Fallback: delete the table
                        if self.controller.delete_table(table_name):
                            cleared_count += 1

            self.status_label.config(text=f"🧹 Cleared {cleared_count} finalized tables")

            # Force refresh all data and UI components
            self.refresh_all_data()
            self.update_table_button_colors()

            # If current table was cleared, refresh its details
            if self.current_table_name:
                current_table = self.controller.get_table(self.current_table_name)
                if not current_table or not current_table.items:
                    self.refresh_table_details()

            # Trigger observer pattern to ensure all UI updates
            self.on_data_changed()

    def save_to_daily_sales(self, table) -> None:
        """Save finalized table data to daily sales records"""
        try:
            from datetime import datetime
            import json

            # Create sales data structure
            sales_data = {
                "table_name": f"Table {table.table_number}",
                "table_number": table.table_number,
                "finalized_at": datetime.now().isoformat(),
                "items": [],
                "total_amount": table.get_total(),
                "items_count": len(table.items)
            }

            # Add item details
            for item in table.items:
                item_data = {
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "total": item.total
                }
                sales_data["items"].append(item_data)

            # Save to daily sales
            self.update_daily_sales(sales_data)

        except Exception as e:
            print(f"Error saving to daily sales: {e}")
            # Don't show error to user as this is background operation

    def update_daily_sales(self, sales_data: dict) -> None:
        """Update daily sales summary and detailed records"""
        try:
            from datetime import datetime

            # Get the data directory path
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
            data_dir.mkdir(exist_ok=True)

            today = datetime.now().strftime("%Y-%m-%d")
            daily_sales_file = data_dir / f"daily_sales_{today}.json"

            # Load existing daily data or create new
            if daily_sales_file.exists():
                with open(daily_sales_file, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
            else:
                daily_data = {
                    "date": today,
                    "total_sales": 0.0,
                    "total_orders": 0,
                    "items_sold": {},
                    "hourly_breakdown": {},
                    "orders": []  # Detailed order records
                }

            # Update summary
            daily_data["total_sales"] += sales_data["total_amount"]
            daily_data["total_orders"] += 1

            # Update items sold count
            for item in sales_data["items"]:
                item_name = item["name"]
                if item_name in daily_data["items_sold"]:
                    daily_data["items_sold"][item_name] += item["quantity"]
                else:
                    daily_data["items_sold"][item_name] = item["quantity"]

            # Update hourly breakdown
            hour = datetime.fromisoformat(sales_data["finalized_at"]).strftime("%H:00")
            if hour in daily_data["hourly_breakdown"]:
                daily_data["hourly_breakdown"][hour] += sales_data["total_amount"]
            else:
                daily_data["hourly_breakdown"][hour] = sales_data["total_amount"]

            # Add detailed order record
            daily_data["orders"].append(sales_data)

            # Save daily data
            with open(daily_sales_file, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error updating daily sales: {e}")

    def select_table(self, table_number: int) -> None:
        """Select a table by number"""
        table_name = f"Table {table_number}"

        # Get or create the table
        table = self.controller.get_or_create_table(table_name, table_number)

        if not table:
            messagebox.showerror("Error", f"Could not create or access {table_name}")
            return

        self.current_table_name = table_name

        # Update UI displays
        self.refresh_table_details()
        self.update_table_button_colors()
        self.status_label.config(text=f"📋 Selected {table_name}")

    def clear_selected_table(self, auto_clear: bool = False) -> None:
        """Clear the selected table (make it available for reuse)"""
        if not self.current_table_name:
            if not auto_clear:  # Only show warning if not auto-clearing
                messagebox.showwarning("Warning", "Please select a table to clear!")
            return

        table = self.controller.get_table(self.current_table_name)
        if not table:
            # If table doesn't exist, just update the UI
            self.refresh_table_details()
            self.update_table_button_colors()
            return

        # If table has items and is finalized, save to daily sales before clearing
        if table.items and not table.is_active:
            self.save_to_daily_sales(table)

        # Only ask for confirmation if it's a manual clear and table is active with items
        if table.is_active and table.items and not auto_clear:
            if not messagebox.askyesno("Confirm", f"Clear {self.current_table_name}? This will remove all items without finalizing the bill."):
                return

        # Use existing delete method or clear items
        if hasattr(self.controller, 'clear_table'):
            success = self.controller.clear_table(self.current_table_name)
        else:
            # Fallback: delete the table entirely
            success = self.controller.delete_table(self.current_table_name)

        if success:
            if auto_clear:
                self.status_label.config(text=f"✅ {self.current_table_name} cleared and ready for reuse")
            else:
                self.status_label.config(text=f"🧹 Cleared {self.current_table_name}")
            # Force refresh the table details immediately
            self.refresh_table_details()
            self.update_table_button_colors()
            # Also trigger the observer pattern to ensure all UI updates
            self.on_data_changed()
        else:
            if not auto_clear:  # Only show error if not auto-clearing
                messagebox.showerror("Error", "Failed to clear table!")

    def update_table_button_colors(self) -> None:
        """Update table button colors based on their status"""
        for table_num in range(1, 16):
            table_name = f"Table {table_num}"
            table = self.controller.get_table(table_name)
            btn = self.table_buttons[table_num]

            if not table or not table.items:
                # Empty/Available table - Green
                btn.configure(style='Success.TButton')
                btn.configure(text=f"T{table_num}\n🟢")
            elif table.is_active and table.items:
                # Active table with items - Yellow
                btn.configure(style='Warning.TButton')
                btn.configure(text=f"T{table_num}\n🟡({len(table.items)})")
            elif not table.is_active:
                # Finalized table - Orange/Red
                btn.configure(style='Danger.TButton')
                btn.configure(text=f"T{table_num}\n🔴✓")

    def setup_table_details_panel(self, parent: ttk.Frame) -> None:
        """Setup the table item management panel"""
        details_frame = ttk.LabelFrame(parent, text="🛠️ Item Management", padding="10")
        details_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=8)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)

        # Item controls with modern layout
        controls_container = ttk.Frame(details_frame)
        controls_container.pack(fill=tk.X, pady=(0, 15))

        # Remove button
        ttk.Button(controls_container, text="❌ Remove Selected Item", style='Danger.TButton',
                   command=self.remove_selected_item).pack(fill=tk.X, pady=(0, 8))

        # Quantity update section
        qty_frame = ttk.LabelFrame(controls_container, text="Update Quantity", padding="8")
        qty_frame.pack(fill=tk.X, pady=(0, 8))

        qty_input_frame = ttk.Frame(qty_frame)
        qty_input_frame.pack(fill=tk.X)

        ttk.Label(qty_input_frame, text="New Qty:").pack(side=tk.LEFT, padx=(0, 5))
        self.qty_var = tk.StringVar()
        qty_spinbox = ttk.Spinbox(qty_input_frame, from_=1, to=99, width=8, textvariable=self.qty_var)
        qty_spinbox.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(qty_input_frame, text="🔄 Update", style='Primary.TButton',
                   command=self.update_selected_item_quantity).pack(side=tk.LEFT)

        # Manual item entry section
        manual_frame = ttk.LabelFrame(details_frame, text="Add Custom Item", padding="8")
        manual_frame.pack(fill=tk.X, pady=(0, 15))

        # Item name
        name_frame = ttk.Frame(manual_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(name_frame, text="Item Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.item_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.item_name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Price and quantity
        price_qty_frame = ttk.Frame(manual_frame)
        price_qty_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(price_qty_frame, text="Price:").pack(side=tk.LEFT, padx=(0, 5))
        self.item_price_var = tk.StringVar()
        ttk.Entry(price_qty_frame, textvariable=self.item_price_var, width=10).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(price_qty_frame, text="Qty:").pack(side=tk.LEFT, padx=(0, 5))
        self.item_quantity_var = tk.StringVar(value="1")
        ttk.Spinbox(price_qty_frame, from_=1, to=99, width=8, textvariable=self.item_quantity_var).pack(side=tk.LEFT)

        # Add button
        ttk.Button(manual_frame, text="➕ Add to Table", style='Success.TButton',
                   command=self.add_manual_item_to_table).pack(fill=tk.X)

        # Instructions
        instructions_frame = ttk.Frame(details_frame)
        instructions_frame.pack(fill=tk.BOTH, expand=True)

        instructions_text = """
    💡 Instructions:
    • Select a table from the left panel
    • Click menu items to add them to the table
    • Use controls above to modify items
    • Finalize bill when order is complete
    • Clear table to make it available for reuse
        """

        ttk.Label(instructions_frame, text=instructions_text, style='TLabel',
                  justify=tk.LEFT, wraplength=300).pack(pady=20)

    def setup_items_panel(self, parent: ttk.Frame) -> None:
        """Setup the items panel with enhanced menu items display"""
        items_frame = ttk.LabelFrame(parent, text="🍽️ Menu Items", padding="15")  # Increased padding
        items_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        items_frame.rowconfigure(0, weight=1)
        items_frame.columnconfigure(0, weight=1)

        # Create scrollable frame for products with enhanced styling
        canvas = tk.Canvas(items_frame, bg='#2d2d2d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Load and display products with enhanced layout
        self.load_and_display_products(scrollable_frame)

        # Grid canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Enhanced mousewheel binding with better scroll speed
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/60)), "units")  # Smoother scrolling
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def setup_status_bar(self) -> None:
        """Setup the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status with modern styling
        status_container = ttk.Frame(self.status_bar, padding="10")
        status_container.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_container, text="🟢 Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Sales summary with better formatting
        self.summary_label = ttk.Label(status_container, text="")
        self.summary_label.pack(side=tk.RIGHT)

    def setup_bindings(self) -> None:
        """Setup event bindings"""
        # Add right-click context menu for items tree
        self.items_tree.bind('<Button-3>', self.show_item_context_menu)

        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.create_new_table())
        self.root.bind('<Control-s>', lambda e: self.controller.save_data())
        self.root.bind('<F5>', lambda e: self.refresh_all_data())

        # Add Delete key binding for removing selected item from tree
        self.items_tree.bind('<Delete>', self.on_delete_key_pressed)
        self.items_tree.bind('<BackSpace>', self.on_delete_key_pressed)  # Also support Backspace

        # Add double-click to edit quantity
        self.items_tree.bind('<Double-1>', self.on_item_double_click)

        # Add Enter key to edit quantity
        self.items_tree.bind('<Return>', lambda e: self.edit_item_quantity_dialog())

    def on_item_double_click(self, event) -> None:
        """Handle double-click on items tree to edit quantity"""
        try:
            # Check if an item is selected
            selection = self.items_tree.selection()
            if selection:
                self.edit_item_quantity_dialog()
        except Exception as e:
            print(f"Error handling double-click: {e}")

    def edit_item_quantity_dialog(self) -> None:
        """Show dialog to edit item quantity"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "No table selected!")
            return

        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit!")
            return

        try:
            # Get current item details
            item_values = self.items_tree.item(selection[0], "values")
            if not item_values or len(item_values) < 4:
                messagebox.showerror("Error", "Invalid item selection!")
                return

            item_name = item_values[0]
            current_qty = int(item_values[1])
            item_price = item_values[2].replace('₹', '')

            # Create quantity edit dialog
            qty_window = tk.Toplevel(self.root)
            qty_window.title("✏️ Edit Quantity")
            qty_window.geometry("350x350")
            qty_window.configure(bg='#1e1e1e')
            qty_window.resizable(False, False)

            # Center the window
            qty_window.transient(self.root)
            qty_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(qty_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            ttk.Label(main_frame, text="✏️ Edit Item Quantity",
                      style='Title.TLabel').pack(pady=(0, 15))

            # Item info
            info_frame = ttk.LabelFrame(main_frame, text="Item Details", padding="10")
            info_frame.pack(fill=tk.X, pady=(0, 15))

            ttk.Label(info_frame, text=f"Item: {item_name}",
                      style='TLabel').pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Price: {item_price}",
                      style='TLabel').pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Current Quantity: {current_qty}",
                      style='TLabel').pack(anchor=tk.W, pady=2)

            # Quantity input
            qty_frame = ttk.LabelFrame(main_frame, text="New Quantity", padding="10")
            qty_frame.pack(fill=tk.X, pady=(0, 15))

            qty_input_frame = ttk.Frame(qty_frame)
            qty_input_frame.pack(fill=tk.X)

            # Quantity spinbox with current value
            qty_var = tk.StringVar(value=str(current_qty))
            qty_spinbox = ttk.Spinbox(qty_input_frame, from_=0, to=99, width=10,
                                      textvariable=qty_var, font=('Segoe UI', 12))
            qty_spinbox.pack(side=tk.LEFT, padx=(0, 10))
            qty_spinbox.focus()
            qty_spinbox.select_range(0, tk.END)

            # Quick buttons for common operations
            quick_frame = ttk.Frame(qty_input_frame)
            quick_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            ttk.Button(quick_frame, text="-1", width=4,
                       command=lambda: self.adjust_quantity(qty_var, -1)).pack(side=tk.LEFT, padx=2)
            ttk.Button(quick_frame, text="+1", width=4,
                       command=lambda: self.adjust_quantity(qty_var, 1)).pack(side=tk.LEFT, padx=2)
            ttk.Button(quick_frame, text="+5", width=4,
                       command=lambda: self.adjust_quantity(qty_var, 5)).pack(side=tk.LEFT, padx=2)

            # Result variable
            result = {'confirmed': False, 'new_qty': current_qty}

            def confirm_edit():
                try:
                    new_qty = int(qty_var.get())
                    if new_qty < 0:
                        messagebox.showerror("Invalid Quantity", "Quantity cannot be negative!")
                        return

                    result['confirmed'] = True
                    result['new_qty'] = new_qty
                    qty_window.destroy()

                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter a valid number!")

            def cancel_edit():
                qty_window.destroy()

            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X)

            ttk.Button(buttons_frame, text="✅ Update Quantity",
                       style='Success.TButton', command=confirm_edit).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="❌ Cancel",
                       style='Danger.TButton', command=cancel_edit).pack(side=tk.LEFT)

            # Bind Enter key to confirm
            qty_spinbox.bind('<Return>', lambda e: confirm_edit())
            qty_window.bind('<Escape>', lambda e: cancel_edit())

            # Wait for dialog to close
            qty_window.wait_window()

            # Process result
            if result['confirmed']:
                item_index = self.items_tree.index(selection[0])
                new_qty = result['new_qty']

                if new_qty == 0:
                    # If quantity is 0, ask to remove item
                    if messagebox.askyesno("Remove Item", f"Quantity is 0. Remove {item_name} from the table?"):
                        if self.controller.remove_item_from_table(self.current_table_name, item_index):
                            self.status_label.config(text=f"❌ Removed {item_name}")
                        else:
                            messagebox.showerror("Error", "Failed to remove item!")
                else:
                    # Update quantity
                    if self.controller.update_item_quantity(self.current_table_name, item_index, new_qty):
                        self.status_label.config(text=f"🔄 Updated {item_name} quantity to {new_qty}")
                    else:
                        messagebox.showerror("Error", "Failed to update quantity!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit quantity: {e}")

    def adjust_quantity(self, qty_var: tk.StringVar, adjustment: int) -> None:
        """Adjust quantity by the given amount"""
        try:
            current_qty = int(qty_var.get())
            new_qty = max(0, current_qty + adjustment)  # Don't go below 0
            qty_var.set(str(new_qty))
        except ValueError:
            qty_var.set("1")  # Reset to 1 if invalid

    def on_delete_key_pressed(self, event) -> None:
        """Handle Delete/Backspace key press on items tree"""
        try:
            # Check if items tree has focus and an item is selected
            if self.root.focus_get() == self.items_tree:
                selection = self.items_tree.selection()
                if selection:
                    # Call the existing remove function
                    self.remove_selected_item_simple()
            
        except Exception as e:
            print(f"Error handling delete key: {e}")

    def show_item_context_menu(self, event) -> None:
        """Show context menu for items tree"""
        try:
            # Select the item under cursor
            item = self.items_tree.identify_row(event.y)
            if item:
                self.items_tree.selection_set(item)

                # Create context menu
                context_menu = tk.Menu(self.root, tearoff=0)
                context_menu.add_command(label="✏️ Edit Quantity", command=self.edit_item_quantity_dialog)
                context_menu.add_separator()
                context_menu.add_command(label="❌ Remove Item", command=self.remove_selected_item_simple)
                context_menu.add_command(label="➕ Add Same Item", command=self.add_same_item)

                # Show menu
                context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def remove_selected_item_simple(self) -> None:
        """Remove the selected item from the table (simplified version)"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "No table selected!")
            return
    
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
    
        item_index = self.items_tree.index(selection[0])
    
        if messagebox.askyesno("Confirm", "Remove this item?"):
            if self.controller.remove_item_from_table(self.current_table_name, item_index):
                self.status_label.config(text="❌ Item removed")
            else:
                messagebox.showerror("Error", "Failed to remove item!")

    def add_same_item(self) -> None:
        """Add another instance of the selected item"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "No table selected!")
            return
    
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item!")
            return
    
        # Get item details from the tree
        values = self.items_tree.item(selection[0], "values")
        if values and len(values) >= 3:
            item_name = values[0]
            # Extract price from the price column (remove ₹ symbol)
            price_str = values[2].replace('₹', '')
            try:
                price = float(price_str)
                
                # Add item to table
                if self.controller.add_item_to_table(self.current_table_name, item_name, price, 1):
                    self.status_label.config(text=f"🛒 Added another {item_name}")
                else:
                    messagebox.showerror("Error", "Failed to add item!")
            except ValueError:
                messagebox.showerror("Error", "Invalid price format!")

    def on_data_changed(self) -> None:
        """Handle data changes from controller"""
        self.refresh_tables_list()
        self.refresh_table_details()
        self.update_status_bar()

    def on_table_select(self, event) -> None:
        """Handle table selection - simplified since no tree selection"""
        pass
    
    def on_item_select(self, event) -> None:
        """Handle item selection - no longer needed but kept for compatibility"""
        pass
    
    def create_new_table(self) -> None:
        """Find and select the next available table"""
        for table_num in range(1, 16):
            table_name = f"Table {table_num}"
            table = self.controller.get_table(table_name)
            
            if not table or not table.items:
                self.select_table(table_num)
                return
        
        messagebox.showwarning("Warning", "All tables are occupied! Please finalize or clear a table first.")

    def delete_selected_table(self) -> None:
        """This method is replaced by clear_selected_table"""
        self.clear_selected_table()

    def finalize_selected_table(self) -> None:
        """Finalize the selected table with receipt generation"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "Please select a table to finalize!")
            return

        table = self.controller.get_table(self.current_table_name)
        if not table:
            messagebox.showerror("Error", "Table not found!")
            return

        if not table.is_active:
            # If table is already finalized, offer to clear it
            if messagebox.askyesno("Table Finalized", f"{self.current_table_name} is already finalized. Clear it for reuse?"):
                self.clear_selected_table()
            return

        if not table.items:
            messagebox.showwarning("Warning", "Cannot finalize an empty table!")
            return

        # Show bill summary
        total = table.get_total()
        items_summary = "\n".join([f"{item.name} x{item.quantity} = ₹{item.total:.2f}"
                                   for item in table.items])

        bill_text = f"{self.current_table_name} Bill Summary:\n\n{items_summary}\n\nTotal: ₹{total:.2f}"

        if messagebox.askyesno("Finalize Bill", f"{bill_text}\n\nFinalize this bill?"):
            if self.controller.finalize_table(self.current_table_name):
                self.status_label.config(text=f"✅ Finalized {self.current_table_name}")

                # Prepare table data for receipt
                table_data = {
                    'table_name': self.current_table_name,
                    'table_number': table.table_number,
                    'items': [
                        {
                            'name': item.name,
                            'quantity': item.quantity,
                            'price': item.price,
                            'total': item.total
                        }
                        for item in table.items
                    ],
                    'total_amount': total,
                    'finalized_at': datetime.now().isoformat()
                }

                # Show receipt options dialog
                self.show_receipt_options(table_data)

            else:
                messagebox.showerror("Error", "Failed to finalize table!")

    def show_receipt_options(self, table_data: dict) -> None:
        """Show receipt options after finalizing a bill"""
        try:
            # Create receipt options window
            options_window = tk.Toplevel(self.root)
            options_window.title("📄 Receipt Options")
            options_window.geometry("400x300")
            options_window.configure(bg='#1e1e1e')
            options_window.resizable(False, False)

            # Center the window
            options_window.transient(self.root)
            options_window.grab_set()

            # Main frame
            main_frame = ttk.Frame(options_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            ttk.Label(main_frame, text="📄 Bill Finalized Successfully!",
                      font=('Segoe UI', 14, 'bold'), foreground='#00d4ff').pack(pady=(0, 10))

            # Bill summary
            total_amount = table_data.get('total_amount', 0)
            table_name = table_data.get('table_name', 'Unknown')

            ttk.Label(main_frame, text=f"Table: {table_name}",
                      font=('Segoe UI', 12)).pack(pady=2)
            ttk.Label(main_frame, text=f"Total: ₹{total_amount:.2f}",
                      font=('Segoe UI', 12, 'bold'), foreground='#00ff88').pack(pady=2)

            ttk.Label(main_frame, text="What would you like to do?",
                      font=('Segoe UI', 10)).pack(pady=(20, 10))

            # Receipt options buttons
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=10)

            # Preview receipt button
            ttk.Button(buttons_frame, text="👁️ Preview Receipt",
                       command=lambda: self.preview_and_close(table_data, options_window)).pack(fill=tk.X, pady=2)

            # Print receipt button
            ttk.Button(buttons_frame, text="🖨️ Print Receipt",
                       command=lambda: self.print_and_close(table_data, options_window)).pack(fill=tk.X, pady=2)

            # Save receipt button
            ttk.Button(buttons_frame, text="💾 Save Receipt",
                       command=lambda: self.save_and_close(table_data, options_window)).pack(fill=tk.X, pady=2)

            # Separator
            ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)

            # Table management options
            ttk.Label(main_frame, text="Table Management:",
                      font=('Segoe UI', 10)).pack(pady=(10, 5))

            table_buttons_frame = ttk.Frame(main_frame)
            table_buttons_frame.pack(fill=tk.X, pady=5)

            # Clear table button
            ttk.Button(table_buttons_frame, text="🧹 Clear Table for Reuse",
                       command=lambda: self.clear_and_close(options_window)).pack(side=tk.LEFT, padx=(0, 5))

            # Keep finalized button
            ttk.Button(table_buttons_frame, text="📋 Keep as Finalized",
                       command=lambda: self.keep_and_close(options_window)).pack(side=tk.RIGHT, padx=(5, 0))

            # Close button
            ttk.Button(main_frame, text="❌ Close",
                       command=options_window.destroy).pack(pady=(20, 0))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show receipt options: {e}")

    def preview_and_close(self, table_data: dict, options_window: tk.Toplevel) -> None:
        """Preview receipt and close options window"""
        options_window.destroy()
        self.receipt_manager.preview_receipt(table_data, self.root)
        # Automatically clear table after preview
        self.clear_selected_table(auto_clear=True)
        self.update_table_button_colors()

    def print_and_close(self, table_data: dict, options_window: tk.Toplevel) -> None:
        """Print receipt and close options window"""
        options_window.destroy()
        if self.receipt_manager.print_receipt(table_data, self.root):
            # Automatically clear table after successful print
            self.clear_selected_table(auto_clear=True)
        else:
            # If print failed, ask user what to do
            if messagebox.askyesno("Print Failed", "Receipt printing failed!\n\nClear table anyway?"):
                self.clear_selected_table(auto_clear=True)
        self.update_table_button_colors()

    def save_and_close(self, table_data: dict, options_window: tk.Toplevel) -> None:
        """Save receipt and close options window"""
        options_window.destroy()
        if self.receipt_manager.save_receipt(table_data, self.root):
            # Automatically clear table after successful save
            self.clear_selected_table(auto_clear=True)
        else:
            # If save failed, ask user what to do
            if messagebox.askyesno("Save Failed", "Receipt saving failed!\n\nClear table anyway?"):
                self.clear_selected_table(auto_clear=True)
        self.update_table_button_colors()

    def clear_and_close(self, options_window: tk.Toplevel) -> None:
        """Clear table and close options window"""
        options_window.destroy()
        self.clear_selected_table(auto_clear=True)

    def keep_and_close(self, options_window: tk.Toplevel) -> None:
        """Keep table as finalized and close options window"""
        options_window.destroy()
        self.update_table_button_colors()

    def add_manual_item_to_table(self) -> None:
        """Add a manually entered item to the current table"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "Please select a table first!")
            return
        
        # Validate inputs
        item_name = self.item_name_var.get().strip()
        if not item_name:
            messagebox.showerror("Error", "Please enter an item name!")
            return
        
        try:
            price = float(self.item_price_var.get())
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price!")
            return
        
        try:
            quantity = int(self.item_quantity_var.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
            return
        
        # Add item to table
        if self.controller.add_item_to_table(self.current_table_name, item_name, price, quantity):
            self.status_label.config(text=f"🛒 Added {quantity}x {item_name} to {self.current_table_name}")
            self.clear_form()
        else:
            messagebox.showerror("Error", "Failed to add item to table!")
    
    def remove_selected_item(self) -> None:
        """Remove the selected item from the table"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "No table selected!")
            return
        
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        
        item_index = self.items_tree.index(selection[0])
        
        if messagebox.askyesno("Confirm", "Remove this item?"):
            if self.controller.remove_item_from_table(self.current_table_name, item_index):
                self.status_label.config(text="❌ Item removed")
            else:
                messagebox.showerror("Error", "Failed to remove item!")
    
    def update_selected_item_quantity(self) -> None:
        """Update the quantity of the selected item"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "No table selected!")
            return
        
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to update!")
            return
        
        try:
            new_quantity = int(self.qty_var.get())
            if new_quantity < 0:
                raise ValueError("Quantity cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
            return
        
        item_index = self.items_tree.index(selection[0])
        
        if self.controller.update_item_quantity(self.current_table_name, item_index, new_quantity):
            self.status_label.config(text="🔄 Quantity updated")
        else:
            messagebox.showerror("Error", "Failed to update quantity!")
    
    def clear_form(self) -> None:
        """Clear the manual item entry form"""
        self.item_name_var.set("")
        self.item_price_var.set("")
        self.item_quantity_var.set("1")
    
    def refresh_all_data(self) -> None:
        """Refresh all data displays"""
        self.refresh_tables_list()
        self.refresh_table_details()
        self.update_status_bar()

    def refresh_tables_list(self) -> None:
        """Refresh the tables list display"""
        # Update button colors (no tree to update anymore)
        self.update_table_button_colors()

    def refresh_table_details(self) -> None:
        """Refresh the table details display"""
        # Clear existing items first
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        if not self.current_table_name:
            self.table_info_label.config(text="No table selected")
            self.total_label.config(text="Total: ₹0.00")
            return

        table = self.controller.get_table(self.current_table_name)
        if not table or not table.items:
            # Table is empty or doesn't exist
            self.table_info_label.config(text=f"{self.current_table_name} - 🟢 Empty")
            self.total_label.config(text="Total: ₹0.00")
            return
    
        # Update table info
        status = "🟢 Active" if table.is_active else "🔴 Finalized"
        self.table_info_label.config(text=f"{self.current_table_name} - {status}")

        # Add items with price column
        for item in table.items:
            self.items_tree.insert("", "end", values=(
                item.name,
                item.quantity,
                f"₹{item.price:.2f}",
                f"₹{item.total:.2f}"
            ))

        # Update total
        total = table.get_total()
        self.total_label.config(text=f"💰 Total: ₹{total:.2f}")
    
    def update_status_bar(self) -> None:
        """Update the status bar with sales information"""
        tables = self.controller.get_tables()
        active_tables = [t for t in tables if t.is_active]
        finalized_tables = [t for t in tables if not t.is_active]
        
        total_sales = sum(t.get_total() for t in tables)
        
        self.summary_label.config(text=f"🟢 Active: {len(active_tables)} | 🔴 Finalized: {len(finalized_tables)} | 💰 Sales: ₹{total_sales:.2f}")
    
    def run(self) -> None:
        """Start the main loop"""
        self.root.mainloop()
    
    def on_closing(self) -> None:
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.controller.save_data()
            self.root.destroy()

    def load_product_data(self) -> dict:
        """Load all product data from JSON files in productData folder"""
        product_data = {}

        # Get the productData folder path
        current_dir = Path(__file__).parent.parent.parent
        product_data_dir = current_dir / "productData"

        if not product_data_dir.exists():
            print(f"Product data directory not found: {product_data_dir}")
            return product_data

        # Scan all JSON files in the productData folder
        for json_file in product_data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract category name from filename
                category_name = json_file.stem.replace('_', ' ').title()

                # Extract products from different JSON structures
                products = self._extract_products_from_data(data)

                if products:
                    product_data[category_name] = products
                    print(f"Loaded {len(products)} products from {category_name}")
                else:
                    print(f"No valid products found in {json_file}")

            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                print(f"Error loading {json_file}: {e}")
                continue

        return product_data

    def _extract_products_from_data(self, data) -> list:
        """Extract products from various JSON data structures"""
        products = []

        if isinstance(data, list):
            # Data is directly a list of products
            products = data
        elif isinstance(data, dict):
            # Try different common keys for product lists
            for key in ['drinks', 'items', 'products', 'menu', 'food']:
                if key in data and isinstance(data[key], list):
                    products = data[key]
                    break

            # If no common key found, look for any list value
            if not products:
                for value in data.values():
                    if isinstance(value, list) and value:
                        # Check if first item looks like a product
                        if (isinstance(value[0], dict) and
                                any(field in value[0] for field in ['name', 'display_name', 'amount', 'price'])):
                            products = value
                            break

        # Validate and normalize products
        normalized_products = []
        for product in products:
            if isinstance(product, dict):
                normalized_product = self._normalize_product(product)
                if normalized_product:
                    normalized_products.append(normalized_product)

        return normalized_products

    def _normalize_product(self, product: dict) -> dict:
        """Normalize product data to standard format"""
        try:
            # Try to extract name
            name = (product.get('name') or
                    product.get('display_name') or
                    product.get('title') or
                    product.get('item_name'))

            # Try to extract display name
            display_name = (product.get('display_name') or
                            product.get('name') or
                            product.get('title'))

            # Try to extract price/amount
            amount = (product.get('amount') or
                      product.get('price') or
                      product.get('cost') or
                      0.0)

            if name and display_name:
                return {
                    'name': str(name),
                    'display_name': str(display_name),
                    'amount': float(amount)
                }
        except (ValueError, TypeError):
            pass

        return None

    def _create_product_buttons(self, parent_frame: ttk.Frame, products: list, style_name: str) -> None:
        """Create product buttons with simple 5-per-row layout and bigger display"""
        # Clear any existing buttons
        for widget in parent_frame.winfo_children():
            widget.destroy()

        if not products:
            return

        button_width = 140
        font_size = 11

        # Fixed layout: 5 buttons per row
        buttons_per_row = 4
        button_spacing = 10
        row_spacing = 8

        # Create container for all button rows
        buttons_container = ttk.Frame(parent_frame)
        buttons_container.pack(fill=tk.X, pady=10)

        # Create buttons in rows of 5
        for i in range(0, len(products), buttons_per_row):
            row_products = products[i:i + buttons_per_row]

            # Create row frame
            row_frame = ttk.Frame(buttons_container)
            row_frame.pack(fill=tk.X, pady=row_spacing)

            # Create buttons for this row
            for j, product in enumerate(row_products):
                # Truncate long names to fit button
                max_chars = button_width // (font_size - 2)  # Rough character estimate
                item_name = product['display_name']
                if len(item_name) > max_chars:
                    item_name = item_name[:max_chars-3] + "..."

                display_text = f"{item_name}"

                # Create button
                btn = ttk.Button(row_frame,
                                 text=display_text,
                                 style=style_name,
                                 width=button_width // 8,  # Convert to character width
                                 command=lambda p=product: self.add_product_to_table(p))

                # Pack button with spacing
                padx = (button_spacing, 0) if j > 0 else (0, 0)
                btn.pack(side=tk.LEFT, padx=padx, pady=2)

                tooltip_text = f"{product['name']}\nPrice: ₹{product['amount']:.2f}"
                self._create_tooltip(btn, tooltip_text)

    def _optimize_button_layout(self, products: list, available_width: int,
                                min_width: int, max_width: int, spacing: int) -> list:
        """Optimize button layout using smart algorithm"""
        if not products:
            return []

        rows = []
        current_row = []
        current_row_width = 0

        # Try to fit products optimally
        remaining_products = products.copy()

        while remaining_products:
            best_fit = None
            best_fit_index = -1

            # Find the best fitting product for current row
            for i, product in enumerate(remaining_products):
                text_length = len(product['display_name'])
                estimated_width = min(max_width, max(min_width, text_length * 8 + 20))

                # Check if this product fits in current row
                needed_width = estimated_width
                if current_row:
                    needed_width += spacing

                if current_row_width + needed_width <= available_width:
                    # This product fits, check if it's the best fit
                    if best_fit is None or estimated_width > best_fit['width']:
                        best_fit = {
                            'product': product,
                            'width': estimated_width,
                            'index': i
                        }
                        best_fit_index = i

            if best_fit:
                # Add best fitting product to current row
                current_row.append(best_fit['product'])
                current_row_width += best_fit['width']
                if len(current_row) > 1:
                    current_row_width += spacing
                remaining_products.pop(best_fit_index)
            else:
                # No product fits, start new row
                if current_row:
                    rows.append(current_row)
                    current_row = []
                    current_row_width = 0
                else:
                    # Even single product doesn't fit, force add it
                    rows.append([remaining_products.pop(0)])

        # Add last row if not empty
        if current_row:
            rows.append(current_row)

        return rows

    def _truncate_text(self, text: str, max_width: int, font_size: int) -> str:
        """Truncate text to fit within button width with better calculation"""
        # Enhanced character width calculation
        char_width = font_size * 0.65  # Slightly more accurate
        max_chars = int(max_width / char_width) - 4  # Reserve more space for "..."

        if len(text) <= max_chars:
            return text

        # Better truncation - try to break at word boundaries
        if max_chars > 10:  # Only for reasonably sized buttons
            words = text.split()
            truncated = ""
            for word in words:
                if len(truncated + word + " ") <= max_chars - 3:
                    truncated += word + " "
                else:
                    break
            if truncated.strip():
                return truncated.strip() + "..."

        return text[:max_chars] + "..."

    def _create_tooltip(self, widget, text: str) -> None:
        """Create a simple tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
            tooltip.configure(bg='#2d2d2d')

            label = tk.Label(tooltip, text=text,
                             bg='#2d2d2d', fg='#ffffff',
                             font=('Segoe UI', 10),
                             relief='solid', borderwidth=1,
                             padx=8, pady=4,
                             justify=tk.LEFT)
            label.pack()

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def load_and_display_products(self, parent_frame: ttk.Frame) -> None:
        """Load products from JSON files and create buttons with simple layout"""
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Load product data
        product_data = self.load_product_data()

        if not product_data:
            # No-data message
            no_data_frame = ttk.Frame(parent_frame)
            no_data_frame.pack(expand=True, fill=tk.BOTH)

            ttk.Label(no_data_frame, text="🍽️ No Menu Items Found",
                      style='Title.TLabel').pack(pady=(50, 10))
            ttk.Label(no_data_frame, text="Add JSON files to the productData folder\nto display menu items here.",
                      style='TLabel', justify=tk.CENTER).pack(pady=10)
            return

        # Color schemes for categories
        category_colors = [
            {'bg': '#0078d4', 'fg': '#ffffff', 'hover_bg': '#1a86d9'},  # Blue
            {'bg': '#107c10', 'fg': '#ffffff', 'hover_bg': '#128a12'},  # Green
            {'bg': '#d13438', 'fg': '#ffffff', 'hover_bg': '#dc4144'},  # Red
            {'bg': '#ff8c00', 'fg': '#ffffff', 'hover_bg': '#ff9a1a'},  # Orange
            {'bg': '#5c2d91', 'fg': '#ffffff', 'hover_bg': '#6b3aa0'},  # Purple
            {'bg': '#00bcf2', 'fg': '#ffffff', 'hover_bg': '#1ac6f7'},  # Cyan
            {'bg': '#ca5010', 'fg': '#ffffff', 'hover_bg': '#d45a1a'},  # Brown
            {'bg': '#8764b8', 'fg': '#ffffff', 'hover_bg': '#9674c7'},  # Lavender
        ]

        category_index = 0

        for category, products in product_data.items():
            # Get color scheme for this category
            color_scheme = category_colors[category_index % len(category_colors)]
            category_index += 1

            # Create custom style for this category
            style_name = f'Category{category_index}.TButton'
            style = ttk.Style()

            # Get screen-appropriate font size - INCREASED FONT SIZES
            screen_width = self.root.winfo_screenwidth()
            if screen_width >= 1920:
                font_size = 15          # Increased from 11
                header_font_size = 14
            elif screen_width >= 1366:
                font_size = 15          # Increased from 10
                header_font_size = 12
            else:
                font_size = 15          # Increased from 9
                header_font_size = 11
    
            # Button styling with larger fonts
            style.configure(style_name,
                            background=color_scheme['bg'],
                            foreground=color_scheme['fg'],
                            font=('Segoe UI', font_size, 'bold'),  # Using increased font size
                            relief='flat',
                            borderwidth=2,
                            padding=(10, 6),
                            focuscolor='none')

            style.map(style_name,
                      background=[('active', color_scheme['hover_bg']),
                                  ('pressed', color_scheme['bg'])],
                      relief=[('pressed', 'sunken')])

            # Category header
            header_frame = ttk.Frame(parent_frame)
            header_frame.pack(fill=tk.X, pady=(20, 8))

            # Header label
            header_label = ttk.Label(header_frame,
                                     text=f"🏷️ {category} ({len(products)} items)",
                                     font=('Segoe UI', header_font_size, 'bold'),
                                     foreground='#00d4ff')
            header_label.pack(side=tk.LEFT)

            # Separator line
            separator = ttk.Separator(parent_frame, orient='horizontal')
            separator.pack(fill=tk.X, pady=(5, 10))

            # Product buttons frame
            buttons_frame = ttk.Frame(parent_frame)
            buttons_frame.pack(fill=tk.X, pady=(0, 15))

            # Create buttons for products in this category
            self._create_product_buttons(buttons_frame, products, style_name)

    def _is_valid_product(self, product) -> bool:
        """Check if product has required fields"""
        return (isinstance(product, dict) and
                all(key in product for key in ['name', 'display_name', 'amount']))

    def add_product_to_table(self, product: dict) -> None:
        """Add a product from the menu to the current table"""
        if not self.current_table_name:
            messagebox.showwarning("Warning", "Please select a table first!")
            return

        try:
            item_name = product['name']
            price = float(product['amount'])
            quantity = 1  # Default quantity

            # Add item to table
            if self.controller.add_item_to_table(self.current_table_name, item_name, price, quantity):
                self.status_label.config(text=f"🛒 Added {item_name} to {self.current_table_name}")
            else:
                messagebox.showerror("Error", "Failed to add item to table!")

        except (KeyError, ValueError) as e:
            messagebox.showerror("Error", f"Invalid product data: {e}")

    def refresh_product_display(self) -> None:
        """Refresh the product display"""
        # Find the scrollable frame and reload products
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "Menu Items" in child.cget("text"):
                        for canvas_widget in child.winfo_children():
                            if isinstance(canvas_widget, tk.Canvas):
                                scrollable_frame = canvas_widget.nametowidget(canvas_widget.find_all()[0])
                                self.load_and_display_products(scrollable_frame)
                                return

        # Fallback: refresh all data
        self.refresh_all_data()

    def view_sales_reports(self) -> None:
        """Open sales reports window"""
        try:
            # Create a new window for sales reports
            reports_window = tk.Toplevel(self.root)
            reports_window.title("📊 Sales Reports")
            reports_window.geometry("900x700")
            reports_window.configure(bg='#1e1e1e')

            # Apply dark theme to the new window
            style = ttk.Style()

            # Main frame
            main_frame = ttk.Frame(reports_window, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            title_label = ttk.Label(main_frame, text="📊 Sales Reports", style='Title.TLabel')
            title_label.pack(pady=(0, 20))

            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(0, 20))

            ttk.Button(buttons_frame, text="📈 Today's Sales", style='Primary.TButton',
                       command=lambda: self.show_daily_sales_report(reports_window)).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="📅 Select Date", style='Primary.TButton',
                       command=lambda: self.show_date_picker(reports_window)).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="🔄 Refresh",
                       command=lambda: self.refresh_sales_display(reports_window)).pack(side=tk.LEFT)

            # Sales display area
            self.sales_display_frame = ttk.Frame(main_frame)
            self.sales_display_frame.pack(fill=tk.BOTH, expand=True)

            # Show today's sales by default
            self.show_daily_sales_report(reports_window)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open sales reports: {e}")

    def refresh_sales_display(self, parent_window) -> None:
        """Refresh the sales display"""
        if hasattr(self, 'sales_display_frame') and self.sales_display_frame.winfo_exists():
            self.show_daily_sales_report(parent_window)

    def show_daily_sales_report(self, parent_window=None) -> None:
        """Show today's sales summary"""
        try:
            from datetime import datetime

            # If no parent window provided, create a new window
            if parent_window is None:
                reports_window = tk.Toplevel(self.root)
                reports_window.title("📊 Today's Sales Report")
                reports_window.geometry("900x700")
                reports_window.configure(bg='#1e1e1e')

                # Main frame
                main_frame = ttk.Frame(reports_window, padding="15")
                main_frame.pack(fill=tk.BOTH, expand=True)

                # Title
                title_label = ttk.Label(main_frame, text="📊 Today's Sales Report", style='Title.TLabel')
                title_label.pack(pady=(0, 20))

                # Create display frame
                display_frame = ttk.Frame(main_frame)
                display_frame.pack(fill=tk.BOTH, expand=True)
            else:
                # Use existing sales display frame
                display_frame = self.sales_display_frame
                # Clear display frame
                for widget in display_frame.winfo_children():
                    widget.destroy()

            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            self.show_sales_for_date_in_frame(today, display_frame)

        except Exception as e:
            # Create error label in appropriate frame
            if parent_window is None:
                # Create new window for error
                error_window = tk.Toplevel(self.root)
                error_window.title("Error")
                error_window.geometry("400x200")
                error_window.configure(bg='#1e1e1e')

                error_frame = ttk.Frame(error_window, padding="20")
                error_frame.pack(fill=tk.BOTH, expand=True)

                ttk.Label(error_frame, text=f"Error loading daily sales: {e}",
                          style='TLabel').pack(pady=20)
            else:
                # Use existing display frame if it exists
                if hasattr(self, 'sales_display_frame') and self.sales_display_frame.winfo_exists():
                    ttk.Label(self.sales_display_frame, text=f"Error loading daily sales: {e}",
                              style='TLabel').pack(pady=20)

    def show_date_picker(self, parent_window) -> None:
        """Show date picker for sales reports"""
        try:
            from datetime import datetime
            import tkinter.simpledialog as simpledialog

            # Simple date input dialog
            date_str = simpledialog.askstring("Select Date",
                                              "Enter date (YYYY-MM-DD):",
                                              initialvalue=datetime.now().strftime("%Y-%m-%d"))

            if date_str:
                try:
                    # Validate date format
                    datetime.strptime(date_str, "%Y-%m-%d")
                    if hasattr(self, 'sales_display_frame') and self.sales_display_frame.winfo_exists():
                        self.show_sales_for_date_in_frame(date_str, self.sales_display_frame)
                except ValueError:
                    messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show date picker: {e}")

    def show_sales_for_date(self, date_str: str) -> None:
        """Show sales data for a specific date"""
        if hasattr(self, 'sales_display_frame') and self.sales_display_frame.winfo_exists():
            self.show_sales_for_date_in_frame(date_str, self.sales_display_frame)

    def show_sales_for_date_in_frame(self, date_str: str, display_frame: ttk.Frame) -> None:
        """Show sales data for a specific date in the given frame"""
        try:
            # Clear display frame
            for widget in display_frame.winfo_children():
                widget.destroy()

            # Load daily sales data
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
            daily_file = data_dir / f"daily_sales_{date_str}.json"

            if not daily_file.exists():
                ttk.Label(display_frame, text=f"No sales data found for {date_str}",
                          style='TLabel').pack(pady=20)
                return

            with open(daily_file, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)

            # Create notebook for different views
            notebook = ttk.Notebook(display_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=10)

            # Summary tab
            summary_frame = ttk.Frame(notebook)
            notebook.add(summary_frame, text="📊 Summary")

            summary_text = f"""
    📅 Date: {daily_data['date']}
    💰 Total Sales: ₹{daily_data['total_sales']:.2f}
    📋 Total Orders: {daily_data['total_orders']}
            """

            ttk.Label(summary_frame, text=summary_text,
                      style='TLabel', justify=tk.LEFT).pack(pady=20)

            # Items sold section
            if daily_data.get('items_sold'):
                items_label_frame = ttk.LabelFrame(summary_frame, text="🍽️ Items Sold", padding="10")
                items_label_frame.pack(fill=tk.X, pady=10, padx=20)

                # Create treeview for items
                items_columns = ("Item", "Quantity")
                items_tree = ttk.Treeview(items_label_frame, columns=items_columns, show="headings", height=8)

                for col in items_columns:
                    items_tree.heading(col, text=col)
                    items_tree.column(col, width=200)

                for item, qty in daily_data['items_sold'].items():
                    items_tree.insert("", "end", values=(item, qty))

                items_tree.pack(fill=tk.X, pady=5)

            # Hourly breakdown section
            if daily_data.get('hourly_breakdown'):
                hourly_label_frame = ttk.LabelFrame(summary_frame, text="⏰ Hourly Sales", padding="10")
                hourly_label_frame.pack(fill=tk.X, pady=10, padx=20)

                hourly_columns = ("Hour", "Sales")
                hourly_tree = ttk.Treeview(hourly_label_frame, columns=hourly_columns, show="headings", height=6)

                for col in hourly_columns:
                    hourly_tree.heading(col, text=col)
                    hourly_tree.column(col, width=150)

                for hour, sales in sorted(daily_data['hourly_breakdown'].items()):
                    hourly_tree.insert("", "end", values=(hour, f"₹{sales:.2f}"))

                hourly_tree.pack(fill=tk.X, pady=5)

            # Detailed orders tab with removal functionality
            if daily_data.get('orders'):
                orders_frame = ttk.Frame(notebook)
                notebook.add(orders_frame, text="📋 Detailed Orders")

                # Control buttons frame
                controls_frame = ttk.Frame(orders_frame)
                controls_frame.pack(fill=tk.X, pady=(0, 10))

                ttk.Button(controls_frame, text="🗑️ Remove Selected Order",
                           style='Danger.TButton',
                           command=lambda: self.remove_sale_order(date_str, orders_tree, display_frame)).pack(side=tk.LEFT, padx=(0, 10))

                ttk.Button(controls_frame, text="🔄 Refresh",
                           style='Primary.TButton',
                           command=lambda: self.show_sales_for_date_in_frame(date_str, display_frame)).pack(side=tk.LEFT)

                # Create treeview for orders
                orders_columns = ("Time", "Table", "Items", "Total", "Order ID")
                orders_tree = ttk.Treeview(orders_frame, columns=orders_columns, show="headings", height=20)

                column_widths = {"Time": 150, "Table": 100, "Items": 80, "Total": 100, "Order ID": 0}
                for col in orders_columns:
                    orders_tree.heading(col, text=col)
                    if col == "Order ID":
                        orders_tree.column(col, width=0, minwidth=0)  # Hidden column for order index
                    else:
                        orders_tree.column(col, width=column_widths[col])

                # Add orders data with index for identification
                for index, order in enumerate(daily_data['orders']):
                    time_str = order['finalized_at'][11:19]  # Extract time part
                    orders_tree.insert("", "end", values=(
                        time_str,
                        order['table_name'],
                        order['items_count'],
                        f"₹{order['total_amount']:.2f}",
                        index  # Hidden order index
                    ))

                orders_tree.pack(fill=tk.BOTH, expand=True, pady=10)

                # Add scrollbar for orders
                orders_scrollbar = ttk.Scrollbar(orders_frame, orient=tk.VERTICAL, command=orders_tree.yview)
                orders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                orders_tree.configure(yscrollcommand=orders_scrollbar.set)

        except Exception as e:
            ttk.Label(display_frame, text=f"Error loading sales data: {e}",
                      style='TLabel').pack(pady=20)

    def remove_sale_order(self, date_str: str, orders_tree: ttk.Treeview, display_frame: ttk.Frame) -> None:
        """Remove a selected sale order with password protection"""
        try:
            # Check if an order is selected
            selection = orders_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an order to remove!")
                return

            # Get selected order details
            item_values = orders_tree.item(selection[0], "values")
            if not item_values or len(item_values) < 5:
                messagebox.showerror("Error", "Invalid order selection!")
                return

            order_index = int(item_values[4])  # Hidden order index
            table_name = item_values[1]
            total_amount = item_values[3].replace('₹', '')
            time_str = item_values[0]

            # Show password dialog
            if not self.verify_admin_password():
                return

            # Confirm removal
            confirm_msg = (f"Remove this order?\n\n"
                           f"Table: {table_name}\n"
                           f"Time: {time_str}\n"
                           f"Amount: ₹{total_amount}\n\n"
                           f"This action cannot be undone!")

            if not messagebox.askyesno("Confirm Removal", confirm_msg):
                return

            # Load and modify daily sales data
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
            daily_file = data_dir / f"daily_sales_{date_str}.json"

            with open(daily_file, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)

            # Get the order to remove
            if order_index >= len(daily_data['orders']):
                messagebox.showerror("Error", "Order not found!")
                return

            removed_order = daily_data['orders'][order_index]

            # Update totals
            daily_data['total_sales'] -= removed_order['total_amount']
            daily_data['total_orders'] -= 1

            # Update items sold count
            for item in removed_order['items']:
                item_name = item['name']
                if item_name in daily_data['items_sold']:
                    daily_data['items_sold'][item_name] -= item['quantity']
                    if daily_data['items_sold'][item_name] <= 0:
                        del daily_data['items_sold'][item_name]

            # Update hourly breakdown
            from datetime import datetime
            hour = datetime.fromisoformat(removed_order['finalized_at']).strftime("%H:00")
            if hour in daily_data['hourly_breakdown']:
                daily_data['hourly_breakdown'][hour] -= removed_order['total_amount']
                if daily_data['hourly_breakdown'][hour] <= 0:
                    del daily_data['hourly_breakdown'][hour]

            # Remove the order
            daily_data['orders'].pop(order_index)

            # Save updated data
            with open(daily_file, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, indent=2, ensure_ascii=False)

            # Log the removal for audit trail
            self.log_order_removal(date_str, removed_order)

            # Refresh the display
            self.show_sales_for_date_in_frame(date_str, display_frame)

            # Show success message
            messagebox.showinfo("Success", f"Order removed successfully!\n\nTable: {table_name}\nAmount: ₹{removed_order['total_amount']:.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove order: {e}")

    def verify_admin_password(self) -> bool:
        """Verify admin password for sensitive operations"""
        import tkinter.simpledialog as simpledialog

        # Create custom password dialog
        password_window = tk.Toplevel(self.root)
        password_window.title("🔐 Admin Authentication")
        password_window.geometry("400x200")
        password_window.configure(bg='#1e1e1e')
        password_window.resizable(False, False)

        # Center the window
        password_window.transient(self.root)
        password_window.grab_set()

        # Main frame
        main_frame = ttk.Frame(password_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="🔐 Admin Authentication Required",
                  style='Title.TLabel').pack(pady=(0, 20))

        # Warning message
        ttk.Label(main_frame, text="This action requires admin privileges.\nPlease enter the admin password:",
                  style='TLabel', justify=tk.CENTER).pack(pady=(0, 15))

        # Password entry
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, show="*", width=30)
        password_entry.pack(pady=(0, 20))
        password_entry.focus()

        # Result variable
        result = {'authenticated': False}

        def check_password():
            entered_password = password_var.get()
            if entered_password == "H@rsh123":
                result['authenticated'] = True
                password_window.destroy()
            else:
                messagebox.showerror("Access Denied", "Incorrect password!")
                password_var.set("")
                password_entry.focus()

        def cancel_auth():
            password_window.destroy()

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)

        ttk.Button(buttons_frame, text="✅ Authenticate",
                   style='Success.TButton', command=check_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="❌ Cancel",
                   style='Danger.TButton', command=cancel_auth).pack(side=tk.LEFT)

        # Bind Enter key to check password
        password_entry.bind('<Return>', lambda e: check_password())

        # Wait for window to close
        password_window.wait_window()

        return result['authenticated']

    def log_order_removal(self, date_str: str, removed_order: dict) -> None:
        """Log order removal for audit trail"""
        try:
            from datetime import datetime

            # Get the data directory path
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
            data_dir.mkdir(exist_ok=True)

            # Create audit log file
            audit_file = data_dir / "order_removals_audit.json"

            # Load existing audit data or create new
            if audit_file.exists():
                with open(audit_file, 'r', encoding='utf-8') as f:
                    audit_data = json.load(f)
            else:
                audit_data = {"removals": []}

            # Create audit entry
            audit_entry = {
                "removal_timestamp": datetime.now().isoformat(),
                "original_date": date_str,
                "removed_order": removed_order,
                "reason": "Manual removal via admin interface"
            }

            # Add to audit log
            audit_data["removals"].append(audit_entry)

            # Save audit log
            with open(audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error logging order removal: {e}")
            # Don't show error to user as this is background operation

    def view_removal_audit_log(self) -> None:
        """View the audit log of removed orders"""
        try:
            # Create audit window
            audit_window = tk.Toplevel(self.root)
            audit_window.title("🔍 Order Removal Audit Log")
            audit_window.geometry("800x600")
            audit_window.configure(bg='#1e1e1e')

            # Main frame
            main_frame = ttk.Frame(audit_window, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            ttk.Label(main_frame, text="🔍 Order Removal Audit Log",
                      style='Title.TLabel').pack(pady=(0, 20))

            # Load audit data
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
            audit_file = data_dir / "order_removals_audit.json"

            if not audit_file.exists():
                ttk.Label(main_frame, text="No removal history found.",
                          style='TLabel').pack(pady=20)
                return

            with open(audit_file, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)

            # Create treeview for audit entries
            columns = ("Removal Time", "Original Date", "Table", "Amount", "Items")
            audit_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

            column_widths = {"Removal Time": 150, "Original Date": 100, "Table": 100, "Amount": 100, "Items": 80}
            for col in columns:
                audit_tree.heading(col, text=col)
                audit_tree.column(col, width=column_widths[col])

            # Add audit entries
            for entry in reversed(audit_data.get("removals", [])):  # Most recent first
                removal_time = entry['removal_timestamp'][:19].replace('T', ' ')
                original_date = entry['original_date']
                removed_order = entry['removed_order']

                audit_tree.insert("", "end", values=(
                    removal_time,
                    original_date,
                    removed_order['table_name'],
                    f"₹{removed_order['total_amount']:.2f}",
                    removed_order['items_count']
                ))

            audit_tree.pack(fill=tk.BOTH, expand=True, pady=10)

            # Add scrollbar
            audit_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=audit_tree.yview)
            audit_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            audit_tree.configure(yscrollcommand=audit_scrollbar.set)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audit log: {e}")