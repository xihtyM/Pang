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

def compile_ops_x64(toks: list[Token], calls: list[str]):
    strings = []
    
    stack = []
    new_toks: list[Token] = []
    drops = 0
    labels = 0
    
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
    
    labels_dict = {
        "main": ""
    }
    
    res  = "bits 64\n"
    res += "default rel\n"
    res += "\n"
    res += "segment .text\n"
    res += "    global main\n"
    res += "\n"
    res += "    extern ExitProcess"
    
    if calls:
        res += ", " + ", ".join(calls)
    
    res += "\n\n"
    
    current_label = "main"
    nests = []
    
    for tok in new_toks:
        labels_dict[current_label] += "    ; %s - \"%s\" line %d\n" % (tok.typ._name_, tok.filename, tok.ln)
        match tok.typ:
            case TokenType.INT:
                if tok.value >= 1<<64:
                    Croak(ErrorType.IntegerTooLarge, "integer too large to push to the stack, must be a 64 bit integer.")
                
                if tok.value >= 1<<32:
                    labels_dict[current_label] += "    mov     rax, %d\n" % tok.value
                    labels_dict[current_label] += "    push    rax\n\n"
                else:
                    labels_dict[current_label] += "    push    %d\n\n" % tok.value
            case TokenType.STR:
                labels_dict[current_label] += "    lea     rax, [string_%d]\n" % len(strings)
                labels_dict[current_label] += "    push    rax\n\n"
                strings.append(tok.value)
            case TokenType.ADD:
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    add     qword [rsp], rax\n\n"
            case TokenType.IADD:
                labels_dict[current_label] += "    pop     rbx\n"
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    add     qword [rax], rbx\n"
                labels_dict[current_label] += "    push    rax\n\n"
            case TokenType.SUB:
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    sub     qword [rsp], rax\n\n"
            case TokenType.ISUB:
                labels_dict[current_label] += "    pop     rbx\n"
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    sub     qword [rax], rbx\n"
                labels_dict[current_label] += "    push    rax\n\n"
            case TokenType.MUL:
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    imul    qword [rsp], rax\n\n"
            case TokenType.IMUL:
                labels_dict[current_label] += "    pop     rbx\n"
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    imul    qword [rax], rbx\n"
                labels_dict[current_label] += "    push    rax\n\n"
            case TokenType.DUP:
                labels_dict[current_label] += "    push    qword [rsp]\n\n"
            case TokenType.DROP:
                labels_dict[current_label] += "    add     rsp, %d\n\n" % (tok.value * 8)
            case TokenType.SWAP:
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    xchg    qword [rsp], rax\n"
                labels_dict[current_label] += "    push    rax\n\n"
            case TokenType.CALL:
                labels_dict[current_label] += "    mov     rcx, [rsp]\n"
                labels_dict[current_label] += "    mov     rdx, [rsp + 8]\n"
                labels_dict[current_label] += "    mov     r8, [rsp + 16]\n"
                labels_dict[current_label] += "    mov     r9, [rsp + 24]\n"
                labels_dict[current_label] += "    call    %s\n" % tok.value
                labels_dict[current_label] += "    push    rax\n\n"
            case TokenType.APPLY: # dereference
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    push    qword [rax]\n\n"
            case TokenType.QUOTE: # reference
                labels_dict[current_label] += "    lea     rax, [rsp]\n"
                labels_dict[current_label] += "    push    rax\n\n"
            case TokenType.BITNOT:
                labels_dict[current_label] += "    not     qword [rsp]\n\n"
            case TokenType.BITAND:
                labels_dict[current_label] += "    pop     rax\n"
                labels_dict[current_label] += "    and     qword [rsp], rax\n\n"
            case TokenType.IF:
                labels_dict[current_label] += "    cmp     qword [rsp], %d\n" % tok.value
                labels_dict[current_label] += "    %s      .LC%d\n" % (jumps[tok.raw], labels)
                labels += 1
                nests.append(TokenType.IF)
            case TokenType.END:
                current = nests.pop()
                
                if current == TokenType.IF:
                    current_label = ".LC%d" % ((labels - len(nests)) - 1)
                    labels_dict[current_label] = ""
                
    
    labels_dict[current_label] += "    xor     rax, rax\n"
    labels_dict[current_label] += "    call    ExitProcess\n\n"
    
    res += "main:\n"
    res += labels_dict.pop("main")
    
    for label in labels_dict:
        res += "%s:\n" % label
        res += labels_dict[label]
    
    # add strings
    res += "segment .data\n"
    for index, string in enumerate(strings):
        res += "    string_%d db %s%s0\n" % (
            index,
            ",".join(map(str, list(bytes(string, "utf-8")))),
            ", " if string else ""
        )
    
    return res

def compile_ops(toks: list[Token], calls: list[str]) -> str:
    if ARCHITECTURE.lower() in ("x86_64", "x86-64", "x64", "amd64"):
        return compile_ops_x64(toks, calls)
    else:
        Croak(ErrorType.Compile, "unsupported architecture: %s\n" % ARCHITECTURE)

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
    try:
        run_program()
    except Exception as e:
        Croak(ErrorType.Compile,
              "an unexpected error occurred, please make sure your installation is not corrupted.\n",
              "Error message: %s\n" % e)
