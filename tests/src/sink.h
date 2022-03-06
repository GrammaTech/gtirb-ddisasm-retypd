/**
 * Derived constraints for sink_O1
 *
 *! int <= sink_01.out
 *! sink_01.in_0 <= sink_01.out
 */
int sink_01(int x);

/**
 * Derived constraints for sink_02
 *
 *! int <= sink_02.out
 *! sink_02.in_0 <= sink_02.out
 */
int sink_02(int x);

/**
 * Derived constraints for sink_03
 *
 *! int <= sink_03.out
 *! sink_03.in_0 <= sink_03.out
 *! sink_03.in_1 <= sink_03.out
 *! sink_03.in_2 <= sink_03.out
 */
int sink_03(int x, int y, int z);

/**
 * Derived constraints for sink_04
 *
 *! uint <= sink_04.out
 *! sink_04.in_0 <= sink_04.out
 */
unsigned sink_04(unsigned x);

/**
 * Derived constraints for sink_05
 *
 *! uint <= sink_05.out
 *! sink_05.in_0 <= sink_05.out
 */
unsigned sink_05(unsigned x);
