## Pang documentation
Pang is a stack-based, interpreted and compiled programming language.

# How the stack works
- In pang, the stack is a list of signed 64-bit integers. (In interpreted mode they are bignums however.)
- The stack follows the last in first out rule, meaning to pop the stack would remove the last pushed item.
- Pang does not support floating point numbers and there are no types in pang other than integers.
- Whenever an item is refferred to, it just means an integer that is on the stack.

# Pang keywords
Pang has currently got 18 reserved keywords, all of them are listed below with descriptions.
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