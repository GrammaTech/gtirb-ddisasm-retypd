#include <stdlib.h>
#include "inter-prop.h"

int b(struct x* l) {
    return l->a + l->b + rand();
}

int a(struct x* l) {
    l->a = 1;
    return b(l);
}

int main(void) {
    struct x y;
    return a(&y);
}
