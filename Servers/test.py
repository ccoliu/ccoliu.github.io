def fibonacci_sequence(n):
    sequence = [0, 1]
    for i in range(2, n):
        next_num = sequence[i - 1] + sequence[i - 2]
        sequence.append(next_num)
    return sequence


def display_sequence(sequence):
    print("Fibonacci Sequence:")
    for num in sequence:
        print(num)


def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


def print_primes(sequence):
    print("\nPrime Numbers in the Fibonacci Sequence:")
    for num in sequence:
        if is_prime(num):
            print(num)


def main():
    n = 20
    result = fibonacci_sequence(n)
    display_sequence(result)
    print_primes(result)  # Call print_primes if you want to include it


if __name__ == "__main__":
    main()
