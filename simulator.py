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
            'X': 0x0000,    # Index Register X
            'Y': 0x0000,    # Index Register Y (M6801/M6811)
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
        
        while executed < max_instructions:
            self.debug_print(f"🚀 DEBUG: Run loop iteration {executed + 1}")
            
            if not self.step():
                break
                
            executed += 1
            
            # Safety check for infinite loops
            if executed >= max_instructions:
                self.debug_print(f"🚀 DEBUG: Max instructions ({max_instructions}) reached")
                break
        
        self.debug_print(f"🚀 DEBUG: Run completed, executed {executed} instructions")
        return executed
    
    def _execute_instruction(self, opcode: int):
        """Execute a single instruction based on opcode."""
        pc = self.registers['PC']
        self.debug_print(f"🔍 DEBUG: Executing opcode ${opcode:02X} at PC=${pc:04X}")
        
        if opcode == 0x00:  # BRK (Break/Halt)
            self.debug_print("🔍 DEBUG: BRK - halting execution")
            self.execution_halted = True
            
        elif opcode == 0x01:  # NOP
            self.debug_print("🔍 DEBUG: NOP")
            self.registers['PC'] += 1
            
        elif opcode == 0x08:  # INX (Increment X)
            self.registers['X'] = (self.registers['X'] + 1) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: INX, X=${self.registers['X']:04X}")
            self._update_nz_flags(self.registers['X'])
            self.registers['PC'] += 1
            
        elif opcode == 0x09:  # DEX (Decrement X)
            self.registers['X'] = (self.registers['X'] - 1) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: DEX, X=${self.registers['X']:04X}")
            self._update_nz_flags(self.registers['X'])
            self.registers['PC'] += 1
            
        elif opcode == 0x0A:  # CLV (Clear Overflow flag)
            self.debug_print("🔍 DEBUG: CLV - clearing overflow flag")
            self.cc_flags['V'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x0B:  # SEV (Set Overflow flag)
            self.debug_print("🔍 DEBUG: SEV - setting overflow flag")
            self.cc_flags['V'] = 1
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x0C:  # CLC (Clear Carry flag)
            self.debug_print("🔍 DEBUG: CLC - clearing carry flag")
            self.cc_flags['C'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x0D:  # SEC (Set Carry flag)
            self.debug_print("🔍 DEBUG: SEC - setting carry flag")
            self.cc_flags['C'] = 1
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x0E:  # CLI (Clear Interrupt flag)
            self.debug_print("🔍 DEBUG: CLI - clearing interrupt flag")
            self.cc_flags['I'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x0F:  # SEI (Set Interrupt flag)
            self.debug_print("🔍 DEBUG: SEI - setting interrupt flag")
            self.cc_flags['I'] = 1
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x11:  # CBA (Compare A with B)
            result = self.registers['A'] - self.registers['B']
            self.debug_print(f"🔍 DEBUG: CBA, A=${self.registers['A']:02X}, B=${self.registers['B']:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < self.registers['B'])
            self._update_nz_flags(result & 0xFF)
            # Update V flag for signed overflow
            a_sign = (self.registers['A'] & 0x80) != 0
            b_sign = (self.registers['B'] & 0x80) != 0
            result_sign = (result & 0x80) != 0
            self.cc_flags['V'] = 1 if (a_sign != b_sign) and (a_sign != result_sign) else 0
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x06:  # TAP (Transfer A to Condition Codes)
            self.debug_print(f"🔍 DEBUG: TAP, A=${self.registers['A']:02X}")
            # Transfer bits from A to condition code register
            # Only bits 7-6 and 4-0 are transferred (bit 5 is always 1 in CC)
            self.registers['CC'] = (self.registers['A'] & 0xDF) | 0x20  # Keep bit 5 set
            self._unpack_cc_register()  # Update individual flag variables
            self.registers['PC'] += 1
            
        elif opcode == 0x07:  # TPA (Transfer Condition Codes to A)
            self._pack_cc_register()  # Ensure CC register is current
            self.registers['A'] = self.registers['CC']
            self.debug_print(f"🔍 DEBUG: TPA, CC=${self.registers['CC']:02X} -> A=${self.registers['A']:02X}")
            self.registers['PC'] += 1
            
        elif opcode == 0x40:  # NEGA (Negate A)
            old_a = self.registers['A']
            self.registers['A'] = (256 - old_a) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEGA, A=${old_a:02X} -> ${self.registers['A']:02X}")
            self.cc_flags['C'] = 1 if old_a != 0 else 0
            self.cc_flags['V'] = 1 if old_a == 0x80 else 0
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x4A:  # DECA (Decrement A)
            old_a = self.registers['A']
            self.registers['A'] = (self.registers['A'] - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DECA, A=${old_a:02X} -> ${self.registers['A']:02X}")
            self.cc_flags['V'] = 1 if old_a == 0x80 else 0  # Overflow if $80 -> $7F
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x5A:  # DECB (Decrement B)
            old_b = self.registers['B']
            self.registers['B'] = (self.registers['B'] - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DECB, B=${old_b:02X} -> ${self.registers['B']:02X}")
            self.cc_flags['V'] = 1 if old_b == 0x80 else 0  # Overflow if $80 -> $7F
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x50:  # NEGB (Negate B)
            old_b = self.registers['B']
            self.registers['B'] = (256 - old_b) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEGB, B=${old_b:02X} -> ${self.registers['B']:02X}")
            self.cc_flags['C'] = 1 if old_b != 0 else 0
            self.cc_flags['V'] = 1 if old_b == 0x80 else 0
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x51:  # NEGB direct (Negate memory location direct addressing)
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            new_value = (256 - old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEGB direct ${addr:02X}, mem=${old_value:02X} -> ${new_value:02X}")
            self.memory[addr] = new_value
            self.cc_flags['C'] = 1 if old_value != 0 else 0
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0
            self._update_nz_flags(new_value)
            self.registers['PC'] += 2
            
        elif opcode == 0x52:  # NEGB extended (Negate memory location extended addressing)
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            new_value = (256 - old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEGB extended ${addr:04X}, mem=${old_value:02X} -> ${new_value:02X}")
            self.memory[addr] = new_value
            self.cc_flags['C'] = 1 if old_value != 0 else 0
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0
            self._update_nz_flags(new_value)
            self.registers['PC'] += 3
            
        elif opcode == 0x53:  # COMB (Complement B register)
            old_b = self.registers['B']
            self.registers['B'] = (~old_b) & 0xFF
            self.debug_print(f"🔍 DEBUG: COMB, B=${old_b:02X} -> ${self.registers['B']:02X}")
            self.cc_flags['C'] = 1  # COMB always sets carry
            self.cc_flags['V'] = 0  # COMB always clears overflow
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x1B:  # ABA (Add B to A)
            result = self.registers['A'] + self.registers['B']
            self.debug_print(f"🔍 DEBUG: ABA, A=${self.registers['A']:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['A'], self.registers['B'], result)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 1
            
        elif opcode == 0x3A:  # ABX (Add B to X)
            result = self.registers['X'] + self.registers['B']
            self.debug_print(f"🔍 DEBUG: ABX, X=${self.registers['X']:04X}, B=${self.registers['B']:02X}, result=${result:04X}")
            self.registers['X'] = result & 0xFFFF
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
            
        elif opcode == 0x20:  # BRA (Branch Always)
            offset = self.memory[pc + 1]
            if offset & 0x80:  # Check if negative (two's complement)
                offset = offset - 256
            target = (pc + 2 + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: BRA relative offset={offset}, target=${target:04X}")
            self.registers['PC'] = target
            
        elif opcode == 0x24:  # BCC (Branch if Carry Clear)
            offset = self.memory[pc + 1]
            if offset & 0x80:
                offset = offset - 256
            if not self.cc_flags['C']:
                target = (pc + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BCC taking branch to ${target:04X}")
                self.registers['PC'] = target
            else:
                self.debug_print("🔍 DEBUG: BCC not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x25:  # BCS (Branch if Carry Set)
            offset = self.memory[pc + 1]
            if offset & 0x80:
                offset = offset - 256
            if self.cc_flags['C']:
                target = (pc + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BCS taking branch to ${target:04X}")
                self.registers['PC'] = target
            else:
                self.debug_print("🔍 DEBUG: BCS not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x26:  # BNE (Branch if Not Equal)
            offset = self.memory[pc + 1]
            if offset & 0x80:
                offset = offset - 256
            if not self.cc_flags['Z']:
                target = (pc + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BNE taking branch to ${target:04X}")
                self.registers['PC'] = target
            else:
                self.debug_print("🔍 DEBUG: BNE not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x27:  # BEQ (Branch if Equal)
            offset = self.memory[pc + 1]
            if offset & 0x80:
                offset = offset - 256
            self.debug_print(f"🔍 DEBUG: BEQ relative offset={offset}, Z flag={self.cc_flags['Z']}")
            if self.cc_flags['Z']:
                target = (pc + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BEQ taking branch to ${target:04X}")
                self.registers['PC'] = target
            else:
                self.debug_print("🔍 DEBUG: BEQ not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x23:  # BLS (Branch if Lower or Same)
            offset = self.memory[pc + 1]
            if offset & 0x80:
                offset = offset - 256
            # Branch if C=1 OR Z=1 (lower or same for unsigned comparison)
            should_branch = self.cc_flags['C'] or self.cc_flags['Z']
            self.debug_print(f"🔍 DEBUG: BLS relative offset={offset}, C={self.cc_flags['C']}, Z={self.cc_flags['Z']}, branch={should_branch}")
            if should_branch:
                target = (pc + 2 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BLS taking branch to ${target:04X}")
                self.registers['PC'] = target
            else:
                self.debug_print("🔍 DEBUG: BLS not taking branch")
                self.registers['PC'] += 2
                
        elif opcode == 0x30:  # TSX (Transfer Stack Pointer to X)
            self.debug_print(f"🔍 DEBUG: TSX, SP=${self.registers['SP']:04X}")
            self.registers['X'] = (self.registers['SP'] + 1) & 0xFFFF  # TSX adds 1 to SP
            self.registers['PC'] += 1
            
        elif opcode == 0x35:  # TXS (Transfer X to Stack Pointer)
            self.debug_print(f"🔍 DEBUG: TXS, X=${self.registers['X']:04X}")
            self.registers['SP'] = (self.registers['X'] - 1) & 0xFFFF  # TXS subtracts 1 from X
            self.registers['PC'] += 1
            
        elif opcode == 0x36:  # PSHA (Push A to stack)
            self.debug_print(f"🔍 DEBUG: PSHA, A=${self.registers['A']:02X}, SP=${self.registers['SP']:04X}")
            self.memory[self.registers['SP']] = self.registers['A']
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.registers['PC'] += 1
            
        elif opcode == 0x37:  # PSHB (Push B to stack)
            self.debug_print(f"🔍 DEBUG: PSHB, B=${self.registers['B']:02X}, SP=${self.registers['SP']:04X}")
            self.memory[self.registers['SP']] = self.registers['B']
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.registers['PC'] += 1
            
        elif opcode == 0x32:  # PULA (Pull A from stack)
            self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
            self.registers['A'] = self.memory[self.registers['SP']]
            self.debug_print(f"🔍 DEBUG: PULA, A=${self.registers['A']:02X}, SP=${self.registers['SP']:04X}")
            self.registers['PC'] += 1
            
        elif opcode == 0x33:  # PULB (Pull B from stack)
            self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
            self.registers['B'] = self.memory[self.registers['SP']]
            self.debug_print(f"🔍 DEBUG: PULB, B=${self.registers['B']:02X}, SP=${self.registers['SP']:04X}")
            self.registers['PC'] += 1
            
        elif opcode == 0x3C:  # PSHX (Push X register to stack)
            self.debug_print(f"🔍 DEBUG: PSHX, X=${self.registers['X']:04X}, SP=${self.registers['SP']:04X}")
            self.memory[self.registers['SP']] = self.registers['X'] & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.memory[self.registers['SP']] = (self.registers['X'] >> 8) & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.registers['PC'] += 1
            
        elif opcode == 0x38:  # PULX (Pull X register from stack)
            self.debug_print(f"🔍 DEBUG: PULX, SP=${self.registers['SP']:04X}")
            self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
            high = self.memory[self.registers['SP']]
            self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
            low = self.memory[self.registers['SP']]
            self.registers['X'] = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: PULX result, X=${self.registers['X']:04X}")
            self.registers['PC'] += 1
            
        elif opcode == 0x39:  # RTS (Return from Subroutine)
            # Pull return address from stack (low byte first)
            self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
            pc_low = self.memory[self.registers['SP']]
            self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
            pc_high = self.memory[self.registers['SP']]
            
            return_addr = (pc_high << 8) | pc_low
            self.debug_print(f"🔍 DEBUG: RTS to ${return_addr:04X}, SP=${self.registers['SP']:04X}")
            self.registers['PC'] = return_addr
            
        elif opcode == 0x3B:  # RTI (Return from Interrupt)
            # RTI restores the complete processor state from stack in specific order:
            # Stack (top to bottom): CC, B, A, X_high, X_low, PC_high, PC_low
            sp = self.registers['SP']
            
            # Restore CC (Condition Code) register
            sp = (sp + 1) & 0xFFFF
            self.registers['CC'] = self.memory[sp]
            self._unpack_cc_register()  # Update individual flag bits
            
            # Restore B accumulator
            sp = (sp + 1) & 0xFFFF
            self.registers['B'] = self.memory[sp]
            
            # Restore A accumulator  
            sp = (sp + 1) & 0xFFFF
            self.registers['A'] = self.memory[sp]
            
            # Restore X index register (16-bit, high byte first)
            sp = (sp + 1) & 0xFFFF
            x_high = self.memory[sp]
            sp = (sp + 1) & 0xFFFF
            x_low = self.memory[sp]
            self.registers['X'] = (x_high << 8) | x_low
            
            # Restore PC (Program Counter, 16-bit, high byte first)
            sp = (sp + 1) & 0xFFFF
            pc_high = self.memory[sp]
            sp = (sp + 1) & 0xFFFF
            pc_low = self.memory[sp]
            pc_addr = (pc_high << 8) | pc_low
            
            # Update stack pointer and program counter
            self.registers['SP'] = sp
            self.registers['PC'] = pc_addr
            
            self.debug_print(f"🔍 DEBUG: RTI - restored state: PC=${pc_addr:04X}, A=${self.registers['A']:02X}, B=${self.registers['B']:02X}, X=${self.registers['X']:04X}, CC=${self.registers['CC']:02X}, SP=${self.registers['SP']:04X}")
            
        elif opcode == 0x3D:  # MUL (Multiply A by B)
            result = self.registers['A'] * self.registers['B']
            self.debug_print(f"🔍 DEBUG: MUL, A=${self.registers['A']:02X}, B=${self.registers['B']:02X}, result=${result:04X}")
            self.registers['A'] = (result >> 8) & 0xFF  # High byte to A
            self.registers['B'] = result & 0xFF          # Low byte to B
            self._update_carry_flag(self.registers['B'] & 0x80)  # Set C if bit 7 of low byte is set
            self.registers['PC'] += 1
            
        elif opcode == 0x3E:  # WAI (Wait for Interrupt)
            self.debug_print("🔍 DEBUG: WAI - halting execution (wait for interrupt)")
            self.execution_halted = True
            
        # Load/Store Instructions
        elif opcode == 0x86:  # LDA immediate
            value = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: LDA immediate ${value:02X}")
            self.registers['A'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0x96:  # LDA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDA direct ${addr:02X}, value=${value:02X}")
            self.registers['A'] = value
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
            
        elif opcode == 0xA6:  # LDA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:02X}")
            self.registers['A'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xC6:  # LDB immediate
            value = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: LDB immediate ${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xD6:  # LDB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDB direct ${addr:02X}, value=${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xF6:  # LDB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDB extended ${addr:04X}, value=${value:02X}")
            self.registers['B'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0xE6:  # LDB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: LDB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:02X}")
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
            
        elif opcode == 0xDE:  # LDX direct
            addr = self.memory[pc + 1]
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDX direct ${addr:02X}, value=${value:04X}")
            self.registers['X'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        elif opcode == 0xFE:  # LDX extended
            addr_high = self.memory[pc + 1]
            addr_low = self.memory[pc + 2]
            addr = (addr_high << 8) | addr_low
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDX extended ${addr:04X}, value=${value:04X}")
            self.registers['X'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0xEE:  # LDX indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDX indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:04X}")
            self.registers['X'] = value
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        # LDD (Load Double accumulator) Instructions
        elif opcode == 0xCC:  # LDD immediate
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDD immediate ${value:04X}")
            self.registers['A'] = high
            self.registers['B'] = low
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
            addr_high = self.memory[pc + 1]
            addr_low = self.memory[pc + 2]
            addr = (addr_high << 8) | addr_low
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDD extended ${addr:04X}, value=${value:04X}")
            self.registers['A'] = high
            self.registers['B'] = low
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0xEC:  # LDD indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: LDD indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:04X}")
            self.registers['A'] = high
            self.registers['B'] = low
            self._update_nz_flags(value)
            self.registers['PC'] += 2
            
        # Store Instructions
        elif opcode == 0x97:  # STA direct
            addr = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: STA direct ${addr:02X}, A=${self.registers['A']:02X}")
            self.memory[addr] = self.registers['A']
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xB7:  # STA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: STA extended ${addr:04X}, A=${self.registers['A']:02X}")
            self.memory[addr] = self.registers['A']
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 3
            
        elif opcode == 0xA7:  # STA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: STA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}")
            self.memory[addr] = self.registers['A']
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xD7:  # STB direct
            addr = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: STB direct ${addr:02X}, B=${self.registers['B']:02X}")
            self.memory[addr] = self.registers['B']
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xF7:  # STB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: STB extended ${addr:04X}, B=${self.registers['B']:02X}")
            self.memory[addr] = self.registers['B']
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 3
            
        elif opcode == 0xE7:  # STB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: STB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}")
            self.memory[addr] = self.registers['B']
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
                
        elif opcode == 0xDF:  # STX direct
            addr = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: STX direct ${addr:02X}, X=${self.registers['X']:04X}")
            self.memory[addr] = (self.registers['X'] >> 8) & 0xFF
            self.memory[addr + 1] = self.registers['X'] & 0xFF
            self._update_nz_flags(self.registers['X'])
            self.registers['PC'] += 2
            
        elif opcode == 0xFF:  # STX extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: STX extended ${addr:04X}, X=${self.registers['X']:04X}")
            self.memory[addr] = (self.registers['X'] >> 8) & 0xFF
            self.memory[addr + 1] = self.registers['X'] & 0xFF
            self._update_nz_flags(self.registers['X'])
            self.registers['PC'] += 3
            
        # STD (Store Double accumulator) Instructions
        elif opcode == 0xDD:  # STD direct
            addr = self.memory[pc + 1]
            d_value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: STD direct ${addr:02X}, D=${d_value:04X}")
            self.memory[addr] = self.registers['A']
            self.memory[addr + 1] = self.registers['B']
            self._update_nz_flags(d_value)
            self.registers['PC'] += 2
            
        elif opcode == 0xFD:  # STD extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            d_value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: STD extended ${addr:04X}, D=${d_value:04X}")
            self.memory[addr] = self.registers['A']
            self.memory[addr + 1] = self.registers['B']
            self._update_nz_flags(d_value)
            self.registers['PC'] += 3
            
        elif opcode == 0xED:  # STD indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            d_value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: STD indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, D=${d_value:04X}")
            self.memory[addr] = self.registers['A']
            self.memory[addr + 1] = self.registers['B']
            self._update_nz_flags(d_value)
            self.registers['PC'] += 2
            
        # Arithmetic Instructions
        elif opcode == 0x8B:  # ADDA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['A'], value, result)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xCB:  # ADDB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['B'], value, result)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
            
        # Subtraction Instructions
        elif opcode == 0x90:  # SUBA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: SUBA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xF0:  # SUBB extended (corrected from 0xF2)
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: SUBB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 3
            
        # ADDD (Add to Double accumulator) Instructions
        elif opcode == 0xC3:  # ADDD immediate
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            value = (high << 8) | low
            d_reg = (self.registers['A'] << 8) | self.registers['B']
            result = d_reg + value
            self.debug_print(f"🔍 DEBUG: ADDD immediate ${value:04X}, D=${d_reg:04X}, result=${result:04X}")
            self._update_carry_flag(result > 0xFFFF)
            result = result & 0xFFFF
            self.registers['A'] = (result >> 8) & 0xFF
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xD3:  # ADDD direct
            addr = self.memory[pc + 1]
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            d_reg = (self.registers['A'] << 8) | self.registers['B']
            result = d_reg + value
            self.debug_print(f"🔍 DEBUG: ADDD direct ${addr:02X}, D=${d_reg:04X}, mem=${value:04X}, result=${result:04X}")
            self._update_carry_flag(result > 0xFFFF)
            result = result & 0xFFFF
            self.registers['A'] = (result >> 8) & 0xFF
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xF3:  # ADDD extended
            addr_high = self.memory[pc + 1]
            addr_low = self.memory[pc + 2]
            addr = (addr_high << 8) | addr_low
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            d_reg = (self.registers['A'] << 8) | self.registers['B']
            result = d_reg + value
            self.debug_print(f"🔍 DEBUG: ADDD extended ${addr:04X}, D=${d_reg:04X}, mem=${value:04X}, result=${result:04X}")
            self._update_carry_flag(result > 0xFFFF)
            result = result & 0xFFFF
            self.registers['A'] = (result >> 8) & 0xFF
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xE3:  # ADDD indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            high = self.memory[addr]
            low = self.memory[addr + 1]
            value = (high << 8) | low
            d_reg = (self.registers['A'] << 8) | self.registers['B']
            result = d_reg + value
            self.debug_print(f"🔍 DEBUG: ADDD indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, D=${d_reg:04X}, mem=${value:04X}, result=${result:04X}")
            self._update_carry_flag(result > 0xFFFF)
            result = result & 0xFFFF
            self.registers['A'] = (result >> 8) & 0xFF
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        # Comparison Instructions
        elif opcode == 0x81:  # CMP A immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMP A immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
            
        elif opcode == 0xC1:  # CMP B immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMP B immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
            
        elif opcode == 0x91:  # CMPA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMPA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
            
        elif opcode == 0xD1:  # CMPB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
            
        elif opcode == 0x8C:  # CPX immediate
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            value = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: CPX immediate ${value:04X}, X=${self.registers['X']:04X}")
            self._compare_16bit(self.registers['X'], value)
            self.registers['PC'] += 3
            
        # Jump Instructions
        elif opcode == 0x7E:  # JMP extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: JMP extended to ${addr:04X}")
            self.registers['PC'] = addr
            
        elif opcode == 0x6E:  # JMP indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: JMP indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, target=${addr:04X}")
            self.registers['PC'] = addr
            
        # M6801 Division and Shift Instructions
        elif opcode == 0x02:  # IDIV (Integer Divide)
            # Divide D by X, quotient in X, remainder in D
            d_value = (self.registers['A'] << 8) | self.registers['B']
            x_value = self.registers['X']
            if x_value == 0:
                self.debug_print("🔍 DEBUG: IDIV by zero, setting flags")
                self.cc_flags['C'] = 1  # Set carry on divide by zero
                self.cc_flags['V'] = 1  # Set overflow on divide by zero
            else:
                quotient = d_value // x_value
                remainder = d_value % x_value
                self.debug_print(f"🔍 DEBUG: IDIV, D=${d_value:04X} / X=${x_value:04X} = Q=${quotient:04X}, R=${remainder:04X}")
                self.registers['X'] = quotient & 0xFFFF
                self.registers['A'] = (remainder >> 8) & 0xFF
                self.registers['B'] = remainder & 0xFF
                self.cc_flags['C'] = 0
                self.cc_flags['V'] = 0
                self._update_nz_flags(quotient)
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x03:  # FDIV (Fractional Divide)
            # Divide D by X, result in X, remainder in D (fractional)
            d_value = (self.registers['A'] << 8) | self.registers['B']
            x_value = self.registers['X']
            if x_value == 0 or d_value >= x_value:
                self.debug_print("🔍 DEBUG: FDIV invalid operation, setting flags")
                self.cc_flags['C'] = 1  # Set carry on invalid operation
                self.cc_flags['V'] = 1  # Set overflow on invalid operation
            else:
                # Shift D left 16 positions and divide by X
                shifted_d = d_value << 16
                quotient = shifted_d // x_value
                remainder = shifted_d % x_value
                self.debug_print(f"🔍 DEBUG: FDIV, D=${d_value:04X} / X=${x_value:04X} = Q=${quotient:04X}")
                self.registers['X'] = quotient & 0xFFFF
                self.registers['A'] = (remainder >> 24) & 0xFF
                self.registers['B'] = (remainder >> 16) & 0xFF
                self.cc_flags['C'] = 0
                self.cc_flags['V'] = 0
                self._update_nz_flags(quotient)
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x04:  # LSRD (Logical Shift Right Double)
            d_value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: LSRD, D=${d_value:04X}")
            self.cc_flags['C'] = d_value & 1  # Save LSB in carry
            d_value = d_value >> 1
            self.registers['A'] = (d_value >> 8) & 0xFF
            self.registers['B'] = d_value & 0xFF
            self._update_nz_flags(d_value)
            self.registers['PC'] += 1
            
        elif opcode == 0x05:  # ASLD (Arithmetic Shift Left Double)
            d_value = (self.registers['A'] << 8) | self.registers['B']
            self.debug_print(f"🔍 DEBUG: ASLD, D=${d_value:04X}")
            self.cc_flags['C'] = (d_value & 0x8000) >> 15  # Save MSB in carry
            # Check for overflow (sign change)
            self.cc_flags['V'] = ((d_value & 0x8000) >> 15) ^ ((d_value & 0x4000) >> 14)
            d_value = (d_value << 1) & 0xFFFF
            self.registers['A'] = (d_value >> 8) & 0xFF
            self.registers['B'] = d_value & 0xFF
            self._update_nz_flags(d_value)
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        # M6811 Bit Manipulation Instructions
        elif opcode == 0x12:  # BRSET direct
            addr = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            offset = self.memory[pc + 3]
            # Convert offset to signed 8-bit value
            if offset > 127:
                offset = offset - 256
            
            mem_value = self.memory[addr]
            test_result = mem_value & mask
            self.debug_print(f"🔍 DEBUG: BRSET direct ${addr:02X}, mask=${mask:02X}, mem=${mem_value:02X}, test=${test_result:02X}")
            
            if test_result != 0:  # If any masked bits are set, branch
                new_pc = (self.registers['PC'] + 4 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BRSET branch taken to ${new_pc:04X}")
                self.registers['PC'] = new_pc
            else:
                self.debug_print("🔍 DEBUG: BRSET branch not taken")
                self.registers['PC'] += 4
                
        elif opcode == 0x13:  # BRCLR direct
            addr = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            offset = self.memory[pc + 3]
            # Convert offset to signed 8-bit value
            if offset > 127:
                offset = offset - 256
            
            mem_value = self.memory[addr]
            test_result = mem_value & mask
            self.debug_print(f"🔍 DEBUG: BRCLR direct ${addr:02X}, mask=${mask:02X}, mem=${mem_value:02X}, test=${test_result:02X}")
            
            if test_result == 0:  # If all masked bits are clear, branch
                new_pc = (self.registers['PC'] + 4 + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BRCLR branch taken to ${new_pc:04X}")
                self.registers['PC'] = new_pc
            else:
                self.debug_print("🔍 DEBUG: BRCLR branch not taken")
                self.registers['PC'] += 4
                
        elif opcode == 0x14:  # BSET direct
            addr = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            
            old_value = self.memory[addr]
            new_value = old_value | mask  # Set bits specified by mask
            self.memory[addr] = new_value
            self.debug_print(f"🔍 DEBUG: BSET direct ${addr:02X}, mask=${mask:02X}, mem=${old_value:02X} -> ${new_value:02X}")
            
            # Update flags based on result
            self._update_nz_flags(new_value)
            self.cc_flags['V'] = 0  # BSET always clears V flag
            self._pack_cc_register()
            self.registers['PC'] += 3
            
        elif opcode == 0x15:  # BCLR direct
            addr = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            
            old_value = self.memory[addr]
            new_value = old_value & (~mask)  # Clear bits specified by mask
            self.memory[addr] = new_value
            self.debug_print(f"🔍 DEBUG: BCLR direct ${addr:02X}, mask=${mask:02X}, mem=${old_value:02X} -> ${new_value:02X}")
            
            # Update flags based on result
            self._update_nz_flags(new_value)
            self.cc_flags['V'] = 0  # BCLR always clears V flag
            self._pack_cc_register()
            self.registers['PC'] += 3
            
        elif opcode == 0x1C:  # BSET indexed
            offset = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            addr = (self.registers['X'] + offset) & 0xFFFF
            
            old_value = self.memory[addr]
            new_value = old_value | mask  # Set bits specified by mask
            self.memory[addr] = new_value
            self.debug_print(f"🔍 DEBUG: BSET indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mask=${mask:02X}, mem=${old_value:02X} -> ${new_value:02X}")
            
            # Update flags based on result
            self._update_nz_flags(new_value)
            self.cc_flags['V'] = 0  # BSET always clears V flag
            self._pack_cc_register()
            self.registers['PC'] += 3
            
        elif opcode == 0x1D:  # BCLR indexed
            offset = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            addr = (self.registers['X'] + offset) & 0xFFFF
            
            old_value = self.memory[addr]
            new_value = old_value & (~mask)  # Clear bits specified by mask
            self.memory[addr] = new_value
            self.debug_print(f"🔍 DEBUG: BCLR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mask=${mask:02X}, mem=${old_value:02X} -> ${new_value:02X}")
            
            # Update flags based on result
            self._update_nz_flags(new_value)
            self.cc_flags['V'] = 0  # BCLR always clears V flag
            self._pack_cc_register()
            self.registers['PC'] += 3
            
        elif opcode == 0x1E:  # BRSET indexed
            offset = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            branch_offset = self.memory[pc + 3]
            # Convert offset to signed 8-bit value
            if branch_offset > 127:
                branch_offset = branch_offset - 256
                
            addr = (self.registers['X'] + offset) & 0xFFFF
            mem_value = self.memory[addr]
            test_result = mem_value & mask
            self.debug_print(f"🔍 DEBUG: BRSET indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mask=${mask:02X}, mem=${mem_value:02X}, test=${test_result:02X}")
            
            if test_result != 0:  # If any masked bits are set, branch
                new_pc = (self.registers['PC'] + 4 + branch_offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BRSET indexed branch taken to ${new_pc:04X}")
                self.registers['PC'] = new_pc
            else:
                self.debug_print("🔍 DEBUG: BRSET indexed branch not taken")
                self.registers['PC'] += 4
                
        elif opcode == 0x1F:  # BRCLR indexed
            offset = self.memory[pc + 1]
            mask = self.memory[pc + 2]
            branch_offset = self.memory[pc + 3]
            # Convert offset to signed 8-bit value
            if branch_offset > 127:
                branch_offset = branch_offset - 256
                
            addr = (self.registers['X'] + offset) & 0xFFFF
            mem_value = self.memory[addr]
            test_result = mem_value & mask
            self.debug_print(f"🔍 DEBUG: BRCLR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mask=${mask:02X}, mem=${mem_value:02X}, test=${test_result:02X}")
            
            if test_result == 0:  # If all masked bits are clear, branch
                new_pc = (self.registers['PC'] + 4 + branch_offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: BRCLR indexed branch taken to ${new_pc:04X}")
                self.registers['PC'] = new_pc
            else:
                self.debug_print("🔍 DEBUG: BRCLR indexed branch not taken")
                self.registers['PC'] += 4
                
        # Additional M6800 Instructions
        elif opcode == 0x3F:  # SWI (Software Interrupt)
            # SWI saves the complete processor state to stack in specific order:
            # Save PC (current PC + 1 to point to next instruction)
            next_pc = (self.registers['PC'] + 1) & 0xFFFF
            pc_high = (next_pc >> 8) & 0xFF
            pc_low = next_pc & 0xFF
            
            # Save PC (Program Counter, low byte first)
            self.memory[self.registers['SP']] = pc_low
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.memory[self.registers['SP']] = pc_high
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            # Save X index register (low byte first)
            self.memory[self.registers['SP']] = self.registers['X'] & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.memory[self.registers['SP']] = (self.registers['X'] >> 8) & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            # Save A accumulator
            self.memory[self.registers['SP']] = self.registers['A']
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            # Save B accumulator
            self.memory[self.registers['SP']] = self.registers['B']
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            # Save CC (Condition Code) register
            self._pack_cc_register()  # Ensure CC register is up to date
            self.memory[self.registers['SP']] = self.registers['CC']
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            # Set interrupt mask flag
            self.cc_flags['I'] = 1
            self._pack_cc_register()
            
            self.debug_print(f"🔍 DEBUG: SWI - saved state: PC=${next_pc:04X}, A=${self.registers['A']:02X}, B=${self.registers['B']:02X}, X=${self.registers['X']:04X}, CC=${self.registers['CC']:02X}, SP=${self.registers['SP']:04X}")
            
            # In a real system, this would vector to the interrupt handler at a fixed address
            # For simulation purposes, we'll halt execution
            self.debug_print("🔍 DEBUG: SWI - software interrupt, halting (in real system would vector to interrupt handler)")
            self.execution_halted = True
            
        elif opcode == 0x8F:  # XGDX (Exchange D and X) - M6811
            d_value = (self.registers['A'] << 8) | self.registers['B']
            x_value = self.registers['X']
            self.debug_print(f"🔍 DEBUG: XGDX, D=${d_value:04X}, X=${x_value:04X}")
            self.registers['A'] = (x_value >> 8) & 0xFF
            self.registers['B'] = x_value & 0xFF
            self.registers['X'] = d_value
            self.registers['PC'] += 1
            
        # M6811 Prefix Instructions ($18 prefix)
        elif opcode == 0x18:  # M6811 Extended Instructions
            if pc + 1 >= 0x10000:
                self.debug_print(f"❌ DEBUG: M6811 prefix $18 at PC=${pc:04X} but no next byte")
                self.execution_halted = True
                return False
                
            next_opcode = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: M6811 prefix $18 at PC=${pc:04X}, next opcode=${next_opcode:02X}")
            
            if next_opcode == 0xCE:  # LDY immediate
                high = self.memory[pc + 2]
                low = self.memory[pc + 3]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: LDY immediate ${value:04X}")
                self.registers['Y'] = value
                self._update_nz_flags(value)
                self.registers['PC'] += 4
                
            elif next_opcode == 0xDE:  # LDY direct
                addr = self.memory[pc + 2]
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: LDY direct ${addr:02X}, value=${value:04X}")
                self.registers['Y'] = value
                self._update_nz_flags(value)
                self.registers['PC'] += 3
                
            elif next_opcode == 0xFE:  # LDY extended
                addr_high = self.memory[pc + 2]
                addr_low = self.memory[pc + 3]
                addr = (addr_high << 8) | addr_low
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: LDY extended ${addr:04X}, value=${value:04X}")
                self.registers['Y'] = value
                self._update_nz_flags(value)
                self.registers['PC'] += 4
                
            elif next_opcode == 0xEE:  # LDY indexed
                offset = self.memory[pc + 2]
                addr = (self.registers['X'] + offset) & 0xFFFF
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: LDY indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, value=${value:04X}")
                self.registers['Y'] = value
                self._update_nz_flags(value)
                self.registers['PC'] += 3
                
            elif next_opcode == 0xDF:  # STY direct
                addr = self.memory[pc + 2]
                self.debug_print(f"🔍 DEBUG: STY direct ${addr:02X}, Y=${self.registers['Y']:04X}")
                self.memory[addr] = (self.registers['Y'] >> 8) & 0xFF
                self.memory[addr + 1] = self.registers['Y'] & 0xFF
                self._update_nz_flags(self.registers['Y'])
                self.registers['PC'] += 3
                
            elif next_opcode == 0xFF:  # STY extended
                addr_high = self.memory[pc + 2]
                addr_low = self.memory[pc + 3]
                addr = (addr_high << 8) | addr_low
                self.debug_print(f"🔍 DEBUG: STY extended ${addr:04X}, Y=${self.registers['Y']:04X}")
                self.memory[addr] = (self.registers['Y'] >> 8) & 0xFF
                self.memory[addr + 1] = self.registers['Y'] & 0xFF
                self._update_nz_flags(self.registers['Y'])
                self.registers['PC'] += 4
                
            elif next_opcode == 0xEF:  # STY indexed
                offset = self.memory[pc + 2]
                addr = (self.registers['X'] + offset) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: STY indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, Y=${self.registers['Y']:04X}")
                self.memory[addr] = (self.registers['Y'] >> 8) & 0xFF
                self.memory[addr + 1] = self.registers['Y'] & 0xFF
                self._update_nz_flags(self.registers['Y'])
                self.registers['PC'] += 3
                
            elif next_opcode == 0x08:  # INY (Increment Y)
                self.registers['Y'] = (self.registers['Y'] + 1) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: INY, Y=${self.registers['Y']:04X}")
                self._update_nz_flags(self.registers['Y'])
                self.registers['PC'] += 2
                
            elif next_opcode == 0x09:  # DEY (Decrement Y)
                self.registers['Y'] = (self.registers['Y'] - 1) & 0xFFFF
                self.debug_print(f"🔍 DEBUG: DEY, Y=${self.registers['Y']:04X}")
                self._update_nz_flags(self.registers['Y'])
                self.registers['PC'] += 2
                
            elif next_opcode == 0x8C:  # CPY immediate
                high = self.memory[pc + 2]
                low = self.memory[pc + 3]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: CPY immediate ${value:04X}, Y=${self.registers['Y']:04X}")
                self._compare_16bit(self.registers['Y'], value)
                self.registers['PC'] += 4
                
            elif next_opcode == 0x9C:  # CPY direct
                addr = self.memory[pc + 2]
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: CPY direct ${addr:02X}, Y=${self.registers['Y']:04X}, mem=${value:04X}")
                self._compare_16bit(self.registers['Y'], value)
                self.registers['PC'] += 3
                
            elif next_opcode == 0xBC:  # CPY extended
                addr_high = self.memory[pc + 2]
                addr_low = self.memory[pc + 3]
                addr = (addr_high << 8) | addr_low
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: CPY extended ${addr:04X}, Y=${self.registers['Y']:04X}, mem=${value:04X}")
                self._compare_16bit(self.registers['Y'], value)
                self.registers['PC'] += 4
                
            elif next_opcode == 0xAC:  # CPY indexed,Y
                offset = self.memory[pc + 2]
                addr = (self.registers['Y'] + offset) & 0xFFFF
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: CPY indexed,Y, Y=${self.registers['Y']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${value:04X}")
                self._compare_16bit(self.registers['Y'], value)
                self.registers['PC'] += 3
                
            elif next_opcode == 0x1A:  # ABY (Add B to Y)
                result = self.registers['Y'] + self.registers['B']
                self.debug_print(f"🔍 DEBUG: ABY, Y=${self.registers['Y']:04X}, B=${self.registers['B']:02X}, result=${result:04X}")
                self.registers['Y'] = result & 0xFFFF
                self.registers['PC'] += 2
                
            elif next_opcode == 0x3C:  # PSHY (Push Y to stack)
                self.debug_print(f"🔍 DEBUG: PSHY, Y=${self.registers['Y']:04X}, SP=${self.registers['SP']:04X}")
                self.memory[self.registers['SP']] = self.registers['Y'] & 0xFF
                self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
                self.memory[self.registers['SP']] = (self.registers['Y'] >> 8) & 0xFF
                self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
                self.registers['PC'] += 2
                
            elif next_opcode == 0x38:  # PULY (Pull Y from stack)
                self.debug_print(f"🔍 DEBUG: PULY, SP=${self.registers['SP']:04X}")
                self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
                high = self.memory[self.registers['SP']]
                self.registers['SP'] = (self.registers['SP'] + 1) & 0xFFFF
                low = self.memory[self.registers['SP']]
                self.registers['Y'] = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: PULY result, Y=${self.registers['Y']:04X}")
                self.registers['PC'] += 2
                
            elif next_opcode == 0x8F:  # XGDY (Exchange D and Y)
                d_value = (self.registers['A'] << 8) | self.registers['B']
                y_value = self.registers['Y']
                self.debug_print(f"🔍 DEBUG: XGDY, D=${d_value:04X}, Y=${y_value:04X}")
                self.registers['A'] = (y_value >> 8) & 0xFF
                self.registers['B'] = y_value & 0xFF
                self.registers['Y'] = d_value
                self.registers['PC'] += 2
                
            elif next_opcode == 0x30:  # TSY (Transfer SP to Y)
                self.debug_print(f"🔍 DEBUG: TSY, SP=${self.registers['SP']:04X}")
                self.registers['Y'] = (self.registers['SP'] + 1) & 0xFFFF
                self.registers['PC'] += 2
                
            elif next_opcode == 0x35:  # TYS (Transfer Y to SP)
                self.debug_print(f"🔍 DEBUG: TYS, Y=${self.registers['Y']:04X}")
                self.registers['SP'] = (self.registers['Y'] - 1) & 0xFFFF
                self.registers['PC'] += 2
                
            elif next_opcode == 0xCF:  # STS extended (Store Stack Pointer)
                addr_high = self.memory[pc + 2]
                addr_low = self.memory[pc + 3]
                addr = (addr_high << 8) | addr_low
                self.debug_print(f"🔍 DEBUG: STS extended ${addr:04X}, SP=${self.registers['SP']:04X}")
                self.memory[addr] = (self.registers['SP'] >> 8) & 0xFF
                self.memory[addr + 1] = self.registers['SP'] & 0xFF
                self._update_nz_flags(self.registers['SP'])
                self.registers['PC'] += 4
                
            elif next_opcode == 0xDC:  # LDD direct (M6811 extended)
                addr = self.memory[pc + 2]
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                self.debug_print(f"🔍 DEBUG: LDD direct (M6811) ${addr:02X}, value=${value:04X}")
                self.registers['A'] = high
                self.registers['B'] = low
                self._update_nz_flags(value)
                self.registers['PC'] += 3
                
            else:
                self.debug_print(f"❌ DEBUG: Unknown M6811 instruction $18 ${next_opcode:02X} at PC=${pc:04X}")
                self.execution_halted = True
                return False
            
        elif opcode == 0x8D:  # BSR (Branch to Subroutine)
            offset = self.memory[pc + 1]
            if offset & 0x80:  # Sign extend for negative offset
                offset = offset - 256
            
            # Calculate return address (PC + 2 for BSR instruction length)
            return_addr = (pc + 2) & 0xFFFF
            
            # Push return address to stack (high byte first)
            self.memory[self.registers['SP']] = (return_addr >> 8) & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.memory[self.registers['SP']] = return_addr & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            # Calculate target address
            target = (pc + 2 + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: BSR relative offset={offset}, return_addr=${return_addr:04X}, target=${target:04X}, SP=${self.registers['SP']:04X}")
            self.registers['PC'] = target
            
        elif opcode == 0xAD:  # JSR indexed
            offset = self.memory[pc + 1]
            target = (self.registers['X'] + offset) & 0xFFFF
            
            # Calculate return address (PC + 2 for JSR instruction length)
            return_addr = (pc + 2) & 0xFFFF
            
            # Push return address to stack (high byte first)
            self.memory[self.registers['SP']] = (return_addr >> 8) & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.memory[self.registers['SP']] = return_addr & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            self.debug_print(f"🔍 DEBUG: JSR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, target=${target:04X}, return_addr=${return_addr:04X}, SP=${self.registers['SP']:04X}")
            self.registers['PC'] = target
            
        elif opcode == 0xBD:  # JSR extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            target = (high << 8) | low
            
            # Calculate return address (PC + 3 for JSR instruction length)
            return_addr = (pc + 3) & 0xFFFF
            
            # Push return address to stack (high byte first)
            self.memory[self.registers['SP']] = (return_addr >> 8) & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            self.memory[self.registers['SP']] = return_addr & 0xFF
            self.registers['SP'] = (self.registers['SP'] - 1) & 0xFFFF
            
            self.debug_print(f"🔍 DEBUG: JSR extended to ${target:04X}, return_addr=${return_addr:04X}, SP=${self.registers['SP']:04X}")
            self.registers['PC'] = target
        
        elif opcode == 0xCB:  # ADDB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['B'], value, result)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
            
        # ADC (Add with Carry) Instructions
        elif opcode == 0x89:  # ADCA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCA immediate ${value:02X}, A=${self.registers['A']:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['A'], value, result, self.cc_flags['C'])
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0x99:  # ADCA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xB9:  # ADCA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 3
            
        elif opcode == 0xA9:  # ADCA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xC9:  # ADCB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCB immediate ${value:02X}, B=${self.registers['B']:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xD9:  # ADCB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xF9:  # ADCB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 3
            
        elif opcode == 0xE9:  # ADCB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] + value + self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: ADCB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
        
        # M6811 Prefix Instructions ($1A prefix)
        elif opcode == 0x1A:  # M6811 CPD Instructions
            if pc + 1 >= 0x10000:
                self.debug_print(f"❌ DEBUG: M6811 prefix $1A at PC=${pc:04X} but no next byte")
                self.execution_halted = True
                return False
                
            next_opcode = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: M6811 prefix $1A at PC=${pc:04X}, next opcode=${next_opcode:02X}")
            
            if next_opcode == 0x83:  # CPD immediate
                high = self.memory[pc + 2]
                low = self.memory[pc + 3]
                value = (high << 8) | low
                d_reg = (self.registers['A'] << 8) | self.registers['B']
                self.debug_print(f"🔍 DEBUG: CPD immediate ${value:04X}, D=${d_reg:04X}")
                self._compare_16bit(d_reg, value)
                self.registers['PC'] += 4
                
            elif next_opcode == 0x93:  # CPD direct
                addr = self.memory[pc + 2]
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                d_reg = (self.registers['A'] << 8) | self.registers['B']
                self.debug_print(f"🔍 DEBUG: CPD direct ${addr:02X}, D=${d_reg:04X}, mem=${value:04X}")
                self._compare_16bit(d_reg, value)
                self.registers['PC'] += 3
                
            elif next_opcode == 0xB3:  # CPD extended
                addr_high = self.memory[pc + 2]
                addr_low = self.memory[pc + 3]
                addr = (addr_high << 8) | addr_low
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                d_reg = (self.registers['A'] << 8) | self.registers['B']
                self.debug_print(f"🔍 DEBUG: CPD extended ${addr:04X}, D=${d_reg:04X}, mem=${value:04X}")
                self._compare_16bit(d_reg, value)
                self.registers['PC'] += 4
                
            elif next_opcode == 0xA3:  # CPD indexed
                offset = self.memory[pc + 2]
                addr = (self.registers['X'] + offset) & 0xFFFF
                high = self.memory[addr]
                low = self.memory[addr + 1]
                value = (high << 8) | low
                d_reg = (self.registers['A'] << 8) | self.registers['B']
                self.debug_print(f"🔍 DEBUG: CPD indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, D=${d_reg:04X}, mem=${value:04X}")
                self._compare_16bit(d_reg, value)
                self.registers['PC'] += 3
                
            else:
                self.debug_print(f"❌ DEBUG: Unknown M6811 instruction $1A ${next_opcode:02X} at PC=${pc:04X}")
                self.execution_halted = True
                return False
        
        # AND (Logical AND) Instructions
        elif opcode == 0x84:  # ANDA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: ANDA immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x94:  # ANDA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: ANDA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xB4:  # ANDA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: ANDA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xA4:  # ANDA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: ANDA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xC4:  # ANDB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: ANDB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xD4:  # ANDB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: ANDB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xF4:  # ANDB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: ANDB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xE4:  # ANDB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: ANDB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # AND always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # BIT (Bit Test) Instructions
        elif opcode == 0x85:  # BITA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: BITA immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x95:  # BITA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: BITA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xB5:  # BITA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: BITA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xA5:  # BITA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] & value
            self.debug_print(f"🔍 DEBUG: BITA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xC5:  # BITB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: BITB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xD5:  # BITB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: BITB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xF5:  # BITB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: BITB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xE5:  # BITB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] & value
            self.debug_print(f"🔍 DEBUG: BITB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.cc_flags['V'] = 0  # BIT always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # EOR (Exclusive OR) Instructions
        elif opcode == 0x88:  # EORA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] ^ value
            self.debug_print(f"🔍 DEBUG: EORA immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x98:  # EORA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] ^ value
            self.debug_print(f"🔍 DEBUG: EORA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xB8:  # EORA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] ^ value
            self.debug_print(f"🔍 DEBUG: EORA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xA8:  # EORA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] ^ value
            self.debug_print(f"🔍 DEBUG: EORA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xC8:  # EORB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] ^ value
            self.debug_print(f"🔍 DEBUG: EORB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xD8:  # EORB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] ^ value
            self.debug_print(f"🔍 DEBUG: EORB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xF8:  # EORB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] ^ value
            self.debug_print(f"🔍 DEBUG: EORB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xE8:  # EORB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] ^ value
            self.debug_print(f"🔍 DEBUG: EORB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # EOR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # ORA (Logical OR) Instructions 
        elif opcode == 0x8A:  # ORAA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] | value
            self.debug_print(f"🔍 DEBUG: ORAA immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x9A:  # ORAA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] | value
            self.debug_print(f"🔍 DEBUG: ORAA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xBA:  # ORAA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] | value
            self.debug_print(f"🔍 DEBUG: ORAA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xAA:  # ORAA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] | value
            self.debug_print(f"🔍 DEBUG: ORAA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xCA:  # ORAB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] | value
            self.debug_print(f"🔍 DEBUG: ORAB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xDA:  # ORAB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] | value
            self.debug_print(f"🔍 DEBUG: ORAB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0xFA:  # ORAB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] | value
            self.debug_print(f"🔍 DEBUG: ORAB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0xEA:  # ORAB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] | value
            self.debug_print(f"🔍 DEBUG: ORAB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 0  # ORA always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # SBC (Subtract with Carry) Instructions
        elif opcode == 0x82:  # SBCA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCA immediate ${value:02X}, A=${self.registers['A']:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0x92:  # SBCA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xB2:  # SBCA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 3
            
        elif opcode == 0xA2:  # SBCA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xC2:  # SBCB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCB immediate ${value:02X}, B=${self.registers['B']:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xD2:  # SBCB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xF2:  # SBCB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 3
            
        elif opcode == 0xE2:  # SBCB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] - value - self.cc_flags['C']
            self.debug_print(f"🔍 DEBUG: SBCB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={self.cc_flags['C']}, result=${result & 0xFF:02X}")
            self._update_carry_flag(result < 0)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
        
        # Remaining ADD Instructions (missing modes)
        elif opcode == 0x9B:  # ADDA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xBB:  # ADDA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 3
            
        elif opcode == 0xAB:  # ADDA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xDB:  # ADDB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xFB:  # ADDB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 3
            
        elif opcode == 0xEB:  # ADDB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_carry_flag(result > 255)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
        
        # Remaining SUB Instructions (missing modes)
        elif opcode == 0x80:  # SUBA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: SUBA immediate ${value:02X}, A=${self.registers['A']:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xB0:  # SUBA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: SUBA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 3
            
        elif opcode == 0xA0:  # SUBA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: SUBA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self.registers['A'] = result & 0xFF
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 2
            
        elif opcode == 0xC0:  # SUBB immediate
            value = self.memory[pc + 1]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: SUBB immediate ${value:02X}, B=${self.registers['B']:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xD0:  # SUBB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: SUBB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
            
        elif opcode == 0xE0:  # SUBB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: SUBB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
        
        # Remaining CMP Instructions (missing modes)
        elif opcode == 0xB1:  # CMPA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMPA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 3
            
        elif opcode == 0xA1:  # CMPA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMPA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['A'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
            
        elif opcode == 0xD1:  # CMPB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
            
        elif opcode == 0xF1:  # CMPB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 3
            
        elif opcode == 0xE1:  # CMPB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self._update_nz_flags(result & 0xFF)
            self.registers['PC'] += 2
        
        # Missing SUBB DIR mode
        elif opcode == 0xD0:  # SUBB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: SUBB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_carry_flag(self.registers['B'] < value)
            self.registers['B'] = result & 0xFF
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 2
        
        # TST (Test) Instructions
        elif opcode == 0x4D:  # TSTA (Test A)
            self.debug_print(f"🔍 DEBUG: TSTA, A=${self.registers['A']:02X}")
            self.cc_flags['V'] = 0  # TST always clears overflow
            self.cc_flags['C'] = 0  # TST always clears carry
            self._update_nz_flags(self.registers['A'])
            self.registers['PC'] += 1
            
        elif opcode == 0x5D:  # TSTB (Test B)
            self.debug_print(f"🔍 DEBUG: TSTB, B=${self.registers['B']:02X}")
            self.cc_flags['V'] = 0  # TST always clears overflow
            self.cc_flags['C'] = 0  # TST always clears carry
            self._update_nz_flags(self.registers['B'])
            self.registers['PC'] += 1
            
        elif opcode == 0x7D:  # TST extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: TST extended ${addr:04X}, mem=${value:02X}")
            self.cc_flags['V'] = 0  # TST always clears overflow
            self.cc_flags['C'] = 0  # TST always clears carry
            self._update_nz_flags(value)
            self.registers['PC'] += 3
            
        elif opcode == 0x6D:  # TST indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            self.debug_print(f"🔍 DEBUG: TST indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${value:02X}")
            self.cc_flags['V'] = 0  # TST always clears overflow
            self.cc_flags['C'] = 0  # TST always clears carry
            self._update_nz_flags(value)
            self.registers['PC'] += 2
        
        # ASL (Arithmetic Shift Left) Instructions
        elif opcode == 0x48:  # ASLA (Arithmetic Shift Left A)
            old_a = self.registers['A']
            result = (old_a << 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: ASLA, A=${old_a:02X} -> ${result:02X}")
            self.registers['A'] = result
            self.cc_flags['C'] = 1 if (old_a & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_a & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x58:  # ASLB (Arithmetic Shift Left B)
            old_b = self.registers['B']
            result = (old_b << 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: ASLB, B=${old_b:02X} -> ${result:02X}")
            self.registers['B'] = result
            self.cc_flags['C'] = 1 if (old_b & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_b & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x78:  # ASL extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = (old_value << 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: ASL extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_value & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x68:  # ASL indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = (old_value << 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: ASL indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_value & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # ASR (Arithmetic Shift Right) Instructions
        elif opcode == 0x47:  # ASRA (Arithmetic Shift Right A)
            old_a = self.registers['A']
            result = (old_a >> 1) | (old_a & 0x80)  # Preserve sign bit
            self.debug_print(f"🔍 DEBUG: ASRA, A=${old_a:02X} -> ${result:02X}")
            self.registers['A'] = result
            self.cc_flags['C'] = 1 if (old_a & 0x01) else 0
            self.cc_flags['V'] = 0  # ASR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x57:  # ASRB (Arithmetic Shift Right B)
            old_b = self.registers['B']
            result = (old_b >> 1) | (old_b & 0x80)  # Preserve sign bit
            self.debug_print(f"🔍 DEBUG: ASRB, B=${old_b:02X} -> ${result:02X}")
            self.registers['B'] = result
            self.cc_flags['C'] = 1 if (old_b & 0x01) else 0
            self.cc_flags['V'] = 0  # ASR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x77:  # ASR extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = (old_value >> 1) | (old_value & 0x80)  # Preserve sign bit
            self.debug_print(f"🔍 DEBUG: ASR extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x01) else 0
            self.cc_flags['V'] = 0  # ASR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x67:  # ASR indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = (old_value >> 1) | (old_value & 0x80)  # Preserve sign bit
            self.debug_print(f"🔍 DEBUG: ASR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x01) else 0
            self.cc_flags['V'] = 0  # ASR always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # LSR (Logical Shift Right) Instructions  
        elif opcode == 0x44:  # LSRA (Logical Shift Right A)
            old_a = self.registers['A']
            result = old_a >> 1
            self.debug_print(f"🔍 DEBUG: LSRA, A=${old_a:02X} -> ${result:02X}")
            self.registers['A'] = result
            self.cc_flags['C'] = 1 if (old_a & 0x01) else 0
            self.cc_flags['V'] = 1 if (old_a & 0x80) else 0  # Set if bit 7 was set
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x54:  # LSRB (Logical Shift Right B)
            old_b = self.registers['B']
            result = old_b >> 1
            self.debug_print(f"🔍 DEBUG: LSRB, B=${old_b:02X} -> ${result:02X}")
            self.registers['B'] = result
            self.cc_flags['C'] = 1 if (old_b & 0x01) else 0
            self.cc_flags['V'] = 1 if (old_b & 0x80) else 0  # Set if bit 7 was set
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x74:  # LSR extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = old_value >> 1
            self.debug_print(f"🔍 DEBUG: LSR extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x01) else 0
            self.cc_flags['V'] = 1 if (old_value & 0x80) else 0  # Set if bit 7 was set
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x64:  # LSR indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = old_value >> 1
            self.debug_print(f"🔍 DEBUG: LSR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x01) else 0
            self.cc_flags['V'] = 1 if (old_value & 0x80) else 0  # Set if bit 7 was set
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # ROL (Rotate Left) Instructions
        elif opcode == 0x49:  # ROLA (Rotate Left A)
            old_a = self.registers['A']
            old_carry = self.cc_flags['C']
            result = ((old_a << 1) | old_carry) & 0xFF
            self.debug_print(f"🔍 DEBUG: ROLA, A=${old_a:02X}, C={old_carry} -> A=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['C'] = 1 if (old_a & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_a & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x59:  # ROLB (Rotate Left B)
            old_b = self.registers['B']
            old_carry = self.cc_flags['C']
            result = ((old_b << 1) | old_carry) & 0xFF
            self.debug_print(f"🔍 DEBUG: ROLB, B=${old_b:02X}, C={old_carry} -> B=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['C'] = 1 if (old_b & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_b & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x79:  # ROL extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            old_carry = self.cc_flags['C']
            result = ((old_value << 1) | old_carry) & 0xFF
            self.debug_print(f"🔍 DEBUG: ROL extended ${addr:04X}, mem=${old_value:02X}, C={old_carry} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_value & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x69:  # ROL indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            old_carry = self.cc_flags['C']
            result = ((old_value << 1) | old_carry) & 0xFF
            self.debug_print(f"🔍 DEBUG: ROL indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X}, C={old_carry} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x80) else 0
            self.cc_flags['V'] = 1 if ((old_value & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # ROR (Rotate Right) Instructions
        elif opcode == 0x46:  # RORA (Rotate Right A)
            old_a = self.registers['A']
            old_carry = self.cc_flags['C']
            result = (old_a >> 1) | (old_carry << 7)
            self.debug_print(f"🔍 DEBUG: RORA, A=${old_a:02X}, C={old_carry} -> A=${result:02X}")
            self.registers['A'] = result
            self.cc_flags['C'] = 1 if (old_a & 0x01) else 0
            self.cc_flags['V'] = 1 if ((old_a & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x56:  # RORB (Rotate Right B)
            old_b = self.registers['B']
            old_carry = self.cc_flags['C']
            result = (old_b >> 1) | (old_carry << 7)
            self.debug_print(f"🔍 DEBUG: RORB, B=${old_b:02X}, C={old_carry} -> B=${result:02X}")
            self.registers['B'] = result
            self.cc_flags['C'] = 1 if (old_b & 0x01) else 0
            self.cc_flags['V'] = 1 if ((old_b & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x76:  # ROR extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            old_carry = self.cc_flags['C']
            result = (old_value >> 1) | (old_carry << 7)
            self.debug_print(f"🔍 DEBUG: ROR extended ${addr:04X}, mem=${old_value:02X}, C={old_carry} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x01) else 0
            self.cc_flags['V'] = 1 if ((old_value & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x66:  # ROR indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            old_carry = self.cc_flags['C']
            result = (old_value >> 1) | (old_carry << 7)
            self.debug_print(f"🔍 DEBUG: ROR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X}, C={old_carry} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if (old_value & 0x01) else 0
            self.cc_flags['V'] = 1 if ((old_value & 0x80) != (result & 0x80)) else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # CLR (Clear) Instructions
        elif opcode == 0x4F:  # CLRA (Clear A)
            self.debug_print("🔍 DEBUG: CLRA")
            self.registers['A'] = 0x00
            self.cc_flags['N'] = 0
            self.cc_flags['Z'] = 1
            self.cc_flags['V'] = 0
            self.cc_flags['C'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x5F:  # CLRB (Clear B)
            self.debug_print("🔍 DEBUG: CLRB")
            self.registers['B'] = 0x00
            self.cc_flags['N'] = 0
            self.cc_flags['Z'] = 1
            self.cc_flags['V'] = 0
            self.cc_flags['C'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 1
            
        elif opcode == 0x0F:  # CLR direct
            addr = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: CLR direct ${addr:02X}")
            self.memory[addr] = 0x00
            self.cc_flags['N'] = 0
            self.cc_flags['Z'] = 1
            self.cc_flags['V'] = 0
            self.cc_flags['C'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 2
            
        elif opcode == 0x7F:  # CLR extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            self.debug_print(f"🔍 DEBUG: CLR extended ${addr:04X}")
            self.memory[addr] = 0x00
            self.cc_flags['N'] = 0
            self.cc_flags['Z'] = 1
            self.cc_flags['V'] = 0
            self.cc_flags['C'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 3
            
        elif opcode == 0x6F:  # CLR indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            self.debug_print(f"🔍 DEBUG: CLR indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}")
            self.memory[addr] = 0x00
            self.cc_flags['N'] = 0
            self.cc_flags['Z'] = 1
            self.cc_flags['V'] = 0
            self.cc_flags['C'] = 0
            self._pack_cc_register()
            self.registers['PC'] += 2
        
        # COM (Complement) Instructions
        elif opcode == 0x43:  # COMA (Complement A)
            old_a = self.registers['A']
            result = (~old_a) & 0xFF
            self.debug_print(f"🔍 DEBUG: COMA, A=${old_a:02X} -> ${result:02X}")
            self.registers['A'] = result
            self.cc_flags['C'] = 1  # COM always sets carry
            self.cc_flags['V'] = 0  # COM always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x03:  # COM direct
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            result = (~old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: COM direct ${addr:02X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1  # COM always sets carry
            self.cc_flags['V'] = 0  # COM always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x73:  # COM extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = (~old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: COM extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1  # COM always sets carry
            self.cc_flags['V'] = 0  # COM always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x63:  # COM indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = (~old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: COM indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1  # COM always sets carry
            self.cc_flags['V'] = 0  # COM always clears overflow
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # NEG (Negate) Instructions - Memory modes
        elif opcode == 0x00:  # NEG direct
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            result = (256 - old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEG direct ${addr:02X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if old_value != 0 else 0
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x70:  # NEG extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = (256 - old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEG extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if old_value != 0 else 0
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x60:  # NEG indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = (256 - old_value) & 0xFF
            self.debug_print(f"🔍 DEBUG: NEG indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['C'] = 1 if old_value != 0 else 0
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # INC (Increment) Instructions
        elif opcode == 0x4C:  # INCA (Increment A)
            old_a = self.registers['A']
            result = (old_a + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INCA, A=${old_a:02X} -> ${result:02X}")
            self.registers['A'] = result
            self.cc_flags['V'] = 1 if old_a == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x5C:  # INCB (Increment B)
            old_b = self.registers['B']
            result = (old_b + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INCB, B=${old_b:02X} -> ${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 1 if old_b == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x0C:  # INC direct
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            result = (old_value + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INC direct ${addr:02X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x7C:  # INC extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = (old_value + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INC extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x6C:  # INC indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = (old_value + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INC indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        # DEC (Decrement) Instructions - Memory modes
        elif opcode == 0x0A:  # DEC direct
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            result = (old_value - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DEC direct ${addr:02X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0  # Overflow if $80 -> $7F
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x7A:  # DEC extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            old_value = self.memory[addr]
            result = (old_value - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DEC extended ${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0  # Overflow if $80 -> $7F
            self._update_nz_flags(result)
            self.registers['PC'] += 3
            
        elif opcode == 0x6A:  # DEC indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            old_value = self.memory[addr]
            result = (old_value - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DEC indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0  # Overflow if $80 -> $7F
            self._update_nz_flags(result)
            self.registers['PC'] += 2
        
        else:
            self.debug_print(f"❌ DEBUG: Unknown opcode ${opcode:02X} at PC=${pc:04X}")
            self.execution_halted = True
            return False
        
        return True 
    
    def _update_nz_flags(self, value):
        """Update N and Z flags based on value."""
        self.cc_flags['N'] = 1 if (value & 0x80) else 0
        self.cc_flags['Z'] = 1 if value == 0 else 0
        self._pack_cc_register()
    
    def _compare_16bit(self, reg_value, compare_value):
        """Compare two 16-bit values and update flags."""
        result = reg_value - compare_value
        
        # Update flags
        self.cc_flags['Z'] = 1 if result == 0 else 0
        self.cc_flags['N'] = 1 if (result & 0x8000) else 0
        self.cc_flags['C'] = 1 if reg_value < compare_value else 0
        
        # Overflow flag (V)
        # Set if the signs of the operands are different and the sign of the result
        # differs from the sign of the minuend
        reg_sign = reg_value & 0x8000
        comp_sign = compare_value & 0x8000
        result_sign = result & 0x8000
        
        if reg_sign != comp_sign and reg_sign != result_sign:
            self.cc_flags['V'] = 1
        else:
            self.cc_flags['V'] = 0
            
        self._pack_cc_register()
    
    def _update_carry_flag(self, carry: bool):
        """Update carry flag and pack CC register."""
        self.debug_print(f"🚩 DEBUG: Carry flag updated: {self.cc_flags['C']}->{1 if carry else 0}")
        self.cc_flags['C'] = 1 if carry else 0
        self._pack_cc_register()
    
    def _update_half_carry_flag(self, operand1: int, operand2: int, carry_in: int = 0):
        """Update half-carry flag based on bit 3 to bit 4 carry."""
        # Calculate carry from bit 3 to bit 4
        half_carry = ((operand1 & 0x0F) + (operand2 & 0x0F) + carry_in) > 0x0F
        self.cc_flags['H'] = 1 if half_carry else 0
        self.debug_print(f"🚩 DEBUG: Half-carry flag updated: H={self.cc_flags['H']}")
        
    def _update_arithmetic_flags(self, operand1: int, operand2: int, result: int, carry_in: int = 0):
        """Update all arithmetic flags for ADD/ADC operations."""
        # Update half-carry flag
        self._update_half_carry_flag(operand1, operand2, carry_in)
        
        # Update carry flag
        self._update_carry_flag(result > 255)
        
        # Update N and Z flags
        self._update_nz_flags(result & 0xFF)
        
        # Update V flag for signed overflow
        # Overflow occurs when adding two positive numbers gives negative result
        # or adding two negative numbers gives positive result
        operand1_sign = operand1 & 0x80
        operand2_sign = operand2 & 0x80
        result_sign = (result & 0xFF) & 0x80
        
        if operand1_sign == operand2_sign and operand1_sign != result_sign:
            self.cc_flags['V'] = 1
        else:
            self.cc_flags['V'] = 0
            
        self._pack_cc_register()
    
    def _pack_cc_register(self):
        """Pack condition code flags into CC register."""
        self.registers['CC'] = (
            (self.cc_flags['H'] << 5) |
            (self.cc_flags['I'] << 4) |
            (self.cc_flags['N'] << 3) |
            (self.cc_flags['Z'] << 2) |
            (self.cc_flags['V'] << 1) |
            (self.cc_flags['C'] << 0)
        )
    
    def _unpack_cc_register(self):
        """Unpack CC register into individual flags."""
        cc = self.registers['CC']
        self.cc_flags['H'] = (cc >> 5) & 1
        self.cc_flags['I'] = (cc >> 4) & 1
        self.cc_flags['N'] = (cc >> 3) & 1
        self.cc_flags['Z'] = (cc >> 2) & 1
        self.cc_flags['V'] = (cc >> 1) & 1
        self.cc_flags['C'] = (cc >> 0) & 1
    
    # Public interface methods
    def get_state(self) -> Dict[str, Any]:
        """Get complete simulator state."""
        return {
            'registers': self.registers.copy(),
            'flags': self.cc_flags.copy(),
            'halted': self.execution_halted,
            'instruction_count': self.instruction_count,
            'program_loaded': bool(self.program_data),
            'program_start': self.program_start
        }
    
    def get_memory_dump(self, start_addr: int = None, length: int = 256) -> str:
        """Get formatted memory dump."""
        if start_addr is None:
            # Show memory around program area
            if self.program_data:
                start_addr = min(self.program_data.keys())
                start_addr = (start_addr // 16) * 16  # Align to 16-byte boundary
            else:
                start_addr = 0x1000  # Default start
        
        # Ensure start address is valid
        start_addr = max(0, min(start_addr, 0xFFFF))
        end_addr = min(start_addr + length, 0x10000)
        
        dump = f"Memory Dump (${start_addr:04X} - ${end_addr-1:04X}):\n"
        dump += "Address  +0 +1 +2 +3 +4 +5 +6 +7 +8 +9 +A +B +C +D +E +F  ASCII\n"
        dump += "-" * 70 + "\n"
        
        for addr in range(start_addr, end_addr, 16):
            # Address column
            line = f"{addr:04X}:   "
            
            # Hex values
            hex_part = ""
            ascii_part = ""
            
            for i in range(16):
                byte_addr = addr + i
                if byte_addr < end_addr:
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
            dump += line + "\n"
            
            # Limit output to reasonable size
            if len(dump) > 4000:
                dump += "... (truncated)\n"
                break
        
        return dump
    
    def get_memory_value(self, address: int) -> int:
        """Get value from memory address."""
        if 0 <= address <= 0xFFFF:
            return self.memory[address]
        return 0
    
    def set_memory_value(self, address: int, value: int):
        """Set value at memory address."""
        if 0 <= address <= 0xFFFF:
            self.memory[address] = value & 0xFF
    
    def get_register_value(self, register: str) -> int:
        """Get register value by name."""
        return self.registers.get(register, 0)
    
    def set_register_value(self, register: str, value: int):
        """Set register value by name."""
        if register in self.registers:
            if register in ['A', 'B', 'CC']:
                self.registers[register] = value & 0xFF
            elif register in ['X', 'Y', 'SP', 'PC']:
                self.registers[register] = value & 0xFFFF
            else:
                self.registers[register] = value
                
            # Update flags if CC register was modified
            if register == 'CC':
                self._unpack_cc_register()
    
    def is_halted(self) -> bool:
        """Check if simulator is halted."""
        return self.execution_halted
    
    def get_instruction_count(self) -> int:
        """Get number of instructions executed."""
        return self.instruction_count

def main():
    """Test the simulator with a simple program."""
    simulator = M6800Simulator()
    
    # Simple test program
    test_program = {
        0x1000: 0x86,  # LDA #$55
        0x1001: 0x55,
        0x1002: 0xB7,  # STA $2000
        0x1003: 0x20,
        0x1004: 0x00,
        0x1005: 0x00   # BRK
    }
    
    print("Loading test program...")
    simulator.load_program(test_program)
    
    print("\nRunning simulation...")
    steps = simulator.run()
    
    print(f"\nSimulation completed in {steps} steps")
    print(f"Final state: {simulator.get_state()}")
    print(f"\nMemory dump:")
    print(simulator.get_memory_dump(0x1000, 64))

if __name__ == "__main__":
    main() 