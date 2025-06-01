# Motorola 6800 Assembler with Interactive Simulator

**System Programming Course - Final Project**  
**Spring 2024-2025**

## Overview

This project implements a complete Motorola 6800 Assembler with an interactive graphical user interface and processor simulator. The assembler translates assembly language instructions into machine code (object code) and provides real-time visualization of the assembly process, including line-by-line mapping between source code and generated machine code. The integrated simulator allows step-by-step execution of assembled programs with full register and memory monitoring.

## Features

### Core Assembler Features ✅
- **Complete M6800 Instruction Set Support**: All major instruction types including load/store, arithmetic, logical, branch, and control instructions
- **Enhanced M6801/M6811 Support**: Extended instruction set including 16-bit operations, Y register, advanced arithmetic
- **Multiple Addressing Modes**: Immediate, Direct, Extended, Indexed, Inherent, and Relative addressing
- **Label Resolution**: Support for symbolic labels with forward and backward references
- **Pseudo-Instruction Handling**: ORG (origin) and END directives
- **Two-Pass Assembly**: Efficient label resolution and code generation
- **Comprehensive Error Detection**: Syntax validation and meaningful error messages
- **Command Line Support**: Assemble files directly from command line

### User Interface Features ✅
- **Modern GUI Interface**: Built with Python Tkinter for cross-platform compatibility
- **Assembly Code Editor**: Syntax-aware text editor with line numbering
- **Real-time Assembly**: Assemble code with F5 key or button click
- **Multiple Output Views**:
  - Object Code display in formatted hex
  - Line-by-line Assembly-Object mapping table
  - Error and message reporting
- **File Operations**: New, Open, Save, Save As with assembly file support
- **Built-in Examples**: Load sample programs to test the assembler
- **Integrated Help**: Complete instruction set reference

### Execution Simulator Features ✅
- **Complete M6800 Processor Simulation**: Full register set (A, B, X, SP, PC, CC)
- **Memory Visualization**: Formatted memory dump display with ASCII representation
- **Step-by-Step Execution**: Execute instructions one at a time with debugging
- **Continuous Execution**: Run programs until completion or halt
- **Program Loading**: Load assembled programs directly into simulator memory
- **Register Monitoring**: Real-time register value display in hex format
- **Condition Flags**: Full condition code register support (N, Z, V, C, H)
- **Execution Logging**: Detailed debug logs for instruction tracing
- **Reset Functionality**: Reset processor state while preserving loaded program

### Additional Features ✅
- **Instruction Set Reference**: Built-in help with complete instruction documentation
- **Cross-Platform Support**: Runs on Windows, macOS, and Linux
- **Professional Documentation**: Comprehensive code documentation and user guide
- **Tutorial Examples**: Progressive learning examples from basic to advanced
- **Error Recovery**: Robust error handling with meaningful messages

## Technical Specifications

- **Programming Language**: Python 3.7+
- **GUI Framework**: Tkinter (built-in with Python)
- **Architecture**: Modular design with separate assembler, simulator, and GUI components
- **Instruction Set**: Complete Motorola 6800 instruction set + M6801/M6811 enhancements
- **Memory Model**: 64KB address space (0x0000-0xFFFF)
- **Number Formats**: Decimal, hexadecimal ($), and binary (%) support
- **Multi-byte Instructions**: Support for 2-byte and 3-byte M6811 opcodes
- **Debug Logging**: Comprehensive execution tracing and state monitoring

## Project Structure

```
assembler/
├── simulator_gui.py     # Main GUI application entry point
├── m6800_assembler.py   # Core assembler engine with command line support
├── simulator.py         # M6800 processor simulator
├── README.md           # This documentation file
├── logs/               # Debug and execution logs
└── examples/           # Progressive tutorial assembly programs
    ├── ultra_basic.asm # Simplest load/store operations
    ├── arithmetic.asm  # Basic arithmetic and comparisons
    ├── data_copy.asm   # Array operations and data copying
    ├── min_max.asm     # Finding minimum/maximum values
    └── sorting.asm     # Bubble sort algorithm (most complex)
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

4. **Run the GUI Application**
   ```bash
   python simulator_gui.py
   ```

5. **Use Command Line Assembler (Optional)**
   ```bash
   python m6800_assembler.py examples/arithmetic.asm
   ```

## Usage Guide

### Getting Started

1. **Launch the GUI Application**
   ```bash
   python simulator_gui.py
   ```

2. **Load Example Code**
   - Click "Load Example" button to see a sample program
   - Or use File → Open to load your own assembly file
   - Start with `ultra_basic.asm` for beginners

3. **Assemble Code**
   - Press F5 or click "Assemble (F5)" button
   - View results in the tabbed output area

4. **Simulate Execution**
   - Click "Load Program" in the Simulator tab
   - Use "Step" for instruction-by-instruction execution
   - Use "Run" for continuous execution
   - Monitor registers and memory in real-time

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
        BRA     FINISH   ; Branch to finish
        
ERROR   LDA     #$FF     ; Load error code
        STA     $3000    ; Store error code
        
FINISH  SWI              ; Software interrupt (halt)
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
   - **Step**: Execute one instruction at a time for debugging
   - **Run**: Execute until completion, halt, or error
   - **Reset**: Reset processor to initial state
4. **Monitor**: Watch registers and memory update in real-time
5. **Debug**: Check logs for detailed execution trace

## Tutorial Examples

The project includes progressive tutorial examples:

### 1. ultra_basic.asm (11 lines)
**Learning Goals**: Basic load and store operations
```assembly
START   LDA     #$42     ; Load accumulator A
        STA     $50      ; Store A at memory
        LDB     #$24     ; Load accumulator B
        STB     $51      ; Store B at memory
