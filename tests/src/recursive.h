struct recursive_type;

struct recursive_type {
    int padding;
    struct recursive_type* recursive;
};
/**
 * Generated constraints for test_recursive at -O1
 *
 * #[O1] test_recursive.in_0 ⊑ RDI_1536
 * #[O1] RDI_1536 ⊑ RDI_1536.store.σ8@8
 * #[O1] int ⊑ RDI_1530.store.σ4@0
 * #[O1] test_recursive.in_0 ⊑ RDI_1530
 * #[O1] void ⊑ test_recursive.out
 */
/**
 * Generated constraints for test_recursive at -O2
 *
 * #[O2] test_recursive.in_0 ⊑ RDI_1558
 * #[O2] RDI_1558 ⊑ RDI_1558.store.σ8@8
 * #[O2] void ⊑ test_recursive.out
 * #[O2] test_recursive.in_0 ⊑ RDI_1552
 * #[O2] int ⊑ RDI_1552.store.σ4@0
 */
/**
 * Generated constraints for test_recursive at -O3
 *
 * #[O3] test_recursive.in_0 ⊑ RDI_1558
 * #[O3] RDI_1558 ⊑ RDI_1558.store.σ8@8
 * #[O3] void ⊑ test_recursive.out
 * #[O3] test_recursive.in_0 ⊑ RDI_1552
 * #[O3] int ⊑ RDI_1552.store.σ4@0
 */

/**
 * Derived constraints for test_recursive
 *
 *! int ⊑ test_recursive.in_0.store.σ4@0
 *! void ⊑ test_recursive.out
 *! test_recursive.in_0.store.σ8@8.store ⊑ test_recursive.in_0.store
 *! test_recursive.in_0 ⊑ test_recursive.in_0.store.σ8@8
 *! test_recursive.in_0.store.σ8@8.store.σ8@8 ⊑ test_recursive.in_0.store.σ8@8
 */
void test_recursive(struct recursive_type* type);
