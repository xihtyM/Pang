from pang_lib import *

if __name__ == "__main__":
    Croak("lexer cannot be ran by itself.")

class Lexer():
    def __init__(self, src: str, filename: str = "N/A") -> None:
        self.index = 0
        self.fn = filename
        self.raw = src
        self.size = len(src)
        self.toks: list[Token] = []
        self.includes: list[str] = []
        
        self.assembly = {}
        self.labels = {}

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
        raw = self._get()

        while self._peek() and self._peek() in "0123456789":
            raw += self._get()
        
        # hex
        if raw in ("0", "-0", "+0") and self._peek() in ("x", "X"):
            raw += self._get()
            
            while self._peek() and self._peek() in "0123456789abcdefABCDEF":
                raw += self._get()
            
            self.toks.append(Token(
                TokenType.INT, raw, int(raw, 16),
                self.fn, self.line(start)))
                
            return
        
        # octal
        if raw in ("0", "-0", "+0") and self._peek() in ("o", "O"):
            raw += self._get()
            
            while self._peek() and self._peek() in "01234567":
                raw += self._get()
            
            self.toks.append(Token(
                TokenType.INT, raw, int(raw, 8),
                self.fn, self.line(start)))

            return
        
        # float/double
        if self._peek() == ".":
            raw += self._get()
            
            while self._peek() and self._peek() in "0123456789":
                raw += self._get()
        
            self.toks.append(Token(
                TokenType.DOUBLE, raw, raw,
                self.fn, self.line(start)))

            return
            

        if raw.startswith(("0", "-0", "+0")) and len(raw) > 1:
            Croak(
                ErrorType.Syntax,
                "leading zeros in integer literals are prohibited; ",
                "use 0o for octal integers instead.\n\n",
                "Found in file \"%s\" (detected at line: %d)." % (
                    self.fn, self.line(start)))

        self.toks.append(Token(
            TokenType.INT, raw, int(raw),
            self.fn, self.line(start)))

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
                    "unterminated string literal: %s\n\n" % raw,
                    "Found in file \"%s\" (detected at line: %d)" % (
                        self.fn, self.line(start)))

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
                    "unterminated string literal: %s\n\n" % raw,
                    "Found in file \"%s\" (detected at line: %d)" % (
                        self.fn, self.line(start)))

            
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
        self.assembly.update(new_toks.assembly)
        self.toks += new_toks.toks

    def asm(self) -> None:
        while self._peek() in " \n\t":
            if not self._get():
                Croak(ErrorType.Syntax, "asm must have an identifier")
        
        self.identifier()
        
        identifier = self.toks.pop()
        
        if identifier.typ != TokenType.ID:
            Croak(ErrorType.Syntax, "asm must have an identifier")
        
        name = "__" + identifier.value + "_def_asm"
        
        self.assembly[name] = ""
        
        while self._peek() in " \n\t":
            if not self._get():
                Croak(ErrorType.Syntax, "asm must have an assembly string")
        
        if self._get() != "\"":
            Croak(ErrorType.Syntax, "asm must have an assembly string")
        
        while self._peek() != "\"":
            if not self._peek():
                Croak(ErrorType.Syntax, "assembly string must be terminated")
            
            self.assembly[name] += self._get()
        
        self.assembly[name] = self.assembly[name].strip("\n")
        self.assembly[name] += "\n    ret"

        self._get()
    
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
        
        if raw[0] == "$":
            self.toks.append(Token(
                TokenType.LABEL,
                raw[1:],
                raw[1:],
                self.fn, 
                self.line(start)))
            return
        
        if raw == "macro":
            self.toks.append(Token(TokenType.MACRO, raw, raw, self.fn, self.line(start)))
        elif raw == "end":
            self.toks.append(Token(TokenType.END, raw, raw, self.fn, self.line(start)))
        elif raw == "include":
            self.include_file()
        elif raw == "asm":
            self.asm()
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
            
            if current in "$_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
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
                        self.fn, self.line(self.index), current
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
        macros = {}

        # Add macros
        for tok in self.toks:
            if tok.typ == TokenType.LABEL:
                if tok.value in macros:
                    Croak(
                        ErrorType.Syntax,
                        "multiple definitions for identifier %s, found in file \"%s\" (at line %d)" % (
                            tok.raw, tok.filename, tok.ln
                    ))
                
                # set it so that there is an error on multiple definitions
                macros[tok.value] = []
            
            if tok.typ == TokenType.MACRO:
                if macro:
                    Croak(
                        ErrorType.Syntax,
                        "macro cannot define a macro in itself, found in file \"%s\" (at line %d)" % (
                            tok.filename, tok.ln
                    ))

                macro_name = True
                continue
            
            if macro_name:
                if tok.typ != TokenType.ID:
                    Croak(
                        ErrorType.Syntax,
                        "macro name must be an identifier, found in file \"%s\" (at line %d)" % (
                            tok.filename, tok.ln
                    ))
                
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
                        ))
                    
                    macros[cur_name] = cur_toks
                    
                    cur_toks = []
                    continue
                
                if tok.typ == TokenType.END and skip_end:
                    skip_end -= 1
                
                if tok.typ != TokenType.ID:
                    cur_toks.append(tok)
                else:
                    asm_name = "__" + tok.value + "_def_asm"
                    
                    if tok.value not in macros and asm_name not in self.assembly:
                        Croak(
                            ErrorType.Name,
                            "undefined reference to identifier %s in file \"%s\" (detected at line: %d)" % (
                                tok.raw, tok.filename, tok.ln
                        ))
                    
                    if tok.value in macros and asm_name in self.assembly:
                        Croak(
                            ErrorType.Compile,
                            "redefinition of identifier %s in file \"%s\" (detected at line: %d)" % (
                            tok.raw, tok.filename, tok.ln
                        ))
                    
                    if asm_name in self.assembly:
                        tok.value = asm_name
                        cur_toks.append(tok)
                        continue
                    
                    for macro_tok in macros[tok.value]:#[0]:
                        cur_toks.append(macro_tok)
        
        skip_macro = False

        for tok in self.toks:
            if skip_macro:
                if tok.typ == TokenType.END:
                    skip_macro = False
                
                continue
            
            if tok.typ == TokenType.LABEL:
                self.labels[tok.value] = len(macro_added_toks)
                continue
                
            if tok.typ == TokenType.ID:
                asm_name = "__" + tok.value + "_def_asm"
                if not tok.value in macros and asm_name not in self.assembly:
                    Croak(
                        ErrorType.Name,
                        "undefined reference to identifier %s in file \"%s\" (detected at line: %d)" % (
                            tok.raw, tok.filename, tok.ln
                    ))

                if tok.value in macros and asm_name in self.assembly:
                    Croak(
                        ErrorType.Compile,
                        "redefinition of identifier %s in file \"%s\" (detected at line: %d)" % (
                        tok.raw, tok.filename, tok.ln
                    ))
                
                if asm_name in self.assembly:
                    tok.value = asm_name
                    macro_added_toks.append(tok)
                    continue
                
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
