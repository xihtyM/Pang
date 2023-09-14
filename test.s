bits 64
default rel

segment .text
    global main

    extern ExitProcess, __acrt_iob_func, strlen, fwrite

main:
    ; INT - "test.pang" line 3
    push    10

    ; WHILE - "test.pang" line 3
LOC_1:
    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; INT - "test.pang" line 3
    push    0

    ; NOT_EQUAL - "test.pang" line 3
    mov     rcx, 0
    mov     rdx, 1
    pop     rbx
    pop     rax
    cmp     rax, rbx
    cmovn   rcx, rdx
    push    rcx

    ; DO - "test.pang" line 3
    pop     rax
    test    rax, rax
    jz      LOC_49

    ; STR - "test.pang" line 4
    lea     rax, [string_0]
    push    rax

    ; INT - "test.pang" line 8
    push    1

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    __acrt_iob_func
    push    rax

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    strlen
    push    rax

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 8
    push    1

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    fwrite
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 5
    add     rsp, 16

    ; INT - "test.pang" line 6
    push    1

    ; SUB - "test.pang" line 6
    pop     rax
    sub     qword [rsp], rax

    ; DUP - "test.pang" line 7
    push    qword [rsp]

    ; INT - "test.pang" line 7
    push    1

    ; EQUAL - "test.pang" line 7
    mov     rcx, 0
    mov     rdx, 1
    pop     rbx
    pop     rax
    cmp     rax, rbx
    cmove   rcx, rdx
    push    rcx

    ; IF - "test.pang" line 7
    pop     rax
    test    rax, rax
    jz      LOC_48

    ; STR - "test.pang" line 8
    lea     rax, [string_1]
    push    rax

    ; INT - "test.pang" line 8
    push    1

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    __acrt_iob_func
    push    rax

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    strlen
    push    rax

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 8
    push    1

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; CALL - "test.pang" line 8
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    fwrite
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 8
    add     rsp, 8

    ; SWAP - "test.pang" line 8
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 9
    add     rsp, 16

    ; END - "test.pang" line 10
LOC_48:
    ; END - "test.pang" line 11
    jmp     LOC_1
LOC_49:
    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 72,101,108,108,111,32,87,111,114,108,100,33,10, 0
    string_1 db 49,32,109,111,114,101,32,116,111,32,103,111,33,10, 0
