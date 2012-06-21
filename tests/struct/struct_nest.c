struct S1{
	int a;
};

struct S2{
	int b;
	struct S1 *sp;
	struct S3{
		int c;
		int d;
	}s3;
	struct {
		int e;
		int f;
	}s4;
}
