from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
import sys
import os
from time import perf_counter

gtch = True

try:
    from msvcrt import getche
except ImportError:
    gtch = False

class ErrorType(Enum):
    Syntax = auto()
    Command = auto()
class TokenType(Enum):
    ID = auto()
    IF = auto()
    DO = auto()
    INT = auto()
    SUB = auto()
    ADD = auto()
    STR = auto()
    END = auto()
    DUP = auto()
    PUSH = auto()
    SWAP = auto()
    DROP = auto()
    PUTS = auto()
    GETS = auto()
    TYPE = auto()
    OPEN = auto()
    BACK = auto()
    FRONT = auto()
    FLUSH = auto()
    WHILE = auto()
    MACRO = auto()
    CLEAR = auto()
    THROW = auto()
    DIVMOD = auto()
    SYSCALL = auto()
    MULTIPLY = auto()
    CONDITION = auto()

@dataclass
class Token():
    typ: TokenType
    raw: Union[str, int]
    ind: int

T_READLINE = 0
T_READALL = -1

o_buf = ""

def Croak(err_typ: ErrorType, msg: str):
    if err_typ == ErrorType.Syntax:
        print("SyntaxError: %s" % msg)
    elif err_typ == ErrorType.Command:
        print("CommandError: %s" % msg)
    exit(1)

