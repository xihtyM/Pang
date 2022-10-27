from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
import sys
import os

gtch = True

try:
    from msvcrt import getche
except ImportError:
    gtch = False

class TokenType(Enum):
    ID = auto()
    DO = auto()
    INT = auto()
    SUB = auto()
    ADD = auto()
    STR = auto()
    END = auto()
    DUP = auto()
    PUSH = auto()
    SWAP = auto()
    OVER = auto()
    DROP = auto()
    PUTS = auto()
    GETS = auto()
    TYPE = auto()
    OPEN = auto()
    BACK = auto()
    FRONT = auto()
    WHILE = auto()
    MACRO = auto()
    CLEAR = auto()
    CONDITION = auto()

@dataclass
class Token():
    typ: TokenType
    raw: Union[str, int]
    ind: int

T_READLINE = 0
T_READALL = -1

class Lexer():
    def __init__(self, src) -> None:
        self.index = 0
        self.raw = src
        self.size = len(src)
        self.toks: list[Token] = []

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

    def string(self) -> None:
        start = self.index
        raw = ""

        # Add 1 to index to skip \"\' character
        self.index += 1

        while self._peek() not in "\"\'":
            raw += self._peek()

            if not self._get():
                assert False, "EOF literal without terminating string: %s:%d" % (raw, self.index)

        # Add 1 to index to skip \"\' character
        self.index += 1

        self.toks.append(Token(TokenType.STR, raw, start))

    def comment_or_while(self) -> None:
        start = self.index
        self.index += 1

        if self._peek() == "/":
            while self._peek() != "\n":
                if not self._get():
                    break
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

        new_toks = Lexer(open(include_filename, "r", encoding="utf-8").read())
        new_toks.get_tokens_without_macros()

        for tok in new_toks.toks:
            self.toks.append(tok)

    def identifier(self) -> None:
        start = self.index
        raw = self._get()

        while self._peek() in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            raw += self._peek()

            if not self._get():
                break
        
        if raw in ("int", "char", "string"):
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
            elif current == ";":
                self.atom(TokenType.CLEAR)
            elif current == ":":
                self.atom(TokenType.OPEN)
            elif current == "{":
                self.atom(TokenType.GETS)
            elif current == "}":
                self.atom(TokenType.DUP)
            elif current == "#":
                self.atom(TokenType.OVER)
            elif current == "@":
                self.atom(TokenType.BACK)
            elif current == "~":
                self.atom(TokenType.FRONT)
            #elif current == "?":
            #    self.atom(TokenType.IF)
            elif current in "\"\'":
                self.string()
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
            if tok.typ in (TokenType.DO, ):
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
                    for macro_tok in macros[tok.raw]:
                        cur_toks.append(macro_tok)
        
        keys = macros.keys()
        skip_macro = False
        skip_end = 0

        for tok in self.toks:

            if skip_macro:
                if tok.typ in (TokenType.DO, ):
                    skip_end += 1
                elif tok.typ == TokenType.END and not skip_end:
                    skip_macro = False
                elif tok.typ == TokenType.END and skip_end:
                    skip_end -= 1
                
                continue
                
            if tok.raw in keys and tok.typ == TokenType.ID:
                for macro_tok in macros[tok.raw]:
                    macro_added_toks.append(macro_tok)
            elif tok.typ == TokenType.MACRO:
                # skip macros as they have already been added
                skip_macro = True
            else:
                macro_added_toks.append(tok)
        
        self.toks = macro_added_toks

