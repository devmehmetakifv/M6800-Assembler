; Simple Arithmetic Operations Example
; Demonstrates basic arithmetic with two 8-bit numbers
; Author: M6800 Assembly Tutorial

        ORG     $1000    ; Set origin address to $1000

; Initialize two numbers for arithmetic operations
START   LDA     #$15     ; Load first number (21 decimal) into A
        STA     $50      ; Store first number at $50
        LDB     #$0A     ; Load second number (10 decimal) into B  
        STB     $51      ; Store second number at $51

; Addition: A + B
        LDA     $50      ; Load first number
        LDB     $51      ; Load second number  
        STB     $60      ; Store B in temp location for comparison
        ADD     $51      ; Add second number to A (A = A + memory[$51])
        STA     $52      ; Store sum at $52 (result = 31 decimal)

; Subtraction: A - B  
        LDA     $50      ; Load first number (21)
        SUB     $51      ; Subtract second number (A = 21 - 10 = 11)
        STA     $53      ; Store difference at $53

; Comparison and conditional storage
        LDA     $50      ; Load first number (21)
        CMP     $51      ; Compare A with second number (10)
        BLS     SMALLER  ; Branch if A <= memory[$51]
        
        ; A is larger than B
        LDA     #$01     ; Set flag to 1 (A > B)
        STA     $54      ; Store comparison result
        BRA     DONE     ; Branch to end
        
SMALLER ; A is smaller or equal to B  
        LDA     #$00     ; Set flag to 0 (A <= B)
        STA     $54      ; Store comparison result

DONE    ; Set completion flag
        LDA     #$FF     ; Completion marker
        STA     $5000    ; Store at completion address
        
        SWI              ; Software interrupt (halt)
        END              ; End of program

; Memory Layout:
; $50: First number (21)
; $51: Second number (10) 
; $52: Sum result (31)
; $53: Difference result (11)
; $54: Comparison flag (1 if first > second, 0 otherwise)
; $60: Temporary storage
; $5000: Program completion flag 