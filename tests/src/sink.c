#include "sink.h"

int sink_01(int x) {
    return x / 4;
}

int sink_02(int x) {
    if ( x > 5 ) {
        return 2;
    }
    else {
        return 3;
    }
}

int sink_03(int x, int y, int z) {
    if ( x > y ) {
        return x * z;
    }
    else {
        return z * z;
    }
}

unsigned sink_04(unsigned x) {
    return x / 4;
}

unsigned sink_05(unsigned x) {
    if ( x > 5 ) {
        return 3;
    }
    else {
        return 4;
    }
}

int main() {
    volatile int x, y, z = 0;
    volatile int o1 = sink_01(x);
    volatile int o2 = sink_02(y);
    volatile int o3 = sink_03(x, y, z);
    volatile int o4 = sink_04(x);
    volatile int o5 = sink_05(x);
    return 0;
}
