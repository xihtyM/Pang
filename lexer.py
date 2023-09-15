from pang_lib import *

if __name__ == "__main__":
    Croak("lexer cannot be ran by itself.")


class Lexer():
    def __init__(self, src: str, filename: str = "N/A") -> None:
        self.index = 0
        self.fn = filename
        self.raw = src
        self.size = len(src)
        self.line = 1
        self.toks: list[Token] = []
        self.includes = set()
        self.calls = set()

        self.lexing_call = False

    def _get(self) -> str:
        """ Returns current value and index++ """

        self.index += 1

        if self.index - 1 >= self.size:
            return ""
        
        if self.raw[self.index - 1] == "\n":
            self.line += 1
        
        return self.raw[self.index - 1]

    def _peek(self) -> str:
        """ Returns current value """
        if self.index >= self.size:
            return ""

        return self.raw[self.index]

    def skip_whitespace(self) -> None:
        while self._peek() in " \t\n":
            self._get()

            if not self._peek():
                break

    def atom(self, tok_typ: TokenType) -> None:
        self.toks.append(Token(tok_typ, self._peek(),
                         self._get(), self.fn, self.line))

    def num(self) -> None:
        line = self.line
        raw = self._get()

        while self._peek() and self._peek() in "0123456789":
            raw += self._get()

        if raw in ("0", "-0", "+0") and self._peek() in ("x", "X"):
            raw += self._get()
            while self._peek() and self._peek() in "0123456789abcdefABCDEF":
                raw += self._get()

            self.toks.append(Token(
                TokenType.INT, raw, int(raw, 16),
                self.fn, line))

            return
        elif raw in ("0", "-0", "+0") and self._peek() in ("o", "O"):
            raw += self._get()
            while self._peek() and self._peek() in "01234567":
                raw += self._get()

            self.toks.append(Token(
                TokenType.INT, raw, int(raw, 8),
                self.fn, line))

            return

        if raw.startswith(("0", "-0", "+0")) and len(raw) > 1:
            Croak(
                ErrorType.Syntax,
                "leading zeros in integer literals are prohibited; ",
                "use 0o for octal integers instead.\n\n",
                "Found in file \"%s\" (detected at line: %d)." % (
                    self.fn, line))

        self.toks.append(Token(TokenType.INT, raw, int(raw),
                         self.fn, line))

    def raw_string(self) -> None:
        line = self.line
        raw = ""

        # Add 1 to index to skip \" character
        self._get()

        while self._peek() != "\"":
            raw += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated raw string literal: %s\n\n" % raw,
                    "Found in file \"%s\" (detected at line: %d)" % (
                        self.fn, line))

        # Add 1 to index to skip \" character
        self._get()

        self.toks.append(Token(TokenType.STR, "r\"%s\"" %
                         raw, raw, self.fn, line))

    def string(self) -> None:
        line = self.line
        raw = ""

        # Add 1 to index to skip \" character
        self._get()

        while self._peek() != "\"":
            raw += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated string literal: %s\n\n" % raw,
                    "Found in file \"%s\" (detected at line: %d)" % (
                        self.fn, line))

            if self._peek() == "\"" and not raw.endswith("\\\\") and raw[-1] == "\\":
                raw += self._get()

        # Add 1 to index to skip \" character
        self._get()

        self.toks.append(Token(TokenType.STR, "\"%s\"" % raw, raw.encode(
            "raw_unicode_escape").decode("unicode_escape"), self.fn, line))

    def char(self) -> None:
        line = self.line

        # Add 1 to index to skip \' character
        self._get()

        raw = self._get()

        if raw == "\'":
            Croak(
                ErrorType.Syntax,
                "char must contain a value in file \"%s\" (detected at line: %d)" % (
                    self.fn, line
                )
            )
        elif raw == "\\":
            while self._peek() != "\'":
                raw += self._peek()

                if not self._get():
                    Croak(
                        ErrorType.Syntax,
                        "unterminated char literal in file \"%s\" (detected at line: %d)" % (
                            self.fn, line
                        )
                    )

            raw = raw.encode("raw_unicode_escape").decode("unicode_escape")

        if len(raw) != 1 or self._get() != "\'":
            Croak(
                ErrorType.Syntax,
                "char must be 1 character long, in file \"%s\" (detected at line: %d)" % (
                    self.fn, line
                )
            )

        self.toks.append(Token(TokenType.INT, raw, ord(raw),
                         self.fn, line))

    def comment(self) -> None:
        self._get()
        
        next_ch = self._get()

        if next_ch == "/":
            while (cur := self._get()) != "\n":
                if not cur:
                    break
            return
        elif next_ch == "*":
            while (cur := self._get()):
                if cur + self._peek() == "*/":
                    break
            self._get()
            return

        Croak(ErrorType.Syntax, "expected // or /* */ comment")

    def include_file(self) -> None:
        self.skip_whitespace()

        systemfile = self._peek() == "\'"

        if self._get() not in "\'\"":
            Croak(
                ErrorType.Syntax,
                "must include a string or system library in file \"%s\" (detected at line: %d)" % (
                    self.fn, self.line
                )
            )

        include_filename = self._get()

        while (self._peek() != "\"" and not systemfile) or (self._peek() != "\'" and systemfile):
            include_filename += self._peek()

            if not self._get():
                Croak(
                    ErrorType.Syntax,
                    "unterminated string literal in file \"%s\" (detected at line: %d)" % (
                        self.fn, self.line
                    )
                )

        # Add 1 to index to skip \" or \' character
        self._get()

        if systemfile:
            include_filename = PANG_SYS + include_filename

        # skip as has already been included
        if include_filename in self.includes:
            return
        
        new_toks = Lexer(open(include_filename, "r",
                         encoding="utf-8").read(), include_filename)
        new_toks.includes = self.includes
        new_toks.includes.add(self.fn)
        new_toks.get_tokens_without_macros()

        self.includes.update(new_toks.includes)
        self.includes.add(include_filename)

        self.toks += new_toks.toks

    def call(self) -> None:
        if not self.lexing_call:
            line = self.line
            self.lexing_call = True

            self.skip_whitespace()

            if self._peek() not in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                Croak(
                    ErrorType.Syntax,
                    "expected identifier, got %s\nDetected at line %d in file \"%s\"" % (
                        self.get_error_type(), line, self.fn
                    ))
            
            self.identifier()
            self.toks[-1] = Token(TokenType.CALL, "call",
                                  self.toks[-1].value, self.fn, self.toks[-1].ln)
            self.lexing_call = False
            return

        Croak(ErrorType.Syntax, "cannot call keyword 'call'")

    def identifier(self) -> None:
        line = self.line
        raw = self._get()

        if raw == "r" and self._peek() == "\"":
            self.raw_string()
            return

        while (cur := self._get()) in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            raw += cur

            if not cur:
                break
        
        self.line = line
        self.index -= 1

        if raw in keyword_map:
            self.toks.append(Token(keyword_map.get(raw), raw,
                             raw, self.fn, line))
        elif raw == "call":
            self.call()
        elif raw == "include":
            self.include_file()
        else:
            self.toks.append(Token(TokenType.ID, raw, raw,
                             self.fn, line))

    def get_tokens_without_macros(self) -> None:
        current = ""
        while self._peek():
            end = False
            while self._peek() in " \t\n":
                self._get()

                if not self._peek():
                    end = True
                    break

            if end:
                break

            current = self._peek()

            if current in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                self.identifier()
            elif current in "+-1234567890":
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
                Croak(
                    ErrorType.Syntax,
                    "invalid character found in file \"%s\" (detected at line: %d): %c" % (
                        self.fn, self.line, current
                    )
                )

    def get_tokens(self) -> None:
        self.get_tokens_without_macros()
        
        macro_added_toks = []
        macro = False
        macro_name = False
        skip_end = 0
        cur_name = ""
        cur_tok = Token()
        cur_toks = []
        macros = {
            "__VERSION__": [Token(TokenType.INT, str(PANG_VER), int(PANG_VER))],
            "__BASE_FILE__": [Token(TokenType.STR, self.fn, realpath(self.fn))],
            "__TIME__": [Token(TokenType.STR, COMPILE_TIME, COMPILE_TIME)],
            "__DATE__": [Token(TokenType.STR, COMPILE_DATE, COMPILE_DATE)],
            "__ARCH__": [Token(TokenType.STR, ARCHITECTURE, ARCHITECTURE)],
        }
        
        __ENUM__ = 0

        # Add all definitions of macros to the macros variable
        for tok in self.toks:
            if tok.typ in (TokenType.WHILE, TokenType.IF):
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
                    if tok.value == "__ENUM__":
                        cur_toks.append(tok) # keep it the same token so it can be expanded with the rest
                        continue
                    elif tok.value == "__LINE__":
                        cur_toks.append(Token(TokenType.INT, str(tok.ln), tok.ln, tok.filename, tok.ln))
                        continue
                    elif tok.value == "__FILE__":
                        cur_toks.append(Token(TokenType.STR, tok.filename, realpath(tok.filename), tok.filename, tok.ln))
                        continue
                    
                    if tok.value not in macros:
                        Croak(
                            ErrorType.Name,
                            "undefined reference to identifier %s in file \"%s\" (detected at line: %d)" % (
                                tok.raw, tok.filename, tok.ln
                            )
                        )
                    
                    for macro_tok in macros[tok.value]:
                        cur_toks.append(Token(macro_tok.typ, macro_tok.raw,
                                              macro_tok.value, macro_tok.filename,
                                              macro_tok.ln))

        skip_macro = False
        skip_end = 0

        for tok in self.toks:
            if skip_macro:
                if tok.typ in (TokenType.WHILE, TokenType.IF):
                    skip_end += 1
                elif tok.typ == TokenType.END and not skip_end:
                    skip_macro = False
                elif tok.typ == TokenType.END and skip_end:
                    skip_end -= 1

                continue

            if tok.typ == TokenType.ID:
                # Add more predefined macros
                if tok.value == "__ENUM__":
                    macro_added_toks.append(Token(TokenType.INT, str(__ENUM__), __ENUM__,
                                                  tok.filename, tok.ln))
                    __ENUM__ += 1
                    continue
                elif tok.value == "__LINE__":
                    macro_added_toks.append(Token(TokenType.INT, str(tok.ln), tok.ln,
                                                  tok.filename, tok.ln))
                    continue
                elif tok.value == "__FILE__":
                    macro_added_toks.append(Token(TokenType.STR, tok.filename, realpath(tok.filename), tok.filename, tok.ln))
                    continue
                
                if tok.value not in macros:
                    Croak(
                        ErrorType.Name,
                        "undefined reference to identifier %s in file \"%s\" (detected at line: %d)" % (
                            tok.raw, tok.filename, tok.ln
                        )
                    )

                for macro_tok in macros[tok.value]:
                    if macro_tok.typ == TokenType.CALL:
                        self.calls.add(macro_tok.value)
                    
                    # Add predefined macros
                    if macro_tok.typ == TokenType.ID:
                        if macro_tok.value == "__ENUM__":
                            macro_added_toks.append(Token(TokenType.INT, str(__ENUM__), __ENUM__,
                                                    macro_tok.filename, macro_tok.ln))
                            __ENUM__ += 1
                        continue

                    macro_added_toks.append(Token(macro_tok.typ, macro_tok.raw,
                                              macro_tok.value, tok.filename,
                                              tok.ln))
            elif tok.typ == TokenType.MACRO:
                # skip macros as they have already been added
                skip_macro = True
            elif tok.typ == TokenType.CALL:
                self.calls.add(tok.value)
                macro_added_toks.append(tok)
            else:
                macro_added_toks.append(tok)

        self.toks = macro_added_toks
        
        if DEBUG:
            print("\n".join([str(tok.typ) for tok in self.toks]))
