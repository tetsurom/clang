struct S{
    union {
        double d;
        int i;
        struct string{
            char *p;
            unsigned int size;
        }str;
};
