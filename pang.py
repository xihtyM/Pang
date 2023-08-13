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

def compile_ops(toks: list[Token], asm_funcs: dict[str, str]):
    strings = []
    
    stack = []
    new_toks: list[Token] = []
    
    # optimise tokens
    for tok in toks:
        new_toks.append(tok)
        
        match tok.typ:
            case TokenType.INT:
                stack.append(tok.value)
                allocs += 1
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
            case _:
                stack = []
    
    out  = "bits 64\n"
    out += "default rel\n"
    out += "\n"
    out += "segment .text\n"
    out += "    global main\n"
    out += "\n"
    out += "    extern ExitProcess, WriteFile, GetStdHandle\n"
    out += "\n"
    out += "main:\n"
    
    for tok in new_toks:
        out += "    ; %s - \"%s\" line %d\n" % (tok.typ._name_, tok.filename, tok.ln)
        match tok.typ:
            case TokenType.INT:
                out += "    push    %d\n\n" % tok.value
            case TokenType.STR:
                out += "    lea     rax, [string_%d]\n" % len(strings)
                out += "    push    rax\n\n"
                strings.append(tok.value)
            case TokenType.ADD:
                out += "    pop     rbx\n"
                out += "    pop     rax\n"
                out += "    add     rax, rbx\n"
                out += "    push    rax\n\n"
            case TokenType.SUB:
                out += "    pop     rbx\n"
                out += "    pop     rax\n"
                out += "    sub     rax, rbx\n"
                out += "    push    rax\n\n"
            case TokenType.MUL:
                out += "    pop     rbx\n"
                out += "    pop     rax\n"
                out += "    imul    rax, rbx\n"
                out += "    push    rax\n\n"
            case TokenType.DUP:
                out += "    push    qword [rsp]\n\n"
            case TokenType.DROP:
                out += "    pop     rax\n\n"
            case TokenType.SWAP:
                out += "    pop     rax\n"
                out += "    pop     rbx\n"
                out += "    push    rbx\n"
                out += "    push    rax\n\n"
            case TokenType.ID:
                out += "    call    %s\n\n" % tok.value
    
    out += "    xor     rax, rax\n"
    out += "    call    ExitProcess\n\n"
    
    for name in asm_funcs:
        out += name + ":\n"
        out += asm_funcs[name].strip("\n") + "\n\n"
    
    
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
    
    lex_src = Lexer(src, src_filename)
    lex_src.get_tokens()

    name = "temp.s" if not asm else outname + ".s"
    
    open(name, "w", encoding="utf-8").write(compile_ops(lex_src.toks, lex_src.assembly))    

    if not asm:
        os.system("nasm -fwin64 %s -o temp.obj" % name)
        os.system("ld -s temp.obj -o %s.exe -e main -lkernel32 -lmsvcrt" % outname)
        os.remove("temp.obj")
        os.remove("temp.s")

if __name__ == "__main__":
    run_program()
