#!/usr/bin/env python3
"""
Motorola 6800 Assembler with Interactive Interface
System Programming Course - Final Project
Author: [Student Name]
Date: Spring 2024-2025

Main application entry point with Tkinter GUI interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import logging
from datetime import datetime
from m6800_assembler import M6800Assembler
from simulator import M6800Simulator

class AssemblerGUI:
    def __init__(self, root):
        self.setup_logging()
        self.debug_print("🚀 DEBUG: AssemblerGUI.__init__() called")
        self.root = root
        self.root.title("Motorola 6800 Assembler - Interactive Interface")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure style for better Windows appearance
        style = ttk.Style()
        style.theme_use('clam')  # Modern looking theme
        
        # Initialize assembler and simulator
        self.debug_print("🚀 DEBUG: Initializing assembler and simulator")
        self.assembler = M6800Assembler()
        self.simulator = M6800Simulator()
        
        self.setup_gui()
        self.current_file = None
        self.debug_print("🚀 DEBUG: GUI initialization completed")
        
    def setup_logging(self):
        """Set up logging to save debug output to timestamped files."""
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Generate timestamped log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"logs/gui_debug_{timestamp}.log"
        
        # Set up logger
        self.logger = logging.getLogger('AssemblerGUI')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_filename, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Log startup
        self.debug_print("🚀 M6800 Assembler GUI Debug Log Started")
        self.debug_print(f"📁 Log file: {self.log_filename}")
        
    def debug_print(self, message: str):
        """Print debug message and log to file."""
        print(message)  # Console output
        self.logger.debug(message)  # File output
        
    def get_log_files(self):
        """Get paths to all log files."""
        log_files = {
            'gui': self.log_filename,
            'simulator': getattr(self.simulator, 'log_filename', None)
        }
        return log_files
        
    def create_combined_log(self):
        """Create a combined log file with all debug information."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            combined_filename = f"logs/combined_session_{timestamp}.log"
            
            with open(combined_filename, 'w', encoding='utf-8') as combined_file:
                combined_file.write("=" * 80 + "\n")
                combined_file.write("M6800 ASSEMBLER & SIMULATOR - COMBINED DEBUG LOG\n")
                combined_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                combined_file.write("=" * 80 + "\n\n")
                
                # Add GUI log
                if os.path.exists(self.log_filename):
                    combined_file.write("GUI DEBUG LOG:\n")
                    combined_file.write("-" * 40 + "\n")
                    with open(self.log_filename, 'r', encoding='utf-8') as gui_log:
                        combined_file.write(gui_log.read())
                    combined_file.write("\n\n")
                
                # Add simulator log
                sim_log_file = getattr(self.simulator, 'log_filename', None)
                if sim_log_file and os.path.exists(sim_log_file):
                    combined_file.write("SIMULATOR DEBUG LOG:\n")
                    combined_file.write("-" * 40 + "\n")
                    with open(sim_log_file, 'r', encoding='utf-8') as sim_log:
                        combined_file.write(sim_log.read())
                    combined_file.write("\n\n")
                
                combined_file.write("=" * 80 + "\n")
                combined_file.write("END OF COMBINED LOG\n")
                combined_file.write("=" * 80 + "\n")
            
            self.debug_print(f"📋 DEBUG: Combined log created: {combined_filename}")
            return combined_filename
            
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Failed to create combined log: {e}")
            return None
        
    def setup_gui(self):
        """Set up the main GUI layout."""
        # Create main menu
        self.create_menu()
        
        # Create status bar first (before panels that might use it)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Load or write assembly code to begin")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create main frame with paned window for resizable sections
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create paned window for left/right split
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for assembly code input
        left_frame = ttk.LabelFrame(paned_window, text="Assembly Code Input", padding=5)
        paned_window.add(left_frame, weight=1)
        
        # Right panel for output and mapping
        right_frame = ttk.LabelFrame(paned_window, text="Assembly Output & Analysis", padding=5)
        paned_window.add(right_frame, weight=1)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Assemble menu
        assemble_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Assemble", menu=assemble_menu)
        assemble_menu.add_command(label="Assemble Code", command=self.assemble_code, accelerator="F5")
        assemble_menu.add_command(label="Clear Output", command=self.clear_output)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Instruction Set Reference", command=self.show_instruction_set)
        tools_menu.add_command(label="Memory Viewer", command=self.show_memory_viewer)
        
        # Debug menu
        debug_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Debug", menu=debug_menu)
        debug_menu.add_command(label="View Log Files", command=self.show_log_files)
        debug_menu.add_command(label="Create Combined Log", command=self.create_and_show_combined_log)
        debug_menu.add_command(label="Open Logs Folder", command=self.open_logs_folder)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.assemble_code())
        
    def setup_left_panel(self, parent):
        """Set up the left panel with assembly code input."""
        # Assembly code input area with line numbers
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with line numbers
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Assembly code text area
        self.assembly_text = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, 
                                                      font=('Consolas', 11))
        self.assembly_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events for line numbering
        self.assembly_text.bind('<Any-KeyPress>', self.update_line_numbers)
        self.assembly_text.bind('<Button-1>', self.update_line_numbers)
        self.assembly_text.bind('<MouseWheel>', self.update_line_numbers)
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="Load Example", 
                  command=self.load_example).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Assemble (F5)", 
                  command=self.assemble_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_input).pack(side=tk.LEFT)
        
        # Add some example code initially
        self.load_example()
        
    def setup_right_panel(self, parent):
        """Set up the right panel with output and analysis."""
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Object Code tab
        object_frame = ttk.Frame(notebook)
        notebook.add(object_frame, text="Object Code")
        
        self.object_text = scrolledtext.ScrolledText(object_frame, wrap=tk.NONE,
                                                    font=('Consolas', 10), state='disabled')
        self.object_text.pack(fill=tk.BOTH, expand=True)
        
        # Line-by-Line Mapping tab
        mapping_frame = ttk.Frame(notebook)
        notebook.add(mapping_frame, text="Assembly-Object Mapping")
        
        # Treeview for mapping display
        columns = ('Line', 'Address', 'Object Code', 'Assembly Instruction')
        self.mapping_tree = ttk.Treeview(mapping_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.mapping_tree.heading(col, text=col)
            
        # Configure column widths
        self.mapping_tree.column('Line', width=50)
        self.mapping_tree.column('Address', width=80)
        self.mapping_tree.column('Object Code', width=120)
        self.mapping_tree.column('Assembly Instruction', width=250)
        
        # Add scrollbar to treeview
        mapping_scrollbar = ttk.Scrollbar(mapping_frame, orient=tk.VERTICAL, command=self.mapping_tree.yview)
        self.mapping_tree.configure(yscrollcommand=mapping_scrollbar.set)
        
        self.mapping_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mapping_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Simulator tab
        sim_frame = ttk.Frame(notebook)
        notebook.add(sim_frame, text="Execution Simulator")
        
        self.setup_simulator_panel(sim_frame)
        
        # Errors/Messages tab
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text="Messages")
        
        self.error_text = scrolledtext.ScrolledText(error_frame, wrap=tk.WORD,
                                                   font=('Consolas', 9), state='disabled')
        self.error_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_simulator_panel(self, parent):
        """Set up the execution simulator panel."""
        # Create frames for registers and memory
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Registers frame
        reg_frame = ttk.LabelFrame(top_frame, text="Registers", padding=5)
        reg_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Register labels
        tk.Label(reg_frame, text="Registers:", font=('Consolas', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w')
        tk.Label(reg_frame, text="A:", font=('Consolas', 9)).grid(row=1, column=0, sticky='w')
        tk.Label(reg_frame, text="B:", font=('Consolas', 9)).grid(row=2, column=0, sticky='w')
        tk.Label(reg_frame, text="X:", font=('Consolas', 9)).grid(row=3, column=0, sticky='w')
        tk.Label(reg_frame, text="Y:", font=('Consolas', 9)).grid(row=4, column=0, sticky='w')
        tk.Label(reg_frame, text="SP:", font=('Consolas', 9)).grid(row=5, column=0, sticky='w')
        tk.Label(reg_frame, text="PC:", font=('Consolas', 9)).grid(row=6, column=0, sticky='w')
        tk.Label(reg_frame, text="CC:", font=('Consolas', 9)).grid(row=7, column=0, sticky='w')
        
        # Register value displays
        self.reg_a_label = tk.Label(reg_frame, text="00", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_a_label.grid(row=1, column=1, sticky='w', padx=(5,0))
        
        self.reg_b_label = tk.Label(reg_frame, text="00", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_b_label.grid(row=2, column=1, sticky='w', padx=(5,0))
        
        self.reg_x_label = tk.Label(reg_frame, text="0000", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_x_label.grid(row=3, column=1, sticky='w', padx=(5,0))
        
        self.reg_y_label = tk.Label(reg_frame, text="0000", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_y_label.grid(row=4, column=1, sticky='w', padx=(5,0))
        
        self.reg_sp_label = tk.Label(reg_frame, text="01FF", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_sp_label.grid(row=5, column=1, sticky='w', padx=(5,0))
        
        self.reg_pc_label = tk.Label(reg_frame, text="0000", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_pc_label.grid(row=6, column=1, sticky='w', padx=(5,0))
        
        self.reg_cc_label = tk.Label(reg_frame, text="00", font=('Consolas', 9), bg='white', relief='sunken', width=8)
        self.reg_cc_label.grid(row=7, column=1, sticky='w', padx=(5,0))
        
        # Memory frame
        mem_frame = ttk.LabelFrame(top_frame, text="Memory View", padding=5)
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.memory_text = scrolledtext.ScrolledText(mem_frame, wrap=tk.NONE,
                                                    font=('Consolas', 9), height=8, state='disabled')
        self.memory_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons for simulator
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Load Program", 
                  command=self.load_program).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Reset", 
                  command=self.reset_simulator).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Step", 
                  command=self.step_execution).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Run", 
                  command=self.run_simulation).pack(side=tk.LEFT)
        
    # File operations
    def new_file(self):
        """Create a new file."""
        if self.assembly_text.edit_modified():
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Continue?"):
                return
        
        self.assembly_text.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Motorola 6800 Assembler - New File")
        self.status_var.set("New file created")
        
    def open_file(self):
        """Open an assembly file."""
        filename = filedialog.askopenfilename(
            title="Open Assembly File",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as file:
                    content = file.read()
                
                self.assembly_text.delete(1.0, tk.END)
                self.assembly_text.insert(1.0, content)
                self.current_file = filename
                self.root.title(f"Motorola 6800 Assembler - {os.path.basename(filename)}")
                self.status_var.set(f"Loaded: {filename}")
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
                
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.assembly_text.get(1.0, tk.END))
                self.assembly_text.edit_modified(False)
                self.status_var.set(f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save the file with a new name."""
        filename = filedialog.asksaveasfilename(
            title="Save Assembly File",
            defaultextension=".asm",
            filetypes=[("Assembly files", "*.asm"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as file:
                    file.write(self.assembly_text.get(1.0, tk.END))
                self.current_file = filename
                self.root.title(f"Motorola 6800 Assembler - {os.path.basename(filename)}")
                self.assembly_text.edit_modified(False)
                self.status_var.set(f"Saved as: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def load_example(self):
        """Load an example assembly program."""
        self.debug_print("📝 DEBUG: load_example() called")
        example_code = """; Motorola 6800 Assembly Example
; Simple program to demonstrate assembler features

        ORG     $1000    ; Set origin address
        
START:  LDA     #$55     ; Load accumulator A with immediate value
        STA     $2000    ; Store A at memory location $2000
        LDB     #$AA     ; Load accumulator B with immediate value
        STB     $2001    ; Store B at memory location $2001
        
        LDX     #$2000   ; Load index register with address
        LDA     0,X      ; Load A with value at address in X
        CMP A   #$55     ; Compare A with immediate value
        BEQ     SUCCESS  ; Branch if equal to SUCCESS
        
        JMP     ERROR    ; Jump to ERROR if not equal
        
SUCCESS: LDA    #$01     ; Load success code
        STA     $3000    ; Store success code
        JMP     FINISH   ; Jump to end
        
ERROR:  LDA     #$FF     ; Load error code
        STA     $3000    ; Store error code
        
FINISH: NOP              ; No operation
        
        END              ; End of program"""
        
        self.assembly_text.delete(1.0, tk.END)
        self.assembly_text.insert(1.0, example_code)
        self.update_line_numbers()
        self.status_var.set("Example code loaded")
        self.debug_print("📝 DEBUG: Example code loaded successfully")
    
    def clear_input(self):
        """Clear the input text area."""
        self.debug_print("🗑️ DEBUG: clear_input() called")
        self.assembly_text.delete(1.0, tk.END)
        self.update_line_numbers()
        self.debug_print("🗑️ DEBUG: Input cleared")
        
    def clear_output(self):
        """Clear all output areas."""
        self.debug_print("🗑️ DEBUG: clear_output() called")
        self.object_text.config(state='normal')
        self.object_text.delete(1.0, tk.END)
        self.object_text.config(state='disabled')
        
        for item in self.mapping_tree.get_children():
            self.mapping_tree.delete(item)
            
        self.error_text.config(state='normal')
        self.error_text.delete(1.0, tk.END)
        self.error_text.config(state='disabled')
        
        self.status_var.set("Output cleared")
        self.debug_print("🗑️ DEBUG: Output cleared successfully")
    
    def update_line_numbers(self, event=None):
        """Update line numbers in the text widget."""
        self.root.after_idle(self._update_line_numbers)
        
    def _update_line_numbers(self):
        """Internal method to update line numbers."""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        
        line_count = int(self.assembly_text.index('end-1c').split('.')[0])
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count))
        
        self.line_numbers.insert(1.0, line_numbers_text)
        self.line_numbers.config(state='disabled')
    
    def assemble_code(self):
        """Assemble the current code."""
        self.debug_print("🔨 DEBUG: assemble_code() called")
        try:
            assembly_code = self.assembly_text.get(1.0, tk.END)
            self.debug_print(f"🔨 DEBUG: Assembly code length: {len(assembly_code.strip())} chars")
            
            # Clear previous output
            self.clear_output()
            
            # Perform assembly
            result = self.assembler.assemble(assembly_code)
            self.debug_print(f"🔨 DEBUG: Assembly completed, success: {result['success']}")
            
            if result['success']:
                self.debug_print(f"🔨 DEBUG: Assembly successful, {len(result.get('mappings', []))} mappings generated")
                
                # Display object code
                self.object_text.config(state='normal')
                self.object_text.insert(tk.END, result['object_code'])
                self.object_text.config(state='disabled')
                
                # Display line-by-line mapping
                for mapping in result['mappings']:
                    self.mapping_tree.insert('', tk.END, values=(
                        mapping['line'],
                        mapping['address'],
                        mapping['object_code'],
                        mapping['assembly']
                    ))
                
                # Display messages
                if result['messages']:
                    self.error_text.config(state='normal')
                    for msg in result['messages']:
                        self.error_text.insert(tk.END, f"{msg}\n")
                    self.error_text.config(state='disabled')
                
                self.status_var.set(f"Assembly successful - {len(result['mappings'])} instructions processed")
                self.debug_print("🔨 DEBUG: Assembly output displayed successfully")
                
            else:
                self.debug_print(f"🔨 DEBUG: Assembly failed with {len(result.get('errors', []))} errors")
                
                # Display errors
                self.error_text.config(state='normal')
                for error in result['errors']:
                    self.error_text.insert(tk.END, f"ERROR: {error}\n")
                    self.debug_print(f"🔨 DEBUG: Assembly error: {error}")
                self.error_text.config(state='disabled')
                
                self.status_var.set("Assembly failed - check errors tab")
                
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in assemble_code(): {e}")
            messagebox.showerror("Assembly Error", f"An error occurred during assembly: {str(e)}")
            self.status_var.set("Assembly error occurred")
    
    # Simulator methods
    def load_program(self):
        """Load the assembled program into the simulator."""
        self.debug_print("🔧 DEBUG: load_program() called")
        try:
            assembly_code = self.assembly_text.get(1.0, tk.END)
            self.debug_print(f"🔧 DEBUG: Got assembly code, length: {len(assembly_code.strip())} chars")
            result = self.assembler.assemble(assembly_code)
            self.debug_print(f"🔧 DEBUG: Assembly result success: {result['success']}")
            
            if result['success']:
                self.debug_print(f"🔧 DEBUG: Loading {len(result['object_data'])} bytes into simulator")
                self.simulator.load_program(result['object_data'])
                self.update_simulator_display()
                self.status_var.set("Program loaded into simulator")
                self.debug_print("🔧 DEBUG: Program loaded successfully")
            else:
                self.debug_print(f"🔧 DEBUG: Assembly failed with errors: {result.get('errors', [])}")
                messagebox.showerror("Load Error", "Please assemble the code successfully first")
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in load_program(): {e}")
            messagebox.showerror("Load Error", f"Could not load program: {str(e)}")
    
    def reset_simulator(self):
        """Reset the simulator state."""
        self.debug_print("🔄 DEBUG: reset_simulator() called")
        try:
            self.debug_print("🔄 DEBUG: Calling simulator.reset()")
            self.simulator.reset()
            self.debug_print("🔄 DEBUG: Reset completed, attempting auto-reload")
            
            # Auto-reload the program after reset if assembly was successful
            assembly_code = self.assembly_text.get(1.0, tk.END)
            result = self.assembler.assemble(assembly_code)
            self.debug_print(f"🔄 DEBUG: Assembly for reload - success: {result['success']}")
            
            if result['success']:
                self.debug_print("🔄 DEBUG: Reloading program after reset")
                self.simulator.load_program(result['object_data'])
            
            self.update_simulator_display()
            self.status_var.set("Simulator reset and program reloaded")
            self.debug_print("🔄 DEBUG: Reset and reload completed successfully")
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in reset_simulator(): {e}")
            messagebox.showerror("Reset Error", f"Could not reset simulator: {str(e)}")
    
    def step_execution(self):
        """Execute one instruction in the simulator."""
        self.debug_print("👟 DEBUG: step_execution() called")
        try:
            # Check if a program is loaded
            if not hasattr(self.simulator, 'program_data') or not self.simulator.program_data:
                self.debug_print("⚠️ DEBUG: No program loaded, showing warning")
                messagebox.showwarning("No Program", "Please load a program first using 'Load Program' button")
                return
                
            self.debug_print(f"👟 DEBUG: Program loaded, checking halt state: {self.simulator.is_halted()}")
            
            # Check if execution is already halted
            if self.simulator.is_halted():
                self.debug_print("⚠️ DEBUG: Execution already halted, showing info")
                messagebox.showinfo("Execution Complete", "Program execution has completed. Use Reset to restart.")
                return
            
            pc_before = self.simulator.get_register_value('PC')
            self.debug_print(f"👟 DEBUG: Executing step, PC before: ${pc_before:04X}")
            
            success = self.simulator.step()
            pc_after = self.simulator.get_register_value('PC')
            
            self.debug_print(f"👟 DEBUG: Step result: {success}, PC after: ${pc_after:04X}")
            
            self.update_simulator_display()
            
            if success:
                self.status_var.set(f"Executed one instruction - PC=${self.simulator.get_register_value('PC'):04X}")
                self.debug_print("👟 DEBUG: Step executed successfully")
            else:
                self.status_var.set("Execution halted")
                self.debug_print("👟 DEBUG: Step failed - execution halted")
                if self.simulator.is_halted():
                    messagebox.showinfo("Execution Complete", "Program execution has completed.")
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in step_execution(): {e}")
            messagebox.showerror("Execution Error", f"Could not execute instruction: {str(e)}")
    
    def run_simulation(self):
        """Run the simulation until completion or breakpoint."""
        self.debug_print("🏃 DEBUG: run_simulation() called")
        try:
            # Check if a program is loaded
            if not hasattr(self.simulator, 'program_data') or not self.simulator.program_data:
                self.debug_print("⚠️ DEBUG: No program loaded for run, showing warning")
                messagebox.showwarning("No Program", "Please load a program first using 'Load Program' button")
                return
                
            self.debug_print(f"🏃 DEBUG: Program loaded, checking halt state: {self.simulator.is_halted()}")
            
            # Check if execution is already halted
            if self.simulator.is_halted():
                self.debug_print("⚠️ DEBUG: Already halted for run, showing info")
                messagebox.showinfo("Execution Complete", "Program execution has completed. Use Reset to restart.")
                return
            
            pc_before = self.simulator.get_register_value('PC')
            self.debug_print(f"🏃 DEBUG: Starting run, PC before: ${pc_before:04X}")
            
            steps = self.simulator.run()
            pc_after = self.simulator.get_register_value('PC')
            
            self.debug_print(f"🏃 DEBUG: Run completed, {steps} steps executed, PC after: ${pc_after:04X}")
            
            self.update_simulator_display()
            
            if steps > 0:
                self.status_var.set(f"Simulation completed - {steps} instructions executed")
                self.debug_print(f"🏃 DEBUG: Run successful, showing completion dialog")
                messagebox.showinfo("Simulation Complete", f"Executed {steps} instructions.\nProgram execution completed.")
            else:
                self.debug_print("🏃 DEBUG: No instructions executed during run")
                self.status_var.set("No instructions executed")
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in run_simulation(): {e}")
            messagebox.showerror("Simulation Error", f"Simulation error: {str(e)}")
    
    def update_simulator_display(self):
        """Update the simulator display with current state."""
        self.debug_print("📺 DEBUG: update_simulator_display() called")
        try:
            # Update registers using the existing register display method
            self.update_register_display()
            
            # Update memory view
            self.memory_text.config(state='normal')
            self.memory_text.delete(1.0, tk.END)
            
            memory_dump = self.simulator.get_memory_dump()
            self.memory_text.insert(tk.END, memory_dump)
            self.memory_text.config(state='disabled')
            self.debug_print("📺 DEBUG: Simulator display updated successfully")
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in update_simulator_display(): {e}")
    
    # Help and utility methods
    def show_instruction_set(self):
        """Show the instruction set reference."""
        instruction_window = tk.Toplevel(self.root)
        instruction_window.title("Motorola 6800 Instruction Set Reference")
        instruction_window.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(instruction_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load instruction set reference
        reference_text = self.assembler.get_instruction_reference()
        text_widget.insert(tk.END, reference_text)
        text_widget.config(state='disabled')
    
    def show_memory_viewer(self):
        """Show a detailed memory viewer window."""
        memory_window = tk.Toplevel(self.root)
        memory_window.title("Memory Viewer")
        memory_window.geometry("600x400")
        
        # Memory viewer implementation would go here
        ttk.Label(memory_window, text="Detailed Memory Viewer\n(Feature can be expanded)",
                 font=('Arial', 12)).pack(expand=True)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """Motorola 6800 Assembler
Interactive Assembly Environment

System Programming Course
Final Project - Spring 2024-2025

Features:
• Complete M6800 assembly language support
• Real-time syntax checking
• Object code generation
• Line-by-line assembly mapping
• Execution simulator with step/run modes
• Memory viewer and register monitoring

Author: [Student Name]
"""
        messagebox.showinfo("About M6800 Assembler", about_text)
        
    def show_log_files(self):
        """Show information about current log files."""
        log_files = self.get_log_files()
        
        info_text = "Current Debug Log Files:\n\n"
        info_text += f"GUI Log: {log_files['gui']}\n"
        if log_files['simulator']:
            info_text += f"Simulator Log: {log_files['simulator']}\n"
        else:
            info_text += "Simulator Log: Not created yet\n"
        
        info_text += f"\nLogs are automatically created in the 'logs' folder.\n"
        info_text += "Use 'Create Combined Log' to merge all logs into one file for analysis."
        
        messagebox.showinfo("Debug Log Files", info_text)
        
    def create_and_show_combined_log(self):
        """Create combined log and show path."""
        combined_file = self.create_combined_log()
        if combined_file:
            messagebox.showinfo("Combined Log Created", 
                              f"Combined debug log created:\n{combined_file}\n\n"
                              "This file contains all GUI and simulator debug information "
                              "for the current session.")
        else:
            messagebox.showerror("Error", "Failed to create combined log file.")
            
    def open_logs_folder(self):
        """Open the logs folder in file explorer."""
        try:
            if os.path.exists('logs'):
                if sys.platform == 'win32':
                    os.startfile('logs')
                elif sys.platform == 'darwin':  # macOS
                    os.system('open logs')
                else:  # Linux
                    os.system('xdg-open logs')
            else:
                messagebox.showinfo("Logs Folder", "Logs folder doesn't exist yet. Run some operations to generate logs.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open logs folder: {str(e)}")

    def update_register_display(self):
        """Update the register display with current simulator values."""
        self.debug_print("🖥️ DEBUG: update_register_display() called")
        
        try:
            registers = self.simulator.registers
            
            # Update register labels
            self.reg_a_label.config(text=f"{registers['A']:02X}")
            self.reg_b_label.config(text=f"{registers['B']:02X}")
            self.reg_x_label.config(text=f"{registers['X']:04X}")
            self.reg_y_label.config(text=f"{registers['Y']:04X}")
            self.reg_sp_label.config(text=f"{registers['SP']:04X}")
            self.reg_pc_label.config(text=f"{registers['PC']:04X}")
            self.reg_cc_label.config(text=f"{registers['CC']:02X}")
            
            self.debug_print(f"🖥️ DEBUG: Registers updated - A:{registers['A']:02X} B:{registers['B']:02X} X:{registers['X']:04X} Y:{registers['Y']:04X} SP:{registers['SP']:04X} PC:{registers['PC']:04X} CC:{registers['CC']:02X}")
            
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Error updating register display: {e}")
            # Set default values in case of error
            self.reg_a_label.config(text="--")
            self.reg_b_label.config(text="--")
            self.reg_x_label.config(text="----")
            self.reg_y_label.config(text="----")
            self.reg_sp_label.config(text="----")
            self.reg_pc_label.config(text="----")
            self.reg_cc_label.config(text="--")

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = AssemblerGUI(root)
    
    # Set application icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass  # Icon file not found, continue without it
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 