int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

int power(int base, int exp) {
    int result = 1;
    while (exp > 0) {
        result = result * base;
        exp = exp - 1;
    }
    return result;
}

int main() {
    int n = 5;
    int fact5 = factorial(n);
    int pow2_4 = power(2, 4);

    int outer_var = 100;
    {
        int inner_var = 50;
        outer_var = outer_var + inner_var;
    }

    return fact5 + pow2_4 + outer_var;
}
