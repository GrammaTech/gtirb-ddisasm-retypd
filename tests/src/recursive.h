struct recursive_type;

struct recursive_type {
    int padding;
    struct recursive_type* recursive;
};

/**
 * Derived constraints for test_recursive
 *
 *! int ⊑ test_recursive.in_0.store.σ4@0
 *! void ⊑ test_recursive.out
 *! test_recursive.in_0.store.σ8@8.store ⊑ test_recursive.in_0.store
 *! test_recursive.in_0 ⊑ test_recursive.in_0.store.σ8@8
 *! test_recursive.in_0.store.σ8@8.store.σ8@8 ⊑ test_recursive.in_0.store.σ8@8
 */
void test_recursive_store(struct recursive_type* type);

int test_recursive_load(struct recursive_type* type);
