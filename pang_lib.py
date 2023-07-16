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

T_READLINE = 0
T_READALL = -1

MAX_PREALLOC = 1024
PRE_ARGV_ALLOCATE = 32

PANG_SYS = os.getenv("pang")

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

    # Calls
    CALL = auto()

    # Pointers
    APPLY = auto()
    QUOTE = auto()

    # For undefined tokens
    NONE = auto()

## TODO: REWRITE
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
    "swap": TokenType.SWAP,
    "back": TokenType.BACK,
    "while": TokenType.WHILE,
    "front": TokenType.FRONT,
    "divmod": TokenType.DIVMOD,
    "apply": TokenType.APPLY,
    "quote": TokenType.QUOTE,
    "call": TokenType.CALL,
}

def Croak(err_typ: ErrorType, *msg: str):
    """ Use Croak() for every pang error. """
    print("%sError: " % err_typ._name_, *msg, sep="")
    exit(1)

def find_end(index: int, ops: list[Token]) -> int:
    """ Find the end of a selection block/macro. """
    skip_end = 0
    end = index
    size = len(ops) - 1

    while end < size:
        end += 1

        if ops[end].typ == TokenType.DO:
            skip_end += 1
        
        if ops[end].typ == TokenType.END:
            if not skip_end:
                return end

            skip_end -= 1
    
    Croak(ErrorType.Syntax, "expected end (at line %d)" % (ops[index].ln))
