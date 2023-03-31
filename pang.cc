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

int main(void)
{
    pang::Stack pstack;
    pang::initilize_pang(&pstack);

    pang::push(&pstack, 123321);
    pang::push(&pstack, 1);
    pang::quote(&pstack);
    pang::apply(&pstack);

    std::cout << pang::at(&pstack, 0, true);

    return 0;
}
