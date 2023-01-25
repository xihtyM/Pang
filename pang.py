from time import perf_counter, sleep
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
import sys
import os

PANG_SYS = os.path.dirname(os.path.realpath(__file__)) + "\\"

NEWLINE_SYSCALLS = [
    0x005, 0x006,
    0x007, 0x008,
    0x012,
]

try:
    sys.set_int_max_str_digits(2147483647)
except AttributeError:
    # If there is no limit (in some versions of python).
    # Then this error will be raised, nothing is needed to be done.
    pass

class ErrorType(Enum):
    Name = auto()
    Stack = auto()
    Syntax = auto()
    Command = auto()
    Compile = auto()

class TokenType(Enum):
    # Identifiers
    ID = auto()

    # Bitwise operators
    EXCOR = auto()
    BITOR = auto()
    BITAND = auto()
    BITNOT = auto()
    LSHIFT = auto()
    RSHIFT = auto()

    # All ended statements
    IF = auto()
    DO = auto()
    END = auto()
    WHILE = auto()
    MACRO = auto()

    # Push to stack
    INT = auto()
    STR = auto()

    # Arithmetic
    SUB = auto()
    ADD = auto()
    MUL = auto()
    DIVMOD = auto()

    # Stack operations
    DUP = auto()
    SWAP = auto()
    BACK = auto()
    FRONT = auto()

    # Conditionals
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN = auto()
    SMALLER_THAN = auto()

    # Edit output buffer
    BUF = auto()

    # Syscalls
    SYSCALL = auto()

    # For undefined tokens
    NONE = auto()

@dataclass
class Token():
    typ: TokenType = TokenType.NONE
    raw: str = ""
    value: Union[str, int] = ""
    filename: str = ""
    ln: int = -1

T_READLINE = 0
T_READALL = -1

keyword_map = {
    # Bitwise operators
    "xor": TokenType.EXCOR,
    "bor": TokenType.BITOR,
    "band": TokenType.BITAND,
    "bnot": TokenType.BITNOT,
    "lshift": TokenType.LSHIFT,
    "rshift": TokenType.RSHIFT,

    # Normal tokens
    "if": TokenType.IF,
    "add": TokenType.ADD,
    "sub": TokenType.SUB,
    "mul": TokenType.MUL,
    "dup": TokenType.DUP,
    "buf": TokenType.BUF,
    "swap": TokenType.SWAP,
    "back": TokenType.BACK,
    "while": TokenType.WHILE,
    "front": TokenType.FRONT,
    "divmod": TokenType.DIVMOD,
    "syscall": TokenType.SYSCALL,
}

def Croak(err_typ: ErrorType, msg: str):
    print("%sError: %s" % (err_typ._name_, msg))
    exit(1)

