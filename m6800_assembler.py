#!/usr/bin/env python3
"""
Motorola 6800 Assembler Core Module
Handles instruction parsing, validation, and machine code generation.
"""

import re
from typing import Dict, List, Tuple, Optional, Any

class M6800Assembler:
    """Core assembler class for Motorola 6800 processor."""
    
    def __init__(self):
        """Initialize the assembler with instruction set and addressing modes."""
        self.instruction_set = self._build_instruction_set()
        self.labels = {}  # Label name -> address mapping
        self.current_address = 0x0000
        self.origin_address = 0x0000
        self.assembled_lines = []
        self.errors = []
        self.messages = []
        
    def _build_instruction_set(self) -> Dict[str, Dict]:
        """Build the complete M6800 instruction set with opcodes and addressing modes."""
        return {
            # Accumulator and Memory Operations
            'ABA': {'IMM': None, 'DIR': None, 'EXT': None, 'IDX': None, 'INH': 0x1B},
            'ADC': {'IMM': {'A': 0x89, 'B': 0xC9}, 'DIR': {'A': 0x99, 'B': 0xD9}, 
                   'EXT': {'A': 0xB9, 'B': 0xF9}, 'IDX': {'A': 0xA9, 'B': 0xE9}},
            'ADD': {'IMM': {'A': 0x8B, 'B': 0xCB}, 'DIR': {'A': 0x9B, 'B': 0xDB}, 
                   'EXT': {'A': 0xBB, 'B': 0xFB}, 'IDX': {'A': 0xAB, 'B': 0xEB}},
            'AND': {'IMM': {'A': 0x84, 'B': 0xC4}, 'DIR': {'A': 0x94, 'B': 0xD4}, 
                   'EXT': {'A': 0xB4, 'B': 0xF4}, 'IDX': {'A': 0xA4, 'B': 0xE4}},
            'ASL': {'DIR': 0x08, 'EXT': 0x78, 'IDX': 0x68, 'INH': {'A': 0x48, 'B': 0x58}},
            'ASR': {'DIR': 0x07, 'EXT': 0x77, 'IDX': 0x67, 'INH': {'A': 0x47, 'B': 0x57}},
            
            # Branch Instructions
            'BCC': {'REL': 0x24}, 'BCS': {'REL': 0x25}, 'BEQ': {'REL': 0x27},
            'BGE': {'REL': 0x2C}, 'BGT': {'REL': 0x2E}, 'BHI': {'REL': 0x22},
            'BLE': {'REL': 0x2F}, 'BLS': {'REL': 0x23}, 'BLT': {'REL': 0x2D},
            'BMI': {'REL': 0x2B}, 'BNE': {'REL': 0x26}, 'BPL': {'REL': 0x2A},
            'BRA': {'REL': 0x20}, 'BSR': {'REL': 0x8D}, 'BVC': {'REL': 0x28},
            'BVS': {'REL': 0x29},
            
            # Bit Test Operations
            'BIT': {'IMM': {'A': 0x85, 'B': 0xC5}, 'DIR': {'A': 0x95, 'B': 0xD5}, 
                   'EXT': {'A': 0xB5, 'B': 0xF5}, 'IDX': {'A': 0xA5, 'B': 0xE5}},
            
            # Clear, Complement, Negate
            'CBA': {'INH': 0x11},
            'CLC': {'INH': 0x0C}, 'CLI': {'INH': 0x0E}, 'CLR': {'DIR': 0x0F, 'EXT': 0x7F, 'IDX': 0x6F, 'INH': {'A': 0x4F, 'B': 0x5F}},
            'CLV': {'INH': 0x0A}, 'CMP': {'IMM': {'A': 0x81, 'B': 0xC1}, 'DIR': {'A': 0x91, 'B': 0xD1}, 
                   'EXT': {'A': 0xB1, 'B': 0xF1}, 'IDX': {'A': 0xA1, 'B': 0xE1}},
            'COM': {'DIR': 0x03, 'EXT': 0x73, 'IDX': 0x63, 'INH': {'A': 0x43, 'B': 0x53}},
            'CPX': {'IMM': 0x8C, 'DIR': 0x9C, 'EXT': 0xBC, 'IDX': 0xAC},
            
            # Decimal Adjust
            'DAA': {'INH': 0x19},
            
            # Decrement, Increment
            'DEC': {'DIR': 0x0A, 'EXT': 0x7A, 'IDX': 0x6A, 'INH': {'A': 0x4A, 'B': 0x5A}},
            'DES': {'INH': 0x34}, 'DEX': {'INH': 0x09},
            'EOR': {'IMM': {'A': 0x88, 'B': 0xC8}, 'DIR': {'A': 0x98, 'B': 0xD8}, 
                   'EXT': {'A': 0xB8, 'B': 0xF8}, 'IDX': {'A': 0xA8, 'B': 0xE8}},
            'INC': {'DIR': 0x0C, 'EXT': 0x7C, 'IDX': 0x6C, 'INH': {'A': 0x4C, 'B': 0x5C}},
            'INS': {'INH': 0x31}, 'INX': {'INH': 0x08},
            
            # Jump and Jump to Subroutine
            'JMP': {'EXT': 0x7E, 'IDX': 0x6E},
            'JSR': {'EXT': 0xBD, 'IDX': 0xAD},
            
            # Load Accumulator
            'LDA': {'IMM': 0x86, 'DIR': 0x96, 'EXT': 0xB6, 'IDX': 0xA6},
            'LDB': {'IMM': 0xC6, 'DIR': 0xD6, 'EXT': 0xF6, 'IDX': 0xE6},
            'LDX': {'IMM': 0xCE, 'DIR': 0xDE, 'EXT': 0xFE, 'IDX': 0xEE},
            'LDS': {'IMM': 0x8E, 'DIR': 0x9E, 'EXT': 0xBE, 'IDX': 0xAE},
            
            # Logical Shift
            'LSR': {'DIR': 0x04, 'EXT': 0x74, 'IDX': 0x64, 'INH': {'A': 0x44, 'B': 0x54}},
            
            # No Operation
            'NOP': {'INH': 0x01},
            
            # OR Operations
            'ORA': {'IMM': 0x8A, 'DIR': 0x9A, 'EXT': 0xBA, 'IDX': 0xAA},
            'ORB': {'IMM': 0xCA, 'DIR': 0xDA, 'EXT': 0xFA, 'IDX': 0xEA},
            
            # Push and Pull
            'PSH': {'INH': {'A': 0x36, 'B': 0x37}}, 'PUL': {'INH': {'A': 0x32, 'B': 0x33}},
            
            # Rotate
            'ROL': {'DIR': 0x09, 'EXT': 0x79, 'IDX': 0x69, 'INH': {'A': 0x49, 'B': 0x59}},
            'ROR': {'DIR': 0x06, 'EXT': 0x76, 'IDX': 0x66, 'INH': {'A': 0x46, 'B': 0x56}},
            
            # Return from Interrupt/Subroutine
            'RTI': {'INH': 0x3B}, 'RTS': {'INH': 0x39},
            
            # Subtract with/without Carry
            'SBA': {'INH': 0x10},
            'SBC': {'IMM': {'A': 0x82, 'B': 0xC2}, 'DIR': {'A': 0x92, 'B': 0xD2}, 
                   'EXT': {'A': 0xB2, 'B': 0xF2}, 'IDX': {'A': 0xA2, 'B': 0xE2}},
            'SEC': {'INH': 0x0D}, 'SEI': {'INH': 0x0F}, 'SEV': {'INH': 0x0B},
            'STA': {'DIR': 0x97, 'EXT': 0xB7, 'IDX': 0xA7},
            'STB': {'DIR': 0xD7, 'EXT': 0xF7, 'IDX': 0xE7},
            'STX': {'DIR': 0xDF, 'EXT': 0xFF, 'IDX': 0xEF},
            'STS': {'DIR': 0x9F, 'EXT': 0xBF, 'IDX': 0xAF},
            'SUB': {'IMM': {'A': 0x80, 'B': 0xC0}, 'DIR': {'A': 0x90, 'B': 0xD0}, 
                   'EXT': {'A': 0xB0, 'B': 0xF0}, 'IDX': {'A': 0xA0, 'B': 0xE0}},
            
            # Software Interrupt
            'SWI': {'INH': 0x3F},
            
            # Tab and Transfer
            'TAB': {'INH': 0x16}, 'TAP': {'INH': 0x06}, 'TBA': {'INH': 0x17},
            'TPA': {'INH': 0x07}, 'TST': {'DIR': 0x0D, 'EXT': 0x7D, 'IDX': 0x6D, 'INH': {'A': 0x4D, 'B': 0x5D}},
            'TSX': {'INH': 0x30}, 'TXS': {'INH': 0x35},
            
            # Transfer Index Register
            'WAI': {'INH': 0x3E},
            
            # M6801/M6811 Specific Instructions (Enhanced support)
            'LSRD': {'INH': 0x04},     # Logical shift right D register
            'ASLD': {'INH': 0x05},     # Arithmetic shift left D register  
            'STD': {'DIR': 0xDD, 'EXT': 0xFD, 'IDX': 0xED},  # Store D register
            'LDD': {'IMM': 0xCC, 'DIR': 0xDC, 'EXT': 0xFC, 'IDX': 0xEC},  # Load D register
            'ABX': {'INH': 0x3A},      # Add B to X
            'MUL': {'INH': 0x3D},      # Multiply A * B -> D
            'PSHX': {'INH': 0x3C},     # Push X to stack
            'PULX': {'INH': 0x38},     # Pull X from stack
            'ADDD': {'IMM': 0xC3, 'DIR': 0xD3, 'EXT': 0xF3, 'IDX': 0xE3},  # 16-bit add to D
            
            # M6811 Specific Instructions
            'IDIV': {'INH': 0x02},     # Integer divide D/X -> X remainder D
            'FDIV': {'INH': 0x03},     # Fractional divide D/X -> X remainder D
            'INY': {'INH': 0x18CC},    # Increment Y register (2-byte instruction)
            'DEY': {'INH': 0x18CD},    # Decrement Y register (2-byte instruction)
            'STY': {'DIR': 0x18DF, 'EXT': 0x18FF, 'IDX': 0x18EF},  # Store Y register
            'LDY': {'IMM': 0x18CE, 'DIR': 0x18DE, 'EXT': 0x18FE, 'IDX': 0x18EE},  # Load Y register
            'CPD': {'IMM': 0x1A83, 'DIR': 0x1A93, 'EXT': 0x1AB3, 'IDX': 0x1AA3},  # Compare D
            'CPY': {'IMM': 0x18AC, 'DIR': 0x18BC, 'EXT': 0x18BC, 'IDX': 0x18AC},  # Compare Y
            'ABY': {'INH': 0x18E5},    # Add B to Y
            'PSHY': {'INH': 0x18DC},   # Push Y to stack  
            'PULY': {'INH': 0x18D8},   # Pull Y from stack
            'XGDX': {'INH': 0x8F},     # Exchange D and X
            'XGDY': {'INH': 0x18CF},   # Exchange D and Y
            'TSY': {'INH': 0x18F0},    # Transfer SP to Y
            'TYS': {'INH': 0x18F5},    # Transfer Y to SP
        }
    
    def assemble(self, source_code: str) -> Dict[str, Any]:
        """
        Assemble the given source code and return results.
        
        Args:
            source_code: Assembly source code as string
            
        Returns:
            Dictionary with assembly results including success status, object code, mappings, etc.
        """
        # Reset assembler state
        self.labels = {}
        self.current_address = 0x0000
        self.origin_address = 0x0000
        self.assembled_lines = []
        self.errors = []
        self.messages = []
        
        lines = source_code.strip().split('\n')
        
        # First pass: collect labels and handle pseudo-instructions
        self._first_pass(lines)
        
        # Second pass: generate machine code
        if not self.errors:
            self._second_pass(lines)
        
        # Prepare results
        success = len(self.errors) == 0
        object_code = self._format_object_code() if success else ""
        object_data = self._get_object_data() if success else {}
        
        return {
            'success': success,
            'object_code': object_code,
            'object_data': object_data,
            'mappings': self.assembled_lines,
            'errors': self.errors,
            'messages': self.messages,
            'labels': self.labels
        }
    
    def _first_pass(self, lines: List[str]) -> None:
        """First pass: collect labels and handle pseudo-instructions."""
        self.current_address = self.origin_address
        
        for line_num, line in enumerate(lines, 1):
            clean_line = self._clean_line(line)
            if not clean_line:
                continue
                
            # Check for label with colon first
            if ':' in clean_line:
                parts = clean_line.split(':', 1)
                label = parts[0].strip()
                if self._is_valid_label(label):
                    self.labels[label] = self.current_address
                    clean_line = parts[1].strip() if len(parts) > 1 else ""
            else:
                # Check for label without colon (label followed by instruction)
                tokens = clean_line.split()
                if len(tokens) >= 2:
                    potential_label = tokens[0]
                    potential_instruction = tokens[1].upper()
                    
                    # If first token looks like a label and second token is a known instruction
                    if (self._is_valid_label(potential_label) and 
                        (potential_instruction in self.instruction_set or 
                         potential_instruction in ['ORG', 'END'])):
                        
                        self.labels[potential_label] = self.current_address
                        clean_line = ' '.join(tokens[1:])  # Remove label from line
            
            if not clean_line:
                continue
                
            # Handle pseudo-instructions
            tokens = clean_line.split()
            if tokens:
                opcode = tokens[0].upper()
                
                if opcode == 'ORG':
                    if len(tokens) >= 2:
                        try:
                            self.origin_address = self._parse_number(tokens[1])
                            self.current_address = self.origin_address
                            self.messages.append(f"Line {line_num}: Origin set to ${self.origin_address:04X}")
                        except ValueError:
                            self.errors.append(f"Line {line_num}: Invalid ORG address: {tokens[1]}")
                elif opcode == 'END':
                    break
                elif opcode in self.instruction_set:
                    # Calculate instruction size for address calculation
                    size = self._calculate_instruction_size(opcode, tokens[1:] if len(tokens) > 1 else [])
                    self.current_address += size
    
    def _second_pass(self, lines: List[str]) -> None:
        """Second pass: generate machine code."""
        self.current_address = self.origin_address
        
        for line_num, line in enumerate(lines, 1):
            original_line = line.strip()
            clean_line = self._clean_line(line)
            
            if not clean_line:
                continue
            
            # Handle label with colon
            if ':' in clean_line:
                parts = clean_line.split(':', 1)
                clean_line = parts[1].strip() if len(parts) > 1 else ""
            else:
                # Handle label without colon (label followed by instruction)
                tokens = clean_line.split()
                if len(tokens) >= 2:
                    potential_label = tokens[0]
                    potential_instruction = tokens[1].upper()
                    
                    # If first token looks like a label and second token is a known instruction
                    if (self._is_valid_label(potential_label) and 
                        (potential_instruction in self.instruction_set or 
                         potential_instruction in ['ORG', 'END'])):
                        
                        clean_line = ' '.join(tokens[1:])  # Remove label from line

            if not clean_line:
                continue
            
            tokens = clean_line.split()
            if not tokens:
                continue
                
            opcode = tokens[0].upper()
            
            # Handle pseudo-instructions
            if opcode == 'ORG':
                if len(tokens) >= 2:
                    self.current_address = self._parse_number(tokens[1])
                continue
            elif opcode == 'END':
                break
            
            # Handle regular instructions
            if opcode in self.instruction_set:
                try:
                    operands = tokens[1:] if len(tokens) > 1 else []
                    machine_code = self._assemble_instruction(opcode, operands)
                    
                    self.assembled_lines.append({
                        'line': line_num,
                        'address': f"${self.current_address:04X}",
                        'object_code': ' '.join(f"{byte:02X}" for byte in machine_code),
                        'assembly': original_line
                    })
                    
                    self.current_address += len(machine_code)
                    
                except Exception as e:
                    self.errors.append(f"Line {line_num}: {str(e)}")
            else:
                self.errors.append(f"Line {line_num}: Unknown instruction: {opcode}")
    
    def _assemble_instruction(self, opcode: str, operands: List[str]) -> List[int]:
        """Assemble a single instruction into machine code."""
        instruction_def = self.instruction_set[opcode]
        
        if not operands:
            # Inherent addressing mode
            if 'INH' in instruction_def:
                opcode_bytes = instruction_def['INH']
                if isinstance(opcode_bytes, dict):
                    # For instructions that have register variants but no register specified,
                    # default to accumulator A for operations that typically work on A
                    if opcode in ['INC', 'DEC', 'CLR', 'TST', 'NEG', 'COM', 'ASL', 'ASR', 'LSR', 'ROL', 'ROR']:
                        if 'A' in opcode_bytes:
                            opcode_bytes = opcode_bytes['A']
                        else:
                            raise ValueError(f"Instruction {opcode} requires register specification")
                    else:
                        raise ValueError(f"Instruction {opcode} requires register specification")
                
                # Handle multi-byte opcodes (M6811 instructions)
                if isinstance(opcode_bytes, int):
                    if opcode_bytes > 0xFFFF:  # 3-byte opcode
                        return [(opcode_bytes >> 16) & 0xFF, (opcode_bytes >> 8) & 0xFF, opcode_bytes & 0xFF]
                    elif opcode_bytes > 0xFF:  # 2-byte opcode
                        return [(opcode_bytes >> 8) & 0xFF, opcode_bytes & 0xFF]
                    else:  # 1-byte opcode
                        return [opcode_bytes]
                return [opcode_bytes]
            else:
                raise ValueError(f"Instruction {opcode} requires operands")
        
        # Handle instructions with register specification (like CMP A #$55)
        register = None
        operand_start = 0
        
        # Check if first operand is a register specifier
        if len(operands) > 0 and operands[0].upper() in ['A', 'B']:
            register = operands[0].upper()
            operand_start = 1
        
        # Get the actual operand (skip register if present)
        if operand_start < len(operands):
            operand = ' '.join(operands[operand_start:])
        else:
            operand = ''
        
        # Special handling for instructions that might need default register
        if not register and operand and opcode in ['CMP', 'ADC', 'ADD', 'AND', 'BIT', 'EOR', 'ORA', 'SBC', 'SUB']:
            # Default to accumulator A for comparison and arithmetic operations
            register = 'A'
        
        addressing_mode, parsed_operand = self._parse_operand(operand, opcode)
        
        # Add register info if we found one
        if register:
            parsed_operand['register'] = register
        
        # Get opcode for the addressing mode
        if addressing_mode not in instruction_def:
            raise ValueError(f"Addressing mode {addressing_mode} not supported for {opcode}")
        
        opcode_info = instruction_def[addressing_mode]
        
        # Handle register-specific opcodes
        if isinstance(opcode_info, dict):
            if 'register' in parsed_operand:
                reg = parsed_operand['register']
                if reg not in opcode_info:
                    raise ValueError(f"Register {reg} not supported for {opcode} with {addressing_mode} mode")
                opcode_byte = opcode_info[reg]
            else:
                raise ValueError(f"Instruction {opcode} requires register specification")
        else:
            opcode_byte = opcode_info
        
        # Build machine code - handle multi-byte opcodes
        machine_code = []
        if isinstance(opcode_byte, int):
            if opcode_byte > 0xFFFF:  # 3-byte opcode
                machine_code.extend([(opcode_byte >> 16) & 0xFF, (opcode_byte >> 8) & 0xFF, opcode_byte & 0xFF])
            elif opcode_byte > 0xFF:  # 2-byte opcode
                machine_code.extend([(opcode_byte >> 8) & 0xFF, opcode_byte & 0xFF])
            else:  # 1-byte opcode
                machine_code.append(opcode_byte)
        else:
            machine_code.append(opcode_byte)
        
        # Add operand bytes
        if addressing_mode == 'IMM':
            if 'value' in parsed_operand:
                value = parsed_operand['value']
                if opcode in ['LDX', 'LDS', 'CPX', 'LDD', 'LDY', 'CPD', 'CPY', 'ADDD']:  # 16-bit immediate
                    machine_code.extend([value >> 8, value & 0xFF])
                else:  # 8-bit immediate
                    machine_code.append(value & 0xFF)
        elif addressing_mode == 'DIR':
            machine_code.append(parsed_operand['address'] & 0xFF)
        elif addressing_mode == 'EXT':
            addr = parsed_operand['address']
            machine_code.extend([addr >> 8, addr & 0xFF])
        elif addressing_mode == 'IDX':
            machine_code.append(parsed_operand['offset'] & 0xFF)
        elif addressing_mode == 'REL':
            # Calculate relative offset
            target = parsed_operand['address']
            # Account for multi-byte instruction length
            instruction_length = len(machine_code) + 1  # +1 for the offset byte
            offset = target - (self.current_address + instruction_length)
            if offset < -128 or offset > 127:
                raise ValueError(f"Branch target out of range: {offset}")
            machine_code.append(offset & 0xFF)
        
        return machine_code
    
    def _parse_operand(self, operand: str, opcode: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse an operand and determine its addressing mode.
        
        Returns:
            Tuple of (addressing_mode, parsed_data)
        """
        operand = operand.strip()
        
        # Immediate addressing: #value
        if operand.startswith('#'):
            value_str = operand[1:]
            return 'IMM', {'value': self._parse_number(value_str)}
        
        # Indexed addressing: offset,X
        if ',X' in operand.upper():
            offset_str = operand.upper().replace(',X', '').strip()
            offset = self._parse_number(offset_str) if offset_str else 0
            return 'IDX', {'offset': offset}
        
        # Register specification for inherent instructions
        if operand.upper() in ['A', 'B']:
            return 'INH', {'register': operand.upper()}
        
        # Check if this is a branch instruction - they use relative addressing
        branch_instructions = ['BCC', 'BCS', 'BEQ', 'BGE', 'BGT', 'BHI', 'BLE', 'BLS', 
                              'BLT', 'BMI', 'BNE', 'BPL', 'BRA', 'BSR', 'BVC', 'BVS']
        
        if opcode.upper() in branch_instructions:
            # Branch instructions use relative addressing
            if operand.upper() in self.labels:
                address = self.labels[operand.upper()]
            else:
                address = self._parse_number(operand)
            return 'REL', {'address': address}
        
        # Direct or Extended addressing (determined by address value)
        address = self._parse_number(operand)
        
        # Direct page (0x00-0xFF) vs Extended (0x0100-0xFFFF)
        if address <= 0xFF:
            return 'DIR', {'address': address}
        else:
            return 'EXT', {'address': address}
    
    def _parse_number(self, num_str: str) -> int:
        """Parse a number string (decimal, hex, binary)."""
        num_str = num_str.strip().upper()
        
        if num_str.startswith('$'):
            return int(num_str[1:], 16)
        elif num_str.startswith('0X'):
            return int(num_str, 16)
        elif num_str.startswith('%'):
            return int(num_str[1:], 2)
        elif num_str.startswith('0B'):
            return int(num_str[2:], 2)
        else:
            # Check if it's a label
            if num_str in self.labels:
                return self.labels[num_str]
            # If it's not a number and not a defined label, assume it's a forward reference
            try:
                return int(num_str)
            except ValueError:
                # Return 0 for undefined labels during first pass
                return 0
    
    def _is_branch_target(self, operand: str) -> bool:
        """Check if operand is a branch target (label)."""
        return operand.upper() in self.labels
    
    def _calculate_instruction_size(self, opcode: str, operands: List[str]) -> int:
        """Calculate the size of an instruction in bytes."""
        instruction_def = self.instruction_set[opcode]
        
        if not operands:
            # Inherent instructions - check for multi-byte opcodes
            if 'INH' in instruction_def:
                opcode_val = instruction_def['INH']
                if isinstance(opcode_val, dict):
                    return 1  # Will be determined by register
                
                # Calculate opcode size
                opcode_size = 1
                if isinstance(opcode_val, int):
                    if opcode_val > 0xFFFF:  # 3-byte opcode
                        opcode_size = 3
                    elif opcode_val > 0xFF:  # 2-byte opcode
                        opcode_size = 2
                    else:  # 1-byte opcode
                        opcode_size = 1
                
                return opcode_size
            return 1
        
        # Handle register specification like CMP A #$55
        operand_start = 0
        if len(operands) > 0 and operands[0].upper() in ['A', 'B']:
            operand_start = 1
        
        # Get the actual operand (skip register if present)
        if operand_start < len(operands):
            operand = ' '.join(operands[operand_start:])
        else:
            operand = ''
        
        addressing_mode, _ = self._parse_operand(operand, opcode)
        
        # Get base opcode size
        opcode_size = 1
        if addressing_mode in instruction_def:
            opcode_val = instruction_def[addressing_mode]
            if isinstance(opcode_val, int):
                if opcode_val > 0xFFFF:  # 3-byte opcode
                    opcode_size = 3
                elif opcode_val > 0xFF:  # 2-byte opcode
                    opcode_size = 2
        
        size_map = {
            'INH': opcode_size,
            'IMM': opcode_size + 1,  # Most immediate are opcode + 1 byte, some are + 2
            'DIR': opcode_size + 1,
            'EXT': opcode_size + 2,
            'IDX': opcode_size + 1,
            'REL': opcode_size + 1
        }
        
        size = size_map.get(addressing_mode, opcode_size)
        
        # Special cases for 16-bit immediate addressing
        if addressing_mode == 'IMM' and opcode in ['LDX', 'LDS', 'CPX', 'LDD', 'LDY', 'CPD', 'CPY', 'ADDD']:
            size += 1  # Additional byte for 16-bit immediate
            
        return size
    
    def _clean_line(self, line: str) -> str:
        """Clean a line by removing comments and extra whitespace."""
        # Remove comments
        if ';' in line:
            line = line[:line.index(';')]
        return line.strip()
    
    def _is_valid_label(self, label: str) -> bool:
        """Check if a label name is valid."""
        if not label:
            return False
        if label[0].isdigit():
            return False
        return all(c.isalnum() or c == '_' for c in label)
    
    def _format_object_code(self) -> str:
        """Format the object code for display."""
        if not self.assembled_lines:
            return ""
        
        lines = []
        lines.append("Motorola 6800 Object Code")
        lines.append("=" * 50)
        lines.append(f"Origin Address: ${self.origin_address:04X}")
        lines.append("")
        
        current_addr = None
        hex_line = ""
        addr_line = ""
        
        for item in self.assembled_lines:
            addr = int(item['address'].replace('$', ''), 16)
            hex_bytes = item['object_code'].replace(' ', '')
            
            if current_addr is None:
                current_addr = addr
                addr_line = f"{addr:04X}: "
                hex_line = ""
            
            # If address is not consecutive, start a new line
            if addr != current_addr:
                if hex_line:
                    lines.append(addr_line + hex_line)
                current_addr = addr
                addr_line = f"{addr:04X}: "
                hex_line = ""
            
            # Add hex bytes to current line
            for i in range(0, len(hex_bytes), 2):
                hex_line += hex_bytes[i:i+2] + " "
                current_addr += 1
                
                # Limit to 16 bytes per line
                if len(hex_line.split()) >= 16:
                    lines.append(addr_line + hex_line.strip())
                    addr_line = f"{current_addr:04X}: "
                    hex_line = ""
        
        # Add any remaining hex data
        if hex_line:
            lines.append(addr_line + hex_line.strip())
            
        return '\n'.join(lines)
    
    def _get_object_data(self) -> Dict[int, int]:
        """Get object data as address -> byte mapping."""
        object_data = {}
        
        for item in self.assembled_lines:
            addr = int(item['address'].replace('$', ''), 16)
            hex_bytes = item['object_code'].replace(' ', '')
            
            for i in range(0, len(hex_bytes), 2):
                byte_value = int(hex_bytes[i:i+2], 16)
                object_data[addr] = byte_value
                addr += 1
                
        return object_data
    
    def get_instruction_reference(self) -> str:
        """Get a formatted instruction set reference."""
        reference = """MOTOROLA 6800 INSTRUCTION SET REFERENCE

ADDRESSING MODES:
  INH   - Inherent (no operands)
  IMM   - Immediate (#value)
  DIR   - Direct Page (address 0x00-0xFF)
  EXT   - Extended (address 0x0100-0xFFFF)
  IDX   - Indexed (offset,X)
  REL   - Relative (for branches)

NUMBER FORMATS:
  $1234   - Hexadecimal
  %1010   - Binary
  123     - Decimal

ACCUMULATOR AND MEMORY OPERATIONS:
  ABA     - Add B to A
  ADC A/B - Add with Carry
  ADD A/B - Add
  AND A/B - Logical AND
  ASL     - Arithmetic Shift Left
  ASR     - Arithmetic Shift Right
  BIT A/B - Bit Test
  CBA     - Compare A with B
  CLR     - Clear
  CMP A/B - Compare
  COM     - Complement
  CPX     - Compare Index Register
  DAA     - Decimal Adjust A
  DEC     - Decrement
  EOR A/B - Exclusive OR
  INC     - Increment
  LDA/B   - Load Accumulator
  LDX     - Load Index Register
  LDS     - Load Stack Pointer
  LSR     - Logical Shift Right
  NEG     - Negate
  ORA/B   - Logical OR
  ROL     - Rotate Left
  ROR     - Rotate Right
  SBC A/B - Subtract with Carry
  STA/B   - Store Accumulator
  STX     - Store Index Register
  STS     - Store Stack Pointer
  SUB A/B - Subtract
  TST     - Test

BRANCH INSTRUCTIONS:
  BCC - Branch if Carry Clear
  BCS - Branch if Carry Set
  BEQ - Branch if Equal
  BGE - Branch if Greater or Equal
  BGT - Branch if Greater Than
  BHI - Branch if Higher
  BLE - Branch if Less or Equal
  BLS - Branch if Lower or Same
  BLT - Branch if Less Than
  BMI - Branch if Minus
  BNE - Branch if Not Equal
  BPL - Branch if Plus
  BRA - Branch Always
  BSR - Branch to Subroutine
  BVC - Branch if Overflow Clear
  BVS - Branch if Overflow Set

JUMP AND CONTROL:
  JMP - Jump
  JSR - Jump to Subroutine
  NOP - No Operation
  RTI - Return from Interrupt
  RTS - Return from Subroutine
  SWI - Software Interrupt
  WAI - Wait for Interrupt

REGISTER OPERATIONS:
  DEX/INX - Decrement/Increment X
  DES/INS - Decrement/Increment Stack Pointer
  PSH/PUL - Push/Pull A or B
  TAB/TBA - Transfer A to B / B to A
  TAP/TPA - Transfer A to/from Condition Codes
  TSX/TXS - Transfer Stack Pointer to/from X

CONDITION CODE OPERATIONS:
  CLC/SEC - Clear/Set Carry
  CLI/SEI - Clear/Set Interrupt Mask
  CLV/SEV - Clear/Set Overflow

PSEUDO-INSTRUCTIONS:
  ORG address - Set origin address
  END         - End of program

M6801/M6811 ENHANCED INSTRUCTIONS:
  LSRD    - Logical Shift Right D register
  ASLD    - Arithmetic Shift Left D register
  LDD     - Load D register (16-bit)
  STD     - Store D register (16-bit)
  ABX     - Add B to X register
  MUL     - Multiply A × B → D
  PSHX    - Push X register to stack
  PULX    - Pull X register from stack
  ADDD    - Add to D register (16-bit)
  
M6811 SPECIFIC INSTRUCTIONS:
  IDIV    - Integer Divide D ÷ X → X, remainder in D
  FDIV    - Fractional Divide
  LDY     - Load Y register
  STY     - Store Y register
  INY     - Increment Y register
  DEY     - Decrement Y register
  CPD     - Compare D register
  CPY     - Compare Y register
  ABY     - Add B to Y register
  PSHY    - Push Y register to stack
  PULY    - Pull Y register from stack
  XGDX    - Exchange D and X registers
  XGDY    - Exchange D and Y registers
  TSY     - Transfer SP to Y
  TYS     - Transfer Y to SP

EXAMPLES:
  LDA #$55    ; Load A with immediate value $55
  STA $2000   ; Store A at memory location $2000
  LDX #$1000  ; Load X with address $1000
  LDA 5,X     ; Load A from address X+5
  BEQ LABEL   ; Branch to LABEL if equal
  
LABEL NOP     ; Label definition
      END     ; End of program
"""
        return reference

def main():
    """Test function for the assembler."""
    assembler = M6800Assembler()
    
    test_code = """
        ORG     $1000
START:  LDA     #$55
        STA     $2000
        LDB     #$AA
        STB     $2001
        BEQ     START
        END
    """
    
    result = assembler.assemble(test_code)
    print("Assembly Result:", result)

if __name__ == "__main__":
    main() 