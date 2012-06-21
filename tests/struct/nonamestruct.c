typedef unsigned int size_t;

typedef struct {
	size_t bytesize;
	union {
		char  *bytebuf;
		const struct _kclass **cts;
		struct kvs_t          *kvs;
		struct kopl_t          *opl;
		const struct _kObject **objects;
		struct _kObject       **refhead;  // stack->ref
	};
	size_t bytemax;
} karray_t;


typedef struct kwb_t {
	karray_t *m;
	size_t pos;
} kwb_t;

