// Name:Ibrahim Tarek  Email:ibrahim@example.com  Student ID:1009

/* Problem 1
#include <stdio.h>
int main() {
    long long n;
    scanf("%lld", &n);
    printf("%lld\n", n * 2);
    return 0;
}
 */

/* Problem 2
#include <stdio.h>
int main() {
    long long a, b;
    scanf("%lld %lld", &a, &b);
    printf("%lld\n", a + b);
    return 0;
}
 */

/* Problem 3
#include <stdio.h>
int main() {
    int n;
    scanf("%d", &n);
    long long best, x;
    scanf("%lld", &best);
    for (int i = 1; i < n; i++) {
        scanf("%lld", &x);
        if (x > best) best = x;
    }
    printf("%lld\n", best);
    return 0;
}
 */