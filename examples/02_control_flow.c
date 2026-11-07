int sum_range(int start, int end) {
    int total = 0;
    int i = start;
    while (i <= end) {
        total = total + i;
        i = i + 1;
    }
    return total;
}

int main() {
    int x = 10;
    int y = 20;
    int max_val = 0;

    if (x > y) {
        max_val = x;
    } else {
        max_val = y;
    }

    int sum_sq = 0;
    for (int k = 1; k <= 5; k = k + 1) {
        sum_sq = sum_sq + k * k;
    }

    int range_sum = sum_range(1, 10);
    return max_val + sum_sq + range_sum;
}