class Lexer():
    def __init__(self, src: str, filename: str = "N/A") -> None:
        self.index = 0
        self.fn = filename
        self.raw = src
        self.size = len(src)
        self.toks: list[Token] = []
        self.includes: list[str] = []

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
        self.toks.append(Token(tok_typ, self._get(), self.index - 1))

    def num(self) -> None:
        start = self.index
        raw = ""

        while self._peek() and self._peek() in "1234567890":
            raw += self._get()

        self.toks.append(Token(TokenType.INT, int(raw), start))
    
    #def ptr(self) -> None:
    #    start = self.index
    #    raw = self._get()
    #
    #    while self._peek() and self._peek() in "1234567890":
    #        raw += self._get()
    #    
    #    self.toks.append(Token(TokenType.PTR, raw, start))

    def raw_string(self) -> None:
        start = self.index
        raw = ""

        # Add 1 to index to skip \' character
        self.index += 1

        while self._peek() != "\'":
            raw += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated string literal in file \"%s\" (detected at line: %d)" % (
                        self.fn, 1 + self.raw[:start].count("\n")
                    )
                )

        # Add 1 to index to skip \' character
        self.index += 1

        self.toks.append(Token(TokenType.STR, raw, start))

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
                        self.fn, 1 + self.raw[:start].count("\n")
                    )
                )
            
            if self._peek() == "\"" and not raw.endswith("\\\\") and raw[-1] == "\\":
                raw += self._get()

        # Add 1 to index to skip \" character
        self.index += 1

        self.toks.append(Token(TokenType.STR, raw.encode("utf-8").decode("unicode_escape"), start))

    def comment_or_while(self) -> None:
        start = self.index
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
        
        self.toks.append(Token(TokenType.WHILE, "/", start))

    def include_file(self) -> None:
        while self._peek() in " \n\t":
            if not self._get():
                assert False, "Must include a file"

        if self._get() not in "\"\'":
            assert False, "Include must include a string"
        
        include_filename = self._get()

        while self._peek() not in "\"\'":
            include_filename += self._peek()

            if not self._get():
                assert False, "EOF literal without terminating string: %s:%d" % (include_filename, self.index)
        
        # Add 1 to index to skip \"\' character
        self.index += 1

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

        while self._peek() in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            raw += self._peek()

            if not self._get():
                break
        
        if raw in ("int", "char"):
            self.toks.append(Token(TokenType.TYPE, raw, start))
        elif raw == "macro":
            self.toks.append(Token(TokenType.MACRO, raw, start))
        elif raw == "end":
            self.toks.append(Token(TokenType.END, raw, start))
        elif raw == "include":
            self.include_file()
        elif raw == "do":
            self.toks.append(Token(TokenType.DO, raw, start))
        else:
            self.toks.append(Token(TokenType.ID, raw, start))

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
            
            if current == "+":
                self.atom(TokenType.ADD)
            elif current == "-":
                self.atom(TokenType.SUB)
            elif current == "*":
                self.atom(TokenType.MULTIPLY)
            elif current == "%":
                self.atom(TokenType.DIVMOD)
            elif current == "^":
                self.atom(TokenType.SWAP)
            elif current == "$":
                self.atom(TokenType.PUSH)
            elif current == "[":
                self.atom(TokenType.PUTS)
            elif current == "]":
                self.atom(TokenType.DROP)
            elif current == "/":
                self.comment_or_while()
            elif current == "&":
                self.atom(TokenType.SYSCALL) # TODO: IMPLEMENT SYSCALLS
            elif current == ";":
                self.atom(TokenType.CLEAR)
            elif current == ":":
                self.atom(TokenType.OPEN)
            elif current == "{":
                self.atom(TokenType.GETS)
            elif current == "}":
                self.atom(TokenType.DUP)
            elif current == "@":
                self.atom(TokenType.BACK)
            elif current == "~":
                self.atom(TokenType.FRONT)
            elif current == ".":
                self.atom(TokenType.FLUSH)
            elif current == "?":
                self.atom(TokenType.IF)
            elif current == "\\":
                self.atom(TokenType.THROW)
            elif current == "\"":
                self.string()
            elif current == "\'":
                self.raw_string()
            elif current in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                self.identifier()
            elif current in "1234567890":
                self.num()
            elif current in "<>=!":
                self.atom(TokenType.CONDITION)
            else:
                assert False, "Unhandled token type/raw text: %s:%d" % (current, self.index)

    def get_tokens(self) -> None:
        self.get_tokens_without_macros()

        macro_added_toks = []
        macro = False
        macro_name = False
        skip_end = 0
        cur_name = ""
        cur_toks = []
        macros = {}

        # Add macros
        for tok in self.toks:
            if tok.typ == TokenType.DO:
                skip_end += 1
            
            if tok.typ == TokenType.MACRO:
                if macro:
                    assert False, "Macro cannot include macro: %s:%d" % (tok.raw, tok.ind)

                macro_name = True
                continue
            
            if macro_name:
                if tok.typ != TokenType.ID:
                    assert False, "Macro must have an ID"
                
                cur_name = tok.raw
                macro_name = False
                macro = True
                continue

            if macro:
                if tok.typ == TokenType.END and not skip_end:
                    macro = False
                    macros[cur_name] = cur_toks
                    cur_toks = []
                    continue
                
                if tok.typ == TokenType.END and skip_end:
                    skip_end -= 1
                
                if tok.typ != TokenType.ID:
                    cur_toks.append(tok)
                else:
                    # print(tok.raw) # open(self.includes[0], "r", encoding="utf-8").read().count("\n", 0, tok.ind))
                    if tok.raw not in macros:
                        assert False, "Undefined reference to identifier: %s" % tok.raw
                    
                    for macro_tok in macros[tok.raw]:#[0]:
                        cur_toks.append(macro_tok)
        
        keys = macros.keys()
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
                if not tok.raw in keys:
                    assert False, "Undefined reference to identifier: %s" % tok.raw

                for macro_tok in macros[tok.raw]:
                    macro_added_toks.append(macro_tok)
            elif tok.typ == TokenType.MACRO:
                # skip macros as they have already been added
                skip_macro = True
            else:
                macro_added_toks.append(tok)
        
        self.toks = macro_added_toks

