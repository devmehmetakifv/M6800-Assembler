#!/usr/bin/env python3
"""
Motorola 6800 Processor Simulator
Provides execution simulation with register and memory tracking.
"""

from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime

class M6800Simulator:
    """Motorola 6800 processor simulator."""
    
    def __init__(self):
        """Initialize the simulator with default state."""
        self.setup_logging()
        self.reset()
        
    def setup_logging(self):
        """Set up logging to save debug output to timestamped files."""
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Generate timestamped log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"logs/simulator_debug_{timestamp}.log"
        
        # Set up logger
        self.logger = logging.getLogger('M6800Simulator')
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
        self.debug_print("🚀 M6800 Simulator Debug Log Started")
        self.debug_print(f"📁 Log file: {self.log_filename}")
        
    def debug_print(self, message: str):
        """Print debug message and log to file."""
        print(message)  # Console output
        self.logger.debug(message)  # File output
        
    def reset(self):
        """Reset the simulator to initial state."""
        self.debug_print("🔄 DEBUG: reset() called")
        
        # Store program data before reset (if it exists)
        program_data_backup = getattr(self, 'program_data', {}).copy()
        program_start_backup = getattr(self, 'program_start', 0x0000)
        self.debug_print(f"🔄 DEBUG: Backing up program data: {len(program_data_backup)} bytes")
        
        # Registers
        self.registers = {
            'A': 0x00,      # Accumulator A
            'B': 0x00,      # Accumulator B
            'X': 0x0000,    # Index Register
            'SP': 0x01FF,   # Stack Pointer (starts at top of page 1)
            'PC': 0x0000,   # Program Counter
            'CC': 0x00      # Condition Code Register
        }
        
        # Memory (64KB)
        self.memory = [0x00] * 0x10000
        
        # Initialize program data
        self.program_data = {}
        self.program_start = 0x0000
        
        # Reset execution state
        self.execution_halted = False
        self.instruction_count = 0
        
        # Condition code flags
        self.cc_flags = {
            'H': 0,  # Half Carry (bit 5)
            'I': 0,  # Interrupt Mask (bit 4)
            'N': 0,  # Negative (bit 3)
            'Z': 0,  # Zero (bit 2)
            'V': 0,  # Overflow (bit 1)
            'C': 0   # Carry (bit 0)
        }
        
        self.debug_print("🔄 DEBUG: Reset completed, restoring program data")
        
        # Restore program data and set PC to program start
        if program_data_backup:
            self.program_data = program_data_backup
            self.program_start = program_start_backup
            self.registers['PC'] = self.program_start
            self.debug_print(f"🔄 DEBUG: Restored program, PC set to ${self.program_start:04X}")
            
            # Reload data into memory
            for addr, value in self.program_data.items():
                if 0 <= addr <= 0xFFFF:
                    self.memory[addr] = value & 0xFF
            self.debug_print(f"🔄 DEBUG: Reloaded {len(self.program_data)} bytes into memory")
        else:
            self.debug_print("🔄 DEBUG: No program data to restore")
    
    def load_program(self, object_data: Dict[int, int]):
        """
        Load program data into memory.
        
        Args:
            object_data: Dictionary mapping addresses to byte values
        """
        self.debug_print(f"💾 DEBUG: load_program() called with {len(object_data)} bytes")
        self.program_data = object_data.copy()
        
        # Find program start address (lowest address with data)
        if object_data:
            self.program_start = min(object_data.keys())
            self.registers['PC'] = self.program_start
            self.debug_print(f"💾 DEBUG: Program start address: ${self.program_start:04X}")
            
            # Load data into memory
            for addr, value in object_data.items():
                if 0 <= addr <= 0xFFFF:
                    self.memory[addr] = value & 0xFF
            self.debug_print(f"💾 DEBUG: Loaded program into memory, PC set to ${self.registers['PC']:04X}")
        else:
            self.debug_print("💾 DEBUG: Empty object_data provided")
    
    def step(self) -> bool:
        """
        Execute one instruction.
        
        Returns:
            True if instruction was executed, False if halted
        """
        self.debug_print(f"⚡ DEBUG: step() called, halted: {self.execution_halted}")
        
        if self.execution_halted:
            self.debug_print("⚡ DEBUG: Already halted, returning False")
            return False
            
        try:
            pc = self.registers['PC']
            self.debug_print(f"⚡ DEBUG: Current PC: ${pc:04X}")
            
            if pc < 0 or pc >= 0x10000:
                self.debug_print(f"⚡ DEBUG: PC out of bounds: ${pc:04X}")
                self.execution_halted = True
                return False
            
            # Check if we have a valid program loaded
            if not self.program_data:
                self.debug_print("⚡ DEBUG: No program loaded in simulator")
                self.execution_halted = True
                return False
                
            # Check if PC is within program bounds
            if pc not in self.program_data and self.memory[pc] == 0x00:
                self.debug_print(f"⚡ DEBUG: Execution reached empty memory at PC=${pc:04X}")
                self.execution_halted = True
                return False
                
            # Fetch instruction
            opcode = self.memory[pc]
            self.debug_print(f"⚡ DEBUG: Fetched opcode ${opcode:02X} at PC=${pc:04X}")
            
            # Execute instruction
            self._execute_instruction(opcode)
            self.instruction_count += 1
            
            new_pc = self.registers['PC']
            self.debug_print(f"⚡ DEBUG: Instruction executed, PC: ${pc:04X} -> ${new_pc:04X}, Count: {self.instruction_count}")
            
            return True
            
        except Exception as e:
            self.debug_print(f"❌ DEBUG: Exception in step() at PC=${self.registers['PC']:04X}: {e}")
            self.execution_halted = True
            return False
    
    def run(self, max_instructions: int = 1000) -> int:
        """
        Run simulation until halt or max instructions reached.
        
        Args:
            max_instructions: Maximum number of instructions to execute
            
        Returns:
            Number of instructions executed
        """
        self.debug_print(f"🚀 DEBUG: run() called, max_instructions: {max_instructions}")
        executed = 0
        
        while executed < max_instructions and not self.execution_halted:
            self.debug_print(f"🚀 DEBUG: Run loop iteration {executed + 1}")
            if not self.step():
                self.debug_print(f"🚀 DEBUG: Step failed, breaking run loop")
                break
            executed += 1
            
        self.debug_print(f"🚀 DEBUG: Run completed, executed {executed} instructions")
        return executed
    
    def _execute_instruction(self, opcode: int):
        """Execute a single instruction based on its opcode."""
        pc = self.registers['PC']
        self.debug_print(f"🔍 DEBUG: Executing opcode ${opcode:02X} at PC=${pc:04X}")
        
        # Simple instruction decoder - basic implementation
        if opcode == 0x00:  # BRK (Break/Software Interrupt)
            self.debug_print("🔍 DEBUG: BRK - halting execution")
            self.execution_halted = True
            
        elif opcode == 0x01:  # NOP
            self.debug_print("🔍 DEBUG: NOP instruction")
            self.registers['PC'] += 1
            
        elif opcode == 0x86:  # LDA immediate
            value = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: LDA immediate ${value:02X}")
            self.registers['A'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xC6:  # LDB immediate
            value = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: LDB immediate ${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xCE:  # LDX immediate
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDX immediate ${value:04X}")
            self.registers['X'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0x97:  # STA direct
            addr = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: STA direct ${addr:02X}, A=${self.registers['A']:02X}")
            self.memory[addr] = self.registers['A']
            self.registers['PC'] += 2
            
        elif opcode == 0xB7:  # STA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: STA extended ${addr:04X}, A=${self.registers['A']:02X}")
            self.memory[addr] = self.registers['A']
            self.registers['PC'] += 3
            
        elif opcode == 0xD7:  # STB direct
            addr = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: STB direct ${addr:02X}, B=${self.registers['B']:02X}")
            self.memory[addr] = self.registers['B']
            self.registers['PC'] += 2
            
        elif opcode == 0xF7:  # STB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: STB extended ${addr:04X}, B=${self.registers['B']:02X}")
            self.memory[addr] = self.registers['B']
            self.registers['PC'] += 3
            
        elif opcode == 0x81:  # CMP A immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMP A immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result:02X}")
            self._update_nz_flags(result & 0xFF)
            self._update_carry_flag(result < 0)
            self.registers['PC'] += 2
            
        elif opcode == 0x27:  # BEQ relative
            offset = self.memory[pc + 1]
            if offset > 127:
                offset -= 256  # Convert to signed
            self.debug_print(f"🔍 DEBUG: BEQ relative offset={offset}, Z flag={self.cc_flags['Z']}")
            if self.cc_flags['Z']:
                new_pc = (self.registers['PC'] + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BEQ taking branch to ${new_pc:04X}")
                self.registers['PC'] = new_pc
            else:
                self.debug_print("🔍 DEBUG: BEQ not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x26:  # BNE relative
            offset = self.memory[pc + 1]
            if offset > 127:
                offset -= 256  # Convert to signed
            self.debug_print(f"🔍 DEBUG: BNE relative offset={offset}, Z flag={self.cc_flags['Z']}")
            if not self.cc_flags['Z']:
                new_pc = (self.registers['PC'] + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BNE taking branch to ${new_pc:04X}")
                self.registers['PC'] = new_pc
            else:
                self.debug_print("🔍 DEBUG: BNE not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x20:  # BRA relative
            offset = self.memory[pc + 1]
            if offset > 127:
                offset -= 256  # Convert to signed
            new_pc = (self.registers['PC'] + 2 + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: BRA relative to ${new_pc:04X}")
            self.registers['PC'] = new_pc
            
        elif opcode == 0x7E:  # JMP extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: JMP extended to ${addr:04X}")
            self.registers['PC'] = addr
            
        elif opcode == 0x8B:  # ADD A immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADD A immediate ${value:02X}, A=${self.registers['A']:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0x16:  # TAB
            self.debug_print(f"🔍 DEBUG: TAB, A=${self.registers['A']:02X}")
            self.registers['B'] = self.registers['A']
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x17:  # TBA
            self.debug_print(f"🔍 DEBUG: TBA, B=${self.registers['B']:02X}")
            self.registers['A'] = self.registers['B']
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x4C:  # INC A
            old_a = self.registers['A']
            self.registers['A'] = (self.registers['A'] + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INC A, ${old_a:02X} -> ${self.registers['A']:02X}")
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x5C:  # INC B
            old_b = self.registers['B']
            self.registers['B'] = (self.registers['B'] + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INC B, ${old_b:02X} -> ${self.registers['B']:02X}")
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x4A:  # DEC A
            old_a = self.registers['A']
            self.registers['A'] = (self.registers['A'] - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DEC A, ${old_a:02X} -> ${self.registers['A']:02X}")
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x5A:  # DEC B
            old_b = self.registers['B']
            self.registers['B'] = (self.registers['B'] - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DEC B, ${old_b:02X} -> ${self.registers['B']:02X}")
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x39:  # RTS
            # Pop return address from stack
            sp = self.registers['SP']
            low = self.memory[sp + 1]
            high = self.memory[sp + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: RTS, returning to ${addr:04X}")
            self.registers['PC'] = addr
            self.registers['SP'] = (sp + 2) & 0xFFFF
            
        elif opcode == 0x3F:  # SWI (Software Interrupt)
            self.debug_print("🔍 DEBUG: SWI - halting execution")
            self.execution_halted = True
            
        elif opcode == 0xA6:  # LDA indexed (0,X)
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:02X}")
            self.registers['A'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xE6:  # LDB indexed (0,X)
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0x96:  # LDA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDA direct ${addr:02X}, value=${value:02X}")
            self.registers['A'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xD6:  # LDB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDB direct ${addr:02X}, value=${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xB6:  # LDA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDA extended ${addr:04X}, value=${value:02X}")
            self.registers['A'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0xF6:  # LDB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDB extended ${addr:04X}, value=${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0x91:  # CMP A direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMP A direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}")
            self._update_nz_flags(result & 0xFF)
            self._update_carry_flag(result < 0)
            self.registers['PC'] += 2
            
        elif opcode == 0xB1:  # CMP A extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMP A extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}")
            self._update_nz_flags(result & 0xFF)
            self._update_carry_flag(result < 0)
            self.registers['PC'] += 3
            
        elif opcode == 0xA1:  # CMP A indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMP A indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:02X}")
            self._update_nz_flags(result & 0xFF)
            self._update_carry_flag(result < 0)
            self.registers['PC'] += 2
            
        elif opcode == 0x1C:  # ABX (Add B to X)
            result = self.registers['X'] + self.registers['B']
            self.debug_print(f"🔍 DEBUG: ABX, X=${self.registers['X']:04X}, B=${self.registers['B']:02X}, result=${result:04X}")
            self.registers['X'] = result & 0xFFFF
            self.registers['PC'] += 1
            
        elif opcode == 0xCC:  # LDD immediate (Load Double accumulator)
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDD immediate ${value:04X}")
            self.registers['A'] = (value >> 8) & 0xFF
            self.registers['B'] = value & 0xFF
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0xDC:  # LDD direct
            addr = self.memory[pc + 1]
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDD direct ${addr:02X}, value=${value:04X}")
            self.registers['A'] = high
            self.registers['B'] = low
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xFC:  # LDD extended
            high_addr = self.memory[pc + 1]
            low_addr = self.memory[pc + 2]
            addr = (high_addr << 8) | low_addr
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDD extended ${addr:04X}, value=${value:04X}")
            self.registers['A'] = high
            self.registers['B'] = low
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0xDD:  # STD direct (Store Double accumulator)
            addr = self.memory[pc + 1]
            value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: STD direct ${addr:02X}, D=${value:04X}")
            self.memory[addr] = self.registers['A']
            self.memory[addr + 1] = self.registers['B']
            self.registers['PC'] += 2
            
        elif opcode == 0xFD:  # STD extended
            high_addr = self.memory[pc + 1]
            low_addr = self.memory[pc + 2]
            addr = (high_addr << 8) | low_addr
            value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: STD extended ${addr:04X}, D=${value:04X}")
            self.memory[addr] = self.registers['A']
            self.memory[addr + 1] = self.registers['B']
            self.registers['PC'] += 3
            
        elif opcode == 0x1B:  # ABA (Add B to A)
            result = self.registers['A'] + self.registers['B']
            self.debug_print(f"🔍 DEBUG: ABA, A=${self.registers['A']:02X}, B=${self.registers['B']:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x19:  # DAA (Decimal Adjust A)
            self.debug_print(f"🔍 DEBUG: DAA, A=${self.registers['A']:02X}")
            # Simplified DAA implementation
            a = self.registers['A']
            if ((a & 0x0F) > 9) or self.cc_flags['H']:
                a += 6
            if ((a & 0xF0) > 0x90) or self.cc_flags['C']:
                a += 0x60
                self._update_carry_flag(True)
            self.registers['A'] = a & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x18:  # XGDX (Exchange D with X) - M6811 instruction
            self.debug_print(f"🔍 DEBUG: XGDX, D=${(self.registers['A'] << 8) | self.registers['B']:04X}, X=${self.registers['X']:04X}")
            temp_d = (self.registers['A'] << 8) | self.registers['B']
            temp_x = self.registers['X']
            self.registers['A'] = (temp_x >> 8) & 0xFF
            self.registers['B'] = temp_x & 0xFF
            self.registers['X'] = temp_d
            self.registers['PC'] += 1
            
        elif opcode == 0x3D:  # MUL (Multiply A × B → D)
            result = self.registers['A'] * self.registers['B']
            self.debug_print(f"🔍 DEBUG: MUL, A=${self.registers['A']:02X} × B=${self.registers['B']:02X} = ${result:04X}")
            self.registers['A'] = (result >> 8) & 0xFF
            self.registers['B'] = result & 0xFF
            self._update_carry_flag((result & 0x80) != 0)  # C = bit 7 of result
            self.registers['PC'] += 1
            
        elif opcode == 0x30:  # TSX (Transfer Stack Pointer to Index Register)
            self.debug_print(f"🔍 DEBUG: TSX, SP=${self.registers['SP']:04X}")
            self.registers['X'] = self.registers['SP'] + 1  # M6800 TSX adds 1 to SP
            self._update_nz_flags(self.registers['X'])
            self.registers['PC'] += 1
            
        elif opcode == 0xD1:  # CMP B direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMP B direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}")
            self._update_nz_flags(result & 0xFF)
            self._update_carry_flag(result < 0)
            self.registers['PC'] += 2
            
        else:
            # Unknown instruction - halt execution
            self.debug_print(f"❌ DEBUG: Unknown instruction: ${opcode:02X} at PC=${pc:04X}")
            self.execution_halted = True
    
    def _update_nz_flags(self, value: int):
        """Update Negative and Zero flags based on value."""
        old_n = self.cc_flags['N']
        old_z = self.cc_flags['Z']
        self.cc_flags['N'] = 1 if (value & 0x80) != 0 else 0
        self.cc_flags['Z'] = 1 if (value & 0xFF) == 0 else 0
        self._pack_cc_register()
        self.debug_print(f"🚩 DEBUG: Flags updated - N: {old_n}->{self.cc_flags['N']}, Z: {old_z}->{self.cc_flags['Z']}")
    
    def _update_carry_flag(self, carry: bool):
        """Update Carry flag."""
        old_c = self.cc_flags['C']
        self.cc_flags['C'] = 1 if carry else 0
        self._pack_cc_register()
        self.debug_print(f"🚩 DEBUG: Carry flag updated: {old_c}->{self.cc_flags['C']}")
    
    def _pack_cc_register(self):
        """Pack condition code flags into CC register."""
        cc = 0
        cc |= (self.cc_flags['H'] & 1) << 5
        cc |= (self.cc_flags['I'] & 1) << 4
        cc |= (self.cc_flags['N'] & 1) << 3
        cc |= (self.cc_flags['Z'] & 1) << 2
        cc |= (self.cc_flags['V'] & 1) << 1
        cc |= (self.cc_flags['C'] & 1) << 0
        self.registers['CC'] = cc
    
    def _unpack_cc_register(self):
        """Unpack CC register into individual flags."""
        cc = self.registers['CC']
        self.cc_flags['H'] = (cc >> 5) & 1
        self.cc_flags['I'] = (cc >> 4) & 1
        self.cc_flags['N'] = (cc >> 3) & 1
        self.cc_flags['Z'] = (cc >> 2) & 1
        self.cc_flags['V'] = (cc >> 1) & 1
        self.cc_flags['C'] = (cc >> 0) & 1
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current simulator state.
        
        Returns:
            Dictionary containing registers, flags, and execution status
        """
        return {
            'registers': self.registers.copy(),
            'flags': self.cc_flags.copy(),
            'execution_halted': self.execution_halted,
            'instruction_count': self.instruction_count,
            'program_start': self.program_start
        }
    
    def get_memory_dump(self, start_addr: int = None, length: int = 256) -> str:
        """
        Get formatted memory dump.
        
        Args:
            start_addr: Starting address for dump (defaults to program start)
            length: Number of bytes to dump
            
        Returns:
            Formatted memory dump string
        """
        if start_addr is None:
            start_addr = self.program_start
            
        lines = []
        lines.append(f"Memory Dump (from ${start_addr:04X}):")
        lines.append("Address  +0 +1 +2 +3 +4 +5 +6 +7 +8 +9 +A +B +C +D +E +F  ASCII")
        lines.append("-" * 70)
        
        for i in range(0, length, 16):
            addr = start_addr + i
            if addr >= 0x10000:
                break
                
            # Address
            line = f"{addr:04X}:   "
            
            # Hex bytes
            hex_part = ""
            ascii_part = ""
            
            for j in range(16):
                byte_addr = addr + j
                if byte_addr < 0x10000 and i + j < length:
                    byte_val = self.memory[byte_addr]
                    hex_part += f"{byte_val:02X} "
                    
                    # ASCII representation
                    if 32 <= byte_val <= 126:
                        ascii_part += chr(byte_val)
                    else:
                        ascii_part += "."
                else:
                    hex_part += "   "
                    ascii_part += " "
            
            line += hex_part + " " + ascii_part
            lines.append(line)
            
            # Stop if we've shown enough
            if len(lines) > 20:  # Limit display size
                lines.append("... (truncated)")
                break
        
        return '\n'.join(lines)
    
    def get_memory_value(self, address: int) -> int:
        """Get value at memory address."""
        if 0 <= address <= 0xFFFF:
            return self.memory[address]
        return 0
    
    def set_memory_value(self, address: int, value: int):
        """Set value at memory address."""
        if 0 <= address <= 0xFFFF:
            self.memory[address] = value & 0xFF
    
    def get_register_value(self, register: str) -> int:
        """Get register value."""
        return self.registers.get(register.upper(), 0)
    
    def set_register_value(self, register: str, value: int):
        """Set register value."""
        reg = register.upper()
        if reg in self.registers:
            if reg in ['A', 'B', 'CC']:
                self.registers[reg] = value & 0xFF
            else:
                self.registers[reg] = value & 0xFFFF
                
            # Update flags if CC register changed
            if reg == 'CC':
                self._unpack_cc_register()
    
    def is_halted(self) -> bool:
        """Check if execution is halted."""
        return self.execution_halted
    
    def get_instruction_count(self) -> int:
        """Get number of instructions executed."""
        return self.instruction_count

def main():
    """Test function for the simulator."""
    simulator = M6800Simulator()
    
    # Test program: Load A with $55, store at $2000
    test_program = {
        0x1000: 0x86,  # LDA immediate
        0x1001: 0x55,  # value $55
        0x1002: 0xB7,  # STA extended
        0x1003: 0x20,  # high byte of $2000
        0x1004: 0x00,  # low byte of $2000
        0x1005: 0x3F   # SWI (halt)
    }
    
    simulator.load_program(test_program)
    print("Initial state:", simulator.get_state())
    
    # Run simulation
    steps = simulator.run()
    print(f"\nExecuted {steps} instructions")
    print("Final state:", simulator.get_state())
    print(f"Memory at $2000: ${simulator.get_memory_value(0x2000):02X}")

if __name__ == "__main__":
    main() 