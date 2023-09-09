from pang_lib import *
from lexer import Lexer

def remove_prev_2(toks: list[Token]):
    indexes = []
    for index, tok in enumerate(toks[::-1], 1):
        if len(indexes) >= 2:
            break
        
        if tok.typ in (TokenType.INT, TokenType.ADD,
                       TokenType.SUB, TokenType.MUL,
                       TokenType.DIV, TokenType.MOD,
                       TokenType.DUP):
            indexes.append(index)
    
    if len(indexes) != 2:
        Croak(ErrorType.Compile, "optimisation error, open issue on github")
    
    toks.pop(-min(indexes))
    toks.pop(-(max(indexes) - 1))

def compile_ops(toks: list[Token], calls: list[str]):
    strings = []
    
    stack = []
    new_toks: list[Token] = []
    drops = 0
    
    # optimise tokens
    for tok in toks:
        new_toks.append(tok)
        
        if tok.typ != TokenType.DROP:
            drops = 0
        
        match tok.typ:
            case TokenType.INT:
                stack.append(tok.value)
            case TokenType.ADD:
                if len(stack) >= 2:
                    stack.append(stack.pop() + stack.pop())
                    new_toks.pop()
                    remove_prev_2(new_toks)
                    new_toks.append(Token(TokenType.INT, "", stack[-1], tok.filename, tok.ln))
            case TokenType.SUB:
                if len(stack) >= 2:
                    stack.append(-stack.pop() + stack.pop())
                    new_toks.pop()
                    remove_prev_2(new_toks)
                    new_toks.append(Token(TokenType.INT, "", stack[-1], tok.filename, tok.ln))
            case TokenType.MUL:
                if len(stack) >= 2:
                    stack.append(stack.pop() * stack.pop())
                    new_toks.pop()
                    remove_prev_2(new_toks)
                    new_toks.append(Token(TokenType.INT, "", stack[-1], tok.filename, tok.ln))
            case TokenType.DROP:
                if stack:
                    stack.pop()
                
                if drops:
                    new_toks.pop()
                
                drops += 1
                new_toks[-1].value = drops
            case _:
                stack = []
    
    out  = "bits 64\n"
    out += "default rel\n"
    out += "\n"
    out += "segment .text\n"
    out += "    global main\n"
    out += "\n"
    out += "    extern ExitProcess"
    
    if calls:
        out += ", " + ", ".join(calls)
    
    out += "\n\n"
    out += "main:\n"
    
    for tok in new_toks:
        out += "    ; %s - \"%s\" line %d\n" % (tok.typ._name_, tok.filename, tok.ln)
        match tok.typ:
            case TokenType.INT:
                if tok.value >= 1<<64:
                    Croak(ErrorType.IntegerTooLarge, "integer too large to push to the stack, must be a 64 bit integer.")
                
                if tok.value >= 1<<32:
                    out += "    mov     rax, %d\n" % tok.value
                    out += "    push    rax\n\n"
                else:
                    out += "    push    %d\n\n" % tok.value
            case TokenType.STR:
                out += "    lea     rax, [string_%d]\n" % len(strings)
                out += "    push    rax\n\n"
                strings.append(tok.value)
            case TokenType.ADD:
                out += "    pop     rax\n"
                out += "    add     qword [rsp], rax\n\n"
            case TokenType.IADD:
                out += "    pop     rbx\n"
                out += "    pop     rax\n"
                out += "    add     qword [rax], rbx\n"
                out += "    push    rax\n\n"
            case TokenType.SUB:
                out += "    pop     rax\n"
                out += "    sub     qword [rsp], rax\n\n"
            case TokenType.ISUB:
                out += "    pop     rbx\n"
                out += "    pop     rax\n"
                out += "    sub     qword [rax], rbx\n"
                out += "    push    rax\n\n"
            case TokenType.MUL:
                out += "    pop     rax\n"
                out += "    imul    qword [rsp], rax\n\n"
            case TokenType.IMUL:
                out += "    pop     rbx\n"
                out += "    pop     rax\n"
                out += "    imul    qword [rax], rbx\n"
                out += "    push    rax\n\n"
            case TokenType.DUP:
                out += "    push    qword [rsp]\n\n"
            case TokenType.DROP:
                out += "    add     rsp, %d\n\n" % (tok.value * 8)
            case TokenType.SWAP:
                out += "    pop     rax\n"
                out += "    xchg    qword [rsp], rax\n"
                out += "    push    rax\n\n"
            case TokenType.CALL:
                out += "    mov     rcx, [rsp]\n"
                out += "    mov     rdx, [rsp + 8]\n"
                out += "    mov     r8, [rsp + 16]\n"
                out += "    mov     r9, [rsp + 24]\n"
                out += "    call    %s\n" % tok.value
                out += "    push    rax\n\n"
            case TokenType.APPLY: # dereference
                out += "    pop     rax\n"
                out += "    push    qword [rax]\n\n"
            case TokenType.QUOTE: # reference
                out += "    lea     rax, [rsp]\n"
                out += "    push    rax\n\n"
            case TokenType.BITNOT:
                out += "    not     qword [rsp]\n\n"
            case TokenType.BITAND:
                out += "    pop     rax\n"
                out += "    and     qword [rsp], rax\n\n"
    
    out += "    xor     rax, rax\n"
    out += "    call    ExitProcess\n\n"
    
    out += "segment .data\n"
    for index, string in enumerate(strings):
        out += "    string_%d db %s,0\n" % (index, ",".join(map(str, list(bytes(string, "utf-8")))))
    
    return out

def run_program() -> None:
    filename = False
    asm = False

    outname = "a"
    src_filename = None
    
    for arg in sys.argv[1:]: # remove main name
        if filename:
            outname = arg
            filename = None
        elif arg == "-o":
            if filename is None:
                Croak(ErrorType.Command, "cannot have two output names...")
            
            filename = True
        elif arg == "-S":
            asm = True
        else:
            if src_filename:
                Croak(ErrorType.Command, "can only compile 1 file at a time")
            src_filename = arg
    
    if not src_filename:
        Croak(ErrorType.Command, "no filename provided")
    
    src = open(src_filename, "r", encoding="utf-8").read()
    
    time = perf_counter()
    lex_src = Lexer(src, src_filename)
    lex_src.get_tokens()

    name = "temp.s" if not asm else outname + ".s"
    
    open(name, "w", encoding="utf-8").write(compile_ops(lex_src.toks, lex_src.calls))    
    print("Sucessfully compiled in %.5f seconds." % (perf_counter() - time))

    if not asm:
        os.system("nasm -fwin64 %s -o temp.obj" % name)
        os.system("ld -s temp.obj -o %s.exe -e main -lkernel32 -lmsvcrt" % outname)
        os.remove("temp.obj")
        os.remove("temp.s")

if __name__ == "__main__":
    run_program()
