# Motorola 6800 Assembler with Interactive Interface

**System Programming Course - Final Project**  
**Spring 2024-2025**

## Overview

This project implements a complete Motorola 6800 Assembler with an interactive graphical user interface. The assembler translates assembly language instructions into machine code (object code) and provides real-time visualization of the assembly process, including line-by-line mapping between source code and generated machine code.

## Features

### Core Assembler Features ✅
- **Complete M6800 Instruction Set Support**: All major instruction types including load/store, arithmetic, logical, branch, and control instructions
- **Enhanced M6801/M6811 Support**: Extended instruction set including 16-bit operations, Y register, advanced arithmetic
- **Multiple Addressing Modes**: Immediate, Direct, Extended, Indexed, Inherent, and Relative addressing
- **Label Resolution**: Support for symbolic labels with forward and backward references
- **Pseudo-Instruction Handling**: ORG (origin) and END directives
- **Two-Pass Assembly**: Efficient label resolution and code generation
- **Comprehensive Error Detection**: Syntax validation and meaningful error messages

### User Interface Features ✅
- **Modern GUI Interface**: Built with Python Tkinter for Windows compatibility
- **Assembly Code Editor**: Syntax-aware text editor with line numbering
- **Real-time Assembly**: Assemble code with F5 key or button click
- **Multiple Output Views**:
  - Object Code display in formatted hex
  - Line-by-line Assembly-Object mapping table
  - Error and message reporting
- **File Operations**: New, Open, Save, Save As with assembly file support
- **Built-in Examples**: Load sample programs to test the assembler

### Execution Simulator Features ✅
- **M6800 Processor Simulation**: Complete register set (A, B, X, SP, PC, CC)
- **Memory Visualization**: Formatted memory dump display
- **Step-by-Step Execution**: Execute instructions one at a time
- **Program Loading**: Load assembled programs directly into simulator
- **Register Monitoring**: Real-time register value display
- **Condition Flags**: Full condition code register support

### Additional Features ✅
- **Instruction Set Reference**: Built-in help with complete instruction documentation
- **Cross-Platform Support**: Runs on Windows, macOS, and Linux
- **Professional Documentation**: Comprehensive code documentation and user guide
- **Example Programs**: Pre-loaded sample assembly programs

## Technical Specifications

- **Programming Language**: Python 3.7+
- **GUI Framework**: Tkinter (built-in with Python)
- **Architecture**: Modular design with separate assembler, simulator, and GUI components
- **Instruction Set**: Complete Motorola 6800 instruction set + M6801/M6811 enhancements
- **Memory Model**: 64KB address space (0x0000-0xFFFF)
- **Number Formats**: Decimal, hexadecimal ($), and binary (%) support
- **Multi-byte Instructions**: Support for 2-byte and 3-byte M6811 opcodes

## Project Structure

```
assembler/
├── main.py              # Main application entry point
├── m6800_assembler.py   # Core assembler engine
├── simulator.py         # M6800 processor simulator
├── README.md           # This documentation file
├── proposal.txt        # Original project proposal
└── examples/           # Sample assembly programs
    ├── basic.asm       # Basic instruction examples
    ├── fibonacci.asm   # Fibonacci sequence calculator
    ├── sorting.asm     # Bubble sort algorithm
    └── enhanced.asm    # M6801/M6811 enhanced instructions
```

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually included with Python)

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd assembler
   ```

2. **Verify Python Installation**
   ```bash
   python --version
   # Should show Python 3.7 or higher
   ```

3. **Test Tkinter Availability**
   ```bash
   python -c "import tkinter; print('Tkinter is available')"
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## Usage Guide

### Getting Started

1. **Launch the Application**
   ```bash
   python main.py
   ```

2. **Load Example Code**
   - Click "Load Example" button to see a sample program
   - Or use File → Open to load your own assembly file

