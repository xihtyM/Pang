#include "pang.hh"

pang_func(void)
pang::push(
    Stack *pstack,
    intmax_t value)
{
    if (!pstack->freed_mem.size())
    {
        // if there is no free memory
        pstack->mem[pstack->mem_pointer] = to_pang_int(value);
        pstack->stack.push_back(pstack->mem_pointer);
        pstack->mem_pointer++;
        return;
    }

    // integers only take 1 place in memory so it is safe to overwrite any freed mem,
    // just remember to remove it from freed mem afterwards
    // popping from the top of vector should be the fastest, so we should do that.
    FreeBlock &free_block = pstack->freed_mem.back();
    free_block.len--;
    pang_address to_alloc = free_block.start + free_block.len;
    
    pstack->mem[to_alloc] = to_pang_int(value);
    pstack->stack.push_back(to_alloc);

    // remember to remove from freed memory here
    if (!free_block.len)
        pstack->freed_mem.pop_back();
}

pang_func(void)
pang::push(
    Stack *pstack,
    const char *value)
{
    pang_address len = strlen(value) + 1;
    spang_address start = _find_free_block(
        pstack, len);
    
    if (start == -1)
    {
        start = pstack->mem_pointer;
        pstack->mem_pointer += len;
    } else {
        auto it = pstack->freed_mem.begin() + start;

        start = (*it).start;
        (*it).start += len;
        
        if (!((*it).len -= len))
            pstack->freed_mem.erase(it);
    }

    for (pang_address index = 0; value[index]; index++)
    {
        pstack->mem[start + index] = to_pang_int(value[index]);
    }

    if (pstack->freed_mem.size())
    {
        FreeBlock &free_block = pstack->freed_mem.back();
        free_block.len--;
        pang_address ptr = free_block.start + free_block.len;

        pstack->mem[ptr] = to_pang_ptr(start);
        pstack->stack.push_back(ptr);

        // remember to remove from freed memory here
        if (!free_block.len)
            pstack->freed_mem.pop_back();
    } else {
        pstack->mem[pstack->mem_pointer] = to_pang_ptr(start);
        pstack->stack.push_back(pstack->mem_pointer);
        pstack->mem_pointer++;
    }
}

pang_func(void)
pang::purge(
    Stack *pstack,
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

    for (auto it = pstack->stack.rbegin(); it != pstack->stack.rbegin() + n; it++)
        pstack->freed_mem.push_back({*it, (pang_address) 1});
    
    pstack->stack.erase(pstack->stack.end() - n, pstack->stack.end());
}


pang_func(std::ostream &)
operator<<(std::ostream &os,
           pang::Int &p_int)
{
    if (p_int.is_null)
    {
        os << "null";
        return os;
    }

    if (p_int.is_ptr)
    {
        os << "ptr(" << p_int.real << ")";
        return os;
    }

    os << p_int.real;
    return os;
}

void print_stuff(pang::Stack &pstack)
{
    for (auto tup: pstack.freed_mem)
    {
        std::cout << tup.start << '-' << tup.len << ' ';
    }

    std::cout << '\n';

    for (int index = 0; index < pstack.mem_pointer; index++)
    {
        std::cout << pstack.mem[index] << ' ';
    }

    std::cout << '\n';

    for (auto addr: pstack.stack)
    {
        std::cout << pstack.mem[addr] << ' ';
    }

    std::cout << '\n';
}

int main(int argc, char *argv[])
{
    pang::Stack pstack;
    pang::initilize_pang(&pstack);
    
    pang::push(&pstack, "hello");
    pang::free(&pstack);
    pang::purge(&pstack, 1);
    pang::push(&pstack, "tests");
    pang::push(&pstack, 4324);
    pang::swap(&pstack);
    print_stuff(pstack);

    return 0;
}