class Lexer():
    def __init__(self, src: str, filename: str = "N/A") -> None:
        self.index = 0
        self.fn = filename
        self.raw = src
        self.size = len(src)
        self.toks: list[Token] = []
        self.includes: list[str] = []

    def line(self, l_break: int) -> int:
        return self.raw[:l_break].count("\n") + 1

    def _get(self) -> str:
        """ Returns current value and index++ """
        self.index += 1

        if self.index - 1 >= self.size:
            return ""

        return self.raw[self.index - 1]
    
    def _peek(self) -> str:
        """ Returns current value """
        if self.index >= self.size:
            return ""

        return self.raw[self.index]

    def atom(self, tok_typ: TokenType) -> None:
        self.toks.append(Token(tok_typ, self._peek(), self._get(), self.fn, self.line(self.index - 1)))

    def num(self) -> None:
        start = self.index
        raw = ""

        while self._peek() and self._peek() in "1234567890":
            raw += self._get()
        
        if raw == "0" and self._peek() in ("x", "X"):
            raw += self._get()
            while self._peek() and self._peek() in "1234567890abcdefABCDEF":
                raw += self._get()
            
            self.toks.append(Token(
                TokenType.INT, raw, int(raw, 16),
                self.fn, self.line(start)))
                
            return

        self.toks.append(Token(TokenType.INT, raw, int(raw), self.fn, self.line(start)))

    def raw_string(self) -> None:
        start = self.index
        raw = ""

        # Add 1 to index to skip \" character
        self.index += 1

        while self._peek() != "\"":
            raw += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated string literal in file \"%s\" (detected at line: %d)" % (
                        self.fn, self.line(start)
                    )
                )

        # Add 1 to index to skip \" character
        self.index += 1

        self.toks.append(Token(TokenType.STR, "\"%s\"" % raw, raw, self.fn, self.line(start)))

    def string(self) -> None:
        start = self.index
        raw = ""

        # Add 1 to index to skip \" character
        self.index += 1

        while self._peek() != "\"":
            raw += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated string literal in file \"%s\" (detected at line: %d)" % (
                        self.fn, self.line(start)
                    )
                )
            
            if self._peek() == "\"" and not raw.endswith("\\\\") and raw[-1] == "\\":
                raw += self._get()

        # Add 1 to index to skip \" character
        self.index += 1

        self.toks.append(Token(TokenType.STR, "\"%s\"" % raw, raw.encode("raw_unicode_escape").decode("unicode_escape"), self.fn, self.line(start)))

    def char(self) -> None:
        start = self.index

        # Add 1 to index to skip \' character
        self.index += 1

        raw = self._get()

        if raw == "\'":
            Croak(
                ErrorType.Syntax,
                "char must contain a value in file \"%s\" (detected at line: %d)" % (
                    self.fn, self.line(start)
                )
            )
        elif raw == "\\":
            while self._peek() != "\'":
                raw += self._peek()

                if not self._get():
                    Croak(
                        ErrorType.Syntax,
                        "unterminated char literal in file \"%s\" (detected at line: %d)" % (
                            self.fn, self.line(start)
                        )
                    )
            
            raw = raw.encode("raw_unicode_escape").decode("unicode_escape")
        
        if len(raw) != 1 or self._get() != "\'":
            Croak(
                ErrorType.Syntax,
                "char must be 1 character long, in file \"%s\" (detected at line: %d)" % (
                    self.fn, self.line(start)
                )
            )
        
        self.toks.append(Token(TokenType.INT, raw, ord(raw), self.fn, self.line(start)))

    def comment(self) -> None:
        self.index += 1

        if self._peek() == "/":
            while self._peek() != "\n":
                if not self._get():
                    break
            return
        elif self._peek() == "*":
            self.index += 1
            while self._peek():
                if self._get() + self._peek() == "*/":
                    break
            self.index += 1
            return
        
        Croak(ErrorType.Syntax, "expected // or /* */ comment")

    def include_file(self) -> None:
        while self._peek() in " \n\t":
            if not self._get():
                assert False, "Must include a file"

        systemfile = self._peek() == "\'"

        if self._get() not in "\'\"":
            Croak(
                ErrorType.Syntax,
                "must include a string or system library in file \"%s\" (detected at line: %d)" % (
                    self.fn, self.line(self.index)
                )
            )
        
        include_filename = self._get()

        while (self._peek() != "\"" and not systemfile) or (self._peek() != "\'" and systemfile):
            include_filename += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated string literal in file \"%s\" (detected at line: %d)" % (
                        self.fn, self.line(self.index)
                    )
                )
        
        # Add 1 to index to skip \" or \' character
        self.index += 1

        if systemfile:
            include_filename = PANG_SYS + include_filename

        # skip as has already been included
        if include_filename in self.includes:
            return

        new_toks = Lexer(open(include_filename, "r", encoding="utf-8").read(), include_filename)
        new_toks.includes = self.includes
        new_toks.get_tokens_without_macros()

        self.includes.append(include_filename)

        self.toks += new_toks.toks

    def identifier(self) -> None:
        start = self.index
        raw = self._get()

        if raw == "r" and self._peek() == "\"":
            self.raw_string()
            return

        while self._peek() in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            raw += self._peek()

            if not self._get():
                break
        
        if raw == "macro":
            self.toks.append(Token(TokenType.MACRO, raw, raw, self.fn, self.line(start)))
        elif raw == "end":
            self.toks.append(Token(TokenType.END, raw, raw, self.fn, self.line(start)))
        elif raw == "include":
            self.include_file()
        elif raw == "do":
            self.toks.append(Token(TokenType.DO, raw, raw, self.fn, self.line(start)))
        elif raw in keyword_map:
            self.toks.append(Token(keyword_map.get(raw), raw, raw, self.fn, self.line(start)))
        else:
            self.toks.append(Token(TokenType.ID, raw, raw, self.fn, self.line(start)))

    def get_tokens_without_macros(self) -> None:
        while self._peek():
            end = False
            while self._peek() in " \t\n":
                self.index += 1

                if not self._peek():
                    end = True
                    break
                
            if end:
                break
            
            current = self._peek()
            
            if current in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                self.identifier()
            elif current in "1234567890":
                self.num()
            elif current == "\"":
                self.string()
            elif current == "\'":
                self.char()
            elif current == "/":
                self.comment()
            elif current == "=":
                self.atom(TokenType.EQUAL)
            elif current == "!":
                self.atom(TokenType.NOT_EQUAL)
            elif current == ">":
                self.atom(TokenType.GREATER_THAN)
            elif current == "<":
                self.atom(TokenType.SMALLER_THAN)
            else:
                assert False, "Unhandled token type/raw text: %s:%d" % (current, self.index)

    def get_tokens(self) -> None:
        self.get_tokens_without_macros()

        macro_added_toks = []
        macro = False
        macro_name = False
        skip_end = 0
        cur_name = ""
        cur_tok = Token()
        cur_toks = []
        macros = {}

        # Add macros
        for tok in self.toks:
            if tok.typ == TokenType.DO:
                skip_end += 1
            
            if tok.typ == TokenType.MACRO:
                if macro:
                    Croak(
                        ErrorType.Syntax,
                        "macro cannot define a macro in itself, found in file \"%s\" (at line %d)" % (
                            tok.filename, tok.ln
                        )
                    )

                macro_name = True
                continue
            
            if macro_name:
                if tok.typ != TokenType.ID:
                    Croak(
                        ErrorType.Syntax,
                        "macro name must be an identifier, found in file \"%s\" (at line %d)" % (
                            tok.filename, tok.ln
                        )
                    )
                
                cur_tok = tok
                cur_name = cur_tok.value
                macro_name = False
                macro = True
                continue

            if macro:
                if tok.typ == TokenType.END and not skip_end:
                    macro = False

                    if cur_name in macros:
                        Croak(
                            ErrorType.Name, "redefinition of macro %s in file \"%s\" (detected at line: %d)" % (
                                cur_name, cur_tok.filename, cur_tok.ln
                            )
                        )

                    macros[cur_name] = cur_toks
                    cur_toks = []
                    continue
                
                if tok.typ == TokenType.END and skip_end:
                    skip_end -= 1
                
                if tok.typ != TokenType.ID:
                    cur_toks.append(tok)
                else:
                    # print(tok.raw) # open(self.includes[0], "r", encoding="utf-8").read().count("\n", 0, tok.ind))
                    if tok.value not in macros:
                        Croak(
                            ErrorType.Name,
                            "undefined reference to identifier %s in file \"%s\" (detected at line: %d)" % (
                                tok.raw, tok.filename, tok.ln
                            )
                        )
                    
                    for macro_tok in macros[tok.value]:#[0]:
                        cur_toks.append(macro_tok)
        
        skip_macro = False
        skip_end = 0

        for tok in self.toks:
            if skip_macro:
                if tok.typ == TokenType.DO:
                    skip_end += 1
                elif tok.typ == TokenType.END and not skip_end:
                    skip_macro = False
                elif tok.typ == TokenType.END and skip_end:
                    skip_end -= 1
                
                continue
                
            if tok.typ == TokenType.ID:
                if not tok.value in macros:
                    Croak(
                        ErrorType.Name,
                        "undefined reference to identifier %s in file \"%s\" (detected at line: %d)" % (
                            tok.raw, tok.filename, tok.ln
                        )
                    )

                for macro_tok in macros[tok.value]:
                    macro_tok.ln = tok.ln
                    macro_tok.filename = tok.filename

                    macro_added_toks.append(macro_tok)
            elif tok.typ == TokenType.MACRO:
                # skip macros as they have already been added
                skip_macro = True
            else:
                macro_added_toks.append(tok)
        
        self.toks = macro_added_toks

