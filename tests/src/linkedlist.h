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
 * Generated constraints for print_ll at -O1
 *
 * #[O1] RBX_1886 ⊑ RBX_1916
 * #[O1] RBP_1889 ⊑ RBP_1898
 * #[O1] print_ll.in_0 ⊑ RDI_1886
 * #[O1] int ⊑ RDI_1901
 * #[O1] RBP_1898 ⊑ RSI_1898
 * #[O1] int ⊑ RDI_1925
 * #[O1] RBX_1886 ⊑ RBX_1896
 * #[O1] RBX_1916 ⊑ RBX_1896
 * #[O1] print_ll.in_0 ⊑ RDI_1881
 * #[O1] RBX_1896.load.σ4@0 ⊑ RDX_1896
 * #[O1] int ⊑ RAX_1906
 * #[O1] int ⊑ RSP_1935
 * #[O1] RDI_1886 ⊑ RBX_1886
 * #[O1] RBX_1916 ⊑ RBX_1920
 * #[O1] int ⊑ RSP_1877
 * #[O1] RSP_1877 ⊑ RSP_1935
 * #[O1] RBX_1916.load.σ8@8 ⊑ RBX_1916
 * #[O1] RAX_1906 ⊑ print_ll.out
 */
/**
 * Generated constraints for print_ll at -O2
 *
 * #[O2] RBX_2057 ⊑ RBX_2061
 * #[O2] RBX_2030 ⊑ RBX_2040
 * #[O2] int ⊑ RSP_2033
 * #[O2] RBP_2044 ⊑ RSI_2044
 * #[O2] RBX_2040.load.σ4@0 ⊑ RDX_2040
 * #[O2] uint ⊑ RAX_2042
 * #[O2] RBX_2057 ⊑ RBX_2040
 * #[O2] RBX_2030 ⊑ RBX_2057
 * #[O2] int ⊑ RDI_2070
 * #[O2] print_ll.in_0 ⊑ RDI_2016
 * #[O2] RBP_2023 ⊑ RBP_2044
 * #[O2] int ⊑ RSP_2066
 * #[O2] int ⊑ RDI_2047
 * #[O2] RSP_2033 ⊑ RSP_2066
 * #[O2] RDI_2030 ⊑ RBX_2030
 * #[O2] print_ll.in_0 ⊑ RDI_2030
 * #[O2] RBX_2057.load.σ8@8 ⊑ RBX_2057
 * #[O2] int ⊑ RDI_2088
 * #[O2] RAX_2042 ⊑ print_ll.out
 */
/**
 * Generated constraints for print_ll at -O3
 *
 * #[O3] RBX_2057 ⊑ RBX_2061
 * #[O3] RBX_2030 ⊑ RBX_2040
 * #[O3] int ⊑ RSP_2033
 * #[O3] RBP_2044 ⊑ RSI_2044
 * #[O3] RBX_2040.load.σ4@0 ⊑ RDX_2040
 * #[O3] uint ⊑ RAX_2042
 * #[O3] RBX_2057 ⊑ RBX_2040
 * #[O3] RBX_2030 ⊑ RBX_2057
 * #[O3] int ⊑ RDI_2070
 * #[O3] print_ll.in_0 ⊑ RDI_2016
 * #[O3] RBP_2023 ⊑ RBP_2044
 * #[O3] int ⊑ RSP_2066
 * #[O3] int ⊑ RDI_2047
 * #[O3] RSP_2033 ⊑ RSP_2066
 * #[O3] RDI_2030 ⊑ RBX_2030
 * #[O3] print_ll.in_0 ⊑ RDI_2030
 * #[O3] RBX_2057.load.σ8@8 ⊑ RBX_2057
 * #[O3] int ⊑ RDI_2088
 * #[O3] RAX_2042 ⊑ print_ll.out
 */

/**
 * Derived constraints for print_ll
 *
 *!
 */
void print_ll(struct linkedlist* ll);
/**
 * Generated constraints for free_ll at -O1
 *
 * #[O1] RBX_1948 ⊑ RBX_1960
 * #[O1] free_ll.in_0 ⊑ RDI_1942
 * #[O1] RBX_1948 ⊑ RBX_1957
 * #[O1] free_ll.in_0 ⊑ RDI_1948
 * #[O1] RDI_1957 ⊑ RDI_1948
 * #[O1] RDI_1948.load.σ8@8 ⊑ RBX_1948
 * #[O1] RBX_1957 ⊑ RDI_1957
 * #[O1] void ⊑ free_ll.out
 */
/**
 * Generated constraints for free_ll at -O2
 *
 * #[O2] free_ll.in_0 ⊑ RDI_2112
 * #[O2] RBX_2128 ⊑ RBX_2137
 * #[O2] RDI_2140 ⊑ RDI_2128
 * #[O2] RBX_2128 ⊑ RBX_2140
 * #[O2] free_ll.in_0 ⊑ RDI_2128
 * #[O2] RDI_2128.load.σ8@8 ⊑ RBX_2128
 * #[O2] void ⊑ free_ll.out
 * #[O2] RBX_2140 ⊑ RDI_2140
 */
