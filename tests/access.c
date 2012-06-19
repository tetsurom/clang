struct C{
	int d;
};

struct B{
	struct C *c;
};

struct A{
	struct B *b;
};
