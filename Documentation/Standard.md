# Pang standard documentation
Pang has a standard which is basically its "end-goal".

The pang standard is sorted into the following categories:
- Libraries
- OS functionality
- Basic functionality

## Libraries ##
The current standard libraries are:

> Implemented
* `std.pang`
    - The main standard library including most of pangs functionality.

> Unimplemented
* `win.pang`
    - Standard library providing interaction with the Windows API.
* `unix.pang`
    - Standard library providing unix/posix syscalls.

### Library macros ###
All macros provided by standard libraries:
* `std.pang`
    - __Constants__:
        - `false`: Binary false value.
        - `true`: Binary true value.

        - `stdin`: Standard input, expands to 0.
        - `stdout`: Standard output, expands to 1.
        - `stderr`: Standard error output, expands to 2.

        - `_buf_int`: Expands to 0.
        - `_buf_char`: Expands to 1.

        - `readall`: Expands to -1.
        - `readln`: Expands to 0.
    - __Macros__:
        * Booleans:
            - `bool`: Changes the last item on the stack to 1 if it is not 0. [Usage](/Usage/bool.pang)

        * Logical operations or gates:
            - `not`: Performs a logical not gate on the last item on stack. [Usage](/Usage/not.pang)
            - `and`: Performs a logical and gate on the last two items on stack. [Usage](/Usage/and.pang)
            - `or`: Performs a logical or gate on the last two items on stack. [Usage](/Usage/or.pang)
            - `chsin`: Changes the sign of the last item on stack. [Usage](/Usage/chsin.pang)
            - `else`: Performs `not` and then opens an if statement. [Usage](/Usage/else.pang)

        * Stack operations:
            - `clear`: Removes all items on stack. [Usage](/Usage/clear.pang)
            - `drop`: Drops last item on stack. [Usage](/Usage/drop.pang)
            - `div`: Divides the last two items on stack and appends result. [Usage](/Usage/div.pang)
            - `mod`: Calculates the modulo the last two items on stack and appends result. [Usage](/Usage/mod.pang)
            - `over`: Swaps 3rd last and last item on stack. [Usage](/Usage/over.pang)

        * Output:
            - `bufi`: Appends the integer value of the last item on the stack to the output buffer. [Usage](/Usage/bufi.pang)
            - `bufc`: Appends the unicode value of the last item on the stack to the output buffer. [Usage](/Usage/bufc.pang)
            - `bufs`: Appends the last string on the stack to the output buffer. [Usage](/Usage/bufs.pang)

            - `fputi`: Prints the last string on stack taking the last item on stack as the file descriptor. [Usage](/Usage/fputi.pang)
            - `fputc`: Prints the last char on stack taking the last item on stack as the file descriptor. [Usage](/Usage/fputc.pang)
            - `fputs`: Prints the last int on stack taking the last item on stack as the file descriptor. [Usage](/Usage/fputs.pang)

            - `puti`: Prints the last integer on stack to stdout. [Usage](/Usage/puti.pang)
            - `putc`: Prints the last char on stack to stdout. [Usage](/Usage/putc.pang)
            - `puts`: Prints the last string on stack to stdout. [Usage](/Usage/puts.pang)
            - `putln`: Prints the last string on stack to stdout with a newline suffix. [Usage](/Usage/putln.pang)
            - `eputs`: Prints last string on stack to stderr with prefix "Error: " in red, exits with error code 1. [Usage](/Usage/eputs.pang)

            - `cls`: Clears standard output with ansi escape code (not supported on some terminals). [Usage](/Usage/cls.pang)

        * Input:
            - `fread`: Reads everything from file descriptor and appends it as a string to stack, saving the file descriptor as the  last item on the stack. [Usage](/Usage/fread.pang)
            - `freadln`: Reads the first line from file descriptor and appends it as a string to stack, saving the file descriptor  as the last item on the stack. [Usage](/Usage/freadln.pang)
            - `input`: Gets input from stdin appending as a string to stack. [Usage](/Usage/input.pang) 

        * Functions:
            - `range`: Pushes 0..n-1 to the stack, where n is the last item on stack. [Usage](/Usage/range.pang) 
            - `for`: Performs `range` and then opens a while loop. [Usage](/Usage/for.pang) 
            - `array_3d_to_ptr`: Takes a 3d array and appends a pointer to a 2d array at the last item's index. [Usage](/Usage/array_3d_to_ptr.pang)
            - `append_2d_from_ptr`: Takes a pointer to a 2d array and appends it to front of stack. [Usage](/Usage/append_2d_from_ptr.pang)
            - `array_3d_subscript`: Takes a 3d array and appends a 2d array to front of stack at index n. [Usage](/Usage/array_3d_subscript.pang)
