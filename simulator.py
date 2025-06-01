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
        
        if opcode == 0x01:  # NOP
            self.debug_print("🔍 DEBUG: NOP")
            self.registers['PC'] += 1
            
        # CRITICAL: Memory operations must be checked before their inherent counterparts
        # to resolve opcode conflicts (longer instructions have priority)
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
            
        elif opcode == 0x0A:  # DEC direct
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            result = (old_value - 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: DEC direct ${addr:02X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x80 else 0  # Overflow if $80 -> $7F
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
        elif opcode == 0x0C:  # INC direct
            addr = self.memory[pc + 1]
            old_value = self.memory[addr]
            result = (old_value + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INC direct ${addr:02X}, mem=${old_value:02X} -> ${result:02X}")
            self.memory[addr] = result
            self.cc_flags['V'] = 1 if old_value == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 2
            
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
            
        elif opcode == 0x0B:  # SEV (Set Overflow flag)
            self.debug_print("🔍 DEBUG: SEV - setting overflow flag")
            self.cc_flags['V'] = 1
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
            self.cc_flags['C'] = 0  # MUL always clears the carry flag
            self.cc_flags['V'] = 0  # MUL always clears the overflow flag
            self._update_nz_flags(result)  # Update N and Z flags for 16-bit result
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
            
        elif opcode == 0x9B:  # ADDA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['A'], value, result)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xBB:  # ADDA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['A'], value, result)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 3
            
        elif opcode == 0xAB:  # ADDA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] + value
            self.debug_print(f"🔍 DEBUG: ADDA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result:02X}")
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
            
        elif opcode == 0xDB:  # ADDB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['B'], value, result)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xFB:  # ADDB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['B'], value, result)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 3
            
        elif opcode == 0xEB:  # ADDB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] + value
            self.debug_print(f"🔍 DEBUG: ADDB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result:02X}")
            self._update_arithmetic_flags(self.registers['B'], value, result)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
            
        # SBC (Subtract with Carry) Instructions
        elif opcode == 0x82:  # SBCA immediate
            value = self.memory[pc + 1]
            carry = self.cc_flags['C']
            result = self.registers['A'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCA immediate ${value:02X}, A=${self.registers['A']:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result, carry)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0x92:  # SBCA direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            carry = self.cc_flags['C']
            result = self.registers['A'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result, carry)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xB2:  # SBCA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            carry = self.cc_flags['C']
            result = self.registers['A'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result, carry)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 3
            
        elif opcode == 0xA2:  # SBCA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            carry = self.cc_flags['C']
            result = self.registers['A'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result, carry)
            self.registers['A'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xC2:  # SBCB immediate
            value = self.memory[pc + 1]
            carry = self.cc_flags['C']
            result = self.registers['B'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCB immediate ${value:02X}, B=${self.registers['B']:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result, carry)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xD2:  # SBCB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            carry = self.cc_flags['C']
            result = self.registers['B'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result, carry)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
            
        elif opcode == 0xF2:  # SBCB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            carry = self.cc_flags['C']
            result = self.registers['B'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result, carry)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 3
            
        elif opcode == 0xE2:  # SBCB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            carry = self.cc_flags['C']
            result = self.registers['B'] - value - carry
            self.debug_print(f"🔍 DEBUG: SBCB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, C={carry}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result, carry)
            self.registers['B'] = result & 0xFF
            self.registers['PC'] += 2
        
        # Remaining CMP Instructions (missing modes)
        elif opcode == 0xB1:  # CMPA extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMPA extended ${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result)
            self.registers['PC'] += 3
            
        elif opcode == 0xA1:  # CMPA indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMPA indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result)
            self.registers['PC'] += 2
            
        elif opcode == 0xD1:  # CMPB direct
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB direct ${addr:02X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result)
            self.registers['PC'] += 2
            
        elif opcode == 0xF1:  # CMPB extended
            high = self.memory[pc + 1]
            low = self.memory[pc + 2]
            addr = (high << 8) | low
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB extended ${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result)
            self.registers['PC'] += 3
            
        elif opcode == 0xE1:  # CMPB indexed
            offset = self.memory[pc + 1]
            addr = (self.registers['X'] + offset) & 0xFFFF
            value = self.memory[addr]
            result = self.registers['B'] - value
            self.debug_print(f"🔍 DEBUG: CMPB indexed, X=${self.registers['X']:04X}, offset=${offset:02X}, addr=${addr:04X}, B=${self.registers['B']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['B'], value, result)
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
            self.cc_flags['V'] = 0  # LSR always clears V flag
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
        elif opcode == 0x54:  # LSRB (Logical Shift Right B)
            old_b = self.registers['B']
            result = old_b >> 1
            self.debug_print(f"🔍 DEBUG: LSRB, B=${old_b:02X} -> ${result:02X}")
            self.registers['B'] = result
            self.cc_flags['C'] = 1 if (old_b & 0x01) else 0
            self.cc_flags['V'] = 0  # LSR always clears V flag
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
            self.cc_flags['V'] = 0  # LSR always clears V flag
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
            self.cc_flags['V'] = 0  # LSR always clears V flag
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
            
        elif opcode == 0x5C:  # INCB (Increment B)
            old_b = self.registers['B']
            result = (old_b + 1) & 0xFF
            self.debug_print(f"🔍 DEBUG: INCB, B=${old_b:02X} -> ${result:02X}")
            self.registers['B'] = result
            self.cc_flags['V'] = 1 if old_b == 0x7F else 0  # Overflow if $7F -> $80
            self._update_nz_flags(result)
            self.registers['PC'] += 1
            
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
            
        elif opcode == 0x81:  # CMPA immediate
            value = self.memory[pc + 1]
            result = self.registers['A'] - value
            self.debug_print(f"🔍 DEBUG: CMPA immediate ${value:02X}, A={self.registers['A']:02X}, result={result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result)
            self.registers['PC'] += 2
            
        elif opcode == 0x91:  # CMPA direct  
            addr = self.memory[pc + 1]
            value = self.memory[addr]
            result = self.registers['A'] - value
            self.debug_print(f"DEBUG: CMPA direct ${addr:02X}, A=${self.registers['A']:02X}, mem=${value:02X}, result=${result & 0xFF:02X}")
            self._update_subtraction_flags(self.registers['A'], value, result)
            self.registers['PC'] += 2
            
        elif opcode == 0x1C:  # ANDCC immediate (AND with Condition Code register)
            mask = self.memory[pc + 1]
            self.debug_print(f"🔍 DEBUG: ANDCC immediate ${mask:02X}, CC=${self.registers.get('CC', 0):02X}")
            # AND the CC register with the immediate mask
            if 'CC' not in self.registers:
                self._pack_cc_register()  # Ensure CC register exists
            self.registers['CC'] = self.registers['CC'] & mask
            self._unpack_cc_register()  # Update individual flags
            self.debug_print(f"🔍 DEBUG: ANDCC result CC=${self.registers['CC']:02X}")
            self.registers['PC'] += 2
            
        else:
            # Unknown opcode - halt execution
            self.debug_print(f"❌ DEBUG: Unknown opcode ${opcode:02X} at PC=${pc:04X} - halting execution")
            self.execution_halted = True
    
    def get_memory_value(self, address: int) -> int:
        """Get value from memory address."""
        if 0 <= address <= 0xFFFF:
            return self.memory[address]
        return 0
    

    def get_register_value(self, register_name: str) -> int:
        """Get the value of a specific register."""
        if register_name in self.registers:
            return self.registers[register_name]
        return 0
    
    def get_memory_dump(self, start_addr: int = 0x1000, length: int = 256) -> str:
        """
        Generate a formatted memory dump for display.
        
        Args:
            start_addr: Starting address for the dump
            length: Number of bytes to dump
            
        Returns:
            Formatted string with memory contents
        """
        dump_lines = []
        
        # If no program is loaded, show from program start or 0x1000
        if hasattr(self, 'program_data') and self.program_data:
            # Show memory around the program
            min_addr = min(self.program_data.keys())
            max_addr = max(self.program_data.keys())
            start_addr = min_addr & 0xFFF0  # Align to 16-byte boundary
            end_addr = min(0xFFFF, max_addr + 64)
        else:
            # Default view
            end_addr = min(0xFFFF, start_addr + length)
        
        # Generate header
        dump_lines.append('       00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F')
        dump_lines.append('     ' + '-' * 48)
        
        current_addr = start_addr
        while current_addr <= end_addr:
            # Address column
            line = f'{current_addr:04X}: '
            
            # Hex bytes
            hex_bytes = []
            ascii_chars = []
            
            for i in range(16):
                addr = current_addr + i
                if addr <= end_addr and addr <= 0xFFFF:
                    byte_val = self.memory[addr]
                    hex_bytes.append(f'{byte_val:02X}')
                    
                    # ASCII representation
                    if 32 <= byte_val <= 126:
                        ascii_chars.append(chr(byte_val))
                    else:
                        ascii_chars.append('.')
                else:
                    hex_bytes.append('  ')
                    ascii_chars.append(' ')
            
            line += ' '.join(hex_bytes)
            line += '  ' + ''.join(ascii_chars)
            
            dump_lines.append(line)
            current_addr += 16
            
            # Limit output size
            if len(dump_lines) > 50:
                dump_lines.append('... (output truncated)')
                break
        
        return chr(10).join(dump_lines)
    def _update_nz_flags(self, value: int):
        """Update N and Z flags based on result value."""
        # Handle both 8-bit and 16-bit values
        if value > 0xFF:
            # 16-bit value
            self.cc_flags['N'] = 1 if (value & 0x8000) else 0
            self.cc_flags['Z'] = 1 if (value & 0xFFFF) == 0 else 0
        else:
            # 8-bit value
            self.cc_flags['N'] = 1 if (value & 0x80) else 0
            self.cc_flags['Z'] = 1 if (value & 0xFF) == 0 else 0
        self._pack_cc_register()
    
    def _update_carry_flag(self, carry: bool):
        """Update carry flag."""
        self.cc_flags['C'] = 1 if carry else 0
        self._pack_cc_register()
    
    def _update_arithmetic_flags(self, operand1: int, operand2: int, result: int, carry_in: int = 0):
        """
        Update arithmetic flags for addition operations.
        
        Args:
            operand1: First operand
            operand2: Second operand  
            result: Result of operation
            carry_in: Input carry (for ADC operations)
        """
        # Handle both 8-bit and 16-bit operations
        if operand1 > 0xFF or operand2 > 0xFF or result > 0xFFFF:
            # 16-bit operation
            mask = 0xFFFF
            sign_bit = 0x8000
            half_carry_mask = 0x0FFF  # Half carry from bit 11 to 12 for 16-bit
        else:
            # 8-bit operation  
            mask = 0xFF
            sign_bit = 0x80
            half_carry_mask = 0x0F  # Half carry from bit 3 to 4 for 8-bit
        
        # Normalize operands and result
        op1 = operand1 & mask
        op2 = operand2 & mask
        res = result & mask
        
        # Update N and Z flags
        self.cc_flags['N'] = 1 if (res & sign_bit) else 0
        self.cc_flags['Z'] = 1 if res == 0 else 0
        
        # Update C flag (carry/overflow for unsigned arithmetic)
        self.cc_flags['C'] = 1 if result > mask else 0
        
        # Update V flag (overflow for signed arithmetic)
        # V is set if both operands have same sign, but result has different sign
        op1_sign = (op1 & sign_bit) != 0
        op2_sign = (op2 & sign_bit) != 0  
        res_sign = (res & sign_bit) != 0
        self.cc_flags['V'] = 1 if (op1_sign == op2_sign) and (op1_sign != res_sign) else 0
        
        # Update H flag (half carry for BCD operations)
        # For 8-bit: carry from bit 3 to bit 4
        # For 16-bit: carry from bit 11 to bit 12
        half_result = (op1 & half_carry_mask) + (op2 & half_carry_mask) + carry_in
        self.cc_flags['H'] = 1 if half_result > half_carry_mask else 0
        
        self._pack_cc_register()
    
    def _update_subtraction_flags(self, minuend: int, subtrahend: int, result: int, borrow_in: int = 0):
        """
        Update flags for subtraction operations (SUB, SBC, CMP).
        
        Args:
            minuend: Value being subtracted from
            subtrahend: Value being subtracted
            result: Result of subtraction
            borrow_in: Input borrow (for SBC operations)
        """
        # Handle both 8-bit and 16-bit operations
        if minuend > 0xFF or subtrahend > 0xFF:
            # 16-bit operation
            mask = 0xFFFF
            sign_bit = 0x8000
        else:
            # 8-bit operation
            mask = 0xFF
            sign_bit = 0x80
        
        # Normalize operands and result
        min_val = minuend & mask
        sub_val = subtrahend & mask
        res = result & mask
        
        # Update N and Z flags
        self.cc_flags['N'] = 1 if (res & sign_bit) else 0
        self.cc_flags['Z'] = 1 if res == 0 else 0
        
        # Update C flag (borrow for subtraction)
        # C is set if there was a borrow (unsigned underflow)
        unsigned_result = minuend - subtrahend - borrow_in
        self.cc_flags['C'] = 1 if unsigned_result < 0 else 0
        
        # Update V flag (overflow for signed subtraction)
        # V is set if operands have different signs, and result has different sign than minuend
        min_sign = (min_val & sign_bit) != 0
        sub_sign = (sub_val & sign_bit) != 0
        res_sign = (res & sign_bit) != 0
        self.cc_flags['V'] = 1 if (min_sign != sub_sign) and (min_sign != res_sign) else 0
        
        self._pack_cc_register()
    
    def _pack_cc_register(self):
        """Pack individual condition code flags into CC register."""
        # M6800 CC register bit layout:
        # Bit 7: Not used (always 1)
        # Bit 6: Not used (always 1)  
        # Bit 5: H (Half Carry)
        # Bit 4: I (Interrupt mask)
        # Bit 3: N (Negative)
        # Bit 2: Z (Zero)
        # Bit 1: V (Overflow)
        # Bit 0: C (Carry)
        
        self.registers['CC'] = (
            0xC0 |  # Bits 7-6 always set
            (self.cc_flags['H'] << 5) |
            (self.cc_flags['I'] << 4) |
            (self.cc_flags['N'] << 3) |
            (self.cc_flags['Z'] << 2) |
            (self.cc_flags['V'] << 1) |
            (self.cc_flags['C'] << 0)
        )
    
    def _unpack_cc_register(self):
        """Unpack CC register into individual condition code flags."""
        cc = self.registers['CC']
        self.cc_flags['H'] = (cc >> 5) & 1
        self.cc_flags['I'] = (cc >> 4) & 1
        self.cc_flags['N'] = (cc >> 3) & 1
        self.cc_flags['Z'] = (cc >> 2) & 1
        self.cc_flags['V'] = (cc >> 1) & 1
        self.cc_flags['C'] = (cc >> 0) & 1