def simulate_if(stack: list[int], tok_stream: list[Token], start: int, compare_typ: str, condition: Union[str, int]) -> tuple[list[int], int]:
    skip = 0
    index = start + 1

    if type(condition) == int:
        equal = condition != stack[-1] and compare_typ == "!"
        not_equal = condition == stack[-1] and compare_typ == "="
        gt = condition - 1 > stack[-1] and compare_typ == ">"
        st = condition + 1 < stack[-1] and compare_typ == "<"

    editing_stack = any([not_equal, equal, gt, st])

    skip_next_end = 0

    while True:
        tok = tok_stream[index]

        if skip:
            index += 1
            skip -= 1
            continue

        if tok.typ == TokenType.DO and not editing_stack:
            skip_next_end += 1
            index += 1
            continue

        if tok.typ == TokenType.END:
            if skip_next_end:
                skip_next_end -= 1
                index += 1
                continue

            break

        if editing_stack:
            stack, skip = simulate_token(stack, tok_stream, index)

        index += 1
    
    return stack, index - start

def simulate_while(stack: list[int], tok_stream: list[Token], start: int, compare_typ: str, condition: Union[str, int]) -> tuple[list[int], int]:
    skip = 0
    index = start + 1

    if type(condition) == int:
        equal = condition != stack[-1] and compare_typ == "!"
        not_equal = condition == stack[-1] and compare_typ == "="
        gt = condition - 1 > stack[-1] and compare_typ == ">"
        st = condition + 1 < stack[-1] and compare_typ == "<"

    editing_stack = any([not_equal, equal, gt, st])

    skip_next_end = 0

    while True:
        tok = tok_stream[index]

        if skip:
            index += 1
            skip -= 1
            continue

        if tok.typ == TokenType.DO and not editing_stack:
            skip_next_end += 1
            index += 1
            continue

        if tok.typ == TokenType.END:
            if skip_next_end:
                skip_next_end -= 1
                index += 1
                continue
            
            if stack[-1] != condition and compare_typ == "=":
                break
            if stack[-1] == condition and compare_typ == "!":
                break
            if stack[-1] > condition - 1 and compare_typ == ">":
                break
            if stack[-1] < condition + 1 and compare_typ == "<":
                break
            
            index = start + 1
            continue

        if editing_stack:
            stack, skip = simulate_token(stack, tok_stream, index)
        
        index += 1
    
    return stack, index - start

