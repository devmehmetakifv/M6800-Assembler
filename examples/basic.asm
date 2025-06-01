; Basic Motorola 6800 Assembly Example
; Demonstrates fundamental instructions and addressing modes
; Author: System Programming Course Example

        ORG     $1000    ; Set origin address to $1000

; Basic load and store operations
START   LDA     #$42     ; Load accumulator A with immediate value $42
        STA     $50      ; Store A at direct page address $50
        LDB     #$24     ; Load accumulator B with immediate value $24
        STB     $51      ; Store B at direct page address $51

; Extended addressing example
        LDA     #$FF     ; Load A with $FF
        STA     $2000    ; Store A at extended address $2000
        LDB     #$00     ; Load B with $00
        STB     $2001    ; Store B at extended address $2001

; Index register operations
        LDX     #$2000   ; Load X with base address $2000
        LDA     0,X      ; Load A from address in X (indirect)
        INC              ; Increment A
        STA     1,X      ; Store A at address X+1

; Arithmetic operations
        LDA     #$10     ; Load A with $10
        LDB     #$05     ; Load B with $05
        ABA              ; Add B to A (A = A + B)
        STA     $52      ; Store result

; Comparison and branching
        CMP     #$15     ; Compare A with $15
        BEQ     EQUAL    ; Branch if equal
        BRA     NOTEQUAL ; Branch always to NOTEQUAL

EQUAL   LDA     #$01     ; Load success code
        STA     $53      ; Store success indicator
        BRA     FINISH   ; Branch to finish

NOTEQUAL LDA    #$00     ; Load failure code
        STA     $53      ; Store failure indicator

; Register transfer operations
FINISH  TAB              ; Transfer A to B
        TBA              ; Transfer B to A
        
; Clear and test operations
        CLR     $54      ; Clear memory location $54
        TST              ; Test accumulator A
        
; Final halt
        SWI              ; Software interrupt (halt)
        
        END              ; End of program 