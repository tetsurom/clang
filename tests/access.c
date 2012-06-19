struct C{
	int a;
};

struct B{
	struct C *c;
};

struct A{
	struct B *b;
};
