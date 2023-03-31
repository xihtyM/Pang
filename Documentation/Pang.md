# Pang documentation
Pang is a stack-based, interpreted and compiled programming language.

## Arguments ##
* `-c` or `-com`
    - Compilation mode.
* `-o outname`
    - Output file name for compilation.
* `-S`
    - Generates assembly code.
* `-O1`, `-O2` or `-O3`
    - Optimises code.
* `-C` or `-cpp`
    - Generates C++ code.
* `-args`
    - Sets all arguments after the -args flag in interpreting mode.
* `-t`
    - Keep temporary files
* `-g`
    - Enable debugging with gdb (pair with `-t` for easier functionality)

## Command syntax ##
* `pang.py filename.pang arguments`
    - Interpretation mode, arguments (including filename.pang) are pushed to stack.
* `pang.py filename.pang -args arguments`
    - Interpretation mode, arguments are pushed to the stack.
* `pang.py filename.pang -c`
    - Compilation mode, make sure `-c` flag is before all other compilation-specific flags.
    - You can put any compilation argument after `-c`, it is recommended to include `-O` as that optimises your code.
## How the stack works ##
- In pang, the stack is a list of signed 64-bit integers. (In interpreted mode they are bignums however.)
- The stack follows the last in first out rule, meaning to pop the stack would remove the last pushed item.
- Pang does not support floating point numbers and there are no types in pang other than integers.
- Whenever an item is refferred to, it just means an integer that is on the stack.

## Data types ##
As pang is stack-based, every item on the stack is an integer, this means data types such as floats and strings are not supported. However, that doesn't mean that they cannot be made - here is a list of all supported data types in pang:

### Strings/1d arrays ###
1d arrays are an extremely common data type and necessary for almost any programming language. This is how pang implements them:
- 1d arrays are a group of integers appended to the stack.
- 1d arrays are to be suffixed by the length of the array.
- Strings are a type of 1d array, where each character is appended with the length of the string as the suffix.

## argv and argc in pang ##
Pang supports command-line arguments. This is done by appending the args into the stack as follows:
- argv[n] is appended as a string in pang (refer above).
- argc is appended after all arguments.
- this is the same as a standard 3d array in pang.

## Pang keywords ##
Pang has currently got 23 reserved keywords, all of them are listed below with descriptions.
* `xor`
    - Pops 2 items from the end of the stack. Performs a bitwise exclusive or operation on them, pushing the result.
* `bor`
    - Pops 2 items from the end of the stack. Performs a bitwise or operation on them, pushing the result.
* `band`
    - Pops 2 items from the end of the stack. Performs a bitwise and operation on them, pushing the result.
* `bnot`
    - Pops 2 items from the end of the stack. Inverts each bit value, pushing the result.
    For example, if the value was 1101, it would change to 0010.
* `lshift`
    - Pops 1 item (n) from the end of the stack, and bitshifts the last item on the stack left n times.
* `rshift`
    - Pops 1 item (n) from the end of the stack, and bitshifts the last item on the stack right n times.
* `if`
    - Pops 1 item from the end of the stack, if the value is 0 (false), skips until the if block is ended, otherwise (if it is non-zero) continue.
* `add`
    - Pops 2 items from the end of the stack. Adds them together, pushing the result.
* `sub`
    - Pops 2 items from the end of the stack. Subtracting the first popped item from the second popped item, pushing the result.
* `mul`
    - Pops 2 items from the end of the stack. Multiplying them together, pushing the result.
* `dup`
    - Duplicates the last item on the stack.
* `buf`
    - Pops 1 item from the end of the stack. If the value is 1, appends the unicode value of the last item on the stack to the output buffer. If the value is 0, then appends the integer value of the last item on the stack to the output buffer. Raises an error if the item is not 0 or 1.
* `swap`
    - Swaps the last two items on the stack.
* `back`
    - Sends the last item on the stack, to the 0th index (back of the stack).
* `front`
    - Sends the first item (0th index), to the front of the stack (last item on the stack).
* `mul`
    - Pops 2 items from the end of the stack. Multiplying them together, pushing the result.
* `while`
    - Pops 1 item from the end of the stack each iteration, if the value is 0 (false), skips until the while block is ended, otherwise (if it is non-zero) continue. Repeats this process until the popped value is false.
* `divmod`
    - Pops the numerator and pops the denominator from the front of the stack in that order. Pushes the floordiv and remainder of the numerator/denominator.
* `syscall`
    - Pops 1 item from the stack, checks for the syscall number and executes a specific syscall based off the number (see syscalls for info about all the syscalls in pang).
* `do`
    - Block that must be ended.
* `end`
    - Ends `do` block or `macro`.
* `macro`
    - C-style macro (takes arguments pushed onto the stack). Expands with the preprocessor.
* `include`
    - C-style include. `"file.pang"` includes file.pang in the current working directory, `'file.pang'` includes file.pang from the system libraries (installed in %pang%).
