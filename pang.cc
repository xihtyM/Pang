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

    pang::push(&pstack, 123);
    pang::push(&pstack, 321);
    pang::add(&pstack);
    pang::push(&pstack, "hi");
    pang::push(&pstack, 1);
    pang::sub(&pstack);

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
