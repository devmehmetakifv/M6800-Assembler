; Data Copy and Memory Operations Example
; Demonstrates copying data between memory locations
; Author: M6800 Assembly Tutorial

        ORG     $1000    ; Set origin address to $1000

; Initialize source data array (4 bytes)
START   LDA     #$AA     ; Load first data byte
        STA     $2000    ; Store at source[0]
        LDA     #$BB     ; Load second data byte
        STA     $2001    ; Store at source[1]  
        LDA     #$CC     ; Load third data byte
        STA     $2002    ; Store at source[2]
        LDA     #$DD     ; Load fourth data byte
        STA     $2003    ; Store at source[3]

; Copy data from source ($2000-$2003) to destination ($3000-$3003)
COPY1   LDA     $2000    ; Load source[0]
        STA     $3000    ; Store to destination[0]
        
COPY2   LDA     $2001    ; Load source[1] 
        STA     $3001    ; Store to destination[1]
        
COPY3   LDA     $2002    ; Load source[2]
        STA     $3002    ; Store to destination[2]
        
COPY4   LDA     $2003    ; Load source[3]
        STA     $3003    ; Store to destination[3]

; Verify copy by comparing source and destination
VERIFY1 LDA     $2000    ; Load source[0]
        CMP     $3000    ; Compare with destination[0]
        BNE     ERROR    ; Branch if not equal
        
VERIFY2 LDA     $2001    ; Load source[1]
        CMP     $3001    ; Compare with destination[1]  
        BNE     ERROR    ; Branch if not equal
        
VERIFY3 LDA     $2002    ; Load source[2]
        CMP     $3002    ; Compare with destination[2]
        BNE     ERROR    ; Branch if not equal
        
VERIFY4 LDA     $2003    ; Load source[3]
        CMP     $3003    ; Compare with destination[3]
        BNE     ERROR    ; Branch if not equal

; Copy successful
SUCCESS LDA     #$01     ; Success flag
        STA     $5000    ; Store success indicator
        BRA     DONE     ; Branch to end

; Copy failed  
ERROR   LDA     #$00     ; Error flag
        STA     $5000    ; Store error indicator

DONE    LDA     #$FF     ; Completion flag
        STA     $5001    ; Store completion marker
        
        SWI              ; Software interrupt (halt)
        END              ; End of program

; Memory Layout:
; $2000-$2003: Source data array [AA, BB, CC, DD]
; $3000-$3003: Destination data array (copy of source)
; $5000: Success/Error flag (1=success, 0=error)
; $5001: Program completion flag 