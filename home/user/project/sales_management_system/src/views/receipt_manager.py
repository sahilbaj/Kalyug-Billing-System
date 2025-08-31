
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import time

class ReceiptManager:

    def __init__(self, sales_tab):
        self.sales_tab = sales_tab
        self.current_sale_data = None
        self.current_customer_name = None
        self.current_total_amount = None
        self.default_printer_port = None
        self.default_thermal_printer = None

        # Load saved printer configuration on initialization
        self._load_printer_config()

        # Thermal printer settings for 80mm paper
        self.thermal_settings = {
            'char_width': 48,  # Characters per line for 80mm thermal printer
            'paper_width_mm': 80,
            'font_width_mm': 1.67,  # Approximate character width in mm
        }

        # ESC/POS Commands for thermal printer
        self.esc_pos_commands = {
            'ESC': b'\x1b',
            'INIT': b'\x1b@',  # Initialize printer
            'CUT': b'\x1bd\x03',  # Cut paper
            'FEED': b'\n',
            'BOLD_ON': b'\x1bE\x01',  # Bold on
            'BOLD_OFF': b'\x1bE\x00',  # Bold off
            'CENTER': b'\x1ba\x01',  # Center align
            'LEFT': b'\x1ba\x00',  # Left align
            'RIGHT': b'\x1ba\x02',  # Right align
            'FONT_NORMAL': b'\x1b!\x00',  # Normal font
            'FONT_LARGE': b'\x1b!\x11',  # Double height and width
            'FONT_WIDE': b'\x1b!\x20',  # Double width
            'STATUS_REQUEST': b'\x1dr\x01',  # Request paper status
        }

    def ask_receipt_options(self, customer_name, total_amount, sale_data=None):
        """Main receipt options dialog"""
        try:
            # Store current sale data
            self.current_customer_name = customer_name
            self.current_total_amount = total_amount
            self.current_sale_data = sale_data

            # Create options dialog
            dialog = tk.Toplevel(self.sales_tab.frame)
            dialog.title("🧾 Receipt Options")
            dialog.geometry("500x600")
            dialog.resizable(False, False)
            dialog.grab_set()
            dialog.configure(bg='#f8f9fa')

            # Center dialog
            self._center_window(dialog, 500, 600)

            # Main container
            main_frame = tk.Frame(dialog, bg='#f8f9fa', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Header
            self._create_header(main_frame, customer_name, total_amount)

            # Options buttons
            self._create_option_buttons(main_frame, dialog)

            # Footer info
            info_label = tk.Label(main_frame,
                                  text="💡 Use 'Thermal Preview' to see exact 80mm printer output",
                                  font=('Arial', 9), fg='#6c757d', bg='#f8f9fa')
            info_label.pack(pady=(15, 0))

        except Exception as e:
            print(f"Error showing receipt options: {e}")
            self.finalize_sale()

    def _create_header(self, parent, customer_name, total_amount):
        """Create dialog header"""
        header_frame = tk.Frame(parent, bg='#343a40', relief='flat', bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        header_content = tk.Frame(header_frame, bg='#343a40', padx=20, pady=15)
        header_content.pack(fill=tk.X)

        tk.Label(header_content, text="🧾 RECEIPT OPTIONS",
                 font=('Arial', 16, 'bold'), fg='white', bg='#343a40').pack()

        tk.Label(header_content, text=f"✅ Sale completed for: {customer_name}",
                 font=('Arial', 11), fg='#28a745', bg='#343a40').pack(pady=(10, 0))
        tk.Label(header_content, text=f"💰 Total Amount: ₹{total_amount:.2f}",
                 font=('Arial', 12, 'bold'), fg='#ffc107', bg='#343a40').pack(pady=(5, 0))


    def _create_option_buttons(self, parent, dialog):
        """Create option buttons with printer settings"""
        options_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        options_frame.pack(fill=tk.X, pady=(0, 20))

        content = tk.Frame(options_frame, bg='white', padx=20, pady=20)
        content.pack(fill=tk.X)

        button_style = {
            'font': ('Arial', 11, 'bold'),
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 12,
            'cursor': 'hand2',
            'width': 30
        }

        # Thermal Preview Button
        preview_btn = tk.Button(content, text="🖨️ Thermal Preview (80mm)",
                                command=lambda: self._handle_option(dialog, self.show_thermal_preview),
                                bg='#fd7e14', fg='white', **button_style)
        preview_btn.pack(pady=3, fill=tk.X)

        # Print Receipt Button with default printer info
        print_text = "🖨️ Print Receipt"
        if self.default_thermal_printer:
            print_text += f" (Default: {self.default_thermal_printer[:20]}...)"
        
        print_btn = tk.Button(content, text=print_text,
                              command=lambda: self._handle_option(dialog, self.print_receipt),
                              bg='#007bff', fg='white', **button_style)
        print_btn.pack(pady=3, fill=tk.X)

        # Printer Settings Button (if default printer is set)
        if self.default_thermal_printer:
            settings_btn = tk.Button(content, text="⚙️ Change Default Printer",
                                   command=lambda: self._handle_option(dialog, self._change_default_printer),
                                   bg='#6c757d', fg='white', **button_style)
            settings_btn.pack(pady=3, fill=tk.X)

        # WhatsApp Button
        whatsapp_btn = tk.Button(content, text="📱 Send WhatsApp",
                                 command=lambda: self._handle_option(dialog, self.send_whatsapp),
                                 bg='#25d366', fg='white', **button_style)
        whatsapp_btn.pack(pady=3, fill=tk.X)

        # Email Button
        email_btn = tk.Button(content, text="📧 Email Receipt",
                              command=lambda: self._handle_option(dialog, self.send_email),
                              bg='#dc3545', fg='white', **button_style)
        email_btn.pack(pady=3, fill=tk.X)

        # Separator
        tk.Frame(content, height=2, bg='#dee2e6').pack(fill=tk.X, pady=15)

        # Finish Button
        finish_btn = tk.Button(content, text="✅ Finish & New Sale",
                               command=lambda: self._handle_option(dialog, self.finalize_sale),
                               bg='#28a745', fg='white', **button_style)

        finish_btn.pack(pady=3, fill=tk.X)

        # Add hover effects
        buttons_to_hover = [
            (preview_btn, '#fd7e14', '#e8590c'),
            (print_btn, '#007bff', '#0056b3'),
            (whatsapp_btn, '#25d366', '#1da851'),
            (email_btn, '#dc3545', '#c82333'),
            (finish_btn, '#28a745', '#1e7e34')
        ]
        
        if self.default_thermal_printer:
            buttons_to_hover.append((settings_btn, '#6c757d', '#5a6268'))
        
        self._add_hover_effects(buttons_to_hover)

    def _change_default_printer(self):
        """Allow user to change the default printer"""
        try:
            # Reset current default
            old_default = self.default_thermal_printer
            self.default_thermal_printer = None
            
            # Get available printers
            printers = self._get_available_printers()
            
            if not printers:
                messagebox.showerror("No Printers", "No printers found on this system.")
                self.default_thermal_printer = old_default  # Restore old default
                return
            
            # Show selection dialog
            selected_printer = self._select_thermal_printer(printers)
            
            if selected_printer:
                self.default_thermal_printer = selected_printer
                self._save_printer_config(selected_printer)
                messagebox.showinfo("Default Changed", 
                                  f"✅ Default printer changed to:\n{selected_printer}")
                print(f"Default printer changed from {old_default} to {selected_printer}")
            else:
                # User cancelled, restore old default
                self.default_thermal_printer = old_default
                print("Printer change cancelled, restored old default")
            
            # Return to receipt options
            self.ask_receipt_options(self.current_customer_name,
                                   self.current_total_amount,
                                   self.current_sale_data)
            
        except Exception as e:
            print(f"Error changing default printer: {e}")
            messagebox.showerror("Error", f"Failed to change default printer: {str(e)}")
            # Restore old default on error
            self.default_thermal_printer = old_default

    def show_thermal_preview(self):
        """Show EXACT thermal printer preview with 80mm paper simulation"""
        try:
            # Create preview window
            preview_window = tk.Toplevel()
            preview_window.title("🖨️ EXACT 80mm Thermal Printer Preview")
            preview_window.geometry("600x800")
            preview_window.resizable(False, False)
            preview_window.configure(bg='#2c3e50')
    
            # Center window
            self._center_window(preview_window, 600, 800)
    
            # Handle window close event (X button) to return to receipt options
            def on_window_close():
                preview_window.destroy()
                self.ask_receipt_options(self.current_customer_name,
                                       self.current_total_amount,
                                       self.current_sale_data)
    
            preview_window.protocol("WM_DELETE_WINDOW", on_window_close)
    
            # Main container
            main_frame = tk.Frame(preview_window, bg='#2c3e50', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
    
            # Header with specifications
            header_frame = tk.Frame(main_frame, bg='#e74c3c', relief='flat', pady=8)
            header_frame.pack(fill=tk.X, pady=(0, 10))
    
            # Paper simulation frame - exact 80mm width representation
            paper_container = tk.Frame(main_frame, bg='#34495e', relief='solid', bd=3)
            paper_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
            # Paper width indicator
            width_frame = tk.Frame(paper_container, bg='#34495e', height=25)
            width_frame.pack(fill=tk.X)
            width_frame.pack_propagate(False)
    
            tk.Label(width_frame, text="← 80mm Paper Width (48 chars) →",
                     font=('Arial', 9, 'bold'), fg='#ecf0f1', bg='#34495e').pack(expand=True)
    
            # Actual thermal paper simulation (white background, exact width)
            paper_frame = tk.Frame(paper_container, bg='white', relief='solid', bd=1)
            paper_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
            # Generate EXACT thermal receipt with proper formatting
            self._generate_thermal_preview_content(paper_frame)
    
            # Control buttons
            button_frame = tk.Frame(main_frame, bg='#2c3e50')
            button_frame.pack(fill=tk.X)
    
            print_btn = tk.Button(button_frame, text="🖨️ Print This EXACT Format",
                                  command=lambda: self._print_from_preview(preview_window),
                                  font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                                  relief='flat', padx=20, pady=10, cursor='hand2')
            print_btn.pack(side=tk.LEFT, padx=(0, 10))
    
            close_btn = tk.Button(button_frame, text="❌ Close",
                                  command=on_window_close,
                                  font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                                  relief='flat', padx=20, pady=10, cursor='hand2')
            close_btn.pack(side=tk.RIGHT)
    
            # Verification note
            verification_frame = tk.Frame(main_frame, bg='#27ae60', relief='flat', pady=5)
            verification_frame.pack(fill=tk.X, pady=(10, 0))
    
            tk.Label(verification_frame, text="✓ This shows EXACT formatting, spacing, and alignment as thermal printer",
                     font=('Arial', 9, 'bold'), fg='white', bg='#27ae60').pack()
    
        except Exception as e:
            print(f"Error showing thermal preview: {e}")
            messagebox.showerror("Preview Error", f"Failed to show preview: {str(e)}")

    def _show_raw_content(self):
        """Show raw content in a separate window"""
        try:
            raw_window = tk.Toplevel()
            raw_window.title("📄 Raw Content - Exact Printer Output")
            raw_window.geometry("700x600")
            raw_window.configure(bg='#2c3e50')

            self._center_window(raw_window, 700, 600)

            # Header
            header = tk.Label(raw_window, text="Raw Content (Character-by-Character)",
                              font=('Arial', 12, 'bold'), fg='white', bg='#2c3e50')
            header.pack(pady=10)

            # Text area with raw content
            text_frame = tk.Frame(raw_window, bg='white', relief='solid', bd=2)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

            text_area = tk.Text(text_frame, font=('Courier New', 9), bg='white', fg='black',
                                wrap=tk.NONE, state=tk.NORMAL)

            # Scrollbars
            v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
            h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_area.xview)
            text_area.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # Insert raw content
            raw_content = self._generate_common_receipt_content()
            text_area.insert(tk.END, raw_content)
            text_area.config(state=tk.DISABLED)

            # Pack scrollbars and text
            text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

            # Close button
            close_btn = tk.Button(raw_window, text="Close", command=raw_window.destroy,
                                  font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white',
                                  relief='flat', padx=20, pady=8)
            close_btn.pack(pady=(0, 10))

        except Exception as e:
            print(f"Error showing raw content: {e}")

    def _generate_thermal_preview_content(self, parent):
        """Generate EXACT thermal printer preview with proper 80mm formatting simulation"""
        try:
            # Create thermal paper simulation container
            thermal_paper = tk.Frame(parent, bg='white', width=400, height=600)
            thermal_paper.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            thermal_paper.pack_propagate(False)

            # Create scrollable content for the thermal paper
            canvas = tk.Canvas(thermal_paper, bg='white', highlightthickness=0)
            scrollbar = tk.Scrollbar(thermal_paper, orient="vertical", command=canvas.yview)
            content_frame = tk.Frame(canvas, bg='white')

            content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Generate the exact thermal receipt with proper formatting
            # FIXED: Call the correct method for rendering preview
            self._render_thermal_receipt(content_frame)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right")

            # Add paper width indicator
            width_indicator = tk.Label(parent, text="← 80mm Thermal Paper Width →",
                                       font=('Arial', 8, 'italic'), fg='#666666', bg='#f0f0f0')
            width_indicator.pack(pady=(5, 0))

            # Mouse wheel binding
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind("<MouseWheel>", _on_mousewheel)

        except Exception as e:
            print(f"Error generating thermal preview: {e}")
            error_label = tk.Label(parent, text="Error generating thermal preview",
                                   font=('Arial', 10, 'bold'), bg='white', fg='red')
            error_label.pack(anchor='w', padx=10, pady=10)

    def _render_thermal_receipt(self, parent):
        """Render receipt with EXACT thermal printer formatting and positioning"""
        try:
            # Use the SAME content generation method as printing
            raw_content = self._generate_common_receipt_content()
            
            # Split into lines and render each exactly as it will be printed
            lines = raw_content.split('\n')
            
            for line in lines:
                # Skip the cut line indicator (it's just for preview)
                if line.startswith('✂'):
                    self._add_thermal_line(parent, line, font_size=8, center=True, fg_color='#999999')
                    continue
                
                # Detect formatting based on content (same logic as printer)
                if line.strip() == "ANANDA BAKERY":
                    self._add_thermal_line(parent, line, font_size=12, bold=True, center=True, spacing_after=2)
                elif line.strip() in ["Mob no: 07775977224", "Fssai: 21524057002255"]:
                    self._add_thermal_line(parent, line, font_size=9, center=True)
                elif line.strip() == "SALES RECEIPT":
                    self._add_thermal_line(parent, line, font_size=10, bold=True, center=True, spacing_after=8)
                elif "Gross Total" in line:
                    self._add_thermal_line(parent, line, font_size=9, bold=True)
                elif line.strip() == "Have a Nice day":
                    self._add_thermal_line(parent, line, font_size=9, center=True, spacing_after=8)
                else:
                    # All other lines (including items, totals, separators) - exact as printed
                    self._add_thermal_line(parent, line, font_size=9)

        except Exception as e:
            print(f"Error rendering thermal receipt: {e}")
            error_label = tk.Label(parent, text="Error generating thermal preview",
                                   font=('Arial', 10, 'bold'), bg='white', fg='red')
            error_label.pack(anchor='w', padx=10, pady=10)

    def _add_thermal_line(self, parent, text, font_size=9, bold=False, center=False,
                      spacing_after=1, fg_color='black'):
        """Add a line with EXACT thermal printer formatting - matches printer output exactly"""
        try:
            # Calculate font weight
            font_weight = 'bold' if bold else 'normal'
            
            # Use exact same font as thermal printer simulation
            font_family = 'Courier New'  # Monospace to match thermal printer
            
            # Handle centering exactly as the printer does
            display_text = text
            if center and text.strip():
                # Calculate padding for centering (same as printer logic)
                char_width = self.thermal_settings['char_width']
                text_length = len(text.strip())
                if text_length < char_width:
                    padding = (char_width - text_length) // 2
                    display_text = " " * padding + text.strip()
        
            # Create label with exact formatting
            label = tk.Label(
                parent,
                text=display_text,
                font=(font_family, font_size, font_weight),
                bg='white',
                fg=fg_color,
                anchor='w',  # Always left-align the label itself
                justify='left'
            )
        
            label.pack(anchor='w', pady=(0, spacing_after))

        except Exception as e:
            print(f"Error adding thermal line: {e}")

    def _add_thermal_two_column(self, parent, left_text, right_text, col_width):
        """Add two-column text with exact spacing"""
        try:
            # Format text to exact column widths
            formatted_line = f"{left_text:<{col_width}} {right_text}"

            label = tk.Label(
                parent,
                text=formatted_line,
                font=('Courier New', 9),
                bg='white',
                fg='black',
                anchor='w'
            )
            label.pack(anchor='w', pady=(0, 1))

        except Exception as e:
            print(f"Error adding two-column line: {e}")

    def _add_thermal_total_line(self, parent, label_text, amount, label_width, bold=False):
        """Add total line with right-aligned amount"""
        try:
            # Format with exact spacing
            formatted_line = f"{label_text:<{label_width}}{amount:>10.2f}"

            font_weight = 'bold' if bold else 'normal'

            label = tk.Label(
                parent,
                text=formatted_line,
                font=('Courier New', 9, font_weight),
                bg='white',
                fg='black',
                anchor='w'
            )
            label.pack(anchor='w', pady=(0, 1))

        except Exception as e:
            print(f"Error adding total line: {e}")


    def print_receipt(self):
        """Print receipt using Windows installed thermal printer"""
        try:
            # Show printing status
            status_dialog = self._show_printing_status()

            # Generate receipt content
            receipt_content = self._generate_common_receipt_content()

            # Try Windows thermal printer first
            success = self._print_to_windows_thermal_printer(receipt_content)

            # Close status dialog
            if status_dialog:
                status_dialog.destroy()

            if success:
                messagebox.showinfo("Print Success",
                                   "🖨️ Receipt printed successfully!")
            else:
                # Fallback to default system printer
                fallback_success = self._print_to_system_printer(receipt_content)
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

            # Return to options
            self.ask_receipt_options(self.current_customer_name,
                                    self.current_total_amount,
                                    self.current_sale_data)

        except Exception as e:
            print(f"Error printing receipt: {e}")
            messagebox.showerror("Print Error", f"Failed to print: {str(e)}")
            self.ask_receipt_options(self.current_customer_name,
                                    self.current_total_amount,
                                    self.current_sale_data)

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

    def _ask_save_as_default(self, printer_name):
        """Ask user if they want to save the selected printer as default"""
        try:
            dialog = tk.Toplevel()
            dialog.title("Save Default Printer")
            dialog.geometry("450x300")
            dialog.resizable(False, False)
            dialog.grab_set()
            dialog.configure(bg='#f8f9fa')

            self._center_window(dialog, 450, 300)

            # Main frame
            main_frame = tk.Frame(dialog, bg='#f8f9fa', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Header
            header_frame = tk.Frame(main_frame, bg='#17a2b8', relief='flat', pady=10)
            header_frame.pack(fill=tk.X, pady=(0, 15))

            tk.Label(header_frame, text="💾 Save Default Printer",
                     font=('Arial', 14, 'bold'), fg='white', bg='#17a2b8').pack()

            # Message
            message_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1, padx=15, pady=15)
            message_frame.pack(fill=tk.X, pady=(0, 15))

            tk.Label(message_frame, text="Do you want to save this printer as default?",
                     font=('Arial', 11, 'bold'), bg='white').pack()
            
            tk.Label(message_frame, text=f"Printer: {printer_name}",
                     font=('Arial', 10), fg='#007bff', bg='white').pack(pady=(5, 0))
            
            tk.Label(message_frame, text="This will skip printer selection in future prints.",
                     font=('Arial', 9), fg='#6c757d', bg='white').pack(pady=(5, 0))

            # Buttons
            button_frame = tk.Frame(main_frame, bg='#f8f9fa')
            button_frame.pack(fill=tk.X)

            result = [False]  # Use list to modify from inner functions

            def save_default():
                result[0] = True
                dialog.destroy()

            def skip():
                result[0] = False
                dialog.destroy()

            # Yes button
            yes_btn = tk.Button(button_frame, text="✅ Yes, Save as Default",
                               command=save_default,
                               bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                               relief='flat', padx=15, pady=8, cursor='hand2')
            yes_btn.pack(side=tk.LEFT, padx=(0, 10))

            # No button
            no_btn = tk.Button(button_frame, text="❌ No, Just Print Once",
                              command=skip,
                              bg='#6c757d', fg='white', font=('Arial', 10, 'bold'),
                              relief='flat', padx=15, pady=8, cursor='hand2')
            no_btn.pack(side=tk.LEFT)

            # Focus on Yes button
            yes_btn.focus_set()

            # Bind Enter key to Yes
            dialog.bind('<Return>', lambda e: save_default())
            dialog.bind('<Escape>', lambda e: skip())

            dialog.wait_window()
            return result[0]

        except Exception as e:
            print(f"Error in save default dialog: {e}")
            return False

    def _save_printer_config(self, printer_name):
        """Save printer configuration to file"""
        try:
            import json
            import os
            
            # Create config directory if it doesn't exist
            config_dir = os.path.join(os.path.expanduser("~"), ".ananda_bakery")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            config_file = os.path.join(config_dir, "printer_config.json")
            
            config = {
                "default_thermal_printer": printer_name,
                "saved_date": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✓ Printer configuration saved to {config_file}")
            
        except Exception as e:
            print(f"Error saving printer config: {e}")

    def _load_printer_config(self):
        """Load saved printer configuration"""
        try:
            import json
            import os
            
            config_file = os.path.join(os.path.expanduser("~"), ".ananda_bakery", "printer_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                saved_printer = config.get("default_thermal_printer")
                if saved_printer:
                    print(f"✓ Loaded saved default printer: {saved_printer}")
                    self.default_thermal_printer = saved_printer
                    return saved_printer
            
            print("No saved printer configuration found")
            return None
            
        except Exception as e:
            print(f"Error loading printer config: {e}")
            return None

    def _reset_printer_config(self):
        """Reset printer configuration (for settings/preferences)"""
        try:
            import os
            
            config_file = os.path.join(os.path.expanduser("~"), ".ananda_bakery", "printer_config.json")
            
            if os.path.exists(config_file):
                os.remove(config_file)
                print("✓ Printer configuration reset")
            
            self.default_thermal_printer = None
            messagebox.showinfo("Reset Complete", "Printer configuration has been reset.\nYou will be asked to select a printer on next print.")
            
        except Exception as e:
            print(f"Error resetting printer config: {e}")
            messagebox.showerror("Reset Error", f"Failed to reset printer config: {str(e)}")

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

    def _find_windows_thermal_printer(self):
        """Enhanced thermal printer detection with more details"""
        try:
            import subprocess
            
            print("=== SEARCHING FOR THERMAL PRINTERS ===")
            
            # Get detailed printer information
            ps_command = '''
            Get-WmiObject -Class Win32_Printer | ForEach-Object {
                [PSCustomObject]@{
                    Name = $_.Name
                    DriverName = $_.DriverName
                    PortName = $_.PortName
                    Status = $_.Status
                    PrinterState = $_.PrinterState
                    Default = $_.Default
                }
            } | ConvertTo-Json
            '''
            
            result = subprocess.run(['powershell', '-Command', ps_command],
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                try:
                    printers_data = json.loads(result.stdout)
                    if not isinstance(printers_data, list):
                        printers_data = [printers_data]
                    
                    print(f"Found {len(printers_data)} total printers:")
                    
                    thermal_keywords = ['thermal', 'receipt', 'pos', '80mm', '58mm', 'tm-', 'rp-']
                    usb_printers = []
                    thermal_printers = []
                    
                    for printer in printers_data:
                        name = printer.get('Name', '').lower()
                        driver = printer.get('DriverName', '').lower()
                        port = printer.get('PortName', '')
                        status = printer.get('Status', '')
                        
                        print(f"  - {printer.get('Name')} (Port: {port}, Status: {status})")
                        
                        # Check for thermal printer keywords
                        is_thermal = any(keyword in name or keyword in driver for keyword in thermal_keywords)
                        
                        if is_thermal:
                            thermal_printers.append(printer.get('Name'))
                            print(f"    ✓ Identified as thermal printer")
                        
                        # Also collect USB printers as potential thermal printers
                        if 'USB' in port.upper():
                            usb_printers.append(printer.get('Name'))
                            print(f"    ✓ USB printer detected")
                    
                    # Return thermal printer first, then USB printer
                    if thermal_printers:
                        selected = thermal_printers[0]
                        print(f"Selected thermal printer: {selected}")
                        return selected
                    elif usb_printers:
                        selected = usb_printers[0]
                        print(f"Selected USB printer (likely thermal): {selected}")
                        return selected
                        
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
            
            print("No thermal or USB printers found")
            return None
            
        except Exception as e:
            print(f"Error finding Windows thermal printer: {e}")
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

    def _format_for_thermal_printer(self, content):
        """Format content for thermal printer with proper ESC/POS commands"""
        try:
            raw_data = b''
            
            # Initialize printer - clear any previous state
            raw_data += b'\x1b@'  # ESC @ - Initialize printer
            raw_data += b'\x1bt\x00'  # Select character code table (PC437)
            
            lines = content.split('\n')
            
            for line in lines:
                if line.startswith('✂'):  # Skip cut indicators
                    continue
                    
                line_stripped = line.strip()
                
                # Apply formatting based on content
                if line_stripped == "ANANDA BAKERY":
                    raw_data += b'\x1ba\x01'  # Center align
                    raw_data += b'\x1bE\x01'  # Bold on
                    raw_data += b'\x1b!\x11'  # Double height and width
                    raw_data += line_stripped.encode('utf-8', errors='ignore') + b'\n'
                    raw_data += b'\x1b!\x00'  # Normal size
                    raw_data += b'\x1bE\x00'  # Bold off
                    raw_data += b'\x1ba\x00'  # Left align

                elif line_stripped in ["Mob no: 07775977224", "Fssai: 21524057002255"]:
                    raw_data += b'\x1ba\x01'  # Center align
                    raw_data += line_stripped.encode('utf-8', errors='ignore') + b'\n'
                    raw_data += b'\x1ba\x00'  # Left align
                    
                elif line_stripped == "SALES RECEIPT":
                    raw_data += b'\x1ba\x01'  # Center align
                    raw_data += b'\x1bE\x01'  # Bold on
                    raw_data += b'\x1b!\x10'  # Double width
                    raw_data += line_stripped.encode('utf-8', errors='ignore') + b'\n'
                    raw_data += b'\x1b!\x00'  # Normal size
                    raw_data += b'\x1bE\x00'  # Bold off
                    raw_data += b'\x1ba\x00'  # Left align
                    raw_data += b'\n'  # Extra line after receipt title
                    
                elif "Gross Total" in line:
                    raw_data += b'\x1bE\x01'  # Bold on
                    raw_data += line.encode('utf-8', errors='ignore') + b'\n'
                    raw_data += b'\x1bE\x00'  # Bold off
                    
                elif line_stripped == "Have a Nice day":
                    raw_data += b'\n'  # Extra line before footer
                    raw_data += b'\x1ba\x01'  # Center align
                    raw_data += line_stripped.encode('utf-8', errors='ignore') + b'\n'
                    raw_data += b'\x1ba\x00'  # Left align
                    # CRITICAL FIX: Add sufficient spacing after "Have a Nice day"
                    raw_data += b'\n' * 4  # Add 4 extra line feeds to ensure text is printed    
                else:
                    # Regular lines (items, totals, separators)
                    raw_data += line.encode('utf-8', errors='ignore') + b'\n'
            
            # Optional: Add a form feed to ensure all content is processed
            raw_data += b'\x0c'  # Form feed
            
            # Final cut command
            raw_data += b'\x1dV\x00'  # Full cut
            
            print(f"Generated thermal data: {len(raw_data)} bytes")
            return raw_data
            
        except Exception as e:
            print(f"Error formatting for thermal printer: {e}")
            return content.encode('utf-8', errors='ignore')

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

    def send_whatsapp(self):
        """Send receipt via WhatsApp"""
        try:
            phone = self._get_customer_phone()
            if phone:
                # Use the same content as preview and printer
                content = self._generate_common_receipt_content()
                print(f"Sending WhatsApp to {phone}:\n{content}")
                messagebox.showinfo("WhatsApp", f"📱 Receipt sent to {phone}")
            else:
                messagebox.showwarning("WhatsApp", "No phone number available")

            self.ask_receipt_options(self.current_customer_name,
                                     self.current_total_amount,
                                     self.current_sale_data)
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            messagebox.showerror("WhatsApp Error", f"Failed to send: {str(e)}")

    def send_email(self):
        """Send receipt via email"""
        try:
            email = self._get_customer_email()
            if email:
                # Use the same content as preview and printer
                content = self._generate_common_receipt_content()
                print(f"Sending email to {email}:\n{content}")
                messagebox.showinfo("Email", f"📧 Receipt sent to {email}")
            else:
                messagebox.showwarning("Email", "No email address available")

            self.ask_receipt_options(self.current_customer_name,
                                     self.current_total_amount,
                                     self.current_sale_data)
        except Exception as e:
            print(f"Error sending email: {e}")
            messagebox.showerror("Email Error", f"Failed to send: {str(e)}")

    def finalize_sale(self):
        """Finalize sale and prepare for next"""
        try:
            self.current_sale_data = None
            self.current_customer_name = None
            self.current_total_amount = None

            if hasattr(self.sales_tab, 'update_status'):
                self.sales_tab.update_status("Sale completed - Ready for new sale", "success")

            messagebox.showinfo("Sale Complete", "✅ Sale completed successfully!\nReady for next customer.")
            print("Sale finalized successfully")

        except Exception as e:
            print(f"Error finalizing sale: {e}")

    # Helper methods
    def _center_window(self, window, width, height):
        """Center window on screen"""
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _handle_option(self, dialog, action):
        """Handle option selection"""
        dialog.destroy()
        action()

    def _add_hover_effects(self, button_configs):
        """Add hover effects to buttons"""
        for button, normal_color, hover_color in button_configs:
            def on_enter(e, btn=button, color=hover_color):
                btn.config(bg=color)
            def on_leave(e, btn=button, color=normal_color):
                btn.config(bg=color)
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

    def _get_sale_info(self):
        """Get sale information"""
        if self.current_sale_data:
            return {
                'sale_id': self.current_sale_data.get('sale_id', 'N/A'),
                'date': self.current_sale_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'time': self.current_sale_data.get('time', datetime.now().strftime('%H:%M:%S')),
                'payment': self.current_sale_data.get('payment_method', 'Cash')
            }
        return {
            'sale_id': 'SALE001',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'payment': 'Cash'
        }

    def _get_sale_items(self):
        """Get sale items"""
        items = []

        if self.current_sale_data and 'items' in self.current_sale_data:
            for item in self.current_sale_data['items']:
                items.append({
                    'name': item.get('name', 'Unknown'),
                    'quantity': item.get('quantity', 0),
                    'unit_price': float(item.get('unit_price_with_tax', item.get('unit_price', 0))),
                    'total': float(item.get('total_with_tax', item.get('total', 0)))
                })
        elif hasattr(self.sales_tab, 'sale_tree'):
            for item_id in self.sales_tab.sale_tree.get_children():
                values = self.sales_tab.sale_tree.item(item_id)['values']
                if len(values) >= 8:
                    try:
                        items.append({
                            'name': str(values[1]),
                            'quantity': int(values[4]),
                            'unit_price': float(str(values[3]).replace('₹', '').replace(',', '').strip()),
                            'total': float(str(values[7]).replace('₹', '').replace(',', '').strip())
                        })
                    except (ValueError, IndexError):
                        continue

        if not items:
            items = [
                {'name': 'Sample Item', 'quantity': 1, 'unit_price': 100.00, 'total': 100.00}
            ]

        return items

    def _calculate_totals(self, items_total):
        """Calculate totals with tax"""
        if self.current_sale_data:
            return {
                'subtotal': float(self.current_sale_data.get('base_amount', items_total)),
                'cgst': float(self.current_sale_data.get('cgst_amount', 0)),
                'sgst': float(self.current_sale_data.get('sgst_amount', 0)),
                'total': float(self.current_sale_data.get('total_amount', items_total))
            }

        cgst = items_total * 0.025
        sgst = items_total * 0.025
        total = items_total + cgst + sgst

        return {
            'subtotal': items_total,
            'cgst': cgst,
            'sgst': sgst,
            'total': total
        }

    def _get_customer_phone(self):
        """Get customer phone number"""
        if hasattr(self.sales_tab, 'phone_var'):
            phone = self.sales_tab.phone_var.get().strip()
            if phone:
                return phone

        return simpledialog.askstring("Phone Number", "Enter customer's phone number:")

    def _get_customer_email(self):
        """Get customer email"""
        return simpledialog.askstring("Email Address", "Enter customer's email address:")

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

    def _print_from_preview(self, preview_window):
        """Print from preview window"""
        preview_window.destroy()
        self.print_receipt()

    def _close_and_return(self, window):
        """Close window and return to options"""
        window.destroy()
        self.ask_receipt_options(self.current_customer_name,
                                 self.current_total_amount,
                                 self.current_sale_data)

    def _cleanup_temp_file(self, file_path):
        """Clean up temporary file"""
        try:
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")

    def _generate_common_receipt_content(self):
        """Generate the EXACT raw content that matches both preview and printer output"""
        try:
            char_width = self.thermal_settings['char_width']  # 48 characters
            content = ""

            # Get data
            sale_info = self._get_sale_info()
            items = self._get_sale_items()
            totals = self._calculate_totals(sum(item['total'] for item in items))

            # Header section - EXACT formatting
            content += "ANANDA BAKERY\n"
            content += "Mob no: 07775977224\n"
            content += "Fssai: 21524057002255\n"
            content += "SALES RECEIPT\n"
            # Sale information - EXACT two-column formatting
            col_width = (char_width - 2) // 2  # 23 characters each column

            sale_id_text = f"Sale ID: {sale_info['sale_id']}"
            date_text = f"Date: {sale_info['date']}"
            content += f"{sale_id_text:<{col_width}} {date_text}\n"

            time_text = f"Time: {sale_info['time']}"
            payment_text = f"Payment: {sale_info['payment']}"
            content += f"{time_text:<{col_width}} {payment_text}\n"
            # Separator line
            content += "-" * char_width + "\n"

            # Items header - EXACT column spacing
            content += f"{'Item name':<18} {'QTY':<4} {'PRICE':<7} {'Amount':<12}\n"

            # Items - EXACT formatting with proper truncation and spacing
            for item in items:
                name = item['name'][:18]  # Truncate to exactly 18 characters
                qty = str(item['quantity'])
                price = f"{item['unit_price']:.2f}"
                amount = f"{item['total']:.2f}"

                # Ensure exact column alignment
                content += f"{name:<18} {qty:<4} {price:<7} {amount:<12}\n"

            # Separator line
            content += "-" * char_width + "\n"

            # Totals section - EXACT right alignment
            amount_col = char_width - 10  # 38 chars for label, 10 for amount

            content += f"{'Sub Total':<{amount_col}}{totals['subtotal']:>10.2f}\n"
            content += f"{'CGST':<{amount_col}}{totals['cgst']:>10.2f}\n"
            content += f"{'SGST':<{amount_col}}{totals['sgst']:>10.2f}\n"
            content += f"{'Gross Total':<{amount_col}}{totals['total']:>10.2f}\n"

            # Separator line
            content += "-" * char_width + "\n"
            # Footer - EXACT centering
            content += "Have a Nice day\n" # Empty line after footer
            # Cut line indicator (for preview only - printer ignores this)
            cut_line = "✂" + "-" * (char_width - 2) + "✂"
            content += cut_line + "\n"

            return content

        except Exception as e:
            print(f"Error generating common receipt content: {e}")
            return "Error generating receipt content"

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