class Syscall(Enum):
    # Process control
    FORK = auto() # Unimplemented
    EXIT = auto()
    EXEC = auto() # Unimplemented
    KILL = auto() # Unimplemented

    # File management
    OPEN = auto()
    READ = auto()
    WRITE = auto()
    CLOSE = auto()

    # Device management
    IOCTL = auto() # Unimplemented

    # Information maintenance
    GETPID = auto() # Unimplemented
    ALARM = auto() # Unimplemented
    SLEEP = auto()
    #TIME = auto()

    # Communication
    PIPE = auto() # Unimplemented
    SHMGET = auto() # Unimplemented
    MMAP = auto() # Unimplemented

    # Stack operations
    RESIZE = auto()
    POINTER = auto()
    LENGTH = auto()

def find_end(ind: int, ops: list[Token]) -> int:
    skip_end = 0
    end = ind
    size = len(ops) - 1

    while end < size:
        end += 1

        if ops[end].typ == TokenType.DO:
            skip_end += 1
        
        if ops[end].typ == TokenType.END:
            if not skip_end:
                return end

            skip_end -= 1
    
    Croak(ErrorType.Syntax, "expected end (at line %d)" % (ops[ind].ln))

def get_syscall(num: int, last: str = "pop(&vars.mem)") -> str:
    syscalls = {
        0x002: "exit(%s);\n" % last,
        0x005: "PANG_OPEN(&vars);\n",
        0x006: "PANG_READ(&vars);\n",
        0x007: "PANG_WRITE(&vars);\n",
        0x008: "PANG_CLOSE(&vars);\n",
        0x00C: "std::this_thread::sleep_for(std::chrono::milliseconds(%s));\n" % last,
        0x010: "if (vars.mem.back() > 0) { vars.mem.resize(((int64_t) vars.mem.size()) - pop(&vars.mem)); } else { vars.mem.resize(-pop(&vars.mem)); }\n",
        0x011: "if (vars.mem.back() < 0) { vars.mem.back() += vars.mem.size() - 1; } vars.mem.push_back(vars.mem[%s]);\n" % last,
        0x012: "vars.mem.push_back(vars.mem.size());\n"
    }

    if last != "pop(&vars.mem)":
        last = int(last)
    
    if num in (0x010, 0x011) and type(last) == int:
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

