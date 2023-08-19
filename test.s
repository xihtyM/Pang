bits 64
default rel

segment .text
    global main

    extern ExitProcess, fwrite, fopen, fclose, strlen

main:
    ; STR - "test.pang" line 3
    lea     rax, [string_0]
    push    rax

    ; STR - "test.pang" line 3
    lea     rax, [string_1]
    push    rax

    ; CALL - "test.pang" line 3
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    fopen
    push    rax

    ; STR - "test.pang" line 5
    lea     rax, [string_2]
    push    rax

    ; CALL - "test.pang" line 5
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    strlen
    push    rax

    ; SWAP - "test.pang" line 5
    pop     rax
    pop     rbx
    push    rax
    push    rbx

    ; INT - "test.pang" line 5
    push    1

    ; SWAP - "test.pang" line 5
    pop     rax
    pop     rbx
    push    rax
    push    rbx

    ; CALL - "test.pang" line 5
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    fwrite
    push    rax

    ; DROP - "test.pang" line 5
    pop     rax

    ; SWAP - "test.pang" line 5
    pop     rax
    pop     rbx
    push    rax
    push    rbx

    ; DROP - "test.pang" line 5
    pop     rax

    ; SWAP - "test.pang" line 5
    pop     rax
    pop     rbx
    push    rax
    push    rbx

    ; DROP - "test.pang" line 5
    pop     rax

    ; DROP - "test.pang" line 6
    pop     rax

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    fclose
    push    rax

    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 119,0
    string_1 db 116,101,115,116,46,116,120,116,0
    string_2 db 72,101,108,108,111,44,32,119,111,114,108,100,33,10,0
