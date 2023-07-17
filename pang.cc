#include "pang.hh"

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

int main(int argc, char *argv[])
{
    pang::Stack pstack;
    pang::initilize_pang(&pstack);

    pang::push(&pstack, "hello");
    pang::free(&pstack);
    pang::purge(&pstack, 1);
    pang::push(&pstack, "test");
    //pang::push(&pstack, 4324);


    for (auto tup: pstack.freed_mem)
    {
        std::cout << std::get<0>(tup) << '-' << std::get<1>(tup) << ' ';
    }

    std::cout << '\n';

    for (int index = 0; index <= pstack.mem_pointer; index++)
    {
        std::cout << pstack.mem[index] << ' ';
    }

    std::cout << '\n';

    for (auto addr: pstack.stack)
    {
        std::cout << pstack.mem[addr] << ' ';
    }

    return 0;
}