def compile_ops(toks: list, optimise: bool) -> str:
    """ Compiles to C++ """
    
    if len(toks) <= 0:
        Croak(ErrorType.Compile, "nothing to compile")


    out = ""

    indent_width = 4
    prev_int = []
    prev = Token()
    direct_syscall = False
    direct_buf = False
    direct_divmod = False
    direct_sleep = False
    direct_open = False
    direct_read = False
    direct_write = False
    direct_close = False

    for tok in toks:
        drop_prev_int = True

        if tok.typ == TokenType.STR:
            if prev.typ == TokenType.STR:
                out = remove_newline(out)
                tok.value = prev.value + tok.value

            chars = [ord(ch) for ch in tok.value]
            
            out += "%svars.mem.insert(vars.mem.end(), {%s, %d});\n" % (
                " " * indent_width,
                ", ".join([str(ch) for ch in chars]),
                len(tok.value)
            )
                
            if optimise:
                prev_int += chars + [len(tok.value)]
                drop_prev_int = False
        elif tok.typ == TokenType.INT:
            out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, tok.value)

            if optimise:
                prev_int.append(tok.value)
                drop_prev_int = False
        elif tok.typ == TokenType.BUF:
            if prev_int:
                out = remove_newline(out)

                if len(prev_int) >= 2:
                    out = remove_newline(out)
                    
                    if prev_int[-1] == 1:
                        out += "%svars.buf += %d;\n" % (" " * indent_width, prev_int.pop(-2))
                    elif prev_int[-1] == 0:
                        out += "%svars.buf += \"%d\";\n" % (" " * indent_width, prev_int.pop(-2))
                    else:
                        Croak(ErrorType.Stack, "%d is not a valid number for the buf keyword (1 or 0)...")

                elif prev_int[-1] == 0:
                    out += "%svars.buf += std::to_string(vars.mem.back());\n" % (" " * indent_width)
                elif prev_int[-1] == 1:
                    out += "%svars.buf += vars.mem.back();\n" % (" " * indent_width)
                else:
                    Croak(ErrorType.Stack, "%d is not a valid number for the buf keyword (1 or 0)...")

                prev_int.pop()
                drop_prev_int = False
            else:
                direct_buf = True
                out += "%sPANG_BUF(&vars);\n" % (" " * indent_width)
        elif tok.typ == TokenType.DUP:
            if prev_int:
                out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, prev_int[-1])
                prev_int.append(prev_int[-1])
                drop_prev_int = False
            else:
                out += "%sPANG_DUP;\n" % (" " * indent_width)
        elif tok.typ == TokenType.BACK:
            out += "%sPANG_BACK;\n" % (" " * indent_width)
        elif tok.typ == TokenType.FRONT:
            out += "%sPANG_FRONT;\n" % (" " * indent_width)
        elif tok.typ == TokenType.SWAP:
            if prev.typ == TokenType.SWAP:
                out = remove_newline(out)
            elif len(prev_int) >= 2:
                # Remove two newlines
                out = remove_newline(out)
                out = remove_newline(out)

                out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, prev_int[-1])
                out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, prev_int[-2])

                prev_int[-1], prev_int[-2] = prev_int[-2], prev_int[-1]

                drop_prev_int = False
            else:
                out += "%sPANG_SWAP;\n" % (" " * indent_width)
        
        elif tok.typ == TokenType.ADD:
            if prev_int:
                out = remove_newline(out)

                if len(prev_int) == 1:
                    out += "%svars.mem.back() += %d;\n" % (" " * indent_width, prev_int[-1])
                    prev_int = []
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, prev_int[-2] + prev_int[-1])
                    
                    if len(prev_int) <= 2:
                        prev_int = [prev_int[-2] + prev_int[-1]]
                    else:
                        prev_int = prev_int[:-2] + [prev_int[-2] + prev_int[-1]]

                drop_prev_int = False
            else:
                if prev.typ == TokenType.SWAP:
                    out = remove_newline(out)
                out += "%sPANG_ADD;\n" % (" " * indent_width)
        elif tok.typ == TokenType.SUB:
            if prev_int:
                out = remove_newline(out)
                
                if len(prev_int) == 1:
                    out += "%svars.mem.back() -= %d;\n" % (" " * indent_width, prev_int[-1])
                    prev_int = []
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, prev_int[-2] - prev_int[-1])

                    if len(prev_int) <= 2:
                        prev_int = [prev_int[-2] - prev_int[-1]]
                    else:
                        prev_int = prev_int[:-2] + [prev_int[-2] - prev_int[-1]]
                drop_prev_int = False
            else:
                out += "%sPANG_SUB;\n" % (" " * indent_width)
        elif tok.typ == TokenType.MUL:
            if prev_int:
                cut = out[-out[::-1].find("\n"):]
                out = remove_newline(out)

                if len(prev_int) == 1:
                    binary = bin(prev_int[-1])[2:][::-1]
                    if prev_int[-1] == 1:
                        out += cut
                    elif binary.count("1") == 1:
                        out += "%svars.mem.back() <<= %d;\n" % (" " * indent_width, binary.find("1"))
                    else:
                        out += "%svars.mem.back() *= %d;\n" % (" " * indent_width, prev_int[-1])
                    
                    prev_int = []
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, prev_int[-2] * prev_int[-1])

                    if len(prev_int) <= 2:
                        prev_int = [prev_int[-2] * prev_int[-1]]
                    else:
                        prev_int = prev_int[:-2] + [prev_int[-2] * prev_int[-1]]
                
                drop_prev_int = False
            else:
                out += "%sPANG_MUL;\n" % (" " * indent_width)
        elif tok.typ == TokenType.DIVMOD:
            direct_divmod = True

            out += "%sPANG_DIVMOD(&vars.mem);\n" % (" " * indent_width)
        elif tok.typ == TokenType.GREATER_THAN:
            if prev_int:
                out = remove_newline(out)

                if len(prev_int) == 1:
                    out += "%sPUSH_INTEGER(pop(&vars.mem) < %d);\n" % (" " * indent_width, prev_int.pop())
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, (prev_int[-2] < prev_int[-1]))
                    prev_int[-1] = prev_int.pop(-2) < prev_int[-1]
                
                drop_prev_int = False
            elif prev.typ == TokenType.SWAP:
                out = remove_newline(out)
                out += "%sPANG_ST;\n" % (" " * indent_width)
            else:
                out += "%sPANG_GT;\n" % (" " * indent_width)
        elif tok.typ == TokenType.SMALLER_THAN:
            if prev_int:
                out = remove_newline(out)

                if len(prev_int) == 1:
                    out += "%sPUSH_INTEGER(pop(&vars.mem) > %d);\n" % (" " * indent_width, prev_int.pop())
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, (prev_int[-2] > prev_int[-1]))
                    prev_int[-1] = prev_int.pop(-2) > prev_int[-1]
                
                drop_prev_int = False
            elif prev.typ == TokenType.SWAP:
                out = remove_newline(out)
                out += "%sPANG_GT;\n" % (" " * indent_width)
            else:
                out += "%sPANG_ST;\n" % (" " * indent_width)
        elif tok.typ == TokenType.EQUAL:
            if prev.typ == TokenType.SWAP:
                out = remove_newline(out)
            
            if prev_int:
                out = remove_newline(out)

                if len(prev_int) == 1:
                    out += "%sPUSH_INTEGER(pop(&vars.mem) == %d);\n" % (" " * indent_width, prev_int.pop())
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, (prev_int[-2] == prev_int[-1]))
                    prev_int[-1] = prev_int.pop(-2) == prev_int[-1]
            
                drop_prev_int = False
            else:
                out += "%sPANG_EQU;\n" % (" " * indent_width)
        elif tok.typ == TokenType.NOT_EQUAL:
            if prev.typ == TokenType.SWAP:
                out = remove_newline(out)
            
            if prev_int:
                out = remove_newline(out)

                if len(prev_int) == 1:
                    out += "%sPUSH_INTEGER(pop(&vars.mem) != %d);\n" % (" " * indent_width, prev_int.pop())
                else:
                    out = remove_newline(out)
                    out += "%sPUSH_INTEGER(%d);\n" % (" " * indent_width, (prev_int[-2] != prev_int[-1]))
                    prev_int[-1] = prev_int.pop(-2) != prev_int[-1]
                
                drop_prev_int = False
            else:
                out += "%sPANG_NEQU;\n" % (" " * indent_width)

        elif tok.typ == TokenType.WHILE:
            out += "\n%swhile (pop(&vars.mem)) {\n" % (" " * indent_width)
            indent_width += 4
        elif tok.typ == TokenType.IF:
            out += "\n%sif (pop(&vars.mem)) {\n" % (" " * indent_width)
            indent_width += 4
        
        elif tok.typ == TokenType.END:
            indent_width -= 4
            out += "%s}\n\n" % (" " * indent_width)

        elif tok.typ == TokenType.SYSCALL:
            if len(prev_int) >= 2 and prev_int[-1] not in NEWLINE_SYSCALLS:
                if prev_int[-1] == Syscall.SLEEP.value:
                    direct_sleep = True
                    
                out = remove_newline(out)
                out = remove_newline(out)

                out += "%s%s" % ((" " * indent_width, get_syscall(prev_int.pop(), str(prev_int.pop()))))
            elif prev_int:
                if prev_int[-1] == Syscall.SLEEP.value:
                    direct_sleep = True
                elif prev_int[-1] == Syscall.OPEN.value:
                    direct_open = True
                elif prev_int[-1] == Syscall.READ.value:
                    direct_read = True
                elif prev_int[-1] == Syscall.WRITE.value:
                    direct_write = True
                elif prev_int[-1] == Syscall.CLOSE.value:
                    direct_close = True
                    
                out = remove_newline(out)

                out += "%s%s" % (" " * indent_width, get_syscall(prev_int.pop()))
            else:
                direct_syscall = True
                out += "%sPANG_SYSCALL(&vars);\n" % (" " * indent_width)
        
        if drop_prev_int:
            prev_int = []

        prev = tok
    
    start =  "#include <iostream>\n"
    start += "#include <fstream>\n"
    start += "#include <vector>\n"
    start += "#include <string>\n"
    start += "\n"
    
    if direct_syscall or direct_sleep or not optimise:
        start += "#include <chrono>\n"
        start += "#include <thread>\n"
        start += "\n"
        
    start += "#if defined(WIN32) || defined(_WIN32) || defined(__WIN32) && !defined(__CYGWIN__)\n"
    start += "#define ON_WINDOWS\n"
    start += "#include <locale.h>\n"
    start += "#endif\n"
    start += "\n"
    start += "using std::fstream;\n"
    start += "\n"
    start += "typedef struct Variables {\n"
    start += "    int64_t exit_code;\n"
    start += "    std::string buf;\n"
    start += "    std::vector<int64_t> mem;\n"
    start += "    std::vector<fstream> open_files;\n"
    start += "} Variables;\n"
    start += "\n"
    start += "#define SYSCALL_FORK 1\n"
    start += "#define SYSCALL_EXIT 2\n"
    start += "#define SYSCALL_EXEC 3\n"
    start += "#define SYSCALL_KILL 4\n"
    start += "\n"
    start += "#define SYSCALL_OPEN 5\n"
    start += "#define SYSCALL_READ 6\n"
    start += "#define SYSCALL_WRITE 7\n"
    start += "#define SYSCALL_CLOSE 8\n"
    start += "\n"
    start += "#define SYSCALL_IOCTL 9\n"
    start += "\n"
    start += "#define SYSCALL_GETPID 10\n"
    start += "#define SYSCALL_ALARM 11\n"
    start += "#define SYSCALL_SLEEP 12\n"
    start += "\n"
    start += "#define SYSCALL_PIPE 13\n"
    start += "#define SYSCALL_SHMGET 14\n"
    start += "#define SYSCALL_MMAP 15\n"
    start += "\n"
    start += "#define SYSCALL_RESIZE 16\n"
    start += "#define SYSCALL_POINTER 17\n"
    start += "#define SYSCALL_LENGTH 18\n"
    start += "\n"
    start += "#define READALL -1\n"
    start += "#define READLINE 0\n"
    start += "\n"
    start += "template<typename T> T pop(std::vector<T> *stack, int64_t index = -1) {\n"
    start += "    T value;\n"
    start += "    if ((int64_t) stack->size() < index) {\n"
    start += "        std::cerr << \"StackError: Cannot pop from stack.\\n\";\n"
    start += "        exit(1);\n"
    start += "    }\n"
    start += "\n"
    start += "    if (index >= 0) {\n"
    start += "        value = stack->at(index);\n"
    start += "        stack->erase(stack->begin() + index);\n"
    start += "    } else {\n"
    start += "        value = stack->at(stack->size() + index);\n"
    start += "        stack->erase(stack->end() + index);\n"
    start += "    }\n"
    start += "\n"
    start += "    return value;\n"
    start += "}\n"
    start += "\n"
    
    if direct_divmod or not optimise:
        start += "template<typename T> void PANG_DIVMOD(std::vector<T> *stack) {\n"
        start += "    T denominator = pop(stack);\n"
        start += "    T numerator = pop(stack);\n"
        start += "\n"
        start += "    std::lldiv_t result = std::lldiv(numerator, denominator);\n"
        start += "\n"
        start += "    stack->push_back(result.quot);\n"
        start += "    stack->push_back(result.rem);\n"
        start += "}\n"
        start += "\n"

    if direct_open or direct_syscall or not optimise:
        start += "std::ios_base::openmode flags_to_mode(std::string flags) {\n"
        start += "    if (flags == \"r\") {\n"
        start += "        return std::ios::in;\n"
        start += "    } else if (flags == \"w\") {\n"
        start += "        return std::ios::out | std::ios::trunc;\n"
        start += "    } else if (flags == \"a\") {\n"
        start += "        return std::ios::out | std::ios::app;\n"
        start += "    } else if (flags == \"r+\") {\n"
        start += "        return std::ios::out | std::ios::in;\n"
        start += "    } else if (flags == \"w+\") {\n"
        start += "        return std::ios::out | std::ios::in | std::ios::trunc;\n"
        start += "    } else if (flags == \"a+\") {\n"
        start += "        return std::ios::out | std::ios::in | std::ios::app;\n"
        start += "    } else {\n"
        start += "        std::cerr << \"FlagError: Invalid flag for open \\\"\"\n"
        start += "                  << flags\n"
        start += "                  << \"\\\".\\n\";\n"
        start += "        exit(1);\n"
        start += "    }\n"
        start += "}\n"
        start += "\n"

    if direct_open or direct_syscall or not optimise:
        start += "void PANG_OPEN(Variables *vars) {\n"
        start += "    int64_t length = pop(&vars->mem);\n"
        start += "    std::string flags(vars->mem.end() - length, vars->mem.end());\n"
        start += "    vars->mem.resize(vars->mem.size() - length);\n"
        start += "\n"
        start += "    length = pop(&vars->mem);\n"
        start += "    std::string filename(vars->mem.end() - length, vars->mem.end());\n"
        start += "    vars->mem.resize(vars->mem.size() - length);\n"
        start += "\n"
        start += "    vars->mem.push_back(vars->open_files.size() + 3);\n"
        start += "\n"
        start += "    auto mode = flags_to_mode(flags);\n"
        start += "\n"
        start += "    vars->open_files\n"
        start += "        .push_back(fstream(filename, mode));\n"
        start += "}\n"
        start += "\n"

    if direct_read or direct_syscall or not optimise:
        start += "void PANG_READ(Variables *vars) {\n"
        start += "    int64_t fd = pop(&vars->mem) - 3;\n"
        start += "    int64_t read_typ = pop(&vars->mem);\n"
        start += "\n"
        start += "    if (fd >= (int64_t) vars->open_files.size()) {\n"
        start += "        std::cerr << \"FileError: Invalid file descriptor - \" << fd << \'\\n\';\n"
        start += "        exit(1);\n"
        start += "    }\n"
        start += "\n"
        start += "    if (fd != -3 && fd < 0) {\n"
        start += "        std::cerr << \"FileError: Invalid file descriptor. - \" << fd << \'\\n\';\n"
        start += "        exit(1);\n"
        start += "    } else if (fd == -3) {\n"
        start += "        std::string contents = \"\";\n"
        start += "\n"
        start += "        if (read_typ == READLINE) {\n"
        start += "            std::getline(std::cin, contents);\n"
        start += "        } else {\n"
        start += "            while (true) {\n"
        start += "                char *buf = new char[1];\n"
        start += "                std::cin.read(buf, 1);\n"
        start += "\n"
        start += "                delete[] buf;\n"
        start += "            }\n"
        start += "        }\n"
        start += "\n"
        start += "        for (auto ch: contents) {\n"
        start += "            vars->mem.push_back(ch);\n"
        start += "        }\n"
        start += "\n"
        start += "        vars->mem.push_back(contents.length());\n"
        start += "\n"
        start += "        return;\n"
        start += "    }\n"
        start += "\n"
        start += "    fstream *file_ptr = &vars->open_files[fd];\n"
        start += "\n"
        start += "    if (!(*file_ptr)) {\n"
        start += "        std::cerr << \"FileError: Invalid file descriptor - \" << fd << \'\\n\';\n"
        start += "        exit(1);\n"
        start += "    }\n"
        start += "\n"
        start += "    std::string contents = \"\";\n"
        start += "\n"
        start += "    if (read_typ == READLINE) {\n"
        start += "        std::getline(*file_ptr, contents);\n"
        start += "    } else {\n"
        start += "        file_ptr->seekg(0, file_ptr->end);\n"
        start += "        size_t length = file_ptr->tellg();\n"
        start += "        file_ptr->seekg(0, file_ptr->beg);\n"
        start += "\n"
        start += "        if (read_typ < length && read_typ != READALL) {\n"
        start += "            length = read_typ;\n"
        start += "        }\n"
        start += "\n"
        start += "        if (!length) {\n"
        start += "            vars->mem.push_back(0);\n"
        start += "            return;\n"
        start += "        }\n"
        start += "\n"
        start += "        char *buf = new char[length];\n"
        start += "\n"
        start += "        file_ptr->read(buf, length);\n"
        start += "\n"
        start += "        if (!(*file_ptr)) {\n"
        start += "            std::cerr << \"FileError: could not read from file.\\n\";\n"
        start += "            exit(1);\n"
        start += "        }\n"
        start += "\n"
        start += "        contents.assign(buf, length);\n"
        start += "\n"
        start += "        delete[] buf;\n"
        start += "    }\n"
        start += "\n"
        start += "    for (auto ch: contents) {\n"
        start += "        vars->mem.push_back(ch);\n"
        start += "    }\n"
        start += "\n"
        start += "    vars->mem.push_back(contents.length());\n"
        start += "}\n"
        start += "\n"

    if direct_write or direct_syscall or not optimise:
        start += "void PANG_WRITE(Variables *vars) {\n"
        start += "    int64_t fd = pop(&vars->mem) - 3;\n"
        start += "\n"
        start += "    if (fd >= 0) {\n"
        start += "        vars->open_files[fd] << vars->buf;\n"
        start += "        vars->open_files[fd].flush();\n"
        start += "        vars->buf = \"\";\n"
        start += "\n"
        start += "        return;\n"
        start += "    }\n"
        start += "\n"
        start += "    switch (fd) {\n"
        start += "        case -2: { std::cout << vars->buf; break; }\n"
        start += "        case -1: { std::cerr << vars->buf; break; }\n"
        start += "\n"
        start += "        default: {\n"
        start += "            std::cerr << \"FileError: Invalid file descriptor.\\n\";\n"
        start += "            exit(1);\n"
        start += "        }\n"
        start += "    }\n"
        start += "\n"
        start += "    vars->buf = \"\";\n"
        start += "}\n"
        start += "\n"

    if direct_close or direct_syscall or not optimise:
        start += "void PANG_CLOSE(Variables *vars) {\n"
        start += "    int64_t fd = pop(&vars->mem) - 3;\n"
        start += "\n"
        start += "    if (fd >= 0) {\n"
        start += "        vars->open_files[fd].close();\n"
        start += "        return;\n"
        start += "    }\n"
        start += "\n"
        start += "    switch (fd) {\n"
        start += "        case -3: { fclose(stdin); break; }\n"
        start += "        case -2: { fclose(stdout); break; }\n"
        start += "        case -1: { fclose(stderr); break; }\n"
        start += "\n"
        start += "        default: {\n"
        start += "            std::cerr << \"FileError: Invalid file descriptor.\\n\";\n"
        start += "            exit(1);\n"
        start += "        }\n"
        start += "    }\n"
        start += "}\n"
        start += "\n"

    if direct_buf or not optimise:
        start += "#define PANG_BUF \\\n"
        start += "    switch (pop(&vars.mem)) { \\\n"
        start += "        case 0: { vars.buf += std::to_string(vars.mem.back()); break; } \\\n"
        start += "        case 1: { vars.buf += vars.mem.back(); break; } \\\n"
        start += "    \\\n"
        start += "        default: { \\\n"
        start += "            std::cerr << \"BufferError: Invalid buf type.\\n\"; \\\n"
        start += "            exit(1); \\\n"
        start += "        } \\\n"
        start += "    } \n"
    
    if direct_syscall or not optimise:
        start += "void PANG_SYSCALL(Variables *vars) {\n"
        start += "    int64_t syscall_num = pop(&vars->mem);\n"
        start += "\n"
        start += "    switch (syscall_num) {\n"
        start += "        case SYSCALL_EXIT: {\n"
        start += "            exit(pop(&vars->mem));\n"
        start += "        }\n"
        start += "\n"
        start += "        case SYSCALL_OPEN: { PANG_OPEN(vars); break; }\n"
        start += "        case SYSCALL_READ: { PANG_READ(vars); break; }\n"
        start += "        case SYSCALL_WRITE: { PANG_WRITE(vars); break; }\n"
        start += "        case SYSCALL_CLOSE: { PANG_CLOSE(vars); break; }\n"
        start += "\n"
        start += "        case SYSCALL_SLEEP: {\n"
        start += "            std::this_thread::sleep_for(std::chrono::milliseconds(pop(&vars->mem)));\n"
        start += "            break;\n"
        start += "        }\n"
        start += "\n"
        start += "        case SYSCALL_RESIZE: {\n"
        start += "            if (vars->mem.back() > 0) {\n"
        start += "                vars->mem.resize(((int64_t) vars->mem.size()) - pop(&vars->mem));\n"
        start += "            } else {\n"
        start += "                vars->mem.resize(-pop(&vars->mem));\n"
        start += "            }\n"
        start += "            break;\n"
        start += "        }\n"
        start += "\n"
        start += "        case SYSCALL_POINTER: {\n"
        start += "            if (vars->mem.back() < 0) {\n"
        start += "                vars->mem.push_back(pop(&vars->mem) + vars->mem.size());\n"
        start += "            }\n"
        start += "\n"
        start += "            vars->mem.push_back(vars->mem[pop(&vars->mem)]);\n"
        start += "            break;\n"
        start += "        }\n"
        start += "        case SYSCALL_LENGTH: { vars->mem.push_back(vars->mem.size()); break; }\n"
        start += "    }\n"
        start += "}\n"
        start += "\n"
    
    start += "#define PUSH_INTEGER(x) vars.mem.push_back(x)\n"
    start += "#define PANG_DUP   vars.mem.push_back(vars.mem.back())\n"
    start += "\n"
    start += "#define PANG_BACK  vars.mem.insert(vars.mem.begin(), pop(&vars.mem))\n"
    start += "#define PANG_FRONT vars.mem.push_back(pop(&vars.mem, 0))\n"
    start += "#define PANG_SWAP  vars.mem.push_back(pop(&vars.mem, -2))\n"
    start += "\n"
    start += "#define PANG_ADD vars.mem.push_back(pop(&vars.mem, -2) + pop(&vars.mem))\n"
    start += "#define PANG_SUB vars.mem.push_back(pop(&vars.mem, -2) - pop(&vars.mem))\n"
    start += "#define PANG_MUL vars.mem.push_back(pop(&vars.mem, -2) * pop(&vars.mem))\n"
    start += "\n"
    start += "#define PANG_GT vars.mem.push_back(pop(&vars.mem, -2) < pop(&vars.mem))\n"
    start += "#define PANG_ST vars.mem.push_back(pop(&vars.mem, -2) > pop(&vars.mem))\n"
    start += "#define PANG_EQU vars.mem.push_back(pop(&vars.mem, -2) == pop(&vars.mem))\n"
    start += "#define PANG_NEQU vars.mem.push_back(pop(&vars.mem, -2) != pop(&vars.mem))\n"
    start += "\n"
    start += "int main(int argc, char *argv[]) {\n"
    start += "    #ifdef ON_WINDOWS\n"
    start += "    setlocale(LC_ALL, \".utf-8\");\n"
    start += "    #endif\n"
    start += "\n"
    start += "    Variables vars;\n"
    start += "\n"
    start += "    vars.exit_code = -1;\n"
    start += "    vars.buf = \"\";\n"
    start += "\n"
    start += "    std::vector<std::string> args(argv, argv + argc);\n"
    start += "\n"
    start += "    for (auto arg: args) {\n"
    start += "        std::copy(arg.begin(), arg.end(), std::back_inserter(vars.mem));\n"
    start += "        vars.mem.push_back(arg.length());\n"
    start += "    }\n"
    start += "    vars.mem.push_back(argc);\n\n"
    
    return start + out + "}"