def simulate_token(stack: list[int], tok_stream: list[Token], start: int) -> tuple[list[int], int]:
    global o_buf


    tok = tok_stream[start]
    
    skip = 0
    #print(stack, tok.typ) # for debugging
    
    if tok.typ == TokenType.PUSH:
        new_tok = tok_stream[start + 1]

        if new_tok.typ not in (TokenType.INT, TokenType.STR):
            Croak(ErrorType.Syntax, "incorrect data type for push")

        if new_tok.typ == TokenType.STR:
            for ch in new_tok.raw[::-1]:
                stack.append(ord(ch))
            
            stack.append(len(new_tok.raw))
            skip += 1
            return stack, skip

        stack.append(new_tok.raw)
        skip += 1
    elif tok.typ == TokenType.FLUSH:
        stream = stack.pop()

        # stdin is read-only
        if not stream:
            assert False, "stream STDIN is read-only"
        
        if stream not in (1, 2):
            os.ftruncate(stream, 0)
            os.lseek(stream, 0, os.SEEK_SET)
            os.write(stream, bytes(o_buf, encoding="utf-8"))
        elif stream == 1:
            sys.stdout.write(o_buf)
        elif stream == 2:
            sys.stderr.write(o_buf)
        
        o_buf = ""
    elif tok.typ == TokenType.PUTS:
        new_tok = tok_stream[start + 1]

        if new_tok.typ != TokenType.TYPE:
            assert False, "Must be a valid data type: %s:%d" % (new_tok.raw, new_tok.ind)
        
        if new_tok.raw == "char":
            o_buf += chr(stack[-1])
        elif new_tok.raw == "int":
            o_buf += str(stack[-1])
        else:
            assert False, "Incorrect data type for intrinsic PUTS: %s:%d" % (new_tok.raw, new_tok.ind)
    
        skip += 1
    elif tok.typ == TokenType.GETS:
        stream = stack.pop()
        read_typ = stack.pop()
        
        if not stream:
            if read_typ == T_READLINE:
                inp = input()
                for ch in inp[::-1]:
                    stack.append(ord(ch))
                stack.append(len(inp))
            elif read_typ == T_READALL:
                assert False, "Cannot read all characters from STDIN"
            elif read_typ > 0:
                if gtch:
                    inp = ""
                    for _ in range(read_typ):
                        inp += bytes.decode(getche(), encoding="utf-8")
                else:
                    # If getch doesn't exist, just split the string until the max output is reached
                    inp = input()
                
                for ch in inp[::-1][:read_typ]:
                    stack.append(ord(ch))
                
                stack.append(read_typ)
            else:
                assert False, "Invalid read type"
        else:
            fstream = os.fdopen(stream, "r")
            contents = fstream.read()[::-1]

            if read_typ == T_READLINE:
                ln = contents[:contents.find("\n")]
                for ch in ln:
                    stack.append(ord(ch))
                stack.append(len(ln))
            elif read_typ == T_READALL:
                for ch in contents:
                    stack.append(ord(ch))
                stack.append(len(contents))
            elif read_typ > 0:
                for ch in contents[:read_typ]:
                    stack.append(ord(ch))
                stack.append(read_typ)
            else:
                assert False, "Invalid read type"
            os.close(stream)
    elif tok.typ == TokenType.DO:
        typ = tok_stream[start - 3]
        condition = tok_stream[start - 2].raw
        compare_typ = tok_stream[start - 1].raw

        if typ.typ == TokenType.WHILE:
            stack, skip = simulate_while(stack, tok_stream, start, compare_typ, condition)
        elif typ.typ == TokenType.IF:
            stack, skip = simulate_if(stack, tok_stream, start, compare_typ, condition)
        else:
            assert False, "Not implemented"
    elif tok.typ == TokenType.THROW:
        for _ in range(stack.pop()):
            sys.stdout.write(chr(stack.pop()))
        sys.stdout.write("\u001b[0m")
        exit(1)
    elif tok.typ == TokenType.DUP:
        stack.append(stack[-1])
    elif tok.typ == TokenType.OPEN:
        file = ""
        for _ in range(stack.pop()):
            file = file + chr(stack.pop())
        
        try:
            file_descriptor = os.open(file, os.O_RDWR)
        except FileNotFoundError:
            # create file
            open(file, "x")
            file_descriptor = os.open(file, os.O_RDWR)
        
        stack.append(file_descriptor)
    elif tok.typ == TokenType.DROP:
        if len(stack) == 0:
            assert False, "Not enough values on stack to drop: %s:%d" % (tok.raw, tok.ind)

        stack.pop()
    elif tok.typ == TokenType.SWAP:
        if len(stack) < 2:
            assert False, "Not enough values on stack to swap: %s:%d" % (tok.raw, tok.ind)

        stack[-1], stack[-2] = stack[-2], stack[-1]
    elif tok.typ == TokenType.BACK:
        stack.insert(0, stack.pop())
    elif tok.typ == TokenType.FRONT:
        stack.append(stack.pop(0))
    elif tok.typ == TokenType.ADD:
        if len(stack) < 2:
            assert False, "Not enough values on stack to add: %s:%d" % (tok.raw, tok.ind)

        stack.append(stack.pop(-2) + stack.pop())
    elif tok.typ == TokenType.SUB:
        if len(stack) < 2:
            assert False, "Not enough values on stack to sub: %s:%d" % (tok.raw, tok.ind)

        stack.append(stack.pop(-2) - stack.pop())
    elif tok.typ == TokenType.MULTIPLY:
        if len(stack) < 2:
            assert False, "Not enough values on stack to multiply: %s:%d" % (tok.raw, tok.ind)
        
        stack.append(stack.pop(-2) * stack.pop())
    elif tok.typ == TokenType.DIVMOD:
        if len(stack) < 2:
            assert False, "Not enough values on stack to divmod: %s:%d" % (tok.raw, tok.ind)

        stack += divmod(stack.pop(-2), stack.pop())
    elif tok.typ == TokenType.CLEAR:
        stack = []
    #else:
    #    assert False, "Not implemented"
    
    return stack, skip

