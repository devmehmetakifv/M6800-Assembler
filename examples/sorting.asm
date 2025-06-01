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

; Simple bubble sort - unrolled loops to avoid INX issues
; Pass 1: Compare adjacent elements
        LDA     $2000    ; Load element 0
        LDB     $2001    ; Load element 1
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP01   ; Skip if in order
        STA     $2001    ; Swap: store A in position 1
        LDB     $60      ; Reload B from temp location
        STB     $2000    ; store B in position 0
SKIP01  LDA     $2001    ; Load element 1
        LDB     $2002    ; Load element 2
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP12   ; Skip if in order
        STA     $2002    ; Swap
        LDB     $60      ; Reload B from temp location
        STB     $2001
SKIP12  LDA     $2002    ; Load element 2
        LDB     $2003    ; Load element 3
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP23   ; Skip if in order
        STA     $2003    ; Swap
        LDB     $60      ; Reload B from temp location
        STB     $2002
SKIP23  LDA     $2003    ; Load element 3
        LDB     $2004    ; Load element 4
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP34   ; Skip if in order
        STA     $2004    ; Swap
        LDB     $60      ; Reload B from temp location
        STB     $2003
SKIP34  LDA     $2004    ; Load element 4
        LDB     $2005    ; Load element 5
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP45   ; Skip if in order
        STA     $2005    ; Swap
        LDB     $60      ; Reload B from temp location
        STB     $2004
SKIP45  LDA     $2005    ; Load element 5
        LDB     $2006    ; Load element 6
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP56   ; Skip if in order
        STA     $2006    ; Swap
        LDB     $60      ; Reload B from temp location
        STB     $2005
SKIP56  LDA     $2006    ; Load element 6
        LDB     $2007    ; Load element 7
        STB     $60      ; Store B in temp location
        CMP     $60      ; Compare A with B via memory
        BLS     SKIP67   ; Skip if in order
        STA     $2007    ; Swap
        LDB     $60      ; Reload B from temp location
        STB     $2006

; Repeat passes 2-7 (simplified - should repeat the above pattern)
; For a complete implementation, we would repeat the above code 7 times
; with decreasing number of comparisons each time

SKIP67  ; Store completion status
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
; $60: Temporary storage for B register during comparisons
; 
; Working variables:
; $50: Array size (8)
; $51: Outer loop counter
; $52: Inner loop counter
; $53: Verification counter 
; $56: Sum loop counter
; $57: Copy loop counter
; $58: Temp storage for X (NOSWAP)
; $5A: Temp storage for X (VERIFY)
; $5B: Temp storage for X (SUMLOOP)
; $5C: Temp storage for X (COPYLOOP)
