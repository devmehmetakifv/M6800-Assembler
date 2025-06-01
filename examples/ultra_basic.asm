; Basic Motorola 6800 Assembly Example
; Demonstrates fundamental instructions and addressing modes
; Author: System Programming Course Example

        ORG     $1000    ; Set origin address to $1000

; Basic load and store operations
START   LDA     #$42     ; Load accumulator A with immediate value $42
        STA     $50      ; Store A at direct page address $50
        LDB     #$24     ; Load accumulator B with immediate value $24
        STB     $51      ; Store B at direct page address $51