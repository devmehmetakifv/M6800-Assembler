; Find Minimum and Maximum Values Example
; Demonstrates finding min/max in a small array using comparisons
; Author: M6800 Assembly Tutorial

        ORG     $1000    ; Set origin address to $1000

; Initialize test data array (4 numbers)
START   LDA     #$25     ; Load first number (37 decimal)
        STA     $2000    ; Store at array[0]
        LDA     #$42     ; Load second number (66 decimal)
        STA     $2001    ; Store at array[1]
        LDA     #$18     ; Load third number (24 decimal)
        STA     $2002    ; Store at array[2]
        LDA     #$55     ; Load fourth number (85 decimal)
        STA     $2003    ; Store at array[3]

; Initialize min and max with first element
        LDA     $2000    ; Load first element
        STA     $50      ; Store as current minimum
        STA     $51      ; Store as current maximum

; Check element 1 against current min/max
CHK1    LDA     $2001    ; Load array[1] (66)
        CMP     $50      ; Compare with current min (37)
        BLS     CHK1_MAX ; Branch if A <= min (don't update min)
        ; A > min, so don't update min, check max
CHK1_MAX CMP    $51      ; Compare with current max (37)
        BLS     CHK2     ; Branch if A <= max (don't update max)
        ; A > max, update max
        STA     $51      ; Store new maximum

; Check element 2 against current min/max  
CHK2    LDA     $2002    ; Load array[2] (24)
        CMP     $50      ; Compare with current min (37)
        BCC     CHK2_MAX ; Branch if A >= min (don't update min)
        ; A < min, update min
        STA     $50      ; Store new minimum
CHK2_MAX CMP    $51      ; Compare with current max (66)
        BLS     CHK3     ; Branch if A <= max (don't update max)
        ; A > max, update max
        STA     $51      ; Store new maximum

; Check element 3 against current min/max
CHK3    LDA     $2003    ; Load array[3] (85)
        CMP     $50      ; Compare with current min (24)
        BCC     CHK3_MAX ; Branch if A >= min (don't update min)
        ; A < min, update min
        STA     $50      ; Store new minimum
CHK3_MAX CMP    $51      ; Compare with current max (66)
        BLS     DONE     ; Branch if A <= max (don't update max)
        ; A > max, update max
        STA     $51      ; Store new maximum

; Calculate range (max - min)
DONE    LDA     $51      ; Load maximum value
        SUB     $50      ; Subtract minimum (A = max - min)
        STA     $52      ; Store range

; Store results to final locations
        LDA     $50      ; Load minimum value
        STA     $3000    ; Store minimum at $3000
        LDA     $51      ; Load maximum value  
        STA     $3001    ; Store maximum at $3001
        LDA     $52      ; Load range value
        STA     $3002    ; Store range at $3002

; Set completion flag
        LDA     #$FF     ; Completion marker
        STA     $5000    ; Store completion flag
        
        SWI              ; Software interrupt (halt)
        END              ; End of program

; Expected Results:
; Array: [37, 66, 24, 85]
; Minimum: 24 ($18)
; Maximum: 85 ($55)  
; Range: 61 ($3D)
;
; Memory Layout:
; $2000-$2003: Source array [37, 66, 24, 85]
; $50: Working minimum value
; $51: Working maximum value
; $52: Calculated range (max - min)
; $3000: Final minimum value (24)
; $3001: Final maximum value (85)
; $3002: Final range value (61)
; $5000: Program completion flag 