def join(l: list[int]) -> str:
    out = ""

    for ch in l:
        out += chr(ch)
    
    return out

class Interpreter():
    """ Experimental class for interpreting pang """

    def loop(self) -> None:
        if not self.mem:
            self.ind = find_end(self.ind, self.ops)
            return
        
        if not self.mem[-1]:
            self.mem.pop()

            self.ind = find_end(self.ind, self.ops)
            return
        
        start_index = self.ind
        end_index = find_end(self.ind, self.ops)
        
        while self.mem:
            if not self.mem.pop():
                break

            while self.ind < end_index:
                self.inc()
                self.simulate_tok()
            
            self.ind = start_index
        
        self.ind = end_index

    def push(self) -> None:
        to_push = self.cur
        value = to_push.value

        if to_push.typ == TokenType.INT:
            self.mem.append(value)
        else:
            for ch in value:
                self.mem.append(ord(ch))
            
            self.mem.append(len(value))
    
    #def pointer(self, address: pangint) -> None:
    #    address.ptr = True

    def syscall(self) -> None:
        syscall_number = Syscall(self.mem.pop())

        if syscall_number == Syscall.EXIT:
            self.exit_code = self.mem.pop()
        elif syscall_number == Syscall.OPEN:
            self.syscall_open()
        elif syscall_number == Syscall.WRITE:
            self.syscall_write()
        elif syscall_number == Syscall.READ:
            self.syscall_read()
        elif syscall_number == Syscall.CLOSE:
            self.open_files[self.mem.pop()].close()
        elif syscall_number == Syscall.SLEEP:
            sleep(self.mem.pop() / 1000)
        elif syscall_number == Syscall.RESIZE:
            self.mem = self.mem[:-self.mem.pop()]
        elif syscall_number == Syscall.POINTER:
            self.mem.append(self.mem[self.mem.pop()])
        elif syscall_number == Syscall.LENGTH:
            self.mem.append(len(self.mem))

    def syscall_chdir(self) -> None:
        length = self.mem.pop()
        os.chdir(join(self.mem[-length:]))
        self.mem = self.mem[:-length]

    def syscall_open(self) -> None:
        length = self.mem.pop()
        mode = join(self.mem[-length:])
        self.mem = self.mem[:-length]

        length = self.mem.pop()
        filename = join(self.mem[-length:])
        self.mem = self.mem[:-length]

        self.mem.append(len(self.open_files))
        self.open_files.append(open(filename, mode, encoding="utf-8"))
    
    def syscall_read(self) -> None:
        fd = self.mem.pop()
        
        contents = self.open_files[
            fd].read()
        
        self.mem += [ord(ch) for ch in contents]
        self.mem.append(len(contents))
    
    def syscall_write(self) -> None:        
        file = self.open_files[self.mem.pop()]
        
        file.write(self.o_buf)
        file.flush()
        
        self.o_buf = ""

    def buf(self) -> None:
        to_put = self.mem.pop()

        if not to_put:
            self.o_buf += str(self.mem[-1])
        else:
            self.o_buf += chr(self.mem[-1])
        
        
    def inc(self) -> None:
        self.cur = self.ops[self.ind]
        self.ind += 1

        #print([chr(s) for s in self.mem if 0x110000 >= s >= 0])
        #print(self.cur.typ._name_, [chr(s) for s in self.mem if 0x110000 >= s >= 0])

    def condition(self) -> None:
        if self.mem.pop():
            return
        
        self.ind = find_end(self.ind, self.ops)
        self.cur = self.ops[self.ind]
    
    def simulate_tok(self) -> None:
        tok = self.cur

        if tok.typ in (TokenType.INT, TokenType.STR):
            self.push()
        
        # Branches
        elif tok.typ == TokenType.IF:
            self.condition()
        elif tok.typ == TokenType.WHILE:
            self.loop()
        
        # Syscalls
        elif tok.typ == TokenType.SYSCALL:
            self.syscall()
        
        elif tok.typ == TokenType.DUP:            
            self.mem.append(self.mem[-1])
        elif tok.typ == TokenType.BITNOT:
            self.mem[-1] = int(bin(self.mem[-1])[2:].replace("1", " ").replace("0", "1").replace(" ", "0"), 2)
        
        elif tok.typ in (TokenType.DO, TokenType.END):
            pass
        # Need at least 2 items on stack
        else:
            self.simple()
    
    def simple(self) -> None:
        tok = self.cur

        if len(self.mem) < 2:
            Croak(
                ErrorType.Stack,
                "not enough items on stack for stack operation %s (detected at line: %d)" % (
                tok.typ._name_, tok.ln))

        if tok.typ == TokenType.BUF:
            self.buf()
        elif tok.typ == TokenType.SWAP:                
            self.mem[-2], self.mem[-1] = self.mem[-1], self.mem[-2]
        elif tok.typ == TokenType.BACK:
            self.mem.insert(0, self.mem.pop(-1))
        elif tok.typ == TokenType.FRONT:
            self.mem.append(self.mem.pop(0))
        
        # Arithmetic operations
        elif tok.typ == TokenType.SUB:
            self.mem.append(self.mem.pop(-2) - self.mem.pop())
        elif tok.typ == TokenType.ADD:
            self.mem.append(self.mem.pop(-2) + self.mem.pop())
        elif tok.typ == TokenType.MUL:
            self.mem.append(self.mem.pop(-2) * self.mem.pop())
        elif tok.typ == TokenType.DIVMOD:
            self.mem += divmod(self.mem.pop(-2), self.mem.pop())
        
        # Conditionals
        elif tok.typ == TokenType.EQUAL:
            self.mem.append(int(self.mem.pop(-2) == self.mem.pop()))
        elif tok.typ == TokenType.NOT_EQUAL:
            self.mem.append(int(self.mem.pop(-2) != self.mem.pop()))
        elif tok.typ == TokenType.GREATER_THAN:
            self.mem.append(int(self.mem.pop(-2) < self.mem.pop()))
        elif tok.typ == TokenType.SMALLER_THAN:
            self.mem.append(int(self.mem.pop(-2) > self.mem.pop()))
        
        # Bitwise operations
        elif tok.typ == TokenType.BITAND:
            self.mem[-1] &= self.mem.pop(-2)
        elif tok.typ == TokenType.BITOR:
            self.mem[-1] |= self.mem.pop(-2)
        elif tok.typ == TokenType.EXCOR:
            self.mem[-1] ^= self.mem.pop(-2)
        elif tok.typ == TokenType.LSHIFT:
            self.mem.append(self.mem.pop(-2) << self.mem.pop())
        elif tok.typ == TokenType.RSHIFT:
            self.mem.append(self.mem.pop(-2) >> self.mem.pop())

    def run(self) -> None:
        while self.ind < self.size:
            self.inc()
            self.simulate_tok()

            if self.exit_code is not None:
                break

        if self.exit_code is None:
            self.exit_code = -1
    
    def cleanup(self):
        self.ind = 0
        self.o_buf = ""
        self.mem = []

    def __init__(self, args: list[str], ops: list[Token]):
        self.mem = []

        for arg in args:
            for ch in arg:
                self.mem.append(ord(ch))
            
            self.mem.append(len(arg))
                
        self.mem.append(len(args))

        self.ind = 0
        self.exit_code = None
        self.ops = ops
        self.size = len(ops)
        self.o_buf = ""

        self.open_files = [sys.stdin, sys.stdout, sys.stderr]

