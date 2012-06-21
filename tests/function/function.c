typedef int size_t;
struct x;
typedef struct x X;
void f(int a, int b, int c);
struct x *g(int a, int b, int c);
X *g(int a, int b, int c);
int CRYPTO_set_mem_functions(void *(*m)(size_t),void *(*r)(void *,size_t), void (*f)(void *));
