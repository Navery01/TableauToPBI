import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import json
from datetime import datetime

class TableauToPBIDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tableau to Power BI Converter Dashboard")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.input_files = []
        self.output_directory = tk.StringVar(value="./data/output")
        self.conversion_progress = tk.DoubleVar()
        self.current_file = tk.StringVar()
        
        self.setup_styles()
        self.create_dashboard()
        
    def setup_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
    def create_dashboard(self):
        """Create the main dashboard layout"""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_container, text="Tableau to Power BI Converter", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Controls
        self.create_control_panel(main_container)
        
        # Right panel - Monitor and logs
        self.create_monitor_panel(main_container)
        
        # Bottom panel - Progress and status
        self.create_status_panel(main_container)
        
    def create_control_panel(self, parent):
        """Create the left control panel"""
        control_frame = ttk.LabelFrame(parent, text="Conversion Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # File Selection Section
        file_section = ttk.LabelFrame(control_frame, text="File Selection", padding="10")
        file_section.pack(fill="x", pady=(0, 10))
        
        # Input files listbox with scrollbar
        ttk.Label(file_section, text="Tableau Files:", style='Header.TLabel').pack(anchor="w")
        
        listbox_frame = ttk.Frame(file_section)
        listbox_frame.pack(fill="both", expand=True, pady=5)
        
        self.files_listbox = tk.Listbox(listbox_frame, height=6)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # File buttons
        file_buttons = ttk.Frame(file_section)
        file_buttons.pack(fill="x", pady=5)
        
        ttk.Button(file_buttons, text="Add Files", command=self.add_files).pack(side="left", padx=2)
        ttk.Button(file_buttons, text="Add Folder", command=self.add_folder).pack(side="left", padx=2)
        ttk.Button(file_buttons, text="Remove", command=self.remove_selected).pack(side="left", padx=2)
        ttk.Button(file_buttons, text="Clear All", command=self.clear_files).pack(side="left", padx=2)
        
        # Output directory
        output_section = ttk.LabelFrame(control_frame, text="Output Settings", padding="10")
        output_section.pack(fill="x", pady=(0, 10))
        
        ttk.Label(output_section, text="Output Directory:", style='Header.TLabel').pack(anchor="w")
        
        output_frame = ttk.Frame(output_section)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_directory).pack(side="left", fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="right", padx=(5, 0))
        
        # Conversion Options
        options_section = ttk.LabelFrame(control_frame, text="Conversion Options", padding="10")
        options_section.pack(fill="x", pady=(0, 10))
        
        self.preserve_formatting = tk.BooleanVar(value=True)
        self.include_data_sources = tk.BooleanVar(value=True)
        self.convert_calculated_fields = tk.BooleanVar(value=True)
        self.create_backup = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_section, text="Preserve Formatting", 
                       variable=self.preserve_formatting).pack(anchor="w")
        ttk.Checkbutton(options_section, text="Include Data Sources", 
                       variable=self.include_data_sources).pack(anchor="w")
        ttk.Checkbutton(options_section, text="Convert Calculated Fields", 
                       variable=self.convert_calculated_fields).pack(anchor="w")
        ttk.Checkbutton(options_section, text="Create Backup", 
                       variable=self.create_backup).pack(anchor="w")
        
        # Advanced Options (Collapsible)
        self.advanced_visible = tk.BooleanVar()
        ttk.Checkbutton(options_section, text="Show Advanced Options", 
                       variable=self.advanced_visible, 
                       command=self.toggle_advanced).pack(anchor="w", pady=(10, 0))
        
        self.advanced_frame = ttk.Frame(options_section)
        
        self.max_file_size = tk.StringVar(value="100")
        self.output_format = tk.StringVar(value="PBIX")
        
        ttk.Label(self.advanced_frame, text="Max File Size (MB):").pack(anchor="w")
        ttk.Entry(self.advanced_frame, textvariable=self.max_file_size, width=10).pack(anchor="w", pady=2)
        
        ttk.Label(self.advanced_frame, text="Output Format:").pack(anchor="w", pady=(5, 0))
        format_combo = ttk.Combobox(self.advanced_frame, textvariable=self.output_format, 
                                   values=["PBIX", "JSON", "Both"], state="readonly", width=15)
        format_combo.pack(anchor="w", pady=2)
        
        # Action Buttons
        action_section = ttk.Frame(control_frame)
        action_section.pack(fill="x", pady=(10, 0))
        
        self.convert_button = ttk.Button(action_section, text="Start Conversion", 
                                        command=self.start_conversion, style='Accent.TButton')
        self.convert_button.pack(fill="x", pady=2)
        
        self.stop_button = ttk.Button(action_section, text="Stop Conversion", 
                                     command=self.stop_conversion, state="disabled")
        self.stop_button.pack(fill="x", pady=2)
        
    def create_monitor_panel(self, parent):
        """Create the right monitoring panel"""
        monitor_frame = ttk.LabelFrame(parent, text="Conversion Monitor", padding="10")
        monitor_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        monitor_frame.columnconfigure(0, weight=1)
        monitor_frame.rowconfigure(1, weight=1)
        
        # Statistics Section
        stats_frame = ttk.LabelFrame(monitor_frame, text="Statistics", padding="10")
        stats_frame.pack(fill="x", pady=(0, 10))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x")
        
        # Create statistics labels
        self.stats_labels = {}
        stats = [
            ("Files Queued:", "0"), ("Files Processed:", "0"), 
            ("Files Failed:", "0"), ("Success Rate:", "0%"),
            ("Total Time:", "00:00:00"), ("Avg Time/File:", "00:00:00")
        ]
        
        for i, (label, value) in enumerate(stats):
            row, col = i // 2, (i % 2) * 2
            ttk.Label(stats_grid, text=label, style='Header.TLabel').grid(row=row, column=col, sticky="w", padx=5)
            self.stats_labels[label] = ttk.Label(stats_grid, text=value)
            self.stats_labels[label].grid(row=row, column=col+1, sticky="w", padx=5)
        
        # Real-time Log Section
        log_frame = ttk.LabelFrame(monitor_frame, text="Conversion Log", padding="10")
        log_frame.pack(fill="both", expand=True)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side="left")
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side="left", padx=5)
        
        self.auto_scroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Auto-scroll", variable=self.auto_scroll).pack(side="right")
        
    def create_status_panel(self, parent):
        """Create the bottom status panel"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Current file being processed
        ttk.Label(status_frame, text="Current File:", style='Header.TLabel').grid(row=0, column=0, sticky="w")
        current_file_label = ttk.Label(status_frame, textvariable=self.current_file, 
                                      foreground="blue")
        current_file_label.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Progress bar
        ttk.Label(status_frame, text="Progress:", style='Header.TLabel').grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        progress_frame = ttk.Frame(status_frame)
        progress_frame.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.conversion_progress, 
                                           maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1, padx=(5, 0))
        
    def add_files(self):
        """Add individual files"""
        files = filedialog.askopenfilenames(
            title="Select Tableau Files",
            filetypes=[("Tableau Files", "*.twb *.twbx"), ("All Files", "*.*")]
        )
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.files_listbox.insert(tk.END, Path(file).name)
        self.update_stats()
        
    def add_folder(self):
        """Add all Tableau files from a folder"""
        folder = filedialog.askdirectory(title="Select Folder with Tableau Files")
        if folder:
            folder_path = Path(folder)
            tableau_files = list(folder_path.glob("*.twb")) + list(folder_path.glob("*.twbx"))
            for file in tableau_files:
                if str(file) not in self.input_files:
                    self.input_files.append(str(file))
                    self.files_listbox.insert(tk.END, file.name)
        self.update_stats()
        
    def remove_selected(self):
        """Remove selected files from the list"""
        selection = self.files_listbox.curselection()
        for index in reversed(selection):
            self.files_listbox.delete(index)
            del self.input_files[index]
        self.update_stats()
        
    def clear_files(self):
        """Clear all files"""
        self.files_listbox.delete(0, tk.END)
        self.input_files.clear()
        self.update_stats()
        
    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
            
    def toggle_advanced(self):
        """Toggle advanced options visibility"""
        if self.advanced_visible.get():
            self.advanced_frame.pack(fill="x", pady=(5, 0))
        else:
            self.advanced_frame.pack_forget()
            
    def start_conversion(self):
        """Start the conversion process"""
        if not self.input_files:
            messagebox.showwarning("Warning", "Please add files to convert")
            return
            
        self.convert_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start conversion in separate thread
        self.conversion_thread = threading.Thread(target=self.run_conversion)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
        
    def run_conversion(self):
        """Run the actual conversion process"""
        try:
            total_files = len(self.input_files)
            self.log_message(f"Starting conversion of {total_files} files...")
            
            for i, file_path in enumerate(self.input_files):
                self.current_file.set(Path(file_path).name)
                self.log_message(f"Processing: {Path(file_path).name}")
                
                # Simulate conversion process
                import time
                time.sleep(2)  # Replace with actual conversion logic
                
                # Update progress
                progress = ((i + 1) / total_files) * 100
                self.conversion_progress.set(progress)
                self.progress_label.config(text=f"{progress:.0f}%")
                
                self.log_message(f"✓ Completed: {Path(file_path).name}", "success")
                
            self.log_message("All conversions completed successfully!", "success")
            
        except Exception as e:
            self.log_message(f"Error during conversion: {str(e)}", "error")
        finally:
            self.convert_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.current_file.set("")
            
    def stop_conversion(self):
        """Stop the conversion process"""
        # Implementation for stopping conversion
        self.log_message("Conversion stopped by user", "warning")
        self.convert_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
    def log_message(self, message, level="info"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {"info": "black", "success": "green", "warning": "orange", "error": "red"}
        color = colors.get(level, "black")
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Apply color to the last line
        line_start = self.log_text.index("end-2c linestart")
        line_end = self.log_text.index("end-2c lineend")
        self.log_text.tag_add(level, line_start, line_end)
        self.log_text.tag_config(level, foreground=color)
        
        self.log_text.config(state="disabled")
        
        if self.auto_scroll.get():
            self.log_text.see(tk.END)
            
    def clear_log(self):
        """Clear the log"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        
    def save_log(self):
        """Save log to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Log File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log_message(f"Log saved to: {file_path}")
            
    def update_stats(self):
        """Update statistics display"""
        self.stats_labels["Files Queued:"].config(text=str(len(self.input_files)))
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = TableauToPBIDashboard()
    app.run()

if __name__ == "__main__":
    main()
    