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
        """Initialize the assembler."""
        self.instruction_set = self._build_instruction_set()
        self.four_letter_mapping = self._get_4letter_mapping()
        self.labels = {}
        self.assembled_lines = []
        self.errors = []
        self.messages = []
        self.origin_address = 0x1000
        self.current_address = 0x1000
        
    def _build_instruction_set(self) -> Dict[str, Dict]:
        """Build the complete M6800/M6801/M6811 instruction set."""
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
            # --- START CHANGE: UNCOMMENTING INHERENT INSTRUCTIONS ---
            'CLC': {'INH': 0x0C}, # Clear Carry flag
            'CLI': {'INH': 0x0E}, # Clear Interrupt Mask
            'CLR': {'DIR': 0x0F, 'EXT': 0x7F, 'IDX': 0x6F, 'INH': {'A': 0x4F, 'B': 0x5F}},
            'CLV': {'INH': 0x0A}, # Clear Overflow flag
            # --- END CHANGE ---
            'CMP': {'IMM': {'A': 0x81, 'B': 0xC1}, 'DIR': {'A': 0x91, 'B': 0xD1}, 
                   'EXT': {'A': 0xB1, 'B': 0xF1}, 'IDX': {'A': 0xA1, 'B': 0xE1}},
            'COM': {'DIR': 0x03, 'EXT': 0x73, 'IDX': 0x63, 'INH': {'A': 0x43, 'B': 0x53}},
            'NEG': {'DIR': 0x00, 'EXT': 0x70, 'IDX': 0x60, 'INH': {'A': 0x40, 'B': 0x50}},
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
            # --- START CHANGE: UNCOMMENTING INHERENT INSTRUCTIONS ---
            'SEC': {'INH': 0x0D}, # Set Carry flag
            'SEI': {'INH': 0x0F}, # Set Interrupt Mask
            'SEV': {'INH': 0x0B}, # Set Overflow flag
            # --- END CHANGE ---
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
            'TPA': {'INH': 0x07}, 'TST': {'EXT': 0x7D, 'IDX': 0x6D, 'INH': {'A': 0x4D, 'B': 0x5D}},
            'TSX': {'INH': 0x30}, 'TXS': {'INH': 0x35},
            
            # Transfer Index Register
            'WAI': {'INH': 0x3E},
            
            # Break/Halt instruction
            'BRK': {'INH': 0x3F},  # Fixed BRK instruction to align with SWI
            
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
            'CPY': {'IMM': 0x188C, 'DIR': 0x189C, 'EXT': 0x18BC, 'IDX': 0x18AC},  # Compare Y
            'ABY': {'INH': 0x18E5},    # Add B to Y
            'PSHY': {'INH': 0x18DC},   # Push Y to stack  
            'PULY': {'INH': 0x18D8},   # Pull Y from stack
            'XGDX': {'INH': 0x8F},     # Exchange D and X
            'XGDY': {'INH': 0x188F},   # Exchange D and Y
            'TSY': {'INH': 0x18F0},    # Transfer SP to Y
            'TYS': {'INH': 0x18F5},    # Transfer Y to SP
            
            # M6811 Bit Manipulation Instructions
            'BSET': {'DIR': 0x14, 'IDX': 0x1C},    # Set bits in memory
            'BCLR': {'DIR': 0x15, 'IDX': 0x1D},    # Clear bits in memory
            'BRSET': {'DIR': 0x12, 'IDX': 0x1E},   # Branch if bits set
            'BRCLR': {'DIR': 0x13, 'IDX': 0x1F},   # Branch if bits clear
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
        self.current_address = self.origin_address
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
                
            # Use unified label parsing
            label, clean_line = self._parse_line_for_label(clean_line, line_num)
            
            # If we found a label, add it to the symbol table
            if label:
                # Check for duplicate label definition
                if label in self.labels:
                    self.errors.append(f"Line {line_num}: Duplicate label '{label}' - already defined at address ${self.labels[label]:04X}")
                else:
                    self.labels[label] = self.current_address
            
            if not clean_line:
                continue
            
            # Handle pseudo-instructions
            tokens = clean_line.split()
            if tokens:
                opcode = tokens[0].upper()
                
                # Handle both ORG and .ORG
                if opcode == 'ORG' or opcode == '.ORG':
                    if len(tokens) >= 2:
                        try:
                            self.origin_address = self._parse_number(tokens[1])
                            self.current_address = self.origin_address
                            self.messages.append(f"Line {line_num}: Origin set to ${self.origin_address:04X}")
                        except ValueError:
                            self.errors.append(f"Line {line_num}: Invalid ORG address: {tokens[1]}")
                # Handle both END and .END
                elif opcode == 'END' or opcode == '.END':
                    break
                # Handle .BYTE directive
                elif opcode == '.BYTE':
                    if len(tokens) >= 2:
                        try:
                            value = self._parse_number(tokens[1])
                            self.current_address += 1  # .BYTE takes 1 byte
                        except ValueError:
                            self.errors.append(f"Line {line_num}: Invalid .BYTE value: {tokens[1]}")
                elif opcode in self.instruction_set:
                    # Calculate instruction size for address calculation
                    try:
                        # Use unified operand parsing for all instructions
                        operands = self._parse_instruction_operands(opcode, tokens[1:] if len(tokens) > 1 else [])
                        size = self._calculate_instruction_size(opcode, operands)
                        self.current_address += size
                    except ValueError as e:
                        self.errors.append(f"Line {line_num}: Invalid operand for {opcode}: {str(e)}")
                    except Exception as e:
                        self.errors.append(f"Line {line_num}: Error in {opcode}: {str(e)}")
                # Check for 4-letter instruction syntax
                elif opcode in self.four_letter_mapping:
                    # Map 4-letter to 3-letter and calculate size
                    try:
                        mapped_opcode = self.four_letter_mapping[opcode]
                        size = self._calculate_instruction_size(mapped_opcode, tokens[1:] if len(tokens) > 1 else [])
                        self.current_address += size
                    except ValueError as e:
                        self.errors.append(f"Line {line_num}: Invalid operand for {opcode}: {str(e)}")
                    except Exception as e:
                        self.errors.append(f"Line {line_num}: Error in {opcode}: {str(e)}")
    
    def _second_pass(self, lines: List[str]) -> None:
        """Second pass: generate machine code."""
        self.current_address = self.origin_address
        
        for line_num, line in enumerate(lines, 1):
            original_line = line.strip()
            clean_line = self._clean_line(line)
            
            # --- START DEBUG PRINTS (Temporarily add for debugging) ---
            # print(f"DEBUG_SECOND_PASS: Processing line {line_num}: '{original_line}' (clean: '{clean_line}')")
            # --- END DEBUG PRINTS ---

            if not clean_line:
                continue
            
            # Use unified label parsing (ignore label name in second pass, just get remaining line)
            _, clean_line = self._parse_line_for_label(clean_line, line_num)
            
            if not clean_line:
                continue
            
            tokens = clean_line.split()
            if not tokens:
                continue
                
            opcode = tokens[0].upper()
            
            # Handle pseudo-instructions
            # Handle both ORG and .ORG
            if opcode == 'ORG' or opcode == '.ORG':
                if len(tokens) >= 2:
                    self.current_address = self._parse_number(tokens[1])
                continue
            # Handle both END and .END
            elif opcode == 'END' or opcode == '.END':
                break
            # Handle .BYTE directive
            elif opcode == '.BYTE':
                if len(tokens) >= 2:
                    try:
                        value = self._parse_number(tokens[1])
                        self.assembled_lines.append({
                            'line': line_num,
                            'address': f"${self.current_address:04X}",
                            'object_code': f"{value:02X}",
                            'assembly': original_line
                        })
                        self.current_address += 1
                    except ValueError:
                        self.errors.append(f"Line {line_num}: Invalid .BYTE value: {tokens[1]}")
                continue
            
            # Check for 4-letter instruction syntax first
            if opcode in self.four_letter_mapping:
                mapped_opcode = self.four_letter_mapping[opcode]
                # Determine register from 4-letter instruction
                register = opcode[-1] if opcode[-1] in ['A', 'B'] else None
                
                try:
                    operands = tokens[1:] if len(tokens) > 1 else []
                    # Add register to operands if instruction implies it
                    if register and mapped_opcode in ['ADD', 'ADC', 'SUB', 'SBC', 'AND', 'EOR', 'ORA', 'BIT', 'CMP', 
                                                      'TST', 'CLR', 'COM', 'NEG', 'INC', 'DEC', 'ASL', 'ASR', 'LSR', 
                                                      'ROL', 'ROR', 'PSH', 'PUL']:
                        operands = [register] + operands
                    
                    machine_code = self._assemble_instruction(mapped_opcode, operands)
                    
                    self.assembled_lines.append({
                        'line': line_num,
                        'address': f"${self.current_address:04X}",
                        'object_code': ' '.join(f"{byte:02X}" for byte in machine_code),
                        'assembly': original_line
                    })
                    
                    self.current_address += len(machine_code)
                    
                except ValueError as e:
                    self.errors.append(f"Line {line_num}: Invalid operand for {opcode}: {str(e)}")
                except OverflowError as e:
                    self.errors.append(f"Line {line_num}: Value out of range for {opcode}: {str(e)}")
                except KeyError as e:
                    self.errors.append(f"Line {line_num}: Unsupported addressing mode for {opcode}: {str(e)}")
                except Exception as e:
                    self.errors.append(f"Line {line_num}: Assembly error in {opcode}: {str(e)}")
            
            # Handle regular instructions
            elif opcode in self.instruction_set:
                try:
                    # Use unified operand parsing for all instructions
                    operands = self._parse_instruction_operands(opcode, tokens[1:] if len(tokens) > 1 else [])
                    machine_code = self._assemble_instruction(opcode, operands)
                    
                    # --- START DEBUG PRINTS (Temporarily add for debugging) ---
                    # print(f"DEBUG_SECOND_PASS: Line {line_num} ('{original_line.strip()}'): Assembled as {machine_code} (current_address=${self.current_address:04X})")
                    # --- END DEBUG PRINTS ---

                    self.assembled_lines.append({
                        'line': line_num,
                        'address': f"${self.current_address:04X}",
                        'object_code': ' '.join(f"{byte:02X}" for byte in machine_code),
                        'assembly': original_line
                    })
                    
                    self.current_address += len(machine_code)
                    
                except ValueError as e:
                    self.errors.append(f"Line {line_num}: Invalid operand for {opcode}: {str(e)}")
                    # print(f"DEBUG_SECOND_PASS_ERROR: Line {line_num} ('{original_line.strip()}'): ValueError: {e}") # Debug this
                except OverflowError as e:
                    self.errors.append(f"Line {line_num}: Value out of range for {opcode}: {str(e)}")
                except KeyError as e:
                    self.errors.append(f"Line {line_num}: Unsupported addressing mode for {opcode}: {str(e)}")
                except Exception as e:
                    self.errors.append(f"Line {line_num}: Assembly error in {opcode}: {str(e)}")
            else:
                self.errors.append(f"Line {line_num}: Unknown instruction: {opcode}")
    
    def _assemble_instruction(self, opcode: str, operands: List[str]) -> List[int]:
        """Assemble a single instruction into machine code."""
        instruction_def = self.instruction_set[opcode]
        
        # Special handling for M6811 bit manipulation instructions
        if opcode in ['BSET', 'BCLR', 'BRSET', 'BRCLR']:
            parsed_info = self._parse_bit_manipulation_instruction(opcode, operands)
            
            # Get opcode byte for the addressing mode
            addressing_mode = parsed_info['addressing_mode']
            opcode_byte = instruction_def[addressing_mode]
            machine_code = [opcode_byte, parsed_info['address_or_offset'], parsed_info['mask_value']]
                
            # For branch instructions, add the branch target offset
            if opcode in ['BRSET', 'BRCLR']:
                target_addr = parsed_info['branch_target']
                    
                # Calculate relative offset  
                instruction_length = len(machine_code) + 1  # +1 for the offset byte
                offset = target_addr - (self.current_address + instruction_length)
                if offset < -128 or offset > 127:
                    raise ValueError(f"Branch target too far: {offset} bytes (range is -128 to +127)")
                machine_code.append(offset & 0xFF)
                
            return machine_code
        
        # --- START REVISED INHERENT INSTRUCTION HANDLING ---
        if not operands:
            # This handles instructions like ABA, TAB, TBA, NOP, SWI, INCA, TST, etc.
            if 'INH' not in instruction_def:
                # If no operands are provided, but the instruction doesn't have an 'INH' mode, it's an error.
                raise ValueError(f"Instruction {opcode} requires an explicit operand or addressing mode.")
                
            opcode_info = instruction_def['INH'] # This will be either an int or a dict.
            
            if isinstance(opcode_info, dict):
                # This path is for instructions where 'INH' is a dict,
                # meaning they can implicitly operate on A or B, or need selection.
                # Example: ASL, INC, TST (when written without A/B like 'ASL', 'INC')
                
                # Check if it's one of the known implicit accumulator operations
                if opcode in ['ASL', 'ASR', 'LSR', 'ROL', 'ROR', 
                              'INC', 'DEC', 'CLR', 'TST', 'NEG', 'COM']:
                    # These instructions implicitly operate on A if no explicit register is specified.
                    opcode_byte = opcode_info['A'] # Default to A accumulator
                elif opcode in ['PSH', 'PUL']:
                    # PSH/PUL without A/B explicitly given is usually an error in most assemblers
                    # as it's ambiguous. In M6800, PSHA/PSHB are distinct opcodes.
                    # This case should ideally be handled by 4-letter mappings or explicit operand.
                    raise ValueError(f"Instruction {opcode} requires accumulator (A or B) specified for inherent mode (e.g., PSHA).")
                else:
                    # This 'else' should ideally not be hit for standard M6800/6811 instructions
                    # if the instruction_set is complete and correctly structured.
                    # It would indicate an 'INH' entry is a dict but the opcode isn't handled by the above list.
                    raise ValueError(f"Ambiguous inherent instruction {opcode} (no explicit register and not recognized implicit A/B op).")
            else:
                # This path handles truly inherent instructions where the 'INH' definition
                # is a direct integer opcode (e.g., ABA, TAB, TBA, NOP, SWI, DAA, RTI, RTS, etc.).
                opcode_byte = opcode_info # Direct opcode value (e.g., 0x1B for ABA)
            
            # Now, opcode_byte holds the final opcode integer. Build machine code.
            machine_code = []
            if isinstance(opcode_byte, int): # Ensure it's an int, not some other type if logic was flawed.
                if opcode_byte > 0xFFFF:  # 3-byte opcode (e.g. some M6811 prefixed inherent ops)
                    machine_code.extend([(opcode_byte >> 16) & 0xFF, (opcode_byte >> 8) & 0xFF, opcode_byte & 0xFF])
                elif opcode_byte > 0xFF:  # 2-byte opcode (e.g. M6811 INY, DEY)
                    machine_code.extend([(opcode_byte >> 8) & 0xFF, opcode_byte & 0xFF])
                else:  # 1-byte opcode
                    machine_code.append(opcode_byte)
            else:
                # Should not be reached if opcode_info is always int or dict and handled.
                raise ValueError(f"Internal assembler error: Inherent opcode for {opcode} has unexpected type {type(opcode_byte)}.")
            
            return machine_code
        # --- END REVISED INHERENT INSTRUCTION HANDLING ---
        
        # Handle instructions with explicit operands (e.g., LDA #$55, CMP A #$55)
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
            operand = '' # Now operand is empty, but it's okay because we're past 'if not operands'
                         # and this case is for things like "CMP A"
        
        # Special handling for instructions that might need default register (e.g., CMP #$55 -> CMPA #$55)
        # This occurs when an operand is present, but no explicit register 'A' or 'B' was given.
        if not register and operand and opcode in ['CMP', 'ADC', 'ADD', 'AND', 'BIT', 'EOR', 'ORA', 'SBC', 'SUB']:
            # Default to accumulator A for comparison and arithmetic operations if no register explicitly specified
            register = 'A'
        
        addressing_mode, parsed_operand = self._parse_operand(operand, opcode)
        
        # Add register info if we found one
        if register:
            parsed_operand['register'] = register
        
        # Get opcode for the addressing mode
        if addressing_mode not in instruction_def:
            raise ValueError(f"Addressing mode {addressing_mode} not supported for {opcode}")
        
        opcode_info = instruction_def[addressing_mode]
        
        # Handle register-specific opcodes (e.g., ADC A, ADC B)
        if isinstance(opcode_info, dict):
            if 'register' in parsed_operand:
                reg = parsed_operand['register']
                if reg not in opcode_info:
                    raise ValueError(f"Register {reg} not supported for {opcode} with {addressing_mode} mode")
                opcode_byte = opcode_info[reg]
            else:
                # This should only happen if the instruction's addressing mode is a dict (e.g., ADC)
                # but no register was parsed (e.g., "ADC #$10" without "ADC A #$10").
                # The 'register' variable from above already handled this, defaulting to 'A' or setting 'register'.
                # So this else implies a logical error in prior parsing or non-standard instruction.
                raise ValueError(f"Instruction {opcode} requires register specification for {addressing_mode} mode.")
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
            machine_code.append(opcode_byte) # Should not happen if opcode_byte is always int.
        
        # Add operand bytes
        if addressing_mode == 'IMM':
            if 'value' in parsed_operand:
                value = parsed_operand['value']
                if opcode in ['LDX', 'LDS', 'CPX', 'LDD', 'LDY', 'CPD', 'CPY', 'ADDD']:  # 16-bit immediate
                    if value > 0xFFFF:
                        raise ValueError(f"16-bit immediate value ${value:X} too large (max is $FFFF)")
                    machine_code.extend([value >> 8, value & 0xFF])
                else:  # 8-bit immediate
                    if value > 0xFF:
                        raise ValueError(f"8-bit immediate value ${value:X} too large (max is $FF)")
                    machine_code.append(value & 0xFF)
        elif addressing_mode == 'DIR':
            addr = parsed_operand['address']
            if addr > 0xFF:
                raise ValueError(f"Direct page address ${addr:X} too large (max is $FF). Use extended addressing for addresses > $FF")
            machine_code.append(addr & 0xFF)
        elif addressing_mode == 'EXT':
            addr = parsed_operand['address']
            if addr > 0xFFFF:
                raise ValueError(f"Extended address ${addr:X} too large (max is $FFFF)")
            machine_code.extend([addr >> 8, addr & 0xFF])
        elif addressing_mode == 'IDX':
            offset = parsed_operand['offset']
            if offset > 0xFF:
                raise ValueError(f"Indexed offset ${offset:X} too large (max is $FF)")
            machine_code.append(offset & 0xFF)
        elif addressing_mode == 'REL':
            # Calculate relative offset
            target = parsed_operand['address']
            # Account for multi-byte instruction length
            instruction_length = len(machine_code) + 1  # +1 for the offset byte
            offset = target - (self.current_address + instruction_length)
            # Only validate range if target is non-zero (i.e., label was resolved)
            if target != 0 and (offset < -128 or offset > 127):
                if offset < -128:
                    raise ValueError(f"Branch target too far backward: {offset} bytes (min is -128)")
                else:
                    raise ValueError(f"Branch target too far forward: {offset} bytes (max is +127)")
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
        
        # Register specification for inherent instructions (e.g., 'LDA A' (though LDAA is preferred))
        # Note: This branch in _parse_operand is crucial for parsing `CMP A #$55` type syntax.
        # For 'simple' inherent ops like 'ABA', 'TAB', 'NOP', they don't have an 'operand' in assembly
        # so they hit the 'if not operands:' block in _assemble_instruction/size directly.
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
        
        if not num_str:
            raise ValueError("Empty number string")
        
        try:
            if num_str.startswith('$'):
                if len(num_str) == 1:
                    raise ValueError("Incomplete hexadecimal number (missing digits after '$')")
                result = int(num_str[1:], 16)
            elif num_str.startswith('0X'):
                if len(num_str) == 2:
                    raise ValueError("Incomplete hexadecimal number (missing digits after '0x')")
                result = int(num_str, 16)
            elif num_str.startswith('%'):
                if len(num_str) == 1:
                    raise ValueError("Incomplete binary number (missing digits after '%')")
                result = int(num_str[1:], 2)
            elif num_str.startswith('0B'):
                if len(num_str) == 2:
                    raise ValueError("Incomplete binary number (missing digits after '0b')")
                result = int(num_str[2:], 2)
            else:
                # Check if it's a label
                if num_str in self.labels:
                    return self.labels[num_str]
                # If it's not a number and not a defined label, try to parse as number
                try:
                    result = int(num_str)
                except ValueError:
                    # Check if it might be an undefined label (contains valid identifier characters)
                    if self._is_valid_label(num_str):
                        return 0  # Return 0 for undefined labels (forward references) during first pass
                    else:
                        raise ValueError(f"Invalid number format: '{num_str}' - expected decimal, hex ($xx), or binary (%bb)")
            
            # Validate range for 16-bit processor
            if result < 0:
                raise ValueError(f"Negative numbers not allowed: {result}")
            elif result > 0xFFFF:
                raise ValueError(f"Number too large for 16-bit processor: ${result:X} (max is $FFFF)")
                
            return result
            
        except ValueError as e:
            if "invalid literal" in str(e).lower():
                # Improve error message for invalid digit errors
                if num_str.startswith('$') or num_str.startswith('0X'):
                    raise ValueError(f"Invalid hexadecimal number: '{num_str}' - contains invalid characters")
                elif num_str.startswith('%') or num_str.startswith('0B'):
                    raise ValueError(f"Invalid binary number: '{num_str}' - contains invalid characters")
                else:
                    raise ValueError(f"Invalid decimal number: '{num_str}' - contains invalid characters")
            else:
                raise  # Re-raise our custom error messages
    
    def _is_branch_target(self, operand: str) -> bool:
        """Check if operand is a branch target (label)."""
        return operand.upper() in self.labels
    
    def _calculate_instruction_size(self, opcode: str, operands: List[str]) -> int:
        """Calculate the size of an instruction in bytes."""
        instruction_def = self.instruction_set[opcode]
        
        # Special handling for M6811 bit manipulation instructions
        if opcode in ['BSET', 'BCLR', 'BRSET', 'BRCLR']:
            try:
                # Use the unified parser for bit manipulation instructions
                parsed_info = self._parse_bit_manipulation_instruction(opcode, operands)
                return parsed_info['size']
            except ValueError:
                # If parsing fails in the first pass (e.g. forward ref for branch target)
                # still return the expected size. The actual error will be caught in second pass.
                return 3 if opcode in ['BSET', 'BCLR'] else 4 # BSET/BCLR: 3 bytes, BRSET/BRCLR: 4 bytes
        
        # --- START REVISED INHERENT INSTRUCTION HANDLING ---
        if not operands:
            if 'INH' not in instruction_def:
                raise ValueError(f"Instruction {opcode} requires an explicit operand or addressing mode.")
                
            opcode_info = instruction_def['INH']
            opcode_size = 1 # Default for 1-byte inherent
            
            if isinstance(opcode_info, dict):
                # This branch means the 'INH' definition is a dictionary,
                # implying it can take an implicit A or B accumulator.
                if opcode in ['ASL', 'ASR', 'LSR', 'ROL', 'ROR', 
                              'INC', 'DEC', 'CLR', 'TST', 'NEG', 'COM']:
                    opcode_size = 1 # These are 1-byte instructions.
                elif opcode in ['PSH', 'PUL']:
                    raise ValueError(f"Instruction {opcode} requires accumulator (A or B) specified for inherent mode.")
                else:
                    raise ValueError(f"Ambiguous inherent instruction {opcode} (no explicit register for dict-based INH).")
            else:
                # Handles truly inherent instructions with direct integer opcodes (1, 2, or 3 bytes)
                if opcode_info > 0xFFFF:  # 3-byte opcode
                    opcode_size = 3
                elif opcode_info > 0xFF:  # 2-byte opcode
                    opcode_size = 2
                else:  # 1-byte opcode
                    opcode_size = 1
            
            return opcode_size
        # --- END REVISED INHERENT INSTRUCTION HANDLING ---

        # Handle instructions with explicit operands (e.g., LDA #$55, CMP A #$55)
        register = None
        operand_start = 0
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

        addressing_mode, _ = self._parse_operand(operand, opcode)
        
        # Get base opcode size (could be 1, 2, or 3 bytes for M6811 prefixed ops)
        opcode_size = 1
        if addressing_mode in instruction_def:
            opcode_val = instruction_def[addressing_mode]
            if isinstance(opcode_val, int):
                if opcode_val > 0xFFFF:  # 3-byte opcode
                    opcode_size = 3
                elif opcode_val > 0xFF:  # 2-byte opcode
                    opcode_size = 2
        
        # Calculate total size based on addressing mode and operand bytes
        size_map = {
            'INH': opcode_size,  # Should have been handled by the 'if not operands' block above, but good as a fallback/check
            'IMM': opcode_size + 1,  # Most immediate are opcode + 1 byte operand
            'DIR': opcode_size + 1,
            'EXT': opcode_size + 2,
            'IDX': opcode_size + 1,
            'REL': opcode_size + 1
        }
        
        size = size_map.get(addressing_mode, opcode_size)
        
        # Special cases for 16-bit immediate addressing (requires 2 bytes for the value)
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
        """Check if a string is a valid label name."""
        if not label:
            return False
        # Labels should start with letter or underscore and contain only alphanumeric chars and underscores
        if not (label[0].isalpha() or label[0] == '_'):
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

