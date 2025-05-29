; Fibonacci Sequence Calculator
; Calculates the first 10 Fibonacci numbers and stores them in memory
; Author: System Programming Course Example

        ORG     $1000    ; Set origin address

; Initialize variables
START   LDA     #$00     ; First Fibonacci number (F0 = 0)
        STA     $2000    ; Store F0 at memory location $2000
        LDA     #$01     ; Second Fibonacci number (F1 = 1)
        STA     $2001    ; Store F1 at memory location $2001
        
        LDA     #$08     ; Counter for remaining numbers (10 - 2 = 8)
        STA     $50      ; Store counter at $50
        
        LDX     #$2002   ; X points to next storage location

; Main Fibonacci calculation loop
LOOP    LDA     $FFFE,X  ; Load F(n-2) (from X-2)
        LDB     $FFFF,X  ; Load F(n-1) (from X-1)
        ABA              ; A = F(n-2) + F(n-1) = F(n)
        STA     0,X      ; Store F(n) at current location
        
        INX              ; Increment X to next location
        DEC     $50      ; Decrement counter
        BNE     LOOP     ; Continue if counter != 0

; Find the largest Fibonacci number calculated
        LDX     #$2000   ; Reset X to start of array
        LDA     #$0A     ; Load count of numbers (10)
        STA     $51      ; Store count
        LDA     0,X      ; Load first number as initial max
        STA     $52      ; Store current maximum

FINDMAX INX              ; Move to next number
        LDB     0,X      ; Load next number
        CMP     A        ; Compare with current max
        BCC     NEXTNUM  ; Branch if A >= B (no new max)
        TBA              ; Transfer B to A (new maximum)
        STA     $52      ; Store new maximum

NEXTNUM DEC     $51      ; Decrement count
        BNE     FINDMAX  ; Continue if more numbers

; Store results summary
        LDA     $52      ; Load maximum value found
        STA     $3000    ; Store max at $3000
        LDA     #$0A     ; Load count of numbers calculated
        STA     $3001    ; Store count at $3001

; Display memory contents (simulation)
        LDX     #$2000   ; Point to start of results
        LDA     #$0A     ; Counter for display loop
        STA     $53

DISPLAY LDB     0,X      ; Load current Fibonacci number
        STB     $4000,X  ; Store in display area (simulation)
        INX              ; Next location
        DEC     $53      ; Decrement display counter
        BNE     DISPLAY  ; Continue display loop

; Program completion
        LDA     #$FF     ; Load completion code
        STA     $5000    ; Store completion flag
        
        SWI              ; Software interrupt (halt)
        
        END              ; End of program

; Memory Layout:
; $2000-$2009: Fibonacci sequence F0 through F9
; $3000: Maximum Fibonacci number found
; $3001: Count of numbers calculated (10)
; $4000-$4009: Copy of Fibonacci sequence for display
; $5000: Program completion flag
; $50: Work counter
; $51: Find max counter  
; $52: Current maximum value
; $53: Display counter 