def run_program() -> None:
    arg_st = False
    comp = False
    optimise = False
    filename = False
    cpp = False
    asm = False

    args = []
    outname = "a"
    optimise_flag = " "
    
    for arg in sys.argv:
        if arg_st:
            args.append(arg)
        elif filename:
            outname = arg
            filename = None
        elif comp and arg == "-o":
            if filename is None:
                Croak(ErrorType.Command, "cannot have two output names...")
            
            filename = True
        elif comp and arg.startswith("-O"):
            if len(arg) != 3:
                Croak(ErrorType.Command, "invalid flag %s" % arg)
            elif not arg[2].isnumeric():
                Croak(ErrorType.Command, "invalid flag %s" % arg)
            
            optimise = True
            optimise_flag = " %s" % arg
        elif comp and arg == "-S":
            asm = True
        elif arg in ("-c", "-com"):
            comp = True
        elif arg in ("-C", "-cpp"):
            cpp = True
        
        elif arg == "-args":
            arg_st = True
    
    if len(sys.argv) < 2:
        Croak(ErrorType.Command, "must input a file name")
    
    if not (comp or arg_st):
        args = sys.argv[1:]
    elif comp:
        args = [sys.argv[1]]
    
    src = open(sys.argv[1], "r", encoding="utf-8").read()
    
    lex_src = Lexer(src, args[0])
    lex_src.get_tokens()

    if comp:
        print("The compilation is still experimental, it may be buggy.")
        print("You must have g++ in order to compile pang.")
        name = "temp.cc" if not cpp else outname + ".cc"

        open(name, "w", encoding="utf-8").write(compile_ops(lex_src.toks, optimise))
        command = "g++ %s -o %s -Werror" % (name, outname)

        if optimise:
            command += "%s" % optimise_flag
        if asm:
            command += " -S"
        
        if not cpp:
            os.system(command)
            os.remove(name)
        elif asm:
            os.system(command)
        
    else:
        st = perf_counter()
        interpret = Interpreter(args, lex_src.toks)
        interpret.run()
        print(f"\nProgram finished in {perf_counter() - st} seconds (exit code: {interpret.exit_code}).")

if __name__ == "__main__":
    run_program()