def simulate_tokens(args: list[str], tok_stream: list[Token]) -> None:
    stack = []

    for arg in args:
        for ch in arg[::-1]:
            stack.append(ord(ch))
        stack.append(len(arg))
    
    stack.append(len(args))

    skip = 0

    for ind, _ in enumerate(tok_stream):
        if skip:
            skip -= 1
            continue

        stack, skip = simulate_token(stack, tok_stream, ind)

    if len(stack) > 0:
        print(stack)
        assert False, "Must drop all items on stack"

def unmacro_tokens(tok_stream: list[Token]) -> str:
    """ Expands macros etc """

    out = ""
    for tok in tok_stream:
        if tok.typ == TokenType.STR:
            out += "\"" + tok.raw + "\""
        else:
            out += str(tok.raw)
    
    return out 

def find_end(start: int, tok_stream: list[Token]) -> int:
    skip_next_end = 0

    for ind, tok in enumerate(tok_stream[start + 1:]):
        if tok.typ == TokenType.DO:
            skip_next_end += 1
        elif tok.typ == TokenType.END:
            if skip_next_end:
                skip_next_end -= 1
                continue
            return ind
    Croak(ErrorType.Syntax, "no end found")


def compile_tokens(tok_stream: list[Token]) -> str:
    """ Compiles to native binary """

    skip = 0
    curly_end = 0
    no_args = False
    flush = False

    out = ""

    for ind, tok in enumerate(tok_stream):
        if skip:
            skip -= 1
            continue
        if curly_end:
            curly_end -= 1
            if not curly_end:
                out += " }"

        if tok.typ == TokenType.PUSH:
            new_tok = tok_stream[ind + 1]
            skip += 1

            if new_tok.typ not in (TokenType.INT, TokenType.STR):
                Croak(ErrorType.Syntax, "incorrect data type for push")
            
            if new_tok.typ == TokenType.INT:
                out += " PUSH(%d)" % new_tok.raw
            else:
                for ch in new_tok.raw[::-1]:
                    out += " PUSH(%d)" % ord(ch)
                out += " PUSH(%d)" % len(new_tok.raw)
        elif tok.typ == TokenType.FLUSH:
            out += " _FLUSH_(&p_vars);"
            flush = True
        elif tok.typ == TokenType.GETS:
            out += " _READ_(&p_vars);"
        elif tok.typ == TokenType.PUTS:
            new_tok = tok_stream[ind + 1]
            skip += 1

            if new_tok.typ != TokenType.TYPE:
                Croak(ErrorType.Syntax, "incorrect data type for puts")
            
            if new_tok.raw == "char":
                out += " PCHR"
            else:
                out += " PINT"
        elif tok.typ == TokenType.SWAP:
            out += " SWAP"
        elif tok.typ == TokenType.DROP:
            out += " DROP"
        elif tok.typ == TokenType.ADD:
            out += " ADD"
        elif tok.typ == TokenType.SUB:
            out += " SUB"
        elif tok.typ == TokenType.MULTIPLY:
            out += " MUL"
        elif tok.typ == TokenType.DIVMOD:
            out += " DMD"
        elif tok.typ == TokenType.BACK:
            out += " BACK"
        elif tok.typ == TokenType.FRONT:
            out += " FRONT"
        elif tok.typ == TokenType.DUP:
            out += " DUP"
        elif tok.typ == TokenType.OPEN:
            out += " FD_FETCH(&p_vars);"
        elif tok.typ == TokenType.CLEAR:
            if not ind:
                no_args = True
                continue
            out += " p_vars.stack.clear();"
        elif tok.typ == TokenType.DO:
            curly_end = find_end(ind, tok_stream)

            if tok_stream[ind - 1].raw in ("!", "="):
                tok_stream[ind - 1].raw += "="
            
            if tok_stream[ind - 3].typ == TokenType.WHILE:
                out += " while (%s %s p_vars.stack.back()) {" % (str(tok_stream[ind - 2].raw), tok_stream[ind - 1].raw)
            elif tok_stream[ind - 3].typ == TokenType.IF:
                out += " if (%s %s p_vars.stack.back()) {" % (str(tok_stream[ind - 2].raw), tok_stream[ind - 1].raw)

    # boilerplate code
    start = "#include <stdio.h>\n"
    start += "#include <conio.h>\n\n"
    start += "#include <iostream>\n"
    start += "#include <fstream>\n"
    start += "#include <string>\n"
    start += "#include <vector>\n\n"
    start += "#if defined(WIN32) || defined(_WIN32) || defined(__WIN32) && !defined(__CYGWIN__)\n"
    start += "#define ON_WINDOWS\n"
    start += "#include <locale.h>\n"
    start += "#endif\n"
    start += "\n"
    start += "#define T_READLINE 0\n"
    start += "#define T_READALL -1\n"
    start += "\n"
    start += "typedef struct PangVars {\n"
    start += "    std::vector<std::string> files;\n"
    start += "    std::vector<int64_t> stack;\n"
    start += "    std::string o_buf;\n"
    start += "} PangVars;\n"
    start += "\n"
    start += "template<typename T> T pop(std::vector<T> *stack, int64_t index = -1) {\n"
    start += "    T value;\n"
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
    start += "template<typename T> void divmod(std::vector<T> *stack) {\n"
    start += "    T denominator = pop(stack);\n"
    start += "    T numerator = pop(stack);\n"
    start += "\n"
    start += "    std::lldiv_t result = std::lldiv(numerator, denominator);\n"
    start += "\n"
    start += "    stack->push_back(result.quot);\n"
    start += "    stack->push_back(result.rem);\n"
    start += "}\n"
    start += "\n"
    start += "void FD_FETCH(PangVars *p_vars) {\n"
    start += "    std::vector<int64_t> *stack = &p_vars->stack;\n"
    start += "    std::vector<std::string> *files = &p_vars->files;\n"
    start += "    \n"
    start += "    std::string filename = \"\";\n"
    start += "\n"
    start += "    while (0 < stack->back()) {\n"
    start += "        stack->at(stack->size() - 1) -= 1;\n"
    start += "        filename += std::string(1, pop(stack, -2));\n"
    start += "    } stack->at(stack->size() - 1) = files->size() + 3; // +3 to skip stdin stdout stderr\n"
    start += "\n"
    start += "    files->push_back(filename);\n"
    start += "}\n"
    start += "\n"

    start += "void _READ_(PangVars *p_vars) {\n"
    start += "    std::vector<std::string> *files = &p_vars->files;\n"
    start += "    std::vector<int64_t> *stack = &p_vars->stack;\n"
    start += "\n"
    start += "    int64_t stream = pop(stack);\n"
    start += "    int64_t read_typ = pop(stack);\n"
    start += "\n"
    start += "    if (!stream) {\n"
    start += "        if (read_typ == T_READLINE) {\n"
    start += "            std::string ln;\n"
    start += "            std::getline(std::cin, ln);\n"
    start += "            ln = std::string(ln.rbegin(), ln.rend());\n"
    start += "\n"
    start += "            for (auto ch: ln) { stack->push_back(ch); }\n"
    start += "            stack->push_back(ln.size());\n"
    start += "        } else if (read_typ < 0) {\n"
    start += "            std::cerr << \"Error: cannot read negative bytes from stdin\\n\";\n"
    start += "            exit(1);\n"
    start += "        } else {\n"
    start += "            std::string bytes = \"\";\n"
    start += "            int64_t save = read_typ;\n"
    start += "\n"
    start += "            for (; save < 0; save--) {\n"
    start += "                bytes = bytes + std::string(1, getche());\n"
    start += "            }\n"
    start += "            \n"
    start += "            for (auto ch: bytes) { stack->push_back(ch); }\n"
    start += "            stack->push_back(read_typ);\n"
    start += "        }\n"
    start += "    } else {\n"
    start += "        std::ifstream is(files->at(stream - 3), std::ifstream::binary);\n"
    start += "\n"
    start += "        if (read_typ == T_READLINE) {\n"
    start += "            std::string ln;\n"
    start += "            std::getline(is, ln);\n"
    start += "\n"
    start += "            ln = std::string(ln.rbegin(), ln.rend());\n"
    start += "            for (auto ch: ln) { stack->push_back(ch); }\n"
    start += "            stack->push_back(ln.length());\n"
    start += "        } else {\n"
    start += "            is.seekg(0, is.end);\n"
    start += "            size_t length = is.tellg();\n"
    start += "            is.seekg(0, is.beg);\n"
    start += "\n"
    start += "            if ((uint64_t) read_typ < length && read_typ != T_READALL) {\n"
    start += "                length = read_typ;\n"
    start += "            }\n"
    start += "\n"
    start += "            char *buf = new char[length];\n"
    start += "\n"
    start += "            is.read(buf, length);\n"
    start += "\n"
    start += "            if (!is) {\n"
    start += "                std::cerr << \"Error: could not read from file: \" << files->at(stream - 3) << \'\\n\';\n"
    start += "                exit(1);\n"
    start += "            }\n"
    start += "\n"
    start += "            std::string sbuf(buf);\n"
    start += "            sbuf = std::string(sbuf.rbegin(), sbuf.rend());\n"
    start += "\n"
    start += "            for (auto ch: sbuf) { stack->push_back(ch); }\n"
    start += "            stack->push_back(length);\n"
    start += "\n"
    start += "            delete[] buf;\n"
    start += "        }\n"
    start += "\n"
    start += "        is.close();\n"
    start += "    }\n"
    start += "}\n"
    start += "\n"
    
    if flush:
        start += "void _FLUSH_(PangVars *p_vars) {\n"
        start += "    std::vector<std::string> *files = &p_vars->files;\n"
        start += "    std::vector<int64_t> *stack = &p_vars->stack;\n"
        start += "    std::string *o_buf = &p_vars->o_buf;\n"
        start += "\n"
        start += "    int64_t stream = pop(stack);\n"
        start += "\n"
        start += "    if (!stream) {\n"
        start += "        throw \"stream STDIN is read-only\";\n"
        start += "    }\n"
        start += "\n"
        start += "    switch (stream) {\n"
        start += "        case 1:\n"
        start += "            std::cout << *o_buf;\n"
        start += "            break;\n"
        start += "        case 2:\n"
        start += "            std::cerr << *o_buf;\n"
        start += "            break;\n"
        start += "        default: {\n"
        start += "            fclose(fopen(files->at(stream - 3).c_str(), \"w\"));\n"
        start += "            FILE *fd = fopen(files->at(stream - 3).c_str(), \"w\");\n"
        start += "\n"
        start += "            if (fd == NULL) {\n"
        start += "                std::cerr << \"Error: bad filename: \" << files->at(stream) << '\\n';\n"
        start += "                exit(1);\n"
        start += "            }\n"
        start += "\n"
        start += "            fwrite(o_buf->c_str(), 1, o_buf->length(), fd);\n"
        start += "\n"
        start += "            fclose(fd);\n"
        start += "\n"
        start += "            files->resize(files->size() - 1);\n"
        start += "        }\n"
        start += "    }\n"
        start += "\n"
        start += "    o_buf->clear();\n"
        start += "}\n"
        start += "\n"

    start += "#define PUSH(i) p_vars.stack.push_back(i);\n"
    start += "#define DUP p_vars.stack.push_back(p_vars.stack.back());\n"
    start += "#define DROP p_vars.stack.pop_back();\n"
    start += "#define PINT p_vars.o_buf += std::to_string(p_vars.stack.back());\n"
    start += "#define PCHR p_vars.o_buf += std::string(1, p_vars.stack.back());\n"
    start += "#define SWAP std::iter_swap(p_vars.stack.end() - 2, p_vars.stack.end() - 1);\n"
    start += "#define BACK p_vars.stack.insert(p_vars.stack.begin(), pop(&p_vars.stack));\n"
    start += "#define FRONT p_vars.stack.push_back(p_vars.stack.at(0)); p_vars.stack.erase(p_vars.stack.begin());\n"
    start += "\n"
    start += "/* Simple arithmetic */\n"
    start += "#define ADD p_vars.stack.push_back(pop(&p_vars.stack) + pop(&p_vars.stack));\n"
    start += "#define SUB SWAP p_vars.stack.push_back(pop(&p_vars.stack) - pop(&p_vars.stack));\n"
    start += "#define MUL p_vars.stack.push_back(pop(&p_vars.stack) * pop(&p_vars.stack));\n"
    start += "#define DMD divmod(&p_vars.stack);\n"
    start += "\n"
    start += "int main(int argc, char *argv[]) {\n"
    start += "    #ifdef ON_WINDOWS\n"
    start += "    setlocale(LC_ALL, \".utf-8\");\n"
    start += "    #endif\n"
    start += "\n"
    start += "    std::vector<std::string> args(argv + 1, argv + argc);\n"
    start += "    PangVars p_vars;\n"
    start += "    p_vars.o_buf = \"\";\n"
    start += "\n"

    if not no_args:
        start += "    for (auto s: args) {\n"
        start += "        for (auto ch: s) {\n"
        start += "            p_vars.stack.push_back(ch);\n"
        start += "        }\n"
        start += "\n"
        start += "        p_vars.stack.push_back(s.length());\n"
        start += "    }\n"
        start += "\n"
        start += "    p_vars.stack.push_back(argc);\n"

    return start + out + "\n    return 0;\n}\n"#    std::cout << stack.at(0);\n}"

def run_program() -> None:
    arg_st = False
    comp = False
    args = []
    
    for arg in sys.argv:
        if arg_st:
            args.append(arg)
        elif comp:
            outname = arg
            break
        elif arg == "-args":
            arg_st = True
        elif arg in ("-c", "-com"):
            comp = True
    
    if len(sys.argv) < 2:
        Croak(ErrorType.Command, "must input a file name")
    
    if arg_st != True and not comp:
        args = sys.argv[1:]
    elif comp:
        args = [sys.argv[1]]
    
    src = open(args[0], "r", encoding="utf-8").read()
    
    lex_src = Lexer(src, args[0])
    lex_src.get_tokens()

    #print(compile_tokens(lex_src.toks))
    if comp:
        print("The compilation is still experimental, it may be buggy.")
        print("You must have g++ in order to compile pang.")
        open("temp.cc", "w", encoding="utf-8").write(compile_tokens(lex_src.toks))
        os.system("g++ temp.cc -o %s -O3 -Wall" % outname)
        os.remove("temp.cc")
    else:
        st = perf_counter()
        simulate_tokens(args[::-1], lex_src.toks)
        print(f"Program finished in {perf_counter() - st} seconds.")

if __name__ == "__main__":
    run_program()
