typedef unsigned int size_t;
struct S {
    int a;
    short b;
    long c;
    float d;
    double e;
    int (*f)(int x, short y);
    int g[32];
    int h[32][32];
    int *i;
    int *j;
    size_t **k;
};
