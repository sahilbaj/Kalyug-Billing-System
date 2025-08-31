
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
        self.default_thermal_printer = None

    def _print_to_windows_thermal_printer(self, content):
        """Print to Windows installed thermal printer with user selection and default saving"""
        try:
            # Check if we have a saved default printer first
            if self.default_thermal_printer:
                print(f"Using saved default printer: {self.default_thermal_printer}")
                # Verify the printer is still available
                if self._verify_printer_available(self.default_thermal_printer):
                    return self._send_to_windows_printer(content, self.default_thermal_printer)
                else:
                    print(f"Default printer {self.default_thermal_printer} no longer available")
                    self.default_thermal_printer = None  # Reset if not available

            # Get available printers only if no default or default not available
            printers = self._get_available_printers()

            if not printers:
                print("No printers found")
                return False

            # If only one printer, use it directly and save as default
            if len(printers) == 1:
                selected_printer = printers[0].split(" - Port:")[0]  # Extract printer name
                print(f"Using only available printer: {selected_printer}")
                self.default_thermal_printer = selected_printer  # Save as default
                self._save_printer_config(selected_printer)  # Persist to file
                return self._send_to_windows_printer(content, selected_printer)
            else:
                # Show selection dialog for multiple printers
                selected_printer = self._select_thermal_printer(printers)

                if selected_printer:
                    print(f"Selected printer: {selected_printer}")

                    # Ask if user wants to save as default
                    if self._ask_save_as_default(selected_printer):
                        self.default_thermal_printer = selected_printer
                        self._save_printer_config(selected_printer)
                        print(f"Saved {selected_printer} as default printer")

                    return self._send_to_windows_printer(content, selected_printer)
                else:
                    print("No printer selected by user")
                    return False

        except Exception as e:
            print(f"Error printing to Windows thermal printer: {e}")
            return False

    def _verify_printer_available(self, printer_name):
        """Verify if the saved default printer is still available"""
        try:
            import subprocess

            ps_command = f'''
            Get-WmiObject -Class Win32_Printer | Where-Object {{
                $_.Name -eq "{printer_name}" -and $_.PrinterState -ne 3 -and $_.Status -ne "Error"
            }} | Select-Object Name
            '''

            result = subprocess.run(['powershell', '-Command', ps_command],
                                    capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                print(f"✓ Default printer {printer_name} is available")
                return True
            else:
                print(f"✗ Default printer {printer_name} is not available")
                return False

        except Exception as e:
            print(f"Error verifying printer availability: {e}")
            return False

    def _get_available_printers(self):
        """Get list of available printers"""
        try:
            import subprocess

            print("=== GETTING AVAILABLE PRINTERS ===")

            # Get all printers
            ps_command = '''
            Get-WmiObject -Class Win32_Printer | Where-Object {
                $_.PrinterState -ne 3 -and $_.Status -ne "Error"
            } | Select-Object Name, DriverName, PortName, Status | ForEach-Object {
                "$($_.Name) - Port: $($_.PortName) - Status: $($_.Status)"
            }
            '''

            result = subprocess.run(['powershell', '-Command', ps_command],
                                    capture_output=True, text=True, timeout=15)

            if result.returncode == 0 and result.stdout.strip():
                printers = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                print(f"Found {len(printers)} available printers:")
                for printer in printers:
                    print(f"  - {printer}")
                return printers

            print("No printers found")
            return []

        except Exception as e:
            print(f"Error getting available printers: {e}")
            return []

    def _show_simple_printing_status(self, printer_name):
        """Show simple printing status dialog"""
        try:
            dialog = tk.Toplevel()
            dialog.title("Printing...")
            dialog.geometry("350x150")
            dialog.resizable(False, False)
            dialog.grab_set()
            dialog.configure(bg='#f8f9fa')

            self._center_window(dialog, 350, 150)

            # Main frame
            main_frame = tk.Frame(dialog, bg='#f8f9fa', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Icon and text
            tk.Label(main_frame, text="🖨️", font=('Arial', 24), bg='#f8f9fa').pack(pady=5)
            tk.Label(main_frame, text="Printing receipt...",
                     font=('Arial', 12, 'bold'), bg='#f8f9fa').pack()
            tk.Label(main_frame, text=f"To: {printer_name[:40]}...",
                     font=('Arial', 9), fg='#6c757d', bg='#f8f9fa').pack(pady=5)
            tk.Label(main_frame, text="Please wait...",
                     font=('Arial', 10), fg='#007bff', bg='#f8f9fa').pack()

            dialog.update()
            return dialog

        except Exception as e:
            print(f"Error showing simple printing status: {e}")
            return None

    def _send_to_windows_printer(self, content, printer_name):
        """Enhanced Windows printer communication with better error handling"""
        try:
            print(f"=== SENDING TO SELECTED PRINTER: {printer_name} ===")

            # Show simple progress
            progress_dialog = self._show_simple_printing_status(printer_name)

            success = False

            # Method 1: Try win32print with raw data
            try:
                import win32print
                print("Attempting win32print method...")
                success = self._print_with_win32print(content, printer_name)
                if success:
                    if progress_dialog:
                        progress_dialog.destroy()
                    return True
            except ImportError:
                print("win32print not available")
            except Exception as e:
                print(f"win32print method failed: {e}")

            # Method 2: Try system command with raw data
            print("Attempting system command method...")
            success = self._print_with_system_command(content, printer_name)
            if success:
                if progress_dialog:
                    progress_dialog.destroy()
                return True

            # Method 3: Try direct file copy to printer port
            print("Attempting direct port method...")
            success = self._print_to_printer_port(content, printer_name)
            if success:
                if progress_dialog:
                    progress_dialog.destroy()
                return True

            if progress_dialog:
                progress_dialog.destroy()

            print(f"❌ All methods failed for {printer_name}")
            return False

        except Exception as e:
            print(f"Error in _send_to_windows_printer: {e}")
            return False

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
            # Show printing status

            status_dialog = self._show_printing_status()
            # Generate receipt text
            receipt_text = self.generate_receipt_text(table_data)

            # Try Windows thermal printer first
            success = self._print_to_windows_thermal_printer(receipt_text)

            # Close status dialog
            if status_dialog:
                status_dialog.destroy()

            if success:
                messagebox.showinfo("Print Success",
                                    "🖨️ Receipt printed successfully!")
            else:
                # Fallback to default system printer
                fallback_success = self._print_to_system_printer(receipt_text)
                if fallback_success:
                    messagebox.showinfo("Print Success",
                                        "🖨️ Receipt printed to system printer!")
                else:
                    messagebox.showerror("Print Error",
                                         "❌ Failed to print receipt!\n\n"
                                         "Please check:\n"
                                         "• Printer is connected and powered ON\n"
                                         "• Paper is loaded\n"
                                         "• Printer drivers are installed")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to print receipt: {e}")
            return False

    def _show_printing_status(self):
        """Show printing status dialog"""
        try:
            dialog = tk.Toplevel()
            dialog.title("Printing...")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.grab_set()

            self._center_window(dialog, 300, 150)

            tk.Label(dialog, text="🖨️", font=('Arial', 24)).pack(pady=10)
            tk.Label(dialog, text="Printing receipt...", font=('Arial', 12, 'bold')).pack()
            tk.Label(dialog, text="Please wait", font=('Arial', 10), fg='gray').pack(pady=5)

            dialog.update()
            return dialog

        except Exception as e:
            print(f"Error showing printing status: {e}")
            return None

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

    def _print_with_win32print(self, content, printer_name):
        """Print using win32print library with proper thermal printer handling"""
        try:
            import win32print

            print(f"Attempting to print to: {printer_name}")

            # Open printer
            printer_handle = win32print.OpenPrinter(printer_name)

            try:
                # Start document with RAW data type (important for thermal printers)
                doc_info = ("Ananda Bakery Receipt", None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)

                try:
                    # Start page
                    win32print.StartPagePrinter(printer_handle)

                    # Convert content to thermal printer format
                    thermal_data = self._format_for_thermal_printer(content)

                    print(f"Sending {len(thermal_data)} bytes to printer")

                    # Send data in chunks to avoid buffer overflow
                    chunk_size = 1024
                    for i in range(0, len(thermal_data), chunk_size):
                        chunk = thermal_data[i:i + chunk_size]
                        bytes_written = win32print.WritePrinter(printer_handle, chunk)
                        print(f"Wrote {bytes_written} bytes (chunk {i//chunk_size + 1})")
                        time.sleep(0.1)  # Small delay between chunks

                    # CRITICAL FIX: Ensure all data is flushed before ending
                    import win32api
                    win32api.Sleep(500)  # Wait 500ms for printer to process
                    # End page
                    win32print.EndPagePrinter(printer_handle)

                    print(f"✅ Successfully sent print job to {printer_name}")
                    return True

                finally:
                    win32print.EndDocPrinter(printer_handle)

            finally:
                win32print.ClosePrinter(printer_handle)

        except Exception as e:
            print(f"Error with win32print: {e}")
            return False

    def _print_with_system_command(self, content, printer_name):
        """Print using system command with thermal printer optimization"""
        try:
            import tempfile
            import os
            import subprocess

            # For thermal printers, we need to send raw data
            thermal_data = self._format_for_thermal_printer(content)

            # Create temporary binary file for raw data
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.prn', delete=False) as temp_file:
                temp_file.write(thermal_data)
                temp_file_path = temp_file.name

            try:
                # Use copy command to send raw data to printer
                cmd = f'copy /B "{temp_file_path}" "\\\\localhost\\{printer_name}"'
                print(f"Executing: {cmd}")

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    print(f"✅ Successfully printed to {printer_name} via copy command")
                    return True
                else:
                    print(f"❌ Copy command failed: {result.stderr}")

                    # Fallback to print command with text file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as text_file:
                        text_file.write(content)
                        text_file_path = text_file.name

                    cmd2 = f'print /D:"{printer_name}" "{text_file_path}"'
                    result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=30)

                    if result2.returncode == 0:
                        print(f"✅ Successfully printed to {printer_name} via print command")
                        return True
                    else:
                        print(f"❌ Print command also failed: {result2.stderr}")
                        return False

            finally:
                # Clean up temp files after delay
                self.sales_tab.frame.after(5000, lambda: self._cleanup_temp_file(temp_file_path))

        except Exception as e:
            print(f"Error with system print command: {e}")
            return False

    def _print_to_printer_port(self, content, printer_name):
        """Try to print directly to printer port"""
        try:
            import subprocess

            # Get printer port information
            ps_command = f'''
            Get-WmiObject -Class Win32_Printer | Where-Object {{
                $_.Name -eq "{printer_name}"
            }} | Select-Object -ExpandProperty PortName
            '''

            result = subprocess.run(['powershell', '-Command', ps_command],
                                    capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                port_name = result.stdout.strip()
                print(f"Found printer port: {port_name}")

                # If it's a USB port, try direct write
                if 'USB' in port_name.upper():
                    thermal_data = self._format_for_thermal_printer(content)

                    # Try to write directly to the port
                    try:
                        with open(f'\\\\.\\{port_name}', 'wb') as port_file:
                            port_file.write(thermal_data)
                            port_file.flush()
                        print(f"✅ Successfully wrote to port {port_name}")
                        return True
                    except Exception as e:
                        print(f"Direct port write failed: {e}")
                        return False

            return False

        except Exception as e:
            print(f"Error in direct port method: {e}")
            return False

    def _select_thermal_printer(self, printers):
        """Show dialog to select thermal printer"""
        try:
            dialog = tk.Toplevel()
            dialog.title("Select Thermal Printer")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.grab_set()
            dialog.configure(bg='#f8f9fa')

            self._center_window(dialog, 500, 400)

            # Main frame
            main_frame = tk.Frame(dialog, bg='#f8f9fa', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Header
            header_frame = tk.Frame(main_frame, bg='#007bff', relief='flat', pady=10)
            header_frame.pack(fill=tk.X, pady=(0, 20))

            tk.Label(header_frame, text="🖨️ Select Your Thermal Printer",
                     font=('Arial', 14, 'bold'), fg='white', bg='#007bff').pack()

            tk.Label(header_frame, text="Multiple printers found. Please select yours:",
                     font=('Arial', 10), fg='white', bg='#007bff').pack(pady=(5, 0))

            # Printer list frame
            list_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

            # Listbox with scrollbar
            listbox_frame = tk.Frame(list_frame)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            listbox = tk.Listbox(listbox_frame, font=('Arial', 10), height=12,
                                 selectmode=tk.SINGLE, bg='white', fg='black',
                                 selectbackground='#007bff', selectforeground='white')

            scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)

            # Add printers to listbox
            for i, printer in enumerate(printers):
                # Extract just the printer name (before " - Port:")
                printer_name = printer.split(" - Port:")[0]
                display_text = f"{i+1}. {printer}"
                listbox.insert(tk.END, display_text)

            # Select first by default
            if printers:
                listbox.selection_set(0)
                listbox.activate(0)

            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Buttons frame
            button_frame = tk.Frame(main_frame, bg='#f8f9fa')
            button_frame.pack(fill=tk.X)

            selected_printer = [None]

            def select_printer():
                selection = listbox.curselection()
                if selection:
                    selected_text = listbox.get(selection[0])
                    # Extract original printer info
                    printer_index = selection[0]
                    # Get just the printer name (before " - Port:")
                    selected_printer[0] = printers[printer_index].split(" - Port:")[0]
                    dialog.destroy()
                else:
                    messagebox.showwarning("No Selection", "Please select a printer!")

            def cancel():
                selected_printer[0] = None
                dialog.destroy()

            # Double-click to select
            def on_double_click(event):
                select_printer()

            listbox.bind("<Double-Button-1>", on_double_click)

            # Buttons
            select_btn = tk.Button(button_frame, text="✅ Select Printer", command=select_printer,
                                   bg='#28a745', fg='white', font=('Arial', 11, 'bold'),
                                   relief='flat', padx=20, pady=10, cursor='hand2')
            select_btn.pack(side=tk.LEFT, padx=(0, 10))

            cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=cancel,
                                   bg='#dc3545', fg='white', font=('Arial', 11, 'bold'),
                                   relief='flat', padx=20, pady=10, cursor='hand2')
            cancel_btn.pack(side=tk.RIGHT)

            # Info label
            info_label = tk.Label(main_frame,
                                  text="💡 Double-click on a printer to select it quickly",
                                  font=('Arial', 9), fg='#6c757d', bg='#f8f9fa')
            info_label.pack(pady=(10, 0))

            # Focus on listbox
            listbox.focus_set()

            dialog.wait_window()
            return selected_printer[0]

        except Exception as e:
            print(f"Error in printer selection dialog: {e}")
            messagebox.showerror("Error", f"Failed to show printer selection: {str(e)}")
            return None

    def _center_window(self, window, width, height):
        """Center window on screen"""
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")