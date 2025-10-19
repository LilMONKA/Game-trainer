import customtkinter as ctk
from tkinter import messagebox, ttk
import pymem
import pymem.process
import psutil
import struct
import threading
import time
from datetime import datetime

class GameTrainerPro:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("🎮 Game Trainer Pro - Memory Scanner")
        self.root.geometry("1400x900")
        
        # Memory scanning
        self.pm = None
        self.process_name = None
        self.process_id = None
        self.base_address = None
        
        # Scan results
        self.scan_results = []
        self.scan_type = "exact"
        self.value_type = "4bytes"
        
        # Active cheats/freezes
        self.frozen_addresses = {}
        self.active_scripts = []
        
        # Colors
        self.colors = {
            'bg': '#0d1117',
            'card': '#161b22',
            'card_hover': '#1c2128',
            'accent': '#58a6ff',
            'success': '#3fb950',
            'warning': '#d29922',
            'danger': '#f85149',
            'text': '#c9d1d9',
            'subtext': '#8b949e',
            'border': '#30363d'
        }
        
        self.setup_ui()
        self.start_freeze_thread()
    
    def setup_ui(self):
        """Setup main UI"""
        # Header
        self.create_header()
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors['bg'])
        main_container.pack(fill="both", expand=True)
        
        # Left panel - Process & Scan
        self.create_left_panel(main_container)
        
        # Right panel - Results & Cheats
        self.create_right_panel(main_container)
    
    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self.root, height=120, fg_color=self.colors['card'])
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="🎮 GAME TRAINER PRO",
            font=("Arial Black", 32),
            text_color=self.colors['accent']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Advanced Memory Scanner & Trainer",
            font=("Arial", 13),
            text_color=self.colors['subtext']
        ).pack(anchor="w")
        
        # Warning
        warning_frame = ctk.CTkFrame(header, fg_color=self.colors['danger'])
        warning_frame.pack(side="right", padx=30, pady=20)
        
        ctk.CTkLabel(
            warning_frame,
            text="⚠️ SINGLE-PLAYER ONLY",
            font=("Arial Bold", 14),
            text_color="white"
        ).pack(padx=20, pady=10)
        
        ctk.CTkLabel(
            warning_frame,
            text="Never use in online/multiplayer games!",
            font=("Arial", 10),
            text_color="white"
        ).pack(padx=20, pady=(0, 10))
    
    def create_left_panel(self, parent):
        """Create left panel"""
        left_panel = ctk.CTkFrame(parent, width=600, fg_color=self.colors['card'])
        left_panel.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        # Process Selection
        process_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        process_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            process_frame,
            text="🎯 SELECT PROCESS",
            font=("Arial Bold", 16),
            text_color=self.colors['accent']
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        select_frame = ctk.CTkFrame(process_frame, fg_color="transparent")
        select_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.process_combo = ctk.CTkComboBox(
            select_frame,
            values=["Select a process..."],
            width=400,
            height=40,
            font=("Arial", 13),
            command=self.attach_to_process
        )
        self.process_combo.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            select_frame,
            text="🔄 Refresh",
            width=100,
            height=40,
            command=self.refresh_processes
        ).pack(side="left")
        
        # Status
        self.process_status = ctk.CTkLabel(
            process_frame,
            text="Not attached",
            font=("Arial", 11),
            text_color=self.colors['danger']
        )
        self.process_status.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Scan Options
        scan_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        scan_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            scan_frame,
            text="🔍 SCAN OPTIONS",
            font=("Arial Bold", 16),
            text_color=self.colors['accent']
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Value Type
        type_frame = ctk.CTkFrame(scan_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(type_frame, text="Value Type:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        
        self.value_type_var = ctk.StringVar(value="4bytes")
        value_types = ["1byte", "2bytes", "4bytes", "8bytes", "Float", "Double"]
        for vtype in value_types:
            ctk.CTkRadioButton(
                type_frame,
                text=vtype,
                variable=self.value_type_var,
                value=vtype.lower(),
                font=("Arial", 11)
            ).pack(side="left", padx=5)
        
        # Scan Type
        scan_type_frame = ctk.CTkFrame(scan_frame, fg_color="transparent")
        scan_type_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(scan_type_frame, text="Scan Type:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        
        self.scan_type_var = ctk.StringVar(value="exact")
        scan_types = [
            ("Exact Value", "exact"),
            ("Bigger Than", "bigger"),
            ("Smaller Than", "smaller"),
            ("Unknown", "unknown")
        ]
        for label, value in scan_types:
            ctk.CTkRadioButton(
                scan_type_frame,
                text=label,
                variable=self.scan_type_var,
                value=value,
                font=("Arial", 11)
            ).pack(side="left", padx=5)
        
        # Value Input
        input_frame = ctk.CTkFrame(scan_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(input_frame, text="Value:", font=("Arial Bold", 12)).pack(side="left", padx=(0, 10))
        
        self.value_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter value to scan...",
            width=200,
            height=40,
            font=("Arial", 14)
        )
        self.value_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            input_frame,
            text="🔍 First Scan",
            width=120,
            height=40,
            font=("Arial Bold", 13),
            fg_color=self.colors['accent'],
            command=self.first_scan
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            input_frame,
            text="🔄 Next Scan",
            width=120,
            height=40,
            font=("Arial Bold", 13),
            fg_color=self.colors['success'],
            command=self.next_scan
        ).pack(side="left", padx=5)
        
        # Results
        results_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        results_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        header = ctk.CTkFrame(results_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📊 SCAN RESULTS",
            font=("Arial Bold", 16),
            text_color=self.colors['accent']
        ).pack(side="left")
        
        self.result_count = ctk.CTkLabel(
            header,
            text="0 addresses found",
            font=("Arial", 12),
            text_color=self.colors['subtext']
        )
        self.result_count.pack(side="right")
        
        # Results table
        table_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=self.colors['card'], foreground=self.colors['text'], 
                       fieldbackground=self.colors['card'], borderwidth=0)
        style.configure("Treeview.Heading", background=self.colors['bg'], foreground=self.colors['text'],
                       font=("Arial Bold", 11))
        
        self.results_tree = ttk.Treeview(
            table_frame,
            columns=("Address", "Value", "Type"),
            show="headings",
            height=15
        )
        
        self.results_tree.heading("Address", text="Address")
        self.results_tree.heading("Value", text="Value")
        self.results_tree.heading("Type", text="Type")
        
        self.results_tree.column("Address", width=150)
        self.results_tree.column("Value", width=100)
        self.results_tree.column("Type", width=80)
        
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Double-click to add to cheat list
        self.results_tree.bind("<Double-1>", self.add_to_cheat_list)
    
    def create_right_panel(self, parent):
        """Create right panel"""
        right_panel = ctk.CTkFrame(parent, width=600, fg_color=self.colors['card'])
        right_panel.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Cheat Table
        cheat_frame = ctk.CTkFrame(right_panel, fg_color=self.colors['bg'])
        cheat_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        header = ctk.CTkFrame(cheat_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="⭐ ACTIVE CHEATS",
            font=("Arial Bold", 16),
            text_color=self.colors['accent']
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="🗑️ Clear All",
            width=100,
            height=30,
            fg_color=self.colors['danger'],
            command=self.clear_cheats
        ).pack(side="right")
        
        # Cheat table
        table_frame = ctk.CTkFrame(cheat_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.cheat_tree = ttk.Treeview(
            table_frame,
            columns=("Active", "Description", "Address", "Value", "Frozen"),
            show="headings",
            height=12
        )
        
        self.cheat_tree.heading("Active", text="✓")
        self.cheat_tree.heading("Description", text="Description")
        self.cheat_tree.heading("Address", text="Address")
        self.cheat_tree.heading("Value", text="Value")
        self.cheat_tree.heading("Frozen", text="Frozen")
        
        self.cheat_tree.column("Active", width=40)
        self.cheat_tree.column("Description", width=200)
        self.cheat_tree.column("Address", width=120)
        self.cheat_tree.column("Value", width=100)
        self.cheat_tree.column("Frozen", width=60)
        
        cheat_scroll = ctk.CTkScrollbar(table_frame, command=self.cheat_tree.yview)
        self.cheat_tree.configure(yscrollcommand=cheat_scroll.set)
        
        self.cheat_tree.pack(side="left", fill="both", expand=True)
        cheat_scroll.pack(side="right", fill="y")
        
        # Cheat controls
        control_frame = ctk.CTkFrame(cheat_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            control_frame,
            text="✏️ Edit Value",
            width=120,
            command=self.edit_cheat_value
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="❄️ Freeze",
            width=120,
            fg_color=self.colors['accent'],
            command=self.freeze_value
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="🔥 Unfreeze",
            width=120,
            fg_color=self.colors['warning'],
            command=self.unfreeze_value
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame,
            text="🗑️ Delete",
            width=120,
            fg_color=self.colors['danger'],
            command=self.delete_cheat
        ).pack(side="left", padx=5)
        
        # Quick cheats
        quick_frame = ctk.CTkFrame(right_panel, fg_color=self.colors['bg'])
        quick_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            quick_frame,
            text="⚡ QUICK CHEATS",
            font=("Arial Bold", 16),
            text_color=self.colors['accent']
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        quick_buttons = ctk.CTkFrame(quick_frame, fg_color="transparent")
        quick_buttons.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            quick_buttons,
            text="💰 Set to 999999",
            width=160,
            height=45,
            font=("Arial Bold", 12),
            command=lambda: self.quick_set_value(999999)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            quick_buttons,
            text="♾️ Set to MAX",
            width=160,
            height=45,
            font=("Arial Bold", 12),
            command=lambda: self.quick_set_value(2147483647)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            quick_buttons,
            text="➕ Add 1000",
            width=160,
            height=45,
            font=("Arial Bold", 12),
            command=lambda: self.modify_value(1000)
        ).pack(side="left", padx=5)
        
        # Speedhack
        speed_frame = ctk.CTkFrame(right_panel, fg_color=self.colors['bg'])
        speed_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            speed_frame,
            text="⚡ SPEEDHACK",
            font=("Arial Bold", 16),
            text_color=self.colors['accent']
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        speed_controls = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_controls.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(speed_controls, text="Speed:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        
        self.speed_slider = ctk.CTkSlider(
            speed_controls,
            from_=0.1,
            to=5.0,
            width=300,
            number_of_steps=49
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=5)
        
        self.speed_label = ctk.CTkLabel(
            speed_controls,
            text="1.0x",
            font=("Arial Bold", 14),
            width=60
        )
        self.speed_label.pack(side="left", padx=10)
        
        self.speed_slider.configure(command=self.update_speed_label)
        
        ctk.CTkButton(
            speed_controls,
            text="Apply Speed",
            width=120,
            command=self.apply_speedhack
        ).pack(side="left", padx=5)
    
    def refresh_processes(self):
        """Refresh process list"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                # Filter for game-related processes
                if any(ext in name.lower() for ext in ['.exe', 'game', 'play']):
                    processes.append(f"{name} (PID: {pid})")
            except:
                pass
        
        self.process_combo.configure(values=processes if processes else ["No processes found"])
        messagebox.showinfo("Refresh", f"Found {len(processes)} processes")
    
    def attach_to_process(self, selection):
        """Attach to selected process"""
        try:
            # Extract process name and PID
            if "PID:" in selection:
                parts = selection.split("(PID:")
                process_name = parts[0].strip()
                pid = int(parts[1].strip(")"))
                
                # Attach
                self.pm = pymem.Pymem(process_name)
                self.process_name = process_name
                self.process_id = pid
                self.base_address = pymem.process.module_from_name(
                    self.pm.process_handle, process_name
                ).lpBaseOfDll
                
                self.process_status.configure(
                    text=f"✅ Attached to {process_name}",
                    text_color=self.colors['success']
                )
                
                messagebox.showinfo("Success", f"Attached to {process_name}\nPID: {pid}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to attach:\n{str(e)}")
            self.process_status.configure(
                text="❌ Failed to attach",
                text_color=self.colors['danger']
            )
    
    def first_scan(self):
        """Perform first scan"""
        if not self.pm:
            messagebox.showerror("Error", "Please attach to a process first!")
            return
        
        value = self.value_entry.get()
        if not value and self.scan_type_var.get() != "unknown":
            messagebox.showerror("Error", "Please enter a value to scan!")
            return
        
        # Clear previous results
        self.scan_results.clear()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Start scan in thread
        threading.Thread(target=self._perform_first_scan, args=(value,), daemon=True).start()
        messagebox.showinfo("Scanning", "First scan started...\nThis may take a moment.")
    
    def _perform_first_scan(self, value):
        """Perform actual first scan"""
        try:
            scan_type = self.scan_type_var.get()
            value_type = self.value_type_var.get()
            
            # Simulate scan (real implementation would scan process memory)
            # This is a simplified example
            self.scan_results = []
            
            # In real implementation, you would:
            # 1. Iterate through process memory regions
            # 2. Read memory at each address
            # 3. Compare values based on scan type
            # 4. Store matching addresses
            
            # For demo, create some fake results
            import random
            for i in range(20):
                addr = random.randint(0x10000000, 0x7FFFFFFF)
                self.scan_results.append({
                    'address': addr,
                    'value': value if value else "???",
                    'type': value_type
                })
            
            # Update UI
            self.root.after(0, self._update_results_display)
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
    
    def next_scan(self):
        """Perform next scan"""
        if not self.scan_results:
            messagebox.showwarning("Warning", "Perform first scan first!")
            return
        
        value = self.value_entry.get()
        if not value:
            messagebox.showerror("Error", "Please enter a value!")
            return
        
        # Filter previous results
        threading.Thread(target=self._perform_next_scan, args=(value,), daemon=True).start()
        messagebox.showinfo("Scanning", "Next scan started...")
    
    def _perform_next_scan(self, value):
        """Perform actual next scan"""
        try:
            # Filter results based on new value
            filtered = []
            for result in self.scan_results:
                # Re-read memory and compare
                # In real implementation, read actual memory
                # For demo, randomly keep some results
                import random
                if random.random() > 0.5:
                    result['value'] = value
                    filtered.append(result)
            
            self.scan_results = filtered
            self.root.after(0, self._update_results_display)
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
    
    def _update_results_display(self):
        """Update results tree"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for result in self.scan_results[:1000]:  # Limit to 1000 results
            self.results_tree.insert(
                "",
                "end",
                values=(
                    f"0x{result['address']:08X}",
                    result['value'],
                    result['type']
                )
            )
        
        self.result_count.configure(text=f"{len(self.scan_results)} addresses found")
    
    def add_to_cheat_list(self, event):
        """Add selected address to cheat list"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        address = item['values'][0]
        value = item['values'][1]
        vtype = item['values'][2]
        
        # Ask for description
        desc = ctk.CTkInputDialog(
            text="Enter description:",
            title="Add to Cheat List"
        ).get_input()
        
        if desc:
            self.cheat_tree.insert(
                "",
                "end",
                values=("✓", desc, address, value, "No")
            )
    
    def edit_cheat_value(self):
        """Edit selected cheat value"""
        selection = self.cheat_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a cheat to edit!")
            return
        
        item = self.cheat_tree.item(selection[0])
        current_value = item['values'][3]
        
        new_value = ctk.CTkInputDialog(
            text=f"Current value: {current_value}\nEnter new value:",
            title="Edit Value"
        ).get_input()
        
        if new_value:
            # Update value in memory (simplified)
            address = item['values'][2]
            # In real implementation: self.pm.write_int(int(address, 16), int(new_value))
            
            # Update display
            self.cheat_tree.item(
                selection[0],
                values=(item['values'][0], item['values'][1], address, new_value, item['values'][4])
            )
            
            messagebox.showinfo("Success", f"Value set to {new_value}")
    
    def freeze_value(self):
        """Freeze selected cheat value"""
        selection = self.cheat_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a cheat to freeze!")
            return
        
        item = self.cheat_tree.item(selection[0])
        address = item['values'][2]
        value = item['values'][3]
        
        # Add to frozen addresses
        self.frozen_addresses[address] = value
        
        # Update display
        self.cheat_tree.item(
            selection[0],
            values=(item['values'][0], item['values'][1], address, value, "Yes")
        )
        
        messagebox.showinfo("Frozen", f"Value frozen at {value}")
    
    def unfreeze_value(self):
        """Unfreeze selected value"""
        selection = self.cheat_tree.selection()
        if not selection:
            return
        
        item = self.cheat_tree.item(selection[0])
        address = item['values'][2]
        
        if address in self.frozen_addresses:
            del self.frozen_addresses[address]
            
            self.cheat_tree.item(
                selection[0],
                values=(item['values'][0], item['values'][1], address, item['values'][3], "No")
            )
            
            messagebox.showinfo("Unfrozen", "Value unfrozen")
    
    def delete_cheat(self):
        """Delete selected cheat"""
        selection = self.cheat_tree.selection()
        if selection:
            self.cheat_tree.delete(selection[0])
    
    def clear_cheats(self):
        """Clear all cheats"""
        if messagebox.askyesno("Confirm", "Clear all cheats?"):
            for item in self.cheat_tree.get_children():
                self.cheat_tree.delete(item)
            self.frozen_addresses.clear()
    
    def quick_set_value(self, value):
        """Quick set value for selected cheat"""
        selection = self.cheat_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a cheat first!")
            return
        
        item = self.cheat_tree.item(selection[0])
        address = item['values'][2]
        
        # Update value
        self.cheat_tree.item(
            selection[0],
            values=(item['values'][0], item['values'][1], address, str(value), item['values'][4])
        )
        
        messagebox.showinfo("Success", f"Value set to {value}")
    
    def modify_value(self, amount):
        """Modify selected value by amount"""
        selection = self.cheat_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a cheat first!")
            return
        
        item = self.cheat_tree.item(selection[0])
        try:
            current = int(item['values'][3])
            new_value = current + amount
            
            self.cheat_tree.item(
                selection[0],
                values=(item['values'][0], item['values'][1], item['values'][2], str(new_value), item['values'][4])
            )
            
            messagebox.showinfo("Success", f"Value changed to {new_value}")
        except:
            messagebox.showerror("Error", "Invalid value type!")
    
    def update_speed_label(self, value):
        """Update speedhack label"""
        self.speed_label.configure(text=f"{float(value):.1f}x")
    
    def apply_speedhack(self):
        """Apply speedhack"""
        speed = self.speed_slider.get()
        messagebox.showinfo(
            "Speedhack",
            f"Speedhack set to {speed:.1f}x\n\n"
            "Note: Speedhack requires advanced implementation\n"
            "and may not work on all games."
        )
    
    def start_freeze_thread(self):
        """Start thread to maintain frozen values"""
        def freeze_loop():
            while True:
                if self.pm and self.frozen_addresses:
                    for address, value in self.frozen_addresses.items():
                        try:
                            # Write frozen value to memory
                            # In real implementation:
                            # self.pm.write_int(int(address, 16), int(value))
                            pass
                        except:
                            pass
                time.sleep(0.1)  # Update every 100ms
        
        threading.Thread(target=freeze_loop, daemon=True).start()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Show disclaimer
    root = ctk.CTk()
    root.withdraw()
    
    disclaimer = """
    ⚠️ GAME TRAINER PRO - DISCLAIMER ⚠️
    
    This tool is for EDUCATIONAL and SINGLE-PLAYER use only!
    
    ✅ Allowed:
    • Single-player games
    • Games you own
    • Testing and learning
    
    ❌ NEVER use for:
    • Online/multiplayer games (you WILL be banned)
    • Competitive gaming
    • Violating terms of service
    
    By clicking OK, you agree to use this tool responsibly
    and only for legitimate purposes.
    
    Continue?
    """
    
    response = messagebox.askyesno("Disclaimer", disclaimer)
    root.destroy()
    
    if response:
        app = GameTrainerPro()
        app.run()
    else:
        print("User declined disclaimer")