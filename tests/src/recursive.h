struct recursive_type;

struct recursive_type {
    int padding;
    struct recursive_type* recursive;
};

/**
 *! int ⊑ test_recursive.in_0.store.σ4@0
 *! void ⊑ test_recursive.out
 *! test_recursive.in_0.store.σ8@8.store ⊑ test_recursive.in_0.store
 *! test_recursive.in_0 ⊑ test_recursive.in_0.store.σ8@8
 *! test_recursive.in_0.store.σ8@8.store.σ8@8 ⊑ test_recursive.in_0.store.σ8@8
 */
void test_recursive(struct recursive_type* type);
