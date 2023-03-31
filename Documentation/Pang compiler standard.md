# The standard for pang compilers. #

This will be split into x sections, below is a glossary for each section:
1. Keywords
2. The stack and memory
3. Data types
4. Pointers
5. Preprocessor macros
6. Exception handling
7. Optimisations
8. Pang *calls*

---
## 1: Pang keywords ##
> Section not written as of yet

## 2: The stack and memory ##

#### 2.1: The `pang_int` structure ####
**2.1.1**: A `pang_int` is a structure containing the following:
* **2.1.1.1**: A value declaring if the `pang_int` is null or points to null. It will be referred to as `is_null` from now on.
* **2.1.1.2**: A value declaring if the `pang_int` is a pointer. It will be referred to as `is_ptr` from now on.
* **2.1.1.3**: The value of the `pang_int` - must be an `intmax_t`. It will be referred to as `real` from now on.
**2.1.2**: The `pang_null` constant:
* **2.1.2.1**: Real must be 0, is_ptr must be false, and is_null must be true.

#### 2.2: Memory ####
* **2.2.1**: The memory must be an array of `pang_int`s.
* **2.2.2**: The zeroth index of the memory must be `pang_null` (refer to section: 2.1.2).
* **2.2.3**: The memory must contain at least 1,024 `pang_int`s, and can contain up to `UINT16_MAX - 1`.

#### 2.3: The stack ####
* **2.3.1**: The stack is an array of `uint16_t`s.
* **2.3.2**: Each item in the stack is a *pointer* to an address in the memory.
* **2.3.3**: The stack must be expandable, unlike the memory.
* **2.3.4**: The stack must include a stack pointer, which points to the top of memory.
* **2.3.5**: Pushing to the stack involves the following process:
 - **2.3.5.1**: The value will be placed at `memory[stack pointer:stack pointer + length(value)]`. See length[^1].
 - **2.3.5.2**: The stack pointer will be pushed to the stack (marking the start of the value).
 - **2.3.5.3**: The stack pointer will be incremented by `length(value)`.
* **2.3.6**: Dropping from the stack involves the following process:
 - **2.3.6.1**: The stack pointer will be set to the last value on the stack.
 - **2.3.6.2**: The last value on the stack gets popped.

## 3: Data types ##
> Section not written as of yet

## 4: Pointers ##
> Section not written as of yet

## 5: Preprocessor macros ##
> Section not written as of yet

## 6: Exception handling ##
* **6.1**: Pang is not required to handle errors in any way other than exiting the program when an error occurs.
* **6.2**: 0 must be returned if the user does not exit in the program and the program has no faults.
* **6.3**: Full list of the pang errors that can occur and their codes:
 - **6.3.1**: The `NULL_APPLY` error is raised when the programmer tries to dereference a null pointer. Error code `16` (`0x10`).
 - **6.3.2**: The `NULL_QUOTE` error is raised when the programmer tries to reference null (real null, not a pointer). Error code `18` (`0x12`).
 - **6.3.3**: The `NULL_MOVE` error is raised when the programmer tries to move null (real null, not a pointer) around on the stack, null must remain at position 0 at all times. Error code `20` (`0x14`).
 - **6.3.4**: The `APPLY_NON_POINTER` error is raised when the programmer tries to dereference a non-pointer value. Error code `22` (`0x16`).
 - **6.3.5**: The `QUOTE_POINTER` error is raised when the programmer tries to reference a pointer (pointers may point to other pointers, but cannot point to two objects by itself). Error code `24` (`0x18`).
* **6.4**: Each compiler may define their own errors, these may have exit codes in the range of 192-255.

## 7: Optimisations ##
> Section not written as of yet

## 8: Pang *calls* ##
> Section not written as of yet

[^1]: `length` - the length of the value represented in memory. For example `"Hello, World!"` has a length of 14 (including null terminator), or `50` has a length of 1 as it is just an integer.
