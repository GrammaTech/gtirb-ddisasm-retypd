
/**
 * Generated constraints for sink_01 at -O1
 *
 * #[O1] RAX_1530 ⊑ sink_01.out
 * #[O1] RAX_1535 ⊑ sink_01.out
 * #[O1] RAX_1538 ⊑ RFLAGS_1538
 * #[O1] RAX_1538 ⊑ int
 * #[O1] RAX_1538 ⊑ sink_01.out
 * #[O1] RDI_1530 ⊑ RAX_1530
 * #[O1] RDI_1533 ⊑ int
 * #[O1] RDI_1535 ⊑ RAX_1535
 * #[O1] RFLAGS_1533 ⊑ RFLAGS_1535
 * #[O1] RFLAGS_1535 ⊑ RAX_1535
 * #[O1] sink_01.in_0 ⊑ RDI_1530
 * #[O1] sink_01.in_0 ⊑ RDI_1533
 * #[O1] sink_01.in_0 ⊑ RDI_1535
 */
/**
 * Generated constraints for sink_01 at -O2
 *
 * #[O2] RAX_1648 ⊑ sink_01.out
 * #[O2] RAX_1653 ⊑ sink_01.out
 * #[O2] RAX_1656 ⊑ RFLAGS_1656
 * #[O2] RAX_1656 ⊑ int
 * #[O2] RAX_1656 ⊑ sink_01.out
 * #[O2] RDI_1648 ⊑ RAX_1648
 * #[O2] RDI_1651 ⊑ int
 * #[O2] RDI_1653 ⊑ RAX_1653
 * #[O2] RFLAGS_1651 ⊑ RFLAGS_1653
 * #[O2] RFLAGS_1653 ⊑ RAX_1653
 * #[O2] sink_01.in_0 ⊑ RDI_1648
 * #[O2] sink_01.in_0 ⊑ RDI_1651
 * #[O2] sink_01.in_0 ⊑ RDI_1653
 */
/**
 * Generated constraints for sink_01 at -O3
 *
 * #[O3] RAX_1648 ⊑ sink_01.out
 * #[O3] RAX_1653 ⊑ sink_01.out
 * #[O3] RAX_1656 ⊑ RFLAGS_1656
 * #[O3] RAX_1656 ⊑ int
 * #[O3] RAX_1656 ⊑ sink_01.out
 * #[O3] RDI_1648 ⊑ RAX_1648
 * #[O3] RDI_1651 ⊑ int
 * #[O3] RDI_1653 ⊑ RAX_1653
 * #[O3] RFLAGS_1651 ⊑ RFLAGS_1653
 * #[O3] RFLAGS_1653 ⊑ RAX_1653
 * #[O3] sink_01.in_0 ⊑ RDI_1648
 * #[O3] sink_01.in_0 ⊑ RDI_1651
 * #[O3] sink_01.in_0 ⊑ RDI_1653
 *//**
 * Derived constraints for sink_O1
 *
 *! int <= sink_01.out
 *! sink_01.in_0 <= sink_01.out
 */
int sink_01(int x);
/**
 * Generated constraints for sink_02 at -O1
 *
 * #[O1] RAX_1548 ⊑ sink_02.out
 * #[O1] RAX_1548 ⊑ uint
 * #[O1] RAX_1551 ⊑ RFLAGS_1551
 * #[O1] RAX_1551 ⊑ int
 * #[O1] RAX_1551 ⊑ sink_02.out
 * #[O1] RDI_1542 ⊑ int
 * #[O1] RFLAGS_1542 ⊑ RFLAGS_1545
 * #[O1] RFLAGS_1545 ⊑ RAX_1545
 * #[O1] sink_02.in_0 ⊑ RDI_1542
 */
/**
 * Generated constraints for sink_02 at -O2
 *
 * #[O2] RAX_1664 ⊑ RFLAGS_1664
 * #[O2] RAX_1664 ⊑ sink_02.out
 * #[O2] RAX_1664 ⊑ uint
 * #[O2] RAX_1672 ⊑ RFLAGS_1672
 * #[O2] RAX_1672 ⊑ int
 * #[O2] RAX_1672 ⊑ sink_02.out
 * #[O2] RDI_1666 ⊑ int
 * #[O2] RFLAGS_1666 ⊑ RFLAGS_1669
 * #[O2] RFLAGS_1669 ⊑ RAX_1669
 * #[O2] sink_02.in_0 ⊑ RDI_1666
 */
