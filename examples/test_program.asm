; ===============================================
; Simple M6800 Test Program: Countdown Counter
; Tests: Load/Store, Arithmetic, Branching, Memory
; ===============================================

.org $1000                    ; Start program at $1000

; Initialize countdown value
start:
    ldaa #10                  ; Load 10 into accumulator A
    staa counter              ; Store in memory location 'counter'
    ldaa #$00                 ; Clear A
    staa result               ; Clear result location

; Main countdown loop
countdown_loop:
    ldaa counter              ; Load current counter value
    cmpa #0                   ; Compare with 0
    beq  done                 ; Branch to done if zero
    
    ; Do some arithmetic operations
    ldab counter              ; Load counter into B
    aba                       ; Add B to A (A = A + B)
    staa result               ; Store sum in result
    
    ; Decrement counter
    ldaa counter              ; Load counter again
    deca                      ; Decrement A (test our DECA instruction!)
    staa counter              ; Store back to counter
    
    ; Test comparison and branching
    cmpb #5                   ; Compare B with 5
    bls  continue             ; Branch if B <= 5 (test our BLS instruction!)
    
    ; If counter > 5, negate the result
    ldaa result               ; Load result
    nega                      ; Negate it (test NEGA instruction!)
    staa result               ; Store back
    
continue:
    bra  countdown_loop       ; Branch back to loop

; Program completion
done:
    ldaa result               ; Load final result
    staa final_result         ; Store in final location
    swi                       ; Software interrupt (halt)

; Data area
.org $2000
counter:      .byte 0         ; Counter variable
result:       .byte 0         ; Temporary result
final_result: .byte 0         ; Final result storage

.end 