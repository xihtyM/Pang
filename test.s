bits 64
default rel

segment .text
    global main

    extern ExitProcess, fwrite, malloc, free, strlen, __acrt_iob_func

main:
    ; INT - "test.pang" line 3
    push    0

    ; CALL - "test.pang" line 4
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    __acrt_iob_func
    push    rax

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 4
    add     rsp, 8

    ; INT - "test.pang" line 3
    push    256

    ; CALL - "test.pang" line 3
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    malloc
    push    rax

    ; SWAP - "test.pang" line 3
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; STR - "test.pang" line 3
    lea     rax, [string_0]
    push    rax

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

    ; STR - "test.pang" line 4
    lea     rax, [string_1]
    push    rax

    ; INT - "test.pang" line 4
    push    1

    ; CALL - "test.pang" line 4
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    __acrt_iob_func
    push    rax

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 4
    add     rsp, 8

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; CALL - "test.pang" line 4
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    strlen
    push    rax

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; INT - "test.pang" line 4
    push    1

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; CALL - "test.pang" line 4
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    fwrite
    push    rax

    ; DROP - "test.pang" line 4
    add     rsp, 8

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 4
    add     rsp, 8

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 4
    add     rsp, 8

    ; SWAP - "test.pang" line 4
    pop     rax
    xchg    qword [rsp], rax
    push    rax

    ; DROP - "test.pang" line 5
    add     rsp, 8

    ; CALL - "test.pang" line 5
    mov     rcx, [rsp]
    mov     rdx, [rsp + 8]
    mov     r8, [rsp + 16]
    mov     r9, [rsp + 24]
    call    free
    push    rax

    xor     rax, rax
    call    ExitProcess

segment .data
    string_0 db 37,91,94,10,93, 0
    string_1 db 116,101,115,116, 0
