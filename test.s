bits 64
default rel

segment .data
    buf db "%c", 0

segment .text
    global main

    extern ExitProcess
    extern printf

main:
    ; INT - "test.pang" line 1
    push    105

    ; INT - "test.pang" line 1
    push    104

    ; BUF - "test.pang" line 1
    ; temporary replacement of buf to print last item on stack
    pop     rdx
    push    rdx
    sub     rsp, 32
    lea     rcx, [buf]
    call    printf
    add     rsp, 32

    ; DROP - "test.pang" line 1
    pop     rax

    ; BUF - "test.pang" line 1
    ; temporary replacement of buf to print last item on stack
    pop     rdx
    push    rdx
    sub     rsp, 32
    lea     rcx, [buf]
    call    printf
    add     rsp, 32

    xor     rax, rax
    call    ExitProcess
