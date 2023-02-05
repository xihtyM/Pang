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
    - __Functions__:
        - `not`: Performs a logical not gate on the last item on stack.
        - `chsin`: Changes the sign of the last item on stack.
        - `else`: Performs `not` and then opens an if statement.
        - `clear`: Removes all items on stack.
        - `drop`: Drops last item on stack.

        - `bufi`: Appends the integer value of the last item on the stack to the output buffer.
        - `bufc`: Appends the unicode value of the last item on the stack to the output buffer.
        - `bufs`: Appends the last string on the stack to the output buffer.

        - `fputi`: Prints the last string on stack taking the last item on stack as the file descriptor.
        - `fputc`: Prints the last char on stack taking the last item on stack as the file descriptor.
        - `fputs`: Prints the last int on stack taking the last item on stack as the file descriptor.

        - `puti`: Prints the last integer on stack to stdout.
        - `putc`: Prints the last char on stack to stdout.
        - `puts`: Prints the last string on stack to stdout.
        - `putln`: Prints the last string on stack to stdout with a newline suffix.
        - `eputs`: Prints last string on stack to stderr with prefix "Error: " in red, exits with error code 1.

        - `cls`: Clears standard output with ansi escape code (not supported on some terminals).

        - `fread`: Reads everything from file descriptor and appends it as a string to stack, saving the file descriptor as the last item on the stack.
        - `freadln`: Reads the first line from file descriptor and appends it as a string to stack, saving the file descriptor as the last item on the stack.
        - `input`: Gets input from stdin appending as a string to stack.

        - `range`: Pushes 0..n-1 to the stack, where n is the last item on stack.
        - `for`: Performs `range` and then opens a while loop.
        - `div`: Divides the last two items on stack and appends result.
        - `mod`: Calculates the modulo the last two items on stack and appends result.
        - `over`: Swaps 3rd last and last item on stack.
        
