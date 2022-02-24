struct recursive_type;

struct recursive_type {
    int padding;
    struct recursive_type* recursive;
};

void test_recursive(struct recursive_type* type);
