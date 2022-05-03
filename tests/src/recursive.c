#include "recursive.h"

void test_recursive_store(struct recursive_type* type) {
    type->padding = 1;
    type->recursive = type;
}

int test_recursive_load(struct recursive_type* type) {
    int x = 0;

    while ( type->recursive != (void*)0 ) {
        type = type->recursive;
        x++;
    }

    type->padding = x;
    return x;
}


int main(void) {
    volatile struct recursive_type object;
    test_recursive_store(&object);
    test_recursive_load(&object);
    return 0;
}