/**
 * Generated constraints for sink_02 at -O3
 *
 * #[O3] RAX_1664 ⊑ RFLAGS_1664
 * #[O3] RAX_1664 ⊑ sink_02.out
 * #[O3] RAX_1664 ⊑ uint
 * #[O3] RAX_1672 ⊑ RFLAGS_1672
 * #[O3] RAX_1672 ⊑ int
 * #[O3] RAX_1672 ⊑ sink_02.out
 * #[O3] RDI_1666 ⊑ int
 * #[O3] RFLAGS_1666 ⊑ RFLAGS_1669
 * #[O3] RFLAGS_1669 ⊑ RAX_1669
 * #[O3] sink_02.in_0 ⊑ RDI_1666
 */

/**
 * Derived constraints for sink_02
 *
 *! int <= sink_02.out
 *! sink_02.in_0 <= sink_02.out
 */
int sink_02(int x);
/**
 * Generated constraints for sink_03 at -O1
 *
 * #[O1] RAX_1562 ⊑ sink_03.out
 * #[O1] RDI_1555 ⊑ int
 * #[O1] RDI_1565 ⊑ RDX_1565
 * #[O1] RDI_1565 ⊑ RFLAGS_1565
 * #[O1] RDX_1559 ⊑ RFLAGS_1559
 * #[O1] RDX_1559 ⊑ int
 * #[O1] RDX_1562 ⊑ RAX_1562
 * #[O1] RDX_1565 ⊑ RDX_1562
 * #[O1] RDX_1565 ⊑ RFLAGS_1565
 * #[O1] RDX_1565 ⊑ int
 * #[O1] RFLAGS_1555 ⊑ RFLAGS_1557
 * #[O1] RSI_1555 ⊑ int
 * #[O1] sink_03.in_0 ⊑ RDI_1555
 * #[O1] sink_03.in_0 ⊑ RDI_1565
 * #[O1] sink_03.in_1 ⊑ RSI_1555
 * #[O1] sink_03.in_2 ⊑ RDX_1559
 * #[O1] sink_03.in_2 ⊑ RDX_1562
 * #[O1] sink_03.in_2 ⊑ RDX_1565
 */
/**
 * Generated constraints for sink_03 at -O2
 *
 * #[O2] RAX_1687 ⊑ sink_03.out
 * #[O2] RAX_1699 ⊑ sink_03.out
 * #[O2] RDI_1680 ⊑ int
 * #[O2] RDI_1696 ⊑ RDX_1696
 * #[O2] RDI_1696 ⊑ RFLAGS_1696
 * #[O2] RDX_1684 ⊑ RDX_1687
 * #[O2] RDX_1684 ⊑ RFLAGS_1684
 * #[O2] RDX_1684 ⊑ int
 * #[O2] RDX_1687 ⊑ RAX_1687
 * #[O2] RDX_1696 ⊑ RDX_1699
 * #[O2] RDX_1696 ⊑ RFLAGS_1696
 * #[O2] RDX_1696 ⊑ int
 * #[O2] RDX_1699 ⊑ RAX_1699
 * #[O2] RFLAGS_1680 ⊑ RFLAGS_1682
 * #[O2] RSI_1680 ⊑ int
 * #[O2] sink_03.in_0 ⊑ RDI_1680
 * #[O2] sink_03.in_0 ⊑ RDI_1696
 * #[O2] sink_03.in_1 ⊑ RSI_1680
 * #[O2] sink_03.in_2 ⊑ RDX_1684
 * #[O2] sink_03.in_2 ⊑ RDX_1687
 * #[O2] sink_03.in_2 ⊑ RDX_1696
 * #[O2] sink_03.in_2 ⊑ RDX_1699
 */
