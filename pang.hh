#pragma once

#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <utility>

/// Use instead of namespace pang after this.
#define START_NAMESPACE_PANG namespace pang {
#define END_NAMSEPACE_PANG }

/// Use before struct/typedef/function definitions to hint
/// as to what type of function it is.

#define pang_type typedef
#define pang_keyword
#define pang_call(type) type
#define pang_func(type) type
#define pang_inline(type) inline type

/// Section 2.2.3:
/// The amount of pang::Int's the memory can store
/// inside struct Stack.
#define PANG_SIZE 0x0fff

/// Section 6.3:
/// All pang errors that can be thrown.
/// These appear as the exit code to a program
/// and can be used to debug code.

#define PANG_NULL_APPLY        0x10
#define PANG_NULL_QUOTE        0x12
#define PANG_NULL_MOVE         0x14
#define PANG_APPLY_NON_POINTER 0x16
#define PANG_QUOTE_POINTER     0x18

#if (defined(WIN32) || defined(_WIN32) || defined(__WIN32)) && !defined(__CYGWIN__)
#define ON_WINDOWS
#include <locale.h> // setlocale(LC_ALL, ".utf-8");
#include <windows.h> // windows api
#else
#include <unistd.h> // unix syscalls
#endif

START_NAMESPACE_PANG

/// Pang data types/structures:

/// Use pang_address as it is more explicit than uint16_t
/// and easier to change for later.
pang_type uint16_t pang_address;

/// pang_int (section 2.1)
pang_type struct Int
{
    bool is_null;
    bool is_ptr;
    intmax_t real;
} Int;

pang_type struct Stack
{
    Int mem[PANG_SIZE];
    std::vector<pang_address> stack;
    pang_address stack_pointer;
} Stack;

/// Section 2.1.2
#define pang_null \
    (Int{true, false, 0})

/// Initilizers for each pang structure/type.

#define to_pang_int(imax) \
    (Int{false, false, imax})

pang_inline(void)
    /// @brief Initializes the stack.
    /// @param pstack Pointer to the stack to be initialized.
    initilize_pang(Stack *pstack)
{
    pstack->mem[0] = pang_null; // section 2.2.2
    pstack->stack = {0};
    pstack->stack_pointer = 1;
}

/// Utility for each pang structure/type.

pang_inline(Int &)
    /// @brief Returns the pang::Int that the stack[index] points to.
    /// @param pstack Pointer to the stack.
    /// @param index Index of the item on the stack.
    at(Stack *pstack,
       uint16_t index,
       bool reverse = false)
{
    if (reverse)
        index = pstack->stack.size() - (index + 1);

    return pstack->mem[pstack->stack[index]];
}

END_NAMSEPACE_PANG

pang_func(std::ostream &)
/// @brief Overloaded function for std::cout << pang::Int.
operator<<(std::ostream &os,
           pang::Int &p_int);

START_NAMESPACE_PANG

/// Following inline stack operations:
/// push, drop, swap, quote, apply

pang_inline(void)
    /// @brief Push intmax_t value to stack and memory.
    /// @param pstack Pointer to the stack that will be pushed to.
    /// @param value The value to be pushed.
    push(Stack *pstack,
         intmax_t value)
{
    pstack->mem[pstack->stack_pointer] = to_pang_int(value);
    pstack->stack.push_back(pstack->stack_pointer++);
}

pang_inline(void)
    /// @brief Drops top item from stack.
    /// @param pstack Pointer to the stack that will be dropped.
    drop(Stack *pstack)
{
    pstack->stack_pointer = pstack->stack.back();
    pstack->stack.pop_back();
}

pang_inline(void)
    /// @brief Swaps last two items on the stack.
    /// @param pstack Pointer to the stack that will swapped.
    swap(Stack *pstack)
{
    size_t size = pstack->stack.size();

    if (size < 3)
        exit(PANG_NULL_MOVE);

    std::swap(pstack->stack[size - 1], pstack->stack[size - 2]);
}

pang_inline(void)
    /// @brief Turns the last item on the stack to a pointer.
    /// @param pstack Pointer to the stack.
    quote(Stack *pstack)
{
    Int &to_reference = at(pstack, 0, true);

    if (to_reference.is_ptr)
        exit(PANG_QUOTE_POINTER);
    if (to_reference.is_null)
        exit(PANG_NULL_QUOTE);

    to_reference.is_ptr = true;

    if (!to_reference.real)
        to_reference.is_null = true;
}

pang_inline(void)
    /// @brief Dereferences the last item on the stack.
    /// @param pstack Pointer to the stack.
    apply(Stack *pstack)
{
    Int &to_dereference = at(pstack, 0, true);

    if (!to_dereference.is_ptr)
        exit(PANG_APPLY_NON_POINTER);

    if (to_dereference.is_null)
        exit(PANG_NULL_APPLY);

    to_dereference = pstack->mem[to_dereference.real];
}

END_NAMSEPACE_PANG