```

### 2. arithmetic.asm (53 lines)
**Learning Goals**: Arithmetic operations, comparisons, branching
```assembly
START   LDA     #$15     ; Load first number (21)
        STA     $50      ; Store first number
        LDB     #$0A     ; Load second number (10)
        STB     $51      ; Store second number
        
        LDA     $50      ; Load first number
        ADD     $51      ; Add second number (A = 31)
        STA     $52      ; Store sum
        
        LDA     $50      ; Load first number
        CMP     $51      ; Compare with second
        BLS     SMALLER  ; Branch if A <= memory
        ; A is larger...
```

### 3. data_copy.asm (66 lines)
**Learning Goals**: Array operations, data verification, error handling
```assembly
; Copy array from $2000-$2003 to $3000-$3003
COPY1   LDA     $2000    ; Load source[0]
        STA     $3000    ; Store to destination[0]
        
; Verify copy
VERIFY1 LDA     $2000    ; Load source[0]
        CMP     $3000    ; Compare with destination[0]
        BNE     ERROR    ; Branch if not equal
```

### 4. min_max.asm (88 lines)
**Learning Goals**: Array scanning, conditional updates, range calculation
```assembly
; Find minimum and maximum in array
CHK1    LDA     $2001    ; Load array element
        CMP     $50      ; Compare with current min
        BCC     CHK1_MAX ; Branch if A >= min
        STA     $50      ; Update minimum
CHK1_MAX CMP    $51      ; Compare with current max
        BLS     CHK2     ; Branch if A <= max
        STA     $51      ; Update maximum
```

### 5. sorting.asm (117 lines)
**Learning Goals**: Complex algorithms, bubble sort implementation
```assembly
; Bubble sort pass - compare adjacent elements
        LDA     $2000    ; Load element 0
        LDB     $2001    ; Load element 1
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP01   ; Skip if in order
        ; Swap elements...
```

## Supported Instructions

### Data Movement
- `LDA`, `LDB`, `LDX`, `LDS` - Load registers
- `STA`, `STB`, `STX`, `STS` - Store registers
- `TAB`, `TBA` - Transfer between accumulators
- `TSX`, `TXS` - Transfer between stack pointer and X
- `TAP`, `TPA` - Transfer to/from condition codes

### Arithmetic Operations
- `ADD`, `ADC` - Add with/without carry
- `SUB`, `SBC` - Subtract with/without carry
- `INC`, `DEC` - Increment/decrement
- `NEG` - Two's complement negation
- `DAA` - Decimal adjust accumulator

### Logical Operations
- `AND`, `OR`, `EOR` - Bitwise operations
- `COM` - One's complement
- `TST` - Test (compare with zero)
- `BIT` - Bit test

### Shift and Rotate
- `ASL`, `ASR` - Arithmetic shift left/right
- `LSR` - Logical shift right
- `ROL`, `ROR` - Rotate left/right through carry

### Branch Instructions
- `BRA` - Branch always
- `BEQ`, `BNE` - Branch if equal/not equal
- `BCC`, `BCS` - Branch if carry clear/set
- `BPL`, `BMI` - Branch if plus/minus
- `BVC`, `BVS` - Branch if overflow clear/set
- `BHI`, `BLS` - Branch if higher/lower or same
- `BGE`, `BLT` - Branch if greater/less than (signed)
- `BGT`, `BLE` - Branch if greater than/less or equal (signed)

### Jump and Subroutine
- `JMP` - Jump to address
- `JSR` - Jump to subroutine
- `BSR` - Branch to subroutine
- `RTS` - Return from subroutine
- `RTI` - Return from interrupt

### Stack Operations
- `PSH`, `PUL` - Push/pull accumulator
- `INS`, `DES` - Increment/decrement stack pointer

### Control Operations
- `NOP` - No operation
- `SWI` - Software interrupt
- `WAI` - Wait for interrupt
- `CLC`, `SEC` - Clear/set carry flag
- `CLI`, `SEI` - Clear/set interrupt mask
- `CLV`, `SEV` - Clear/set overflow flag

### Comparison
- `CMP` - Compare accumulator
- `CPX` - Compare index register
- `CBA` - Compare accumulators

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

## Error Handling

The assembler provides comprehensive error detection and reporting:

### Syntax Errors
- Invalid instruction mnemonics
- Incorrect operand formats
- Missing required operands
- Invalid number formats

### Semantic Errors
- Undefined labels
- Duplicate label definitions
- Address out of range
- Invalid addressing mode for instruction

### Assembly Errors
- Values too large for data type
- Branch targets out of range
- Unsupported instruction combinations

### Simulator Errors
- Unknown opcodes (graceful halt)
- Memory access violations
- Infinite loop detection
- Stack overflow/underflow

## Command Line Usage

The assembler can be used from the command line for batch processing:

```bash
# Assemble a single file
python m6800_assembler.py examples/arithmetic.asm

# The assembler will output:
# - Success/failure status
# - Object code in hex format
# - Assembly mappings
# - Error messages (if any)
```

## Development and Debugging

### Debug Logging
The simulator creates detailed debug logs in the `logs/` directory:
- `simulator_debug_YYYYMMDD_HHMMSS.log` - Execution trace
- `gui_debug_YYYYMMDD_HHMMSS.log` - GUI interactions

### Contributing
When contributing to this project:
1. Follow Python PEP 8 style guidelines
2. Add comprehensive comments to complex algorithms
3. Test with all provided example programs
4. Update documentation for new features

## License

This project is developed for educational purposes as part of a System Programming course. Please refer to your institution's academic integrity policies when using this code.

## Acknowledgments

- Motorola 6800 Processor Reference Manual
- System Programming Course Materials
- Python Tkinter Documentation