struct linkedlist;

struct linkedlist {
	int value;
	struct linkedlist* next;
};

struct linkedlist* alloc_ll(int value);
void print_ll(struct linkedlist* ll);
void free_ll(struct linkedlist* ll);
void test_ll(struct linkedlist* ll);
