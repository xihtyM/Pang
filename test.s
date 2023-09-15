bits 64
default rel

segment .text
    global main

    extern ExitProcess, printf

main:
    ; STR - "test.pang" line 3
    lea     rax, [string_0]
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; WHILE - "test.pang" line 3
LOC_3:
    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; APPLY - "test.pang" line 3
    pop     rax
    movzx   rax, byte [rax]
    push    rax

    ; INT - "test.pang" line 3
    push    0

    ; NOT_EQUAL - "test.pang" line 3
    mov     rcx, 0
    mov     rdx, 1
    pop     rbx
    pop     rax
    cmp     rax, rbx
    cmovne  rcx, rdx
    push    rcx

    ; DO - "test.pang" line 3
    pop     rax
    test    rax, rax
    jz      LOC_11

    ; INT - "test.pang" line 3
    push    1

    ; ADD - "test.pang" line 3
    pop     rax
    add     qword [rsp], rax

    ; END - "test.pang" line 3
    jmp     LOC_3
LOC_11:
    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; SUB - "test.pang" line 3
    pop     rax
    sub     qword [rsp], rax

    ; STR - "test.pang" line 4
    lea     rax, [string_1]
    push    rax

    ; CALL - "test.pang" line 4
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    printf
    push    rax

    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 72,101,108,108,111,44,32,87,111,114,108,100,33,10, 0
    string_1 db 37,100,10, 0