/**
 * Generated constraints for sink_03 at -O3
 *
 * #[O3] RAX_1687 ⊑ sink_03.out
 * #[O3] RAX_1699 ⊑ sink_03.out
 * #[O3] RDI_1680 ⊑ int
 * #[O3] RDI_1696 ⊑ RDX_1696
 * #[O3] RDI_1696 ⊑ RFLAGS_1696
 * #[O3] RDX_1684 ⊑ RDX_1687
 * #[O3] RDX_1684 ⊑ RFLAGS_1684
 * #[O3] RDX_1684 ⊑ int
 * #[O3] RDX_1687 ⊑ RAX_1687
 * #[O3] RDX_1696 ⊑ RDX_1699
 * #[O3] RDX_1696 ⊑ RFLAGS_1696
 * #[O3] RDX_1696 ⊑ int
 * #[O3] RDX_1699 ⊑ RAX_1699
 * #[O3] RFLAGS_1680 ⊑ RFLAGS_1682
 * #[O3] RSI_1680 ⊑ int
 * #[O3] sink_03.in_0 ⊑ RDI_1680
 * #[O3] sink_03.in_0 ⊑ RDI_1696
 * #[O3] sink_03.in_1 ⊑ RSI_1680
 * #[O3] sink_03.in_2 ⊑ RDX_1684
 * #[O3] sink_03.in_2 ⊑ RDX_1687
 * #[O3] sink_03.in_2 ⊑ RDX_1696
 * #[O3] sink_03.in_2 ⊑ RDX_1699
 */

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
 * Generated constraints for sink_04 at -O1
 *
 * #[O1] RAX_1570 ⊑ sink_04.out
 * #[O1] RAX_1572 ⊑ RFLAGS_1572
 * #[O1] RAX_1572 ⊑ int
 * #[O1] RAX_1572 ⊑ sink_04.out
 * #[O1] RDI_1570 ⊑ RAX_1570
 * #[O1] sink_04.in_0 ⊑ RDI_1570
 */
/**
 * Generated constraints for sink_04 at -O2
 *
 * #[O2] RAX_1712 ⊑ sink_04.out
 * #[O2] RAX_1714 ⊑ RFLAGS_1714
 * #[O2] RAX_1714 ⊑ int
 * #[O2] RAX_1714 ⊑ sink_04.out
 * #[O2] RDI_1712 ⊑ RAX_1712
 * #[O2] sink_04.in_0 ⊑ RDI_1712
 */
/**
 * Generated constraints for sink_04 at -O3
 *
 * #[O3] RAX_1712 ⊑ sink_04.out
 * #[O3] RAX_1714 ⊑ RFLAGS_1714
 * #[O3] RAX_1714 ⊑ int
 * #[O3] RAX_1714 ⊑ sink_04.out
 * #[O3] RDI_1712 ⊑ RAX_1712
 * #[O3] sink_04.in_0 ⊑ RDI_1712
 */

/**
 * Derived constraints for sink_04
 *
 *! uint <= sink_04.out
 *! sink_04.in_0 <= sink_04.out
 */
unsigned sink_04(unsigned x);
/**
 * Generated constraints for sink_05 at -O1
 *
 * #[O1] RAX_1582 ⊑ sink_05.out
 * #[O1] RAX_1582 ⊑ uint
 * #[O1] RAX_1585 ⊑ RFLAGS_1585
 * #[O1] RAX_1585 ⊑ int
 * #[O1] RAX_1585 ⊑ sink_05.out
 * #[O1] RFLAGS_1576 ⊑ RFLAGS_1579
 * #[O1] RFLAGS_1579 ⊑ RAX_1579
 * #[O1] sink_05.in_0 ⊑ RDI_1576
 */
/**
 * Generated constraints for sink_05 at -O2
 *
 * #[O2] RAX_1728 ⊑ RFLAGS_1728
 * #[O2] RAX_1728 ⊑ sink_05.out
 * #[O2] RAX_1728 ⊑ uint
 * #[O2] RAX_1736 ⊑ RFLAGS_1736
 * #[O2] RAX_1736 ⊑ int
 * #[O2] RAX_1736 ⊑ sink_05.out
 * #[O2] RFLAGS_1730 ⊑ RFLAGS_1733
 * #[O2] RFLAGS_1733 ⊑ RAX_1733
 * #[O2] sink_05.in_0 ⊑ RDI_1730
 */
/**
 * Generated constraints for sink_05 at -O3
 *
 * #[O3] RAX_1728 ⊑ RFLAGS_1728
 * #[O3] RAX_1728 ⊑ sink_05.out
 * #[O3] RAX_1728 ⊑ uint
 * #[O3] RAX_1736 ⊑ RFLAGS_1736
 * #[O3] RAX_1736 ⊑ int
 * #[O3] RAX_1736 ⊑ sink_05.out
 * #[O3] RFLAGS_1730 ⊑ RFLAGS_1733
 * #[O3] RFLAGS_1733 ⊑ RAX_1733
 * #[O3] sink_05.in_0 ⊑ RDI_1730
 */

/**
 * Derived constraints for sink_05
 *
 *! uint <= sink_05.out
 *! sink_05.in_0 <= sink_05.out
 */
unsigned sink_05(unsigned x);
