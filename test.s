bits 64
default rel

segment .text
    global main

    extern ExitProcess, WriteFile, GetStdHandle

main:
    ; STR - "test.pang" line 37
    lea     rax, [string_0]
    sub     rsp, 8
    push    rax

    ; ID - "test.pang" line 37
    call    __strlen_def_asm

    ; ID - "test.pang" line 37
    call    ___puts_def_asm

    add     rsp, 8
    xor     rax, rax
    call    ExitProcess

__strlen_def_asm:
    xor     rax, rax
    mov     rdi, [rsp + 8]

.loop:
    cmp     byte [rdi + rax], 0
    je      .done

    inc     rax
    jmp     .loop

.done:
    ret

___puts_def_asm:
    mov     r8, rax
    mov     rdx, [rsp + 8]
    mov     rcx, -11
    call    GetStdHandle
    mov     rcx, rax
    xor     r9, r9
    call    WriteFile
    ret

segment .data
    string_0 db 72,101,108,108,111,44,32,119,111,114,108,100,33,10,0
