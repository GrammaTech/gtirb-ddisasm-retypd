#include <stdlib.h>
#include <stdio.h>

#include "linkedlist.h"

struct linkedlist* alloc_ll(int value) {
	struct linkedlist* ll = (struct linkedlist*) malloc(sizeof(struct linkedlist));
	ll->value = value;
	ll->next = NULL;
	return ll;
}

void print_ll(struct linkedlist* ll) {
	while (ll != NULL) {
		printf("%d ", ll->value);
		ll = ll->next;
	}
	printf("\n");
}

void free_ll(struct linkedlist* ll) {
	struct linkedlist* tmp;
	while (ll != NULL) {
		tmp = ll->next;
		free(ll);
		ll = tmp;
	}
}

void test_ll(struct linkedlist* ll) {
	if (  ll->value > 2 ) {
		ll->value = 1;
		ll->next = ll->next->next;
	}
	else {
		ll->value = 0;
		ll->next = ll->next->next->next;
	}
}


int main(void) {
	struct linkedlist* a = alloc_ll(1);
	struct linkedlist* b = alloc_ll(2);
	struct linkedlist* c = alloc_ll(3);
	a->next = b;
	b->next = c;
	print_ll(a);
	free_ll(a);
	return 0;
}
