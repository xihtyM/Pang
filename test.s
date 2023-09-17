bits 64
default rel

segment .text
    global main

    extern ExitProcess, printf

main:
    ; setup
    mov     r15, 0

    ; QUOTE - "test.pang" line 3
    lea     rax, [rsp]
    push    rax

    ; INT - "test.pang" line 3
    push    8

    ; SUB - "test.pang" line 3
    pop     rax
    sub     qword [rsp], rax

    ; INT - "test.pang" line 3
    push    8

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 3
    push    8

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 3
    push    0

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; APPLY - "test.pang" line 3
    pop     rax
    mov     rax, qword [rax]
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 3
    push    8

    ; SUB - "test.pang" line 3
    pop     rax
    sub     qword [rsp], rax

    ; WHILE - "test.pang" line 3
LOC_15:
    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; APPLY - "test.pang" line 3
    pop     rax
    mov     rax, qword [rax]
    push    rax

    ; DO - "test.pang" line 3
    pop     rax
    test    rax, rax
    jz      LOC_40

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; APPLY - "test.pang" line 3
    pop     rax
    mov     rax, qword [rax]
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; GREATER_THAN - "test.pang" line 3
    pop     rbx
    pop     rax
    cmp     rax, rbx
    setg    r15b
    push    r15

    ; IF - "test.pang" line 3
    pop     rax
    test    rax, rax
    jz      LOC_33

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 3
    add     rsp, 8

    ; ELSE - "test.pang" line 3
    jmp     LOC_37
LOC_33:
    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 3
    add     rsp, 8

    ; END - "test.pang" line 3
LOC_37:
    ; INT - "test.pang" line 3
    push    8

    ; SUB - "test.pang" line 3
    pop     rax
    sub     qword [rsp], rax

    ; END - "test.pang" line 3
    jmp     LOC_15
LOC_40:
    ; DROP - "test.pang" line 3
    add     rsp, 8

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; INT - "test.pang" line 3
    push    0

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; WHILE - "test.pang" line 3
LOC_46:
    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; APPLY - "test.pang" line 3
    pop     rax
    mov     rax, qword [rax]
    push    rax

    ; DO - "test.pang" line 3
    pop     rax
    test    rax, rax
    jz      LOC_58

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; APPLY - "test.pang" line 3
    pop     rax
    mov     rax, qword [rax]
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; ADD - "test.pang" line 3
    pop     rax
    add     qword [rsp], rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 3
    push    8

    ; SUB - "test.pang" line 3
    pop     rax
    sub     qword [rsp], rax

    ; END - "test.pang" line 3
    jmp     LOC_46
LOC_58:
    ; DROP - "test.pang" line 3
    add     rsp, 8

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 3
    add     rsp, 8

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; OVER - "test.pang" line 3
    pop     rax
    xchg    qword [rsp + 8], rax
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DIVMOD - "test.pang" line 3
    pop     rcx
    pop     rax
    cqo
    idiv    rcx
    push    rax
    push    rdx

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 3
    add     rsp, 8

    ; DUP - "test.pang" line 3
    push    qword [rsp]

    ; INT - "test.pang" line 3
    push    0

    ; NOT_EQUAL - "test.pang" line 3
    pop     rbx
    pop     rax
    cmp     rax, rbx
    setne   r15b
    push    r15

    ; IF - "test.pang" line 3
    pop     rax
    test    rax, rax
    jz      LOC_79

    ; SUB - "test.pang" line 3
    pop     rax
    sub     qword [rsp], rax

    ; ADD - "test.pang" line 3
    pop     rax
    add     qword [rsp], rax

    ; ELSE - "test.pang" line 3
    jmp     LOC_80
LOC_79:
    ; DROP - "test.pang" line 3
    add     rsp, 16

    ; END - "test.pang" line 3
LOC_80:
    ; STR - "test.pang" line 3
    lea     rax, [string_0]
    push    rax

    ; CALL - "test.pang" line 3
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    printf
    push    rax

    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 37,100,10,0
