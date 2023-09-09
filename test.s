bits 64
default rel

segment .text
    global main

    extern ExitProcess, printf

main:
    ; INT - "lib\coreprt.pang" line 4
    push    0

    ; INT - "lib\coreprt.pang" line 4
    push    1

    ; INT - "lib\coreprt.pang" line 4
    push    2

    ; INT - "lib\coreprt.pang" line 4
    push    3

    ; INT - "test.pang" line 3
    push    3

    ; STR - "test.pang" line 3
    lea     rax, [string_0]
    push    rax

    ; STR - "test.pang" line 5
    lea     rax, [string_1]
    push    rax

    ; CALL - "test.pang" line 5
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    printf
    push    rax

    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 116,101,115,116,46,112,97,110,103,0
    string_1 db 37,115,32,37,100,32,37,100,32,37,100,32,37,100,32,37,100,10,0