3. **Assemble Code**
   - Press F5 or click "Assemble (F5)" button
   - View results in the tabbed output area

### Writing Assembly Code

The assembler supports standard Motorola 6800 assembly syntax:

```assembly
; Comments start with semicolon
        ORG     $1000    ; Set origin address

START   LDA     #$55     ; Load accumulator A with immediate value
        STA     $2000    ; Store A at memory location $2000
        LDB     #$AA     ; Load accumulator B with immediate value
        STB     $2001    ; Store B at memory location $2001
        
        LDX     #$2000   ; Load index register with address
        LDA     0,X      ; Load A with value at address in X
        CMP     #$55     ; Compare A with immediate value
        BEQ     SUCCESS  ; Branch if equal to SUCCESS
        
        JMP     ERROR    ; Jump to ERROR if not equal
        
SUCCESS LDA     #$01     ; Load success code
        STA     $3000    ; Store success code
        JMP     END      ; Jump to end
        
ERROR   LDA     #$FF     ; Load error code
        STA     $3000    ; Store error code
        
END     NOP              ; No operation
        
        END              ; End of program
```

### Number Formats

- **Decimal**: `123`
- **Hexadecimal**: `$1234` or `0x1234`
- **Binary**: `%1010` or `0b1010`

### Addressing Modes

- **Immediate**: `LDA #$55` (load immediate value)
- **Direct**: `LDA $55` (load from zero page)
- **Extended**: `LDA $1234` (load from full address)
- **Indexed**: `LDA 5,X` (load from X register + offset)
- **Inherent**: `NOP` (no operands)
- **Relative**: `BEQ LABEL` (branch instructions)

### Using the Simulator

1. **Assemble Your Program**: First, successfully assemble your code
2. **Load Program**: Click "Load Program" in the Simulator tab
3. **Execute**:
   - **Step**: Execute one instruction at a time
   - **Run**: Execute until completion or halt
   - **Reset**: Reset processor to initial state

## Supported Instructions

### Data Movement
- `LDA`, `LDB`, `LDX`, `LDS` - Load registers
- `STA`, `STB`, `STX`, `STS` - Store registers
- `TAB`, `TBA` - Transfer between accumulators
- `TSX`, `TXS` - Transfer between stack pointer and X
- `TAP`, `TPA` - Transfer to/from condition codes

### Enhanced M6801/M6811 Instructions
- `LDD`, `STD` - Load/Store D register (16-bit)
- `ADDD` - Add to D register (16-bit)
- `LSRD`, `ASLD` - Shift D register operations
- `MUL` - Multiply A × B → D
- `IDIV`, `FDIV` - Integer and fractional division
- `ABX`, `ABY` - Add B to X/Y registers
- `PSHX`, `PULX` - Push/Pull X register
- `PSHY`, `PULY` - Push/Pull Y register (M6811)
- `LDY`, `STY` - Load/Store Y register (M6811)
- `INY`, `DEY` - Increment/Decrement Y register (M6811)
- `CPD`, `CPY` - Compare D/Y registers (M6811)
- `XGDX`, `XGDY` - Exchange D with X/Y (M6811)
- `TSY`, `TYS` - Transfer between SP and Y (M6811)

### Loop Example
```assembly
        ORG     $1000
        LDA     #$00     ; Initialize counter
LOOP    INC              ; Increment A
        CMP     #$10     ; Compare with 16
        BNE     LOOP     ; Loop if not equal
        STA     $2000    ; Store result
        END
```

### Enhanced M6801/M6811 Example
```assembly
        ORG     $1000
        LDD     #$1234   ; Load D with 16-bit value
        STD     $2000    ; Store D register
        LDA     #$12     ; Load multiplicand
        LDB     #$34     ; Load multiplier
        MUL              ; Multiply A × B → D
        ADDD    #$0001   ; Add 1 to result (16-bit)
        STD     $2002    ; Store final result
        END
```

## Error Handling

## Example Programs