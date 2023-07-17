#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <utility>
#include <tuple>

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
#define PANG_SIZE 0x2000

/// Section 6.3:
/// All pang errors that can be thrown.
/// These appear as the exit code to a program
/// and can be used to debug code.

#define PANG_NULL_APPLY        0x10
#define PANG_NULL_QUOTE        0x12
#define PANG_NULL_MOVE         0x14
#define PANG_NULL_PURGE        0x16
#define PANG_APPLY_NON_POINTER 0x18
#define PANG_QUOTE_POINTER     0x20

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

/// If the pang address needs to be signed, use this.
pang_type int32_t spang_address;

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
    std::vector<std::tuple<pang_address, pang_address>> freed_mem;
    pang_address mem_pointer;
} Stack;

/// Section 2.1.2 
#define pang_null \
    (Int{.is_null=true, .is_ptr=false, .real=0})
#define pang_nullptr \
    (Int{.is_null=true, .is_ptr=true, .real=0})

/// Initilizers for each pang structure/type.

#define to_pang_int(imax) \
    (Int{.is_null=false, .is_ptr=false, .real=imax})
#define to_pang_ptr(imax) \
    (Int{.is_null=false, .is_ptr=true, .real=imax})

pang_inline(void)
    /// @brief Initializes the stack.
    /// @param pstack Pointer to the stack to be initialized.
    initilize_pang(Stack *pstack)
{
    pstack->mem[0] = pang_null; // section 2.2.2
    pstack->mem_pointer = 0;
    pstack->stack = {0};
    pstack->freed_mem = {};
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
    if (!pstack->freed_mem.size())
    {
        // if there is no free memory
        pstack->mem_pointer += 1;
        pstack->mem[pstack->mem_pointer] = to_pang_int(value);
        pstack->stack.push_back(pstack->mem_pointer);
        return;
    }

    // integers only take 1 place in memory so it is safe to overwrite any freed mem,
    // just remember to remove it from freed mem afterwards
    // popping from the top of vector should be the fastest, so we should do that.
    auto free_block(pstack->freed_mem.back());
    std::get<1>(free_block)--;
    pang_address to_alloc = std::get<0>(free_block) + std::get<1>(free_block);
    
    pstack->mem[to_alloc] = to_pang_int(value);
    pstack->stack.push_back(to_alloc);

    // remember to remove from freed memory here
    if (!std::get<1>(free_block))
        pstack->freed_mem.pop_back();
}

pang_inline(void)
    /// @brief Frees a pointer's contents until null is found.
    /// @param pstack Pointer to the stack.
    free(Stack *pstack)
{
    Int ptr = pstack->mem[pstack->stack.back()];

    if (!ptr.is_ptr)
        exit(PANG_APPLY_NON_POINTER);
    
    pang_address len = 0;

    // calculate length
    for (; !pstack->mem[ptr.real + len].is_null; len++);

    pstack->freed_mem.push_back(std::make_tuple(ptr.real, len+1));
}

pang_inline(void)
    /// @brief Push intmax_t value to stack and memory.
    /// @param pstack Pointer to the stack that will be pushed to.
    /// @param value The value to be pushed.
    push(Stack *pstack,
         const char *value)
{
    pang_address len = strlen(value) + 1;
    pang_address index = 0;
    pang_address start = pstack->mem_pointer;

    for (auto it = pstack->freed_mem.begin(); it != pstack->freed_mem.end(); it++)
    {
        auto free_block = *it;
        if (std::get<1>(free_block) > len)
        {
            std::get<1>(free_block) -= len;
            
            start = std::get<0>(free_block);
            std::get<0>(free_block) += len;

            if (!std::get<1>(free_block))
            {
                pstack->freed_mem.erase(it);
            }

            break;
        }
    }

    for (; value[index++];)
    {
        pstack->mem[start + index] = to_pang_int(value[index - 1]);
    }

    // null terminator
    pstack->mem[start + index++] = pang_nullptr;
    pstack->mem[start + index] = to_pang_ptr(start + 1);

    pstack->stack.push_back(start + index);

    if (start == pstack->mem_pointer)
        pstack->mem_pointer += index;
}

pang_inline(void)
    /// @brief Purges n items from top of stack.
    /// @param pstack Pointer to the stack that will be dropped.
    /// @param n The amount of items to be purged. (if it is 0, purge all except null)
    purge(Stack *pstack,
         pang_address n)
{
    if (!n)
    {
        pstack->stack = {0};
        pstack->mem_pointer = 0;
        pstack->freed_mem = {};
        return;
    }

    if (n > (pstack->stack.size() - 1))
        exit(PANG_NULL_PURGE);

    for (auto addr: pstack->stack)
        pstack->freed_mem.push_back(std::make_tuple(addr, 1));
    
    pstack->stack.erase(pstack->stack.end() - n, pstack->stack.end());
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

pang_inline(void)
    /// @brief Adds last two integers on stack and pushes result. (pops both integers).
    /// @param pstack Pointer to the stack.
    add(Stack *pstack)
{
    if (pstack->stack.size() < 3)
        exit(PANG_NULL_PURGE);
    
    intmax_t to_add = pstack->mem[pstack->stack.back()].real;

    // remember to free memory
    pstack->freed_mem.push_back(std::make_tuple(pstack->stack.back(), 1));
    pstack->stack.pop_back();

    pstack->mem[pstack->stack.back()].real += to_add;
}

pang_inline(void)
    /// @brief Subtracts last two integers on stack and pushes result. (pops both integers).
    /// @param pstack Pointer to the stack.
    sub(Stack *pstack)
{
    if (pstack->stack.size() < 3)
        exit(PANG_NULL_PURGE);
    
    intmax_t to_sub = pstack->mem[pstack->stack.back()].real;
    
    // remember to free memory
    pstack->freed_mem.push_back(std::make_tuple(pstack->stack.back(), 1));
    pstack->stack.pop_back();

    pstack->mem[pstack->stack.back()].real -= to_sub;
}

END_NAMSEPACE_PANG
