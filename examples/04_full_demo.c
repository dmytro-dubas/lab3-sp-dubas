float compute_average(int a, int b, int c) {
    float sum = a + b + c;
    return sum / 3.0;
}

int is_prime(int n) {
    if (n <= 1) {
        return 0;
    }
    int d = 2;
    while (d * d <= n) {
        if (n % d == 0) {
            return 0;
        }
        d = d + 1;
    }
    return 1;
}

int main() {
    int const_calc = 100 * 2 + 50 / 2;
    int prime_count = 0;
    for (int i = 2; i <= 20; i = i + 1) {
        if (is_prime(i)) {
            prime_count = prime_count + 1;
        }
    }
    float avg = compute_average(10, 20, 30);
    return prime_count;
}
