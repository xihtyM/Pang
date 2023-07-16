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


def compile_ops(toks: list[Token]) -> str:
    """ Compiles to C++ """
    
    if len(toks) <= 0:
        Croak(ErrorType.Compile, "nothing to compile")
    
    out = ""
    indent_width = 4
    
    for tok in toks:
        if tok.typ == TokenType.STR:
            out += "%spang::push(&pstack, %s);\n" % (
                " " * indent_width, tok.raw)
        elif tok.typ == TokenType.INT:
            out += "%spang::push(&pstack, (intmax_t) %d);\n" % (
                " " * indent_width, tok.value)
        elif tok.typ == TokenType.ADD:
            out += "%spang::add(&pstack);\n" % (
                " " * indent_width)
        elif tok.typ == TokenType.SUB:
            out += "%spang::sub(&pstack);\n" % (
                " " * indent_width)
        elif tok.typ == TokenType.APPLY:
            out += "%spang::apply(&pstack);\n" % (
                " " * indent_width)
        elif tok.typ == TokenType.QUOTE:
            out += "%spang::quote(&pstack);\n" % (
                " " * indent_width)
        elif tok.typ == TokenType.BUF:
            out += "%spang::buf(&pstack);\n" % (
                " " * indent_width)

    start  = "#include \"pang.hh\"\n\n"
    start += "pang_func(std::ostream &)\n"
    start += "operator<<(std::ostream &os,\n"
    start += "        pang::Int &p_int)\n"
    start += "{\n"
    start += "    if (p_int.is_null)\n"
    start += "    {\n"
    start += "        os << \"null\";\n"
    start += "        return os;\n"
    start += "    }\n"
    start += "\n"
    start += "    if (p_int.is_ptr)\n"
    start += "    {\n"
    start += "        os << \"ptr(\" << p_int.real << \")\";\n"
    start += "        return os;\n"
    start += "    }\n"
    start += "\n"
    start += "    os << p_int.real;\n"
    start += "    return os;\n"
    start += "}\n"
    start += "\n"
    start += "int main(int argc, char *argv[])\n"
    start += "{\n"
    start += "    pang::Stack pstack;\n"
    start += "    pang::initilize_pang(&pstack);\n\n"
    
    end  = "\n    for (int index = 0; index <= pstack.mem_pointer; index++)\n"
    end += "    {\n"
    end += "        std::cout << pstack.mem[index] << ' ';\n"
    end += "    }\n"
    end += "\n"
    end += "    std::cout << '\\n';\n"
    end += "\n"
    end += "    for (auto addr: pstack.stack)\n"
    end += "    {\n"
    end += "        std::cout << pstack.mem[addr] << ' ';\n"
    end += "    }\n"
    end += "\n"
    end += "    return 0;\n"
    end += "}\n"
    
    return start + out + end

def join(l: list[int]) -> str:
    out = ""

    for ch in l:
        out += chr(ch)
    
    return out

def run_program() -> None:
    optimise = False
    filename = False
    cpp = False
    asm = False
    gdb = False
    keep_temp = False

    outname = "a"
    optimise_flag = " "
    
    for arg in sys.argv:
        if filename:
            outname = arg
            filename = None
        elif arg == "-o":
            if filename is None:
                Croak(ErrorType.Command, "cannot have two output names...")
            
            filename = True
        elif arg.startswith("-O"):
            if len(arg) != 3:
                Croak(ErrorType.Command, "invalid flag %s" % arg)
            elif not arg[2].isnumeric():
                Croak(ErrorType.Command, "invalid flag %s" % arg)
            
            optimise = True
            optimise_flag = " %s" % arg
        elif arg == "-S":
            asm = True
        elif arg in ("-C", "-cpp"):
            cpp = True
        elif arg == "-g":
            gdb = True
        elif arg == "-t":
            keep_temp = True
    
    if len(sys.argv) < 2:
        Croak(ErrorType.Command, "must input a file name")
    
    src = open(sys.argv[1], "r", encoding="utf-8").read()
    
    lex_src = Lexer(src, sys.argv[1])
    lex_src.get_tokens()

    print("You must have g++ in order to compile pang.")
    name = "temp.cc" if not cpp else outname + ".cc"

    open(name, "w", encoding="utf-8").write(compile_ops(lex_src.toks))
    command = "g++ %s -o %s -Werror -Bdynamic -lstdc++" % (name, outname)

    if gdb:
        command += " -g"
    else:
        command += " -s"

    if optimise:
        command += "%s" % optimise_flag
    if asm:
        command += " -S"
    
    if not cpp:
        os.system(command)
        if not keep_temp:
            os.remove(name)
        
    elif asm:
        os.system(command)

if __name__ == "__main__":
    run_program()
