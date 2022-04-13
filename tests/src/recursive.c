#include "recursive.h"

void test_recursive(struct recursive_type* type) {
    type->padding = 1;
    type->recursive = type;
}

int main(void) {
    volatile struct recursive_type object;
    test_recursive(&object);
    return 0;
}
