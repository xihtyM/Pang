bits 64
default rel

segment .text
    global main

    extern ExitProcess, WriteFile, GetStdHandle

main:
    ; STR - "test.pang" line 3
    lea     rax, [string_0]
    push    rax

    ; ID - "test.pang" line 3
    call    ___strlen_def_asm

    ; ID - "test.pang" line 3
    call    ___puts_def_asm

    xor     rax, rax
    call    ExitProcess

___strlen_def_asm:
    xor     rax, rax
    mov     rdi, [rsp + 8]

.loop:
    cmp     byte [rdi + rax], 0
    je      .done

    inc     rax
    jmp     .loop

.done:
    pop     rbx
    push    rax
    push    rbx
    ret

___puts_def_asm:
    mov     r8, [rsp + 8]
    mov     rdx, [rsp + 16]
    mov     rcx, -11
    call    GetStdHandle
    mov     rcx, rax
    xor     r9, r9
    call    WriteFile
    ret

segment .data
    string_0 db 72,101,108,108,111,44,32,87,111,114,108,100,33,10,0
