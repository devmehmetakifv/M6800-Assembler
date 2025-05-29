; Bubble Sort Algorithm Implementation
; Sorts an array of 8 numbers in ascending order
; Author: System Programming Course Example

        ORG     $1000    ; Set origin address

; Initialize test data array (8 unsorted numbers)
START   LDA     #$45     ; Initialize array with test data
        STA     $2000    ; Array[0] = $45 (69)
        LDA     #$12
        STA     $2001    ; Array[1] = $12 (18)
        LDA     #$89
        STA     $2002    ; Array[2] = $89 (137)
        LDA     #$23
        STA     $2003    ; Array[3] = $23 (35)
        LDA     #$67
        STA     $2004    ; Array[4] = $67 (103)
        LDA     #$34
        STA     $2005    ; Array[5] = $34 (52)
        LDA     #$78
        STA     $2006    ; Array[6] = $78 (120)
        LDA     #$11
        STA     $2007    ; Array[7] = $11 (17)

; Set up sorting parameters
        LDA     #$08     ; Array size = 8
        STA     $50      ; Store array size
        STA     $51      ; Outer loop counter

; Outer loop: for i = 0 to n-1
OUTER   LDA     $51      ; Load outer counter
        DEC              ; Decrement for inner loop limit
        STA     $52      ; Store inner loop counter
        
        LDX     #$2000   ; Reset array pointer to start

; Inner loop: for j = 0 to n-i-1  
INNER   LDA     0,X      ; Load current element
        LDB     1,X      ; Load next element
        CMP     B        ; Compare current with next
        BLS     NOSWAP   ; Branch if current <= next (no swap needed)

; Swap elements (current > next)
        STA     1,X      ; Store current in next position
        STB     0,X      ; Store next in current position

NOSWAP  INX              ; Move to next position
        DEC     $52      ; Decrement inner counter
        BNE     INNER    ; Continue inner loop if not zero

; End of inner loop, check outer loop
        DEC     $51      ; Decrement outer counter
        BNE     OUTER    ; Continue outer loop if not zero

; Sorting complete - verify results
        LDX     #$2000   ; Point to start of sorted array
        LDA     #$07     ; Counter for verification (n-1 comparisons)
        STA     $53

VERIFY  LDB     0,X      ; Load current element
        LDA     1,X      ; Load next element
        CMP     B        ; Compare next with current
        BCS     SORTFAIL ; Branch if next < current (sort failed)
        
        INX              ; Move to next position
        DEC     $53      ; Decrement verification counter
        BNE     VERIFY   ; Continue if more to verify

; Sort successful
        LDA     #$01     ; Success code
        STA     $3000    ; Store success flag
        BRA     STATS    ; Branch to statistics

SORTFAIL LDA    #$00     ; Failure code
        STA     $3000    ; Store failure flag

; Calculate statistics
STATS   LDX     #$2000   ; Point to sorted array
        LDA     0,X      ; Load minimum value (first element)
        STA     $3001    ; Store minimum
        LDA     $2007    ; Load maximum value (last element)
        STA     $3002    ; Store maximum

; Calculate sum of all elements
        LDX     #$2000   ; Reset to start of array
        LDA     #$00     ; Initialize sum
        LDB     #$08     ; Element counter

SUMLOOP ADD     0,X      ; Add current element to sum
        INX              ; Next element
        DEC     B        ; Decrement counter
        BNE     SUMLOOP  ; Continue if more elements

        STA     $3003    ; Store sum

; Copy sorted array to display area
        LDX     #$2000   ; Source array
        LDB     #$08     ; Copy counter

COPY    LDA     0,X      ; Load from source
        STA     $4000,X  ; Store to display area
        INX              ; Next position
        DEC     B        ; Decrement counter
        BNE     COPY     ; Continue copying

; Program completion
        LDA     #$FF     ; Completion flag
        STA     $5000    ; Store completion indicator
        
        SWI              ; Software interrupt (halt)
        
        END              ; End of program

; Memory Layout:
; $2000-$2007: Original array (becomes sorted array)
; $3000: Sort success flag (1=success, 0=failure)
; $3001: Minimum value in sorted array
; $3002: Maximum value in sorted array  
; $3003: Sum of all elements
; $4000-$4007: Copy of sorted array for display
; $5000: Program completion flag
; 
; Working variables:
; $50: Array size (8)
; $51: Outer loop counter
; $52: Inner loop counter
; $53: Verification counter 
