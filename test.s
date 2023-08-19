bits 64
default rel

segment .text
    global main

    extern ExitProcess, puts

main:
    ; STR - "test.pang" line 1
    lea     rax, [string_0]
    push    rax

    ; CALL - "test.pang" line 1
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    puts
    push    rax

    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 72,101,108,108,111,44,32,87,111,114,108,100,33,0
