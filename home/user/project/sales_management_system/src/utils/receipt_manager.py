
import json
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import tempfile

class ReceiptManager:
    """Manages receipt generation and printing for sales"""
    
    def __init__(self):
        self.config = self.load_receipt_config()
        
    def load_receipt_config(self) -> dict:
        """Load receipt configuration"""
        try:
            current_dir = Path(__file__).parent.parent.parent
            config_file = current_dir / "config" / "receipt_config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "restaurant_name": "Restaurant Name",
                    "thermal_printer": {
                        "enabled": True,
                        "printer_name": "default",
                        "paper_width": 58,  # mm
                        "char_per_line": 32
                    },
                    "receipt_format": {
                        "show_header": True,
                        "show_footer": True,
                        "show_gst": True,
                        "show_datetime": True
                    }
                }
                
                # Create config directory and file
                config_file.parent.mkdir(exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                return default_config
                
        except Exception as e:
            print(f"Error loading receipt config: {e}")
            return {}
    
    def generate_receipt_text(self, table_data: dict) -> str:
        """Generate receipt text from table data"""
        try:
            receipt_lines = []
            char_per_line = self.config.get("thermal_printer", {}).get("char_per_line", 32)
            
            # Header
            if self.config.get("receipt_format", {}).get("show_header", True):
                restaurant_name = self.config.get("restaurant_name", "Restaurant")
                receipt_lines.append(self.center_text(restaurant_name, char_per_line))
                receipt_lines.append(self.center_text("=" * min(len(restaurant_name), char_per_line), char_per_line))

                address = self.config.get("address", "")
                if address:
                    receipt_lines.append(self.center_text(address, char_per_line))

                phone = self.config.get("phone", "")
                if phone:
                    receipt_lines.append(self.center_text(f"Ph: {phone}", char_per_line))

                gst_number = self.config.get("gst_number", "")
                if gst_number and self.config.get("receipt_format", {}).get("show_gst", True):
                    receipt_lines.append(self.center_text(f"GST: {gst_number}", char_per_line))

                receipt_lines.append("")

            # Date and time
            if self.config.get("receipt_format", {}).get("show_datetime", True):
                now = datetime.now()
                receipt_lines.append(f"Date: {now.strftime('%d/%m/%Y')} Time: {now.strftime('%H:%M:%S')}")
                receipt_lines.append("")

            # Items header
            receipt_lines.append("Item                 Qty  Amount")
            receipt_lines.append("-" * char_per_line)

            # Items
            total_amount = 0
            for item in table_data.get('items', []):
                item_name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                item_total = item.get('total', quantity * price)
                total_amount += item_total

                # Format item line
                name_width = char_per_line - 10  # Reserve space for qty and amount
                if len(item_name) > name_width:
                    item_name = item_name[:name_width-3] + "..."

                qty_str = f"{quantity:>3}"
                amount_str = f"{item_total:>6.0f}"

                item_line = f"{item_name:<{name_width}}{qty_str}{amount_str}"
                receipt_lines.append(item_line)

            # Total
            receipt_lines.append("-" * char_per_line)
            receipt_lines.append(f"{'TOTAL:':<{char_per_line-8}}{total_amount:>8.2f}")
            receipt_lines.append("=" * char_per_line)

            # Footer
            if self.config.get("receipt_format", {}).get("show_footer", True):
                receipt_lines.append("")
                receipt_lines.append(self.center_text("Thank You!", char_per_line))
                receipt_lines.append(self.center_text("Visit Again!", char_per_line))

            return "\n".join(receipt_lines)

        except Exception as e:
            print(f"Error generating receipt text: {e}")
            return f"Error generating receipt: {e}"

    def center_text(self, text: str, width: int) -> str:
        """Center text within given width"""
        if len(text) >= width:
            return text[:width]
        padding = (width - len(text)) // 2
        return " " * padding + text

    def preview_receipt(self, table_data: dict, parent_window=None) -> None:
        """Show receipt preview window"""
        try:
            # Generate receipt text
            receipt_text = self.generate_receipt_text(table_data)

            # Create preview window
            preview_window = tk.Toplevel(parent_window) if parent_window else tk.Tk()
            preview_window.title("📄 Receipt Preview")
            preview_window.geometry("500x700")
            preview_window.configure(bg='#1e1e1e')

            # Main frame
            main_frame = ttk.Frame(preview_window, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            title_label = ttk.Label(main_frame, text="📄 Receipt Preview",
                                   font=('Segoe UI', 14, 'bold'), foreground='#00d4ff')
            title_label.pack(pady=(0, 20))

            # Receipt display frame
            receipt_frame = ttk.LabelFrame(main_frame, text="Receipt", padding="10")
            receipt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

            # Text widget for receipt
            text_widget = tk.Text(receipt_frame,
                                 font=('Courier New', 10),
                                 bg='#ffffff', fg='#000000',
                                 wrap=tk.NONE, width=40, height=30)
            text_widget.pack(fill=tk.BOTH, expand=True)

            # Insert receipt text
            text_widget.insert('1.0', receipt_text)
            text_widget.config(state=tk.DISABLED)  # Make read-only
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X)
            
            # Print button
            ttk.Button(buttons_frame, text="🖨️ Print Receipt",
                      command=lambda: self.print_receipt(table_data, preview_window)).pack(side=tk.LEFT, padx=(0, 10))
            
            # Save button
            ttk.Button(buttons_frame, text="💾 Save Receipt",
                      command=lambda: self.save_receipt(table_data, preview_window)).pack(side=tk.LEFT, padx=(0, 10))
            
            # Close button
            ttk.Button(buttons_frame, text="❌ Close",
                      command=preview_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show receipt preview: {e}")
    
    def print_receipt(self, table_data: dict, parent_window=None) -> bool:
        """Print receipt to thermal printer"""
        try:
            if not self.config.get("thermal_printer", {}).get("enabled", False):
                messagebox.showwarning("Warning", "Thermal printer is not enabled!")
                return False
            
            # Generate receipt text
            receipt_text = self.generate_receipt_text(table_data)
            
            # Create temporary file for printing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(receipt_text)
                temp_file_path = temp_file.name
            
            try:
                # Print using system default printer
                if os.name == 'nt':  # Windows
                    # Use notepad to print (simple method)
                    subprocess.run(['notepad', '/p', temp_file_path], check=True)
                else:  # Linux/Mac
                    subprocess.run(['lp', temp_file_path], check=True)
                
                messagebox.showinfo("Success", "Receipt sent to printer!")
                return True
                
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Print Error", f"Failed to print receipt: {e}")
                return False
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print receipt: {e}")
            return False
    
    def save_receipt(self, table_data: dict, parent_window=None) -> bool:
        """Save receipt to file"""
        try:
            from tkinter import filedialog
            
            # Generate receipt text
            receipt_text = self.generate_receipt_text(table_data)
            
            # Get save location
            table_name = table_data.get('table_name', 'Unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"Receipt_{table_name}_{timestamp}.txt"
            
            file_path = filedialog.asksaveasfilename(
                parent=parent_window,
                title="Save Receipt",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialvalue=default_filename
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(receipt_text)
                
                messagebox.showinfo("Success", f"Receipt saved to:\n{file_path}")
                return True
            
            return False
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save receipt: {e}")
            return False
    
    def configure_printer(self, parent_window=None) -> None:
        """Open printer configuration dialog"""
        try:
            # Create configuration window
            config_window = tk.Toplevel(parent_window) if parent_window else tk.Tk()
            config_window.title("🖨️ Printer Configuration")
            config_window.geometry("500x400")
            config_window.configure(bg='#1e1e1e')
            
            # Main frame
            main_frame = ttk.Frame(config_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            ttk.Label(main_frame, text="🖨️ Printer Configuration",
                     font=('Segoe UI', 14, 'bold'), foreground='#00d4ff').pack(pady=(0, 20))
            
            # Thermal printer settings
            thermal_frame = ttk.LabelFrame(main_frame, text="Thermal Printer Settings", padding="10")
            thermal_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Enable thermal printer
            thermal_enabled_var = tk.BooleanVar(value=self.config.get("thermal_printer", {}).get("enabled", True))
            ttk.Checkbutton(thermal_frame, text="Enable Thermal Printer",
                           variable=thermal_enabled_var).pack(anchor=tk.W, pady=5)
            
            # Paper width
            width_frame = ttk.Frame(thermal_frame)
            width_frame.pack(fill=tk.X, pady=5)
            ttk.Label(width_frame, text="Paper Width (mm):").pack(side=tk.LEFT)
            width_var = tk.StringVar(value=str(self.config.get("thermal_printer", {}).get("paper_width", 58)))
            ttk.Entry(width_frame, textvariable=width_var, width=10).pack(side=tk.RIGHT)
            
            # Characters per line
            char_frame = ttk.Frame(thermal_frame)
            char_frame.pack(fill=tk.X, pady=5)
            ttk.Label(char_frame, text="Characters per line:").pack(side=tk.LEFT)
            char_var = tk.StringVar(value=str(self.config.get("thermal_printer", {}).get("char_per_line", 32)))
            ttk.Entry(char_frame, textvariable=char_var, width=10).pack(side=tk.RIGHT)
            
            # Restaurant info
            info_frame = ttk.LabelFrame(main_frame, text="Restaurant Information", padding="10")
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Restaurant name
            name_frame = ttk.Frame(info_frame)
            name_frame.pack(fill=tk.X, pady=2)
            ttk.Label(name_frame, text="Restaurant Name:").pack(side=tk.LEFT)
            name_var = tk.StringVar(value=self.config.get("restaurant_name", ""))
            ttk.Entry(name_frame, textvariable=name_var).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            
            # Address
            addr_frame = ttk.Frame(info_frame)
            addr_frame.pack(fill=tk.X, pady=2)
            ttk.Label(addr_frame, text="Address:").pack(side=tk.LEFT)
            addr_var = tk.StringVar(value=self.config.get("address", ""))
            ttk.Entry(addr_frame, textvariable=addr_var).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            
            # Phone
            phone_frame = ttk.Frame(info_frame)
            phone_frame.pack(fill=tk.X, pady=2)
            ttk.Label(phone_frame, text="Phone:").pack(side=tk.LEFT)
            phone_var = tk.StringVar(value=self.config.get("phone", ""))
            ttk.Entry(phone_frame, textvariable=phone_var).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            
            # GST Number
            gst_frame = ttk.Frame(info_frame)
            gst_frame.pack(fill=tk.X, pady=2)
            ttk.Label(gst_frame, text="GST Number:").pack(side=tk.LEFT)
            gst_var = tk.StringVar(value=self.config.get("gst_number", ""))
            ttk.Entry(gst_frame, textvariable=gst_var).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            
            def save_config():
                try:
                    # Update configuration
                    self.config["thermal_printer"]["enabled"] = thermal_enabled_var.get()
                    self.config["thermal_printer"]["paper_width"] = int(width_var.get())
                    self.config["thermal_printer"]["char_per_line"] = int(char_var.get())
                    self.config["restaurant_name"] = name_var.get()
                    self.config["address"] = addr_var.get()
                    self.config["phone"] = phone_var.get()
                    self.config["gst_number"] = gst_var.get()
                    
                    # Save to file
                    current_dir = Path(__file__).parent.parent.parent
                    config_file = current_dir / "config" / "receipt_config.json"
                    config_file.parent.mkdir(exist_ok=True)
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(self.config, f, indent=2, ensure_ascii=False)
                    
                    messagebox.showinfo("Success", "Configuration saved successfully!")
                    config_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
            # Buttons
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X)
            
            ttk.Button(buttons_frame, text="💾 Save Configuration",
                      command=save_config).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="❌ Cancel",
                      command=config_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open printer configuration: {e}")
