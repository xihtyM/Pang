from pang_lib import *
from lexer import Lexer

def get_syscall(num: int, last: str = "pop(&vars.mem)") -> str:
    syscalls = {
        #0x001: "PANG_FORK();\n",
        0x002: "exit(%s);\n" % last,
        0x005: "PANG_OPEN(&vars);\n",
        0x006: "PANG_READ(&vars);\n",
        0x007: "PANG_WRITE(&vars);\n",
        0x008: "PANG_CLOSE(&vars);\n",
        0x00C: "std::this_thread::sleep_for(std::chrono::milliseconds(%s));\n" % last,
        0x010: "if (vars.mem.back() > 0) { vars.mem.resize(((int64_t) vars.mem.size()) - vars.mem.back() - 1); } else { vars.mem.resize(-vars.mem.back()); }\n",
        0x011: "if (vars.mem.back() < 0) { vars.mem.back() += vars.mem.size() - 1; } vars.mem.push_back(vars.mem[%s]);\n" % last,
        0x012: "vars.mem.push_back(vars.mem.size());\n"
    }

    if last != "pop(&vars.mem)":
        last = int(last)
    
    if num in (0x010, 0x011) and type(last) is int:
        if last > 0:
            syscalls[0x010] = "vars.mem.resize(((int64_t) vars.mem.size()) - %d);\n" % last
            syscalls[0x011] = "vars.mem.push_back(vars.mem[%d]);\n" % last
        else:
            syscalls[0x010] = "vars.mem.resize(-%d);\n" % last
            syscalls[0x011] = "vars.mem.back() += vars.mem.size() - 1; vars.mem.push_back(vars.mem[%d]);\n" % last

    if num not in syscalls:
        Croak(ErrorType.Stack, "Syscall number not valid. (number: %d)" % num)

    return syscalls[num]

def remove_newline(_Str: str) -> str:
    seperated = _Str.split("\n")
    if not seperated[-1]:
        seperated = seperated[:-1]

    return "\n".join(seperated[:-1]) + "\n"

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

def compile_ops(toks: list[Token]):
    out  = "bits 64\n"
    out += "default rel\n"
    out += "\n"
    out += "segment .data\n"
    out += "    buf db \"%c\", 0\n"
    out += "\n"
    out += "segment .text\n"
    out += "    global main\n"
    out += "\n"
    out += "    extern ExitProcess\n"
    out += "    extern printf\n"
    out += "\n"
    out += "main:\n"
    
    stack = []
    new_toks: list[Token] = []
    
    # optimise tokens
    for tok in toks:
        new_toks.append(tok)
        
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
            case TokenType.BUF:
                stack = []
    
    for tok in new_toks:
        out += "    ; %s - \"%s\" line %d\n" % (tok.typ._name_, tok.filename, tok.ln)
        match tok.typ:
            case TokenType.INT:
                out += "    push    %d\n\n" % tok.value
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
            case TokenType.BUF:
                out += "    ; temporary replacement of buf to print last item on stack\n"
                out += "    pop     rdx\n"
                out += "    push    rdx\n"
                out += "    sub     rsp, 32\n"
                out += "    lea     rcx, [buf]\n"
                out += "    call    printf\n"
                out += "    add     rsp, 32\n\n"

    out += "    xor     rax, rax\n"
    out += "    call    ExitProcess\n"
    
    return out

def join(l: list[int]) -> str:
    out = ""

    for ch in l:
        out += chr(ch)
    
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

    open(name, "w", encoding="utf-8").write(compile_ops(lex_src.toks))    
        
    os.system("nasm -fwin64 %s -o temp.obj" % name)
    os.system("ld -s temp.obj -o %s.exe -e main -lkernel32 -lmsvcrt" % outname)
    os.remove("temp.obj")
    
    if not asm:
        os.remove("temp.s")

if __name__ == "__main__":
    run_program()