M6811 Bit Manipulation Instructions:
  BSET    - Set bits in memory
  BCLR    - Clear bits in memory
  BRSET   - Branch if bits set
  BRCLR   - Branch if bits clear

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

    def _get_4letter_mapping(self) -> Dict[str, str]:
        """Get mapping of 4-letter M6800 instructions to 3-letter equivalents."""
        return {
            # 4-letter syntax -> 3-letter syntax
            'LDAA': 'LDA',  'LDAB': 'LDB',  'LDAX': 'LDX',  'LDAS': 'LDS',
            'STAA': 'STA',  'STAB': 'STB',  'STAX': 'STX',  'STAS': 'STS',
            'ADDA': 'ADD',  'ADDB': 'ADD',  'ADCA': 'ADC',  'ADCB': 'ADC',
            'SUBA': 'SUB',  'SUBB': 'SUB',  'SBCA': 'SBC',  'SBCB': 'SBC',
            'ANDA': 'AND',  'ANDB': 'AND',  'EORA': 'EOR',  'EORB': 'EOR',
            'ORAA': 'ORA',  'ORAB': 'ORB',  'BITA': 'BIT',  'BITB': 'BIT',
            'CMPA': 'CMP',  'CMPB': 'CMP',  'CPXA': 'CPX',  'CPXB': 'CPX',
            'TSTA': 'TST',  'TSTB': 'TST',  'CLRA': 'CLR',  'CLRB': 'CLR',
            'COMA': 'COM',  'COMB': 'COM',  'NEGA': 'NEG',  'NEGB': 'NEG',
            'INCA': 'INC',  'INCB': 'INC',  'DECA': 'DEC',  'DECB': 'DEC',
            'ASLA': 'ASL',  'ASLB': 'ASL',  'ASRA': 'ASR',  'ASRB': 'ASR',
            'LSRA': 'LSR',  'LSRB': 'LSR',  'ROLA': 'ROL',  'ROLB': 'ROL',
            'RORA': 'ROR',  'RORB': 'ROR',  'PSHA': 'PSH',  'PSHB': 'PSH',
            'PULA': 'PUL',  'PULB': 'PUL',
        }

    def _parse_instruction_operands(self, opcode: str, tokens: List[str]) -> List[str]:
        """
        Parse operands for all instructions, with special handling for bit manipulation instructions.
        
        Args:
            opcode: The instruction opcode
            tokens: The raw operand tokens
            
        Returns:
            List of parsed operands
        """
        # For bit manipulation instructions, join all tokens and use special comma parsing
        if opcode in ['BSET', 'BCLR', 'BRSET', 'BRCLR']:
            operand_string = ' '.join(tokens)
            return self._parse_bit_manipulation_operands(operand_string)
        else:
            # For regular instructions, return tokens as-is
            return tokens

    def _parse_bit_manipulation_operands(self, operand_string: str) -> List[str]:
        """
        Parse operands for bit manipulation instructions (BSET, BCLR, BRSET, BRCLR).
        
        Args:
            operand_string: String containing the operands
            
        Returns:
            List of parsed operands
        """
        if not operand_string.strip():
            return []
        
        # Handle comma-separated operands considering parentheses and quotes
        operands = []
        current_operand = ""
        paren_depth = 0
        in_quotes = False
        
        for char in operand_string:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
                current_operand += char
            elif char == '(' and not in_quotes:
                paren_depth += 1
                current_operand += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                current_operand += char
            elif char == ',' and paren_depth == 0 and not in_quotes:
                operands.append(current_operand.strip())
                current_operand = ""
            else:
                current_operand += char
        
        if current_operand.strip():
            operands.append(current_operand.strip())
        
        return operands
    
    def _parse_bit_manipulation_instruction(self, opcode: str, operands: List[str]) -> Dict[str, Any]:
        """
        Parse bit manipulation instructions (BSET, BCLR, BRSET, BRCLR) into a unified format.
        
        Args:
            opcode: The instruction mnemonic
            operands: List of operand strings
            
        Returns:
            Dictionary containing parsed instruction data with:
            - addressing_mode: 'DIR' or 'IDX'
            - address_or_offset: Address (for DIR) or offset (for IDX)
            - mask_value: Bit mask value
            - branch_target: Branch target address (for BRSET/BRCLR only)
            - size: Total instruction size in bytes
        """
        if len(operands) < 2:
            raise ValueError(f"Instruction {opcode} requires at least two operands: address and bit mask")
        
        # Parse address operand
        addr_operand = operands[0].strip()
        
        # Parse bit mask operand  
        mask_operand = operands[1].strip()
        if not mask_operand.startswith('#'):
            raise ValueError(f"Bit mask for {opcode} must be immediate (#value)")
        mask_value = self._parse_number(mask_operand[1:])
        if mask_value > 0xFF:
            raise ValueError(f"Bit mask ${mask_value:X} too large (max is $FF)")
            
        # Determine addressing mode from address operand
        if ',X' in addr_operand.upper():
            # Indexed addressing
            offset_str = addr_operand.upper().replace(',X', '').strip()
            address_or_offset = self._parse_number(offset_str) if offset_str else 0
            if address_or_offset > 0xFF:
                raise ValueError(f"Indexed offset ${address_or_offset:X} too large (max is $FF)")
            addressing_mode = 'IDX'
        else:
            # Direct addressing
            address_or_offset = self._parse_number(addr_operand)
            if address_or_offset > 0xFF:
                raise ValueError(f"Direct page address ${address_or_offset:X} too large for {opcode} (max is $FF)")
            addressing_mode = 'DIR'
            
        # Calculate size: opcode + address/offset + mask + optional branch target
        size = 3
        branch_target = None
        
        # For branch instructions, parse the branch target
        if opcode in ['BRSET', 'BRCLR']:
            if len(operands) < 3:
                raise ValueError(f"Instruction {opcode} requires three operands: address, bit mask, and branch target")
                
            branch_target_str = operands[2].strip()
            if branch_target_str.upper() in self.labels:
                branch_target = self.labels[branch_target_str.upper()]
            else:
                branch_target = self._parse_number(branch_target_str)
            size = 4  # Add branch offset byte
            
        return {
            'addressing_mode': addressing_mode,
            'address_or_offset': address_or_offset,
            'mask_value': mask_value,
            'branch_target': branch_target,
            'size': size
        }

    def _parse_line_for_label(self, clean_line: str, line_num: int) -> tuple[str, str]:
        """Parse a line for labels and return (label_found, remaining_line).
        
        Args:
            clean_line: Cleaned line of assembly code
            line_num: Line number for error reporting (only used in first pass)
            
        Returns:
            Tuple of (label_found_or_empty, remaining_instruction_line)
        """
        if not clean_line:
            return "", ""
            
        # Check for label with colon first
        if ':' in clean_line:
            parts = clean_line.split(':', 1)
            label = parts[0].strip()
            remaining_line = parts[1].strip() if len(parts) > 1 else ""
            
            if self._is_valid_label(label):
                return label, remaining_line
            else:
                return "", clean_line  # Invalid label, treat as regular line
        else:
            # Check for label without colon (label followed by instruction or standalone)
            tokens = clean_line.split()
            if len(tokens) >= 2:
                potential_label = tokens[0]
                potential_instruction = tokens[1].upper()
                
                # If first token looks like a label and second token is a known instruction
                # BUT first token is NOT itself an instruction (instructions take priority)
                if (self._is_valid_label(potential_label) and 
                    potential_label.upper() not in self.instruction_set and
                    potential_label.upper() not in self.four_letter_mapping and
                    (potential_instruction in self.instruction_set or 
                     potential_instruction in self.four_letter_mapping or
                     potential_instruction in ['ORG', 'END', '.ORG', '.END', '.BYTE'])):
                    
                    remaining_line = ' '.join(tokens[1:])  # Remove label from line
                    return potential_label, remaining_line
            elif len(tokens) == 1:
                # Check for standalone label
                potential_label = tokens[0]
                if self._is_valid_label(potential_label):
                    return potential_label, ""  # No instruction to process
                    
        return "", clean_line  # No label found

# --- MAIN FUNCTION FOR STANDALONE TESTING (KEEP AS IS) ---
def main():
    """Main function that supports command line file input."""
    import sys
    
    if len(sys.argv) > 1:
        # File specified on command line
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                source_code = f.read()
            
            assembler = M6800Assembler()
            result = assembler.assemble(source_code)
            print("Assembly Result:", result)
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        # Run test if no file specified
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