def simulate_while(stack: list[int], tok_stream: list[Token], start: int, compare_typ: Token, condition: Token) -> tuple[list[int], int]:
    skip = 0
    index = start + 1
    editing_stack = True

    if stack[-1] != condition and compare_typ == "=":
        editing_stack = False
    if stack[-1] == condition and compare_typ == "!":
        editing_stack = False
    if stack[-1] > condition - 1 and compare_typ == ">":
        editing_stack = False
    if stack[-1] < condition + 1 and compare_typ == "<":
        editing_stack = False

    skip_next_end = 0

    while True:
        tok = tok_stream[index]

        if skip:
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
    tok = tok_stream[start]
    skip = 0
    
    if tok.typ == TokenType.PUSH:
        new_tok = tok_stream[start + 1]

        if new_tok.typ not in (TokenType.INT, TokenType.STR):
            assert False, "Incorrect data type at index %d" % new_tok.ind

        if new_tok.typ == TokenType.STR:
            for ch in new_tok.raw[::-1]:
                stack.append(ord(ch))
            
            stack.append(len(new_tok.raw))
            skip += 1
            return stack, skip

        stack.append(new_tok.raw)
        skip += 1
    elif tok.typ == TokenType.PUTS:
        stream = stack.pop()

        # stdin is read-only
        if stream == 0:
            assert False, "stream STDIN is read-only"

        new_tok = tok_stream[start + 1]

        if new_tok.typ != TokenType.TYPE:
            assert False, "Must be a valid data type: %s:%d" % (new_tok.raw, new_tok.ind)
        
        if stream not in (1, 2):
            if new_tok.raw == "char":
                os.write(stream, bytes(chr(stack[-1]), encoding="utf-8"))
            elif new_tok.raw == "int":
                os.write(stream, bytes(str(stack[-1]), encoding="utf-8"))
            elif new_tok.raw == "string":
                for _ in range(stack.pop()):
                    os.write(stream, bytes(chr(stack.pop()), encoding="utf-8"))
            else:
                assert False, "Incorrect data type for intrinsic PUTS: %s:%d" % (new_tok.raw, new_tok.ind)
            os.close(stream)
        elif stream == 1:
            if new_tok.raw == "char":
                sys.stdout.write(chr(stack[-1]))
            elif new_tok.raw == "int":
                sys.stdout.write(str(stack[-1]))
            elif new_tok.raw == "string":
                for _ in range(stack.pop()):
                    sys.stdout.write(chr(stack.pop()))
            else:
                assert False, "Incorrect data type for intrinsic PUTS: %s:%d" % (new_tok.raw, new_tok.ind)
        elif stream == 2:
            if new_tok.raw == "char":
                sys.stderr.write(chr(stack[-1]))
            elif new_tok.raw == "int":
                sys.stderr.write(str(stack[-1]))
            elif new_tok.raw == "string":
                for _ in range(stack.pop()):
                    sys.stderr.write(chr(stack.pop()))
            else:
                assert False, "Incorrect data type for intrinsic PUTS: %s:%d" % (new_tok.raw, new_tok.ind)
        skip += 1
    elif tok.typ == TokenType.GETS:
        stream = stack.pop()
        read_typ = stack.pop()
        
        if stream == 0:
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
        loop = tok_stream[start - 3]
        condition = tok_stream[start - 2].raw
        compare_typ = tok_stream[start - 1].raw

        if loop.typ in (TokenType.WHILE, ):
            stack, skip = simulate_while(stack, tok_stream, start, compare_typ, condition)
        else:
            assert False, "Not implemented"
    elif tok.typ == TokenType.DUP:
        stack.append(stack[-1])
    elif tok.typ == TokenType.OVER:
        if len(stack) < 3:
            
            assert False, "Not enough items for intrinsic OVER"
            
        stack[-3], stack[-1] = stack[-1], stack[-3]
    elif tok.typ == TokenType.OPEN:
        file_tok = tok_stream[start + 1]

        if file_tok.typ != TokenType.STR:
            assert False, "Must be a valid string: %s:%d" % (file_tok.raw, file_tok.ind)
        
        try:
            file_descriptor = os.open(file_tok.raw, os.O_RDWR)
        except FileNotFoundError:
            # create file
            open(file_tok.raw, "x")
            file_descriptor = os.open(file_tok.raw, os.O_RDWR)
        stack.append(file_descriptor)
        skip += 1
    elif tok.typ == TokenType.DROP:
        if len(stack) == 0:
            assert False, "Not enough values on stack to drop: %s:%d" % (tok.raw, tok.ind)

        stack.pop()
    elif tok.typ == TokenType.SWAP:
        if len(stack) < 2:
            assert False, "Not enough values on stack to swap: %s:%d" % (tok.raw, tok.ind)

        stack.append(stack.pop(-2))
        stack.append(stack.pop(-1))
    elif tok.typ == TokenType.BACK:
        stack.insert(0, stack.pop())
    elif tok.typ == TokenType.FRONT:
        stack.append(stack.pop(0))
    elif tok.typ == TokenType.ADD:
        if len(stack) < 2:
            assert False, "Not enough values on stack to add: %s:%d" % (tok.raw, tok.ind)

        stack.append(stack.pop(-2) + stack.pop(-1))
    elif tok.typ == TokenType.SUB:
        if len(stack) < 2:
            assert False, "Not enough values on stack to sub: %s:%d" % (tok.raw, tok.ind)

        stack.append(stack.pop(-2) - stack.pop(-1))
    elif tok.typ == TokenType.CLEAR:
        stack = []
    
    return stack, skip

def simulate_tokens(args: list, tok_stream: list[Token]) -> None:
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
        assert False, "Must drop all items on stack"

def compile_tokens(tok_stream: list[Token]) -> str:
    """ Expands macros etc """

    out = ""
    for tok in tok_stream:
        if tok.typ == TokenType.STR:
            out += "\"" + tok.raw + "\""
        else:
            out += str(tok.raw)
    
    return out

def run_program():
    arg_st = False
    args = []
    
    for arg in sys.argv:
        if arg_st:
            args.append(arg)
        elif arg == "-args":
            arg_st = True
    
    if arg_st != True:
        args = sys.argv[1:]
    
    src = open(args[0], "r", encoding="utf-8").read()
    
    lex_src = Lexer(src)
    lex_src.get_tokens()

    simulate_tokens(args[::-1], lex_src.toks)
    #print(compile_tokens(lex_src.toks))

if __name__ == "__main__":
    run_program()
