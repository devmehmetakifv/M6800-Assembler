#!/usr/bin/env python3
"""
Motorola 6800 Assembler with Interactive Interface
System Programming Course - Final Project
Author: Software Engineering (English) - GROUP 2
Date: Spring 2024-2025

Main application entry point with Tkinter GUI interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import logging
import re
from datetime import datetime
from m6800_assembler import M6800Assembler
from simulator import M6800Simulator

class SyntaxHighlighter:
    """Syntax highlighter for M6800 assembly language."""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()
        
        # Define syntax patterns
        self.define_patterns()
        
    def setup_tags(self):
        """Set up text tags for different syntax elements."""
        # Comments - green
        self.text_widget.tag_config("comment", foreground="#008000", font=('Consolas', 11, 'italic'))
        
        # Instructions/Mnemonics - blue
        self.text_widget.tag_config("instruction", foreground="#0000FF", font=('Consolas', 11, 'bold'))
        
        # Directives - purple
        self.text_widget.tag_config("directive", foreground="#800080", font=('Consolas', 11, 'bold'))
        
        # Labels - dark red
        self.text_widget.tag_config("label", foreground="#800000", font=('Consolas', 11, 'bold'))
        
        # Numbers - orange
        self.text_widget.tag_config("number", foreground="#FF6600")
        
        # Registers - teal
        self.text_widget.tag_config("register", foreground="#008080", font=('Consolas', 11, 'bold'))
        
        # Strings - red
        self.text_widget.tag_config("string", foreground="#FF0000")
        
        # Addresses/Memory references - dark green
        self.text_widget.tag_config("address", foreground="#006400")
        
        # Operators - gray
        self.text_widget.tag_config("operator", foreground="#666666")
        
    def define_patterns(self):
        """Define regex patterns for syntax highlighting."""
        # M6800 instruction set (comprehensive list from assembler)
        instructions = [
            'ABA', 'ADC', 'ADD', 'AND', 'ASL', 'ASR',
            'BCC', 'BCS', 'BEQ', 'BGE', 'BGT', 'BHI', 'BLE', 'BLS', 'BLT', 'BMI', 'BNE', 'BPL', 'BRA', 'BSR', 'BVC', 'BVS',
            'BIT', 'BRK',
            'CBA', 'CLC', 'CLI', 'CLR', 'CLV', 'CMP', 'COM', 'CPX', 'NEG',
            'DAA',
            'DEC', 'DES', 'DEX', 'EOR', 'INC', 'INS', 'INX',
            'JMP', 'JSR',
            'LDA', 'LDB', 'LDX', 'LDS', 'LSR',
            'NOP',
            'ORA', 'ORB',
            'PSH', 'PUL',
            'ROL', 'ROR',
            'RTI', 'RTS',
            'SBA', 'SBC', 'SEC', 'SEI', 'SEV', 'STA', 'STB', 'STX', 'STS', 'SUB',
            'SWI',
            'TAB', 'TAP', 'TBA', 'TPA', 'TST', 'TSX', 'TXS',
            'WAI',
            # M6801/M6811 instructions
            'LSRD', 'ASLD', 'STD', 'LDD', 'ABX', 'MUL', 'PSHX', 'PULX', 'ADDD',
            'IDIV', 'FDIV', 'INY', 'DEY', 'STY', 'LDY', 'CPD', 'CPY', 'ABY', 
            'PSHY', 'PULY', 'XGDX', 'XGDY', 'TSY', 'TYS'
        ]
        
        # Assembler directives
        directives = ['ORG', 'END', 'EQU', 'FCB', 'FCC', 'FDB', 'RMB', 'BSZ', 'INCLUDE']
        
        # Registers
        registers = ['A', 'B', 'X', 'Y', 'SP', 'PC', 'CC', 'D']
        
        # Create patterns
        self.patterns = [
            # Comments (highest priority)
            (r';.*$', 'comment'),
            
            # String literals
            (r'"[^"]*"', 'string'),
            (r"'[^']*'", 'string'),
            
            # Labels (word followed by colon)
            (r'^\s*([A-Za-z_][A-Za-z0-9_]*):(?!:)', 'label'),
            
            # Directives
            (fr'\b(?:{"|".join(directives)})\b', 'directive'),
            
            # Instructions (case insensitive)
            (fr'\b(?:{"|".join(instructions)})\b', 'instruction'),
            
            # Numbers (various formats)
            (r'\$[0-9A-Fa-f]+', 'number'),        # Hexadecimal $XX
            (r'%[01]+', 'number'),               # Binary %XXXX
            (r'\b[0-9]+\b', 'number'),           # Decimal
            (r'0x[0-9A-Fa-f]+', 'number'),        # Hex 0xXX
            
            # Memory addressing and operators
            (r'[,()#+\-]', 'operator'),           # Addressing operators
            (r'\b[0-9]+,X\b', 'address'),        # Indexed addressing
            (r'\b[0-9]+,Y\b', 'address'),        # Indexed addressing with Y
            
            # Registers (standalone)
            (fr'\b(?:{"|".join(registers)})\b', 'register'),
        ]
        
        # Compile regex patterns for better performance
        self.compiled_patterns = [(re.compile(pattern, re.MULTILINE | re.IGNORECASE), tag) 
                                 for pattern, tag in self.patterns]
    
    def highlight_all(self):
        """Apply syntax highlighting to the entire text."""
        # Clear all existing tags
        for tag in ['comment', 'instruction', 'directive', 'label', 'number', 'register', 'string', 'address', 'operator']:
            self.text_widget.tag_remove(tag, '1.0', tk.END)
        
        # Get all text
        content = self.text_widget.get('1.0', tk.END)
        
        # Apply patterns in order (comments first to avoid conflicts)
        for pattern, tag in self.compiled_patterns:
            for match in pattern.finditer(content):
                start_idx = self._get_text_index(content, match.start())
                end_idx = self._get_text_index(content, match.end())
                self.text_widget.tag_add(tag, start_idx, end_idx)
    
    def highlight_line(self, line_num):
        """Apply syntax highlighting to a specific line."""
        # Get line content
        start_idx = f"{line_num}.0"
        end_idx = f"{line_num}.end"
        line_content = self.text_widget.get(start_idx, end_idx)
        
        # Clear existing tags for this line
        for tag in ['comment', 'instruction', 'directive', 'label', 'number', 'register', 'string', 'address', 'operator']:
            self.text_widget.tag_remove(tag, start_idx, end_idx)
        
        # Apply patterns to this line
        for pattern, tag in self.compiled_patterns:
            for match in pattern.finditer(line_content):
                match_start = f"{line_num}.{match.start()}"
                match_end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add(tag, match_start, match_end)
    
    def _get_text_index(self, content, char_index):
        """Convert character index to Tkinter text index (line.column)."""
        lines_before = content[:char_index].count('\n')
        line_start = content.rfind('\n', 0, char_index) + 1
        column = char_index - line_start
        return f"{lines_before + 1}.{column}"

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
        
        # Initialize syntax highlighter
        self.syntax_highlighter = SyntaxHighlighter(self.assembly_text)
        
        # Bind events for line numbering and syntax highlighting
        self.assembly_text.bind('<Any-KeyPress>', self.on_text_change)
        self.assembly_text.bind('<Button-1>', self.update_line_numbers)
        self.assembly_text.bind('<MouseWheel>', self.update_line_numbers)
        self.assembly_text.bind('<KeyRelease>', self.on_key_release)
        self.assembly_text.bind('<FocusOut>', self.on_focus_out)
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="Load Example", 
                  command=self.load_example).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Assemble (F5)", 
                  command=self.assemble_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_input).pack(side=tk.LEFT)
        
        # Add syntax highlighting toggle button
        self.highlight_enabled = tk.BooleanVar(value=True)
        highlight_check = ttk.Checkbutton(button_frame, text="Syntax Highlighting", 
                                        variable=self.highlight_enabled,
                                        command=self.toggle_syntax_highlighting)
        highlight_check.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Add some example code initially
        self.load_example()
        
    def on_text_change(self, event=None):
        """Handle text change events for line numbering."""
        self.update_line_numbers(event)
        
    def on_key_release(self, event=None):
        """Handle key release events for syntax highlighting."""
        if self.highlight_enabled.get():
            # Get the current line number
            cursor_pos = self.assembly_text.index(tk.INSERT)
            line_num = int(cursor_pos.split('.')[0])
            
            # For efficiency, only highlight current line on key release
            # Full highlighting happens on focus out or manual trigger
            self.root.after_idle(lambda: self.syntax_highlighter.highlight_line(line_num))
    
    def on_focus_out(self, event=None):
        """Handle focus out events for full syntax highlighting."""
        if self.highlight_enabled.get():
            self.root.after_idle(self.syntax_highlighter.highlight_all)
    
    def toggle_syntax_highlighting(self):
        """Toggle syntax highlighting on/off."""
        if self.highlight_enabled.get():
            # Enable highlighting
            self.syntax_highlighter.highlight_all()
            self.status_var.set("Syntax highlighting enabled")
        else:
            # Disable highlighting by removing all tags
            for tag in ['comment', 'instruction', 'directive', 'label', 'number', 'register', 'string', 'address', 'operator']:
                self.assembly_text.tag_remove(tag, '1.0', tk.END)
            self.status_var.set("Syntax highlighting disabled")
    
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
                
            self.debug_print(f"👟 DEBUG: Program loaded, checking halt state: {self.simulator.execution_halted}")
            
            # Check if execution is already halted
            if self.simulator.execution_halted:
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
                if self.simulator.execution_halted:
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
                
            self.debug_print(f"🏃 DEBUG: Program loaded, checking halt state: {self.simulator.execution_halted}")
            
            # Check if execution is already halted
            if self.simulator.execution_halted:
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
        memory_window.geometry("800x600")
        memory_window.minsize(600, 400)
        
        # Create main frame
        main_frame = ttk.Frame(memory_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel at top
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Address input
        ttk.Label(control_frame, text="Go to Address:").pack(side=tk.LEFT, padx=(0, 5))
        self.addr_var = tk.StringVar(value="1000")
        addr_entry = ttk.Entry(control_frame, textvariable=self.addr_var, width=8)
        addr_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        def go_to_address():
            try:
                addr_str = self.addr_var.get().strip()
                if addr_str.startswith('$'):
                    addr = int(addr_str[1:], 16)
                elif addr_str.startswith('0x'):
                    addr = int(addr_str, 16)
                else:
                    addr = int(addr_str, 16)
                addr = max(0, min(addr, 0xFFE0))  # Keep within valid range
                self.current_mem_addr = addr
                refresh_memory()
            except ValueError:
                messagebox.showerror("Invalid Address", "Please enter a valid hexadecimal address (e.g., 1000, $1000, or 0x1000)")
        
        ttk.Button(control_frame, text="Go", command=go_to_address).pack(side=tk.LEFT, padx=(0, 10))
        
        # Search functionality
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=10)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        def search_memory():
            try:
                search_str = self.search_var.get().strip()
                if not search_str:
                    return
                
                # Parse search value (hex byte)
                if search_str.startswith('$'):
                    search_val = int(search_str[1:], 16)
                elif search_str.startswith('0x'):
                    search_val = int(search_str, 16)
                else:
                    search_val = int(search_str, 16)
                
                search_val = search_val & 0xFF  # Ensure it's a byte
                
                # Search from current address
                start_addr = getattr(self, 'current_mem_addr', 0x1000)
                for addr in range(start_addr, 0x10000):
                    if self.simulator.get_memory_value(addr) == search_val:
                        self.current_mem_addr = addr & 0xFFF0  # Align to 16-byte boundary
                        self.addr_var.set(f"{self.current_mem_addr:04X}")
                        refresh_memory()
                        return
                
                messagebox.showinfo("Search", f"Value ${search_val:02X} not found from address ${start_addr:04X}")
            except ValueError:
                messagebox.showerror("Invalid Search", "Please enter a valid hexadecimal byte value (e.g., FF, $AA, 0x55)")
        
        ttk.Button(control_frame, text="Search", command=search_memory).pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh", command=lambda: refresh_memory()).pack(side=tk.LEFT)
        
        # Memory display frame
        mem_frame = ttk.Frame(main_frame)
        mem_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(mem_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.mem_text = tk.Text(text_frame, font=('Consolas', 10), wrap=tk.NONE, 
                               bg='#f8f8f8', fg='#000000', selectbackground='#0078d4')
        scrollbar_v = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.mem_text.yview)
        scrollbar_h = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.mem_text.xview)
        
        self.mem_text.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Grid layout for text and scrollbars
        self.mem_text.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.mem_status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.mem_status_var).pack(side=tk.LEFT)
        
        # Memory editing functionality
        def on_double_click(event):
            try:
                # Get cursor position
                cursor_pos = self.mem_text.index(tk.INSERT)
                line_num = int(cursor_pos.split('.')[0]) - 1
                col_num = int(cursor_pos.split('.')[1])
                
                # Calculate memory address based on cursor position
                # Format: "ADDR:   +0 +1 +2 ... +F  ASCII"
                # Each line shows 16 bytes starting at line_addr
                
                if line_num < 0:
                    return
                    
                base_addr = getattr(self, 'current_mem_addr', 0x1000) + (line_num * 16)
                
                # Check if click is in hex area (columns 8-55)
                if 8 <= col_num <= 55:
                    # Calculate which byte was clicked
                    hex_col = col_num - 8
                    byte_index = hex_col // 3  # Each hex byte takes 3 chars (XX )
                    
                    if byte_index < 16:
                        addr = base_addr + byte_index
                        if 0 <= addr <= 0xFFFF:
                            edit_memory_value(addr)
                            
            except Exception as e:
                self.debug_print(f"Error in memory viewer double-click: {e}")
        
        def edit_memory_value(address):
            """Edit a memory value at the given address."""
            current_val = self.simulator.get_memory_value(address)
            
            # Create edit dialog
            edit_dialog = tk.Toplevel(memory_window)
            edit_dialog.title(f"Edit Memory at ${address:04X}")
            edit_dialog.geometry("300x150")
            edit_dialog.resizable(False, False)
            edit_dialog.transient(memory_window)
            edit_dialog.grab_set()
            
            # Center the dialog
            edit_dialog.update_idletasks()
            x = memory_window.winfo_x() + (memory_window.winfo_width() // 2) - (edit_dialog.winfo_width() // 2)
            y = memory_window.winfo_y() + (memory_window.winfo_height() // 2) - (edit_dialog.winfo_height() // 2)
            edit_dialog.geometry(f"+{x}+{y}")
            
            # Dialog content
            ttk.Label(edit_dialog, text=f"Address: ${address:04X}").pack(pady=10)
            ttk.Label(edit_dialog, text=f"Current Value: ${current_val:02X} ({current_val})").pack()
            
            ttk.Label(edit_dialog, text="New Value:").pack(pady=(10, 5))
            new_val_var = tk.StringVar(value=f"{current_val:02X}")
            val_entry = ttk.Entry(edit_dialog, textvariable=new_val_var, width=10)
            val_entry.pack()
            val_entry.select_range(0, tk.END)
            val_entry.focus()
            
            def save_value():
                try:
                    val_str = new_val_var.get().strip()
                    if val_str.startswith('$'):
                        new_val = int(val_str[1:], 16)
                    elif val_str.startswith('0x'):
                        new_val = int(val_str, 16)
                    else:
                        new_val = int(val_str, 16)
                    
                    if 0 <= new_val <= 255:
                        self.simulator.set_memory_value(address, new_val)
                        refresh_memory()
                        edit_dialog.destroy()
                        self.mem_status_var.set(f"Updated ${address:04X} = ${new_val:02X}")
                    else:
                        messagebox.showerror("Invalid Value", "Value must be between 0 and 255 (00-FF)")
                except ValueError:
                    messagebox.showerror("Invalid Value", "Please enter a valid hexadecimal value")
            
            def cancel_edit():
                edit_dialog.destroy()
            
            # Buttons
            btn_frame = ttk.Frame(edit_dialog)
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="Save", command=save_value).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancel", command=cancel_edit).pack(side=tk.LEFT, padx=5)
            
            # Bind Enter key to save
            val_entry.bind('<Return>', lambda e: save_value())
            edit_dialog.bind('<Escape>', lambda e: cancel_edit())
        
        # Bind double-click for editing
        self.mem_text.bind('<Double-Button-1>', on_double_click)
        
        # Initialize current address
        self.current_mem_addr = 0x1000
        
        # Navigation functions
        def prev_page():
            self.current_mem_addr = max(0, self.current_mem_addr - 256)
            self.addr_var.set(f"{self.current_mem_addr:04X}")
            refresh_memory()
        
        def next_page():
            self.current_mem_addr = min(0xFF00, self.current_mem_addr + 256)
            self.addr_var.set(f"{self.current_mem_addr:04X}")
            refresh_memory()
        
        # Navigation buttons
        nav_frame = ttk.Frame(status_frame)
        nav_frame.pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="<< Prev Page", command=prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Next Page >>", command=next_page).pack(side=tk.LEFT, padx=2)
        
        def refresh_memory():
            """Refresh the memory display."""
            try:
                start_addr = getattr(self, 'current_mem_addr', 0x1000)
                
                # Generate memory dump for current view (16 lines = 256 bytes)
                self.mem_text.config(state='normal')
                self.mem_text.delete(1.0, tk.END)
                
                # Header
                header = "Address  +0 +1 +2 +3 +4 +5 +6 +7 +8 +9 +A +B +C +D +E +F  ASCII\n"
                header += "-" * 72 + "\n"
                self.mem_text.insert(tk.END, header)
                
                # Memory lines
                for line in range(16):  # Show 16 lines
                    addr = start_addr + (line * 16)
                    if addr > 0xFFFF:
                        break
                    
                    # Address column
                    line_text = f"{addr:04X}:   "
                    
                    # Hex values
                    hex_bytes = []
                    ascii_chars = []
                    
                    for byte_offset in range(16):
                        byte_addr = addr + byte_offset
                        if byte_addr <= 0xFFFF:
                            byte_val = self.simulator.get_memory_value(byte_addr)
                            hex_bytes.append(f"{byte_val:02X}")
                            
                            # ASCII representation
                            if 32 <= byte_val <= 126:
                                ascii_chars.append(chr(byte_val))
                            else:
                                ascii_chars.append(".")
                        else:
                            hex_bytes.append("  ")
                            ascii_chars.append(" ")
                    
                    # Build complete line
                    line_text += " ".join(hex_bytes) + "  " + "".join(ascii_chars) + "\n"
                    self.mem_text.insert(tk.END, line_text)
                
                # Footer with instructions
                footer = "\n" + "=" * 72 + "\n"
                footer += "Instructions: Double-click on hex values to edit • Use Go/Search to navigate\n"
                footer += f"Showing: ${start_addr:04X} - ${min(start_addr + 255, 0xFFFF):04X}"
                self.mem_text.insert(tk.END, footer)
                
                self.mem_text.config(state='disabled')
                self.mem_status_var.set(f"Displaying memory from ${start_addr:04X}")
                
            except Exception as e:
                self.debug_print(f"Error refreshing memory view: {e}")
                self.mem_text.config(state='normal')
                self.mem_text.delete(1.0, tk.END)
                self.mem_text.insert(tk.END, f"Error displaying memory: {str(e)}")
                self.mem_text.config(state='disabled')
        
        # Initial memory display
        refresh_memory()
        
        # Keyboard shortcuts
        def handle_key(event):
            if event.keysym == 'F5':
                refresh_memory()
            elif event.keysym == 'Prior':  # Page Up
                prev_page()
            elif event.keysym == 'Next':   # Page Down
                next_page()
        
        memory_window.bind('<Key>', handle_key)
        memory_window.focus_set()  # Enable keyboard events
    
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

Author: Software Engineering (English) - GROUP 2
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
        
        # Apply syntax highlighting to the loaded example
        if hasattr(self, 'syntax_highlighter') and self.highlight_enabled.get():
            self.root.after_idle(self.syntax_highlighter.highlight_all)
        
        self.status_var.set("Example code loaded")
        self.debug_print("📝 DEBUG: Example code loaded successfully")

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
                
                # Apply syntax highlighting to the loaded file
                if hasattr(self, 'syntax_highlighter') and self.highlight_enabled.get():
                    self.root.after_idle(self.syntax_highlighter.highlight_all)
                
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