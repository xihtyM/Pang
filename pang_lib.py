if __name__ == "__main__":
    print("Error: pang_lib cannot be ran by itself.")
    exit(1)

import sys

# ver < 3.6 is deprecated
if sys.version_info < (3, 6):
    print("DepreciationError: Please install a python version greater than 3.5.")
    exit(1)

from time import perf_counter, sleep
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
import os

## Pang constants ##

PANG_SYS = None# for testing purposes os.getenv("pang")

if PANG_SYS is None:
    PANG_SYS = os.path.dirname(os.path.realpath(__file__))

PANG_SYS += "\\"

NEWLINE_CALLS = [
    0x005, 0x006,
    0x007, 0x008,
    0x012,
]

# Change limit for I/O operations in interpreted mode.
# If there is no limit (in some versions of python).
# Then AttributeError will be raised, nothing is needed to be done.
try:
    sys.set_int_max_str_digits(2147483647)
except AttributeError:
    pass

class ErrorType(Enum):
    """ Used when printing errors with Croak(). """
    Name = auto()
    File = auto()
    Stack = auto()
    Syntax = auto()
    Command = auto()
    Compile = auto()
    IntegerTooLarge = auto()

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

    # Preprocessor
    MACRO = auto()
    END = auto()
    
    # Control flow
    IF = auto()
    WHILE = auto()

    # Push to stack
    INT = auto()
    STR = auto()

    # Arithmetic
    SUB = auto()
    ADD = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()

    # Stack operations
    DUP = auto()
    SWAP = auto()
    DROP = auto()

    # Conditionals
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN = auto()
    SMALLER_THAN = auto()

    # Edit output buffer
    BUF = auto()
    
    # Interaction with c functions or windows api
    CALL = auto()

    # Pointers
    APPLY = auto()
    QUOTE = auto()

    # For undefined tokens
    NONE = auto()


@dataclass
class Token():
    typ: TokenType = TokenType.NONE
    raw: str = ""
    value: Union[str, int] = ""
    filename: str = ""
    ln: int = -1


# Use keyword_map for checking when the identifier is a keyword
# or for getting the correct type of the keyword, e.g:
# token = Token(typ=keyword_map[raw_id_str], ...)
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
    "div": TokenType.DIV,
    "mod": TokenType.MOD,
    "drop": TokenType.DROP,
    "swap": TokenType.SWAP,
    "while": TokenType.WHILE,
    "apply": TokenType.APPLY,
    "quote": TokenType.QUOTE,
}


def Croak(err_typ: ErrorType, *msg: str):
    """ Use Croak() for every pang error. """
    print("%sError: " % err_typ._name_, *msg, sep="")
    exit(1)
