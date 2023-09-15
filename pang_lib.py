if __name__ == "__main__":
    print("Error: pang_lib cannot be ran by itself.")
    exit(1)

import sys

# ver < 3.8 is deprecated
if sys.version_info < (3, 8):
    print("DepreciationError: Please install a python version greater than 3.7.")
    exit(1)

from time import perf_counter, sleep, strftime
from platform import machine
from datetime import date
from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
import os


realpath = os.path.realpath

## Pang constants ##

DEBUG = False

date_obj = date.today()

months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

COMPILE_TIME = strftime("%H:%M:%S")
COMPILE_DATE = "%s %s%d %d" % (months[date_obj.month], (" " if date_obj.day < 10 else ""),
                               date_obj.day, date_obj.year)

ARCHITECTURE = machine()

PANG_SYS = None #os.path.join(os.getenv("pang"), "lib") # for testing purposes use None

if PANG_SYS is None:
    PANG_SYS = os.path.join(os.path.dirname(realpath(__file__)), "lib")

PANG_SYS += os.path.sep

NEWLINE_CALLS = [
    0x005, 0x006,
    0x007, 0x008,
    0x012,
]

PANG_VER = 3.0

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
    NotImplemented = auto()
    IntegerTooLarge = auto()

class TokenType(Enum):
    # Identifiers
    ID = auto()

    # Bitwise operators
    EXCOR = auto() #
    BITOR = auto() #
    BITAND = auto()
    BITNOT = auto()
    LSHIFT = auto()
    RSHIFT = auto()

    # Preprocessor / control flow
    MACRO = auto()
    
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    
    END = auto()
    

    # Push to stack
    INT = auto()
    STR = auto()

    # Arithmetic
    SUB = auto()
    ADD = auto()
    MUL = auto()
    DIV = auto() #
    MOD = auto() #
    IADD = auto()
    ISUB = auto()
    IMUL = auto()
    IDIV = auto() #
    IMOD = auto() #

    # Stack operations
    DUP = auto()
    SWAP = auto()
    DROP = auto()

    # Conditionals
    EQUAL = auto() #
    NOT_EQUAL = auto() #
    GREATER_THAN = auto() #
    SMALLER_THAN = auto() #
    
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
    value: str | int | list = ""
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

    # Branches
    "if": TokenType.IF,
    "do": TokenType.DO,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    
    # Normal tokens
    "add": TokenType.ADD,
    "sub": TokenType.SUB,
    "mul": TokenType.MUL,
    "dup": TokenType.DUP,
    "div": TokenType.DIV,
    "mod": TokenType.MOD,
    "iadd": TokenType.IADD,
    "isub": TokenType.ISUB,
    "imul": TokenType.IMUL,
    "idiv": TokenType.IDIV,
    "imod": TokenType.IMOD,
    "drop": TokenType.DROP,
    "swap": TokenType.SWAP,
    "apply": TokenType.APPLY,
    "quote": TokenType.QUOTE,
    
    "macro": TokenType.MACRO,
    "end": TokenType.END,
}


WIN32_apply_sizes = {
    1: "movzx   rax, byte [rax]",
    2: "movzx   rax, word [rax]",
    4: "mov     eax, dword [rax]",
    8: "mov     rax, qword [rax]",
}


def Croak(err_typ: ErrorType, *msg: str):
    """ Use Croak() for every pang error. """
    print("%sError: " % err_typ._name_, *msg, sep="")
    exit(1)
