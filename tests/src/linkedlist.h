struct linkedlist;

struct linkedlist {
    int value;
    struct linkedlist* next;
};

/**
 * Derived constraints for alloc_ll
 *
 *!
 */
struct linkedlist* alloc_ll(int value);

/**
 * Derived constraints for print_ll
 *
 *!
 */
void print_ll(struct linkedlist* ll);

/**
 * Derived constraints for free_ll
 *
 *! void ⊑ free_ll.out
 *! τ$0.load.σ8@8 ⊑ τ$1
 *! free_ll.in_0 ⊑ τ$0
 *! τ$1 ⊑ τ$0
 */
void free_ll(struct linkedlist* ll);

/**
 * Derived constraints for test_ll
 *
 *!
 */
void test_ll(struct linkedlist* ll);