/**
 * Generated constraints for free_ll at -O3
 *
 * #[O3] free_ll.in_0 ⊑ RDI_2112
 * #[O3] RBX_2128 ⊑ RBX_2137
 * #[O3] RDI_2140 ⊑ RDI_2128
 * #[O3] RBX_2128 ⊑ RBX_2140
 * #[O3] free_ll.in_0 ⊑ RDI_2128
 * #[O3] RDI_2128.load.σ8@8 ⊑ RBX_2128
 * #[O3] void ⊑ free_ll.out
 * #[O3] RBX_2140 ⊑ RDI_2140
 */

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
 * Generated constraints for test_ll at -O1
 *
 * #[O1] RDI_2003.load.σ8@8 ⊑ RAX_2003
 * #[O1] RAX_1988.load.σ8@8 ⊑ RAX_1988
 * #[O1] RAX_2007.load.σ8@8 ⊑ RAX_2007
 * #[O1] RAX_2007 ⊑ RAX_2011
 * #[O1] RAX_2003 ⊑ RAX_2007
 * #[O1] RAX_1988 ⊑ RAX_1992
 * #[O1] test_ll.in_0 ⊑ RDI_1969
 * #[O1] RAX_1980 ⊑ RAX_1984
 * #[O1] test_ll.in_0 ⊑ RDI_1974
 * #[O1] RDI_1980.load.σ8@8 ⊑ RAX_1980
 * #[O1] test_ll.in_0 ⊑ RDI_1997
 * #[O1] RAX_2011 ⊑ RDI_2011.store.σ8@8
 * #[O1] RAX_1984 ⊑ RAX_1988
 * #[O1] RAX_1984.load.σ8@8 ⊑ RAX_1984
 * #[O1] void ⊑ test_ll.out
 * #[O1] RAX_1992 ⊑ RDI_1992.store.σ8@8
 * #[O1] test_ll.in_0 ⊑ RDI_1992
 * #[O1] RDI_1969.load.σ4@0 ⊑ int
 * #[O1] test_ll.in_0 ⊑ RDI_2003
 * #[O1] int ⊑ RDI_1997.store.σ4@0
 * #[O1] int ⊑ RDI_1974.store.σ4@0
 * #[O1] test_ll.in_0 ⊑ RDI_2011
 * #[O1] test_ll.in_0 ⊑ RDI_1980
 */
/**
 * Generated constraints for test_ll at -O2
 *
 * #[O2] test_ll.in_0 ⊑ RDI_2183
 * #[O2] RAX_2173 ⊑ RAX_2183
 * #[O2] RAX_2173.load.σ8@8 ⊑ RAX_2173
 * #[O2] RAX_2198 ⊑ RDI_2198.store.σ8@8
 * #[O2] test_ll.in_0 ⊑ RDI_2177
 * #[O2] RDI_2163.load.σ8@8 ⊑ RAX_2163
 * #[O2] RAX_2163 ⊑ RAX_2167
 * #[O2] test_ll.in_0 ⊑ RDI_2163
 * #[O2] test_ll.in_0 ⊑ RDI_2198
 * #[O2] int ⊑ RDI_2192.store.σ4@0
 * #[O2] void ⊑ test_ll.out
 * #[O2] RAX_2183 ⊑ RDI_2183.store.σ8@8
 * #[O2] test_ll.in_0 ⊑ RDI_2192
 * #[O2] RAX_2167 ⊑ RAX_2198
 * #[O2] test_ll.in_0 ⊑ RDI_2160
 * #[O2] RAX_2167 ⊑ RAX_2173
 * #[O2] int ⊑ RDI_2177.store.σ4@0
 * #[O2] RAX_2167.load.σ8@8 ⊑ RAX_2167
 * #[O2] RDI_2160.load.σ4@0 ⊑ int
 */
/**
 * Generated constraints for test_ll at -O3
 *
 * #[O3] test_ll.in_0 ⊑ RDI_2188
 * #[O3] RAX_2178.load.σ8@8 ⊑ RAX_2178
 * #[O3] RAX_2172.load.σ8@8 ⊑ RAX_2172
 * #[O3] RAX_2163 ⊑ RAX_2172
 * #[O3] test_ll.in_0 ⊑ RDI_2184
 * #[O3] RAX_2184 ⊑ RDI_2184.store.σ8@8
 * #[O3] RDI_2163.load.σ8@8 ⊑ RAX_2163
 * #[O3] test_ll.in_0 ⊑ RDI_2163
 * #[O3] RAX_2172 ⊑ RAX_2178
 * #[O3] RDX_2182 ⊑ RDX_2188
 * #[O3] RAX_2178 ⊑ RAX_2184
 * #[O3] void ⊑ test_ll.out
 * #[O3] RDX_2167 ⊑ RDX_2188
 * #[O3] test_ll.in_0 ⊑ RDI_2160
 * #[O3] uint ⊑ RDX_2182
 * #[O3] RAX_2172 ⊑ RAX_2184
 * #[O3] int ⊑ RDX_2167
 * #[O3] RDX_2188 ⊑ RDI_2188.store.σ4@0
 * #[O3] RDI_2160.load.σ4@0 ⊑ int
 */

/**
 * Derived constraints for test_ll
 *
 *!
 */
void test_ll(struct linkedlist* ll);
