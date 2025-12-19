from calculator.core import ArithmeticOperations
from calculator.utils import format_result, sum_list


def run_demo():
    calc = ArithmeticOperations(precision=4)
    print(f"Calculator Mode: {calc.mode}")

    val_a = 12.34567
    val_b = 8.65432
    raw_sum = calc.add(val_a, val_b)

    display_string = format_result(raw_sum, prefix="Calculated Sum:")
    print(display_string)

    prices = [19.99, 5.50, 10.0, 2.25]
    total = sum_list(prices)

    print(format_result(total, prefix="Total Inventory Value:"))


if __name__ == "__main__":
    run_demo()