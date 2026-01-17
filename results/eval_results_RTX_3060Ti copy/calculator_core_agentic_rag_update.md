# API Documentation: calculator_core

<!-- BEGIN: auto:calculator.core.CalculatorError -->
### `CalculatorError`

**Summary**
Base exception class for the calculator module.

**Parameters**
None

**Returns**
None

**Raises**
- `CalculatorError`: This exception is raised when an error occurs in the calculator operations.

**Examples**
```python
try:
    raise CalculatorError("Invalid operation")
except CalculatorError as e:
    print(f"Caught CalculatorError: {e}")
```

**See also**
- `TestError`: A specific exception class that inherits from `CalculatorError`.
<!-- END: auto:calculator.core.CalculatorError -->

<!-- BEGIN: auto:calculator.core.PrecisionError -->
### `PrecisionError`

**Summary**
A lightweight exception class raised by the calculator when requested precision exceeds acceptable limits.

**Parameters**
- None

**Returns**
- None

**Raises**
- `None`: This exception class does not raise any exceptions.

**Examples**
```python
try:
    result = calculator.calculate(1.0, 2.0, precision=100)
except PrecisionError as e:
    print(f"Precision error: {e}")
```

**See also**
- `CalculatorError`: The base class for all calculator exceptions.
- `CalculationLimitError`: Another exception class for when calculation limits are exceeded.
<!-- END: auto:calculator.core.PrecisionError -->

<!-- BEGIN: auto:calculator.core.TestError -->
### `TestError`

**Summary**
A test-specific exception class used to simulate error conditions during testing without modifying core functionality. This class is intentionally empty (`pass`) to serve as a placeholder for test error scenarios.

**Parameters**
- `None`: This class has no parameters.

**Returns**
- `None`: This class does not return any value.

**Raises**
- `TestError`: This class is designed to be instantiated and raised as a test-specific exception. It does not contain any error handling logic and is used solely for testing purposes.

**Examples**
```python
from calculator.core import TestError

try:
    raise TestError("Test error message")
except TestError as e:
    print(f"Caught test error: {e}")
```

**See also**
- `calculator.core.CalculatorError`: The base error class for the calculator module.
- `calculator.core.PrecisionError`: A subclass of `CalculatorError` for precision-related errors.
- `calculator.core.CalculationLimitError`: A subclass of `CalculatorError` for calculation limit errors.
<!-- END: auto:calculator.core.TestError -->

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->

<!-- END: auto:calculator.core.CalculationLimitError -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `ArithmeticOperations`

**Summary**
A calculator class that supports basic arithmetic operations (addition, subtraction, and multiplication) with configurable precision (default: 4 decimal places, maximum: 10 decimal places). The class validates input values against a range of [-1e10, 1e10] and logs each operation to a history list for audit purposes using Python's logging module.

**Attributes**
- `CURRENT_MODE` (str): The current operation mode (default: 'standard'). This constant determines the behavior of arithmetic operations.

**Methods**
- `add(self, a: float, b: float) -> float`: Adds two numbers with the current precision setting and returns the result rounded to the specified decimal places.
- `subtract(self, a: float, b: float) -> float`: Subtracts the second number from the first with the current precision setting and returns the result rounded to the specified decimal places.
- `multiply(self, a: float, b: float) -> float`: Multiplies two numbers with the current precision setting. **This method is a placeholder and always returns 0.0**.

**Raises**
- `CalculationLimitError`: Raised when input values are outside the range [-1e10, 1e10].
- `ValueError`: Raised if the precision setting is not within the range [0, 10].

**Examples**
```python
import logging

# Configure logging (for demonstration purposes)
logging.basicConfig(level=logging.INFO)

# Create an instance of ArithmeticOperations
arithmetic = ArithmeticOperations()

# Perform addition
result = arithmetic.add(1.2345, 2.3456)
print(f"Addition result: {result}")

# Perform subtraction
result = arithmetic.subtract(5.0, 3.0)
print(f"Subtraction result: {result}")

# Perform multiplication (always returns 0)
result = arithmetic.multiply(10.0, 20.0)
print(f"Multiplication result: {result}")

# Check the current mode
print(f"Current mode: {arithmetic.CURRENT_MODE}")
```

**See also**
- `CalculationLimitError`: Custom exception for input value validation.
<!-- END: auto:calculator.core.ArithmeticOperations -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `__init__`

**Summary**  
Initializes the calculator with a specified precision (0-10, default=2) and sets up a string-based operation history list for tracking user activities.

**Parameters**  
- `precision` (int): The number of decimal places to use for calculations. Must be an integer between 0 and 10 (inclusive). Default value is 2.

**Returns**  
- `None`: The `__init__` method does not return any value.

**Raises**  
- `ValueError`: If the provided `precision` is not an integer in the range [0, 10].

**Examples**  
```python
# Initialize with default precision (2)
calculator = ArithmeticOperations()

# Initialize with precision 5
calculator = ArithmeticOperations(precision=5)
```

**See also**  
- `calculator.core.ArithmeticOperations.history`: The string-based operation history list (list of strings) used for tracking user activities.
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `mode`

**Summary**
Returns the current operation mode of the calculator as a string.

**Parameters**
- None

**Returns**
- (str): The current operation mode as a string (e.g., "Scientific")

**Raises**
- None

**Examples**
```python
from calculator.core import Calculator

calc = Calculator()
print(calc.mode())  # Output: "Scientific"
```

**See also**
- `CURRENT_MODE` (module-level constant)
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `add`

**Summary**
Safely adds two floating-point numbers with input validation, rounding to the class's precision, and logging the operation.

**Parameters**
- `a` (float): First floating-point number to add.
- `b` (float): Second floating-point number to add.

**Returns**
- `float`: The result of the addition, rounded to `self.precision` decimal places.

**Raises**
- `OverflowError`: If the input values cause an overflow (e.g., too large to represent as a float).

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create an instance with precision 2
calc = ArithmeticOperations(precision=2)
result = calc.add(1.234, 5.678)
print(result)  # Output: 6.91
```

**See also**
- `calculator.core.ArithmeticOperations.multiply`
- `calculator.core.ArithmeticOperations.subtract`
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `calculator.core.ArithmeticOperations.subtract`

**Summary**
Subtracts two numbers with input validation and rounding to the specified precision.

**Parameters**
- `a` (float): The first number to subtract.
- `b` (float): The second number to subtract.

**Returns**
- (float): The result of `a - b` rounded to `self.precision` decimal places.

**Raises**
- `CalculatorError`: Raised if input validation fails (e.g., invalid numbers or values outside the defined limits).

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create an instance with precision 2
calc = ArithmeticOperations(precision=2)

# Subtract 5.123 from 10.456
result = calc.subtract(10.456, 5.123)
print(result)  # Output: 5.33
```

**See also**
- `calculator.core.ArithmeticOperations.add`
- `calculator.core.ArithmeticOperations.multiply`
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.multiply -->
### `multiply`

**Summary**
A placeholder method for multiplication operations that returns 0. This method serves as a stub to allow for future implementation while maintaining the class structure.

**Parameters**
None

**Returns**
int: Always returns 0.

**Raises**
No exceptions are raised.

**Examples**
```python
from calculator.core import ArithmeticOperations

calculator = ArithmeticOperations()
result = calculator.multiply()
print(result)  # Output: 0
```

**See also**
- `calculator.core.ArithmeticOperations.subtract`: Subtraction operation method.
- `calculator.core.ArithmeticOperations.mode`: Mode operation method.
<!-- END: auto:calculator.core.ArithmeticOperations.multiply -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
### `_check_limits`

**Summary**
Validates each input value against the numerical range `[-1e12, 1e12]` to prevent overflow or underflow during arithmetic operations in the `ArithmeticOperations` class.

**Parameters**
- `value` (float or list of floats): The input value(s) to be checked. This method accepts a single value or a list of values.

**Returns**
- None: This method does not return any value; it raises an exception if any value is out of bounds.

**Raises**
- `CalculationLimitError`: Raised if any input value is outside the range `[-1e12, 1e12]`.

**Examples**
```python
from arithmetic_operations import ArithmeticOperations

# Example 1: Single value
arithmetic = ArithmeticOperations()
arithmetic._check_limits(1e12)  # Valid

# Example 2: Value outside the range
arithmetic._check_limits(1e13)   # Raises CalculationLimitError
```

**See also**
- `ArithmeticOperations`: The class that uses this method for safe arithmetic operations.
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `_log_op`

**Summary**
A private helper method that records the inputs and output of an arithmetic operation to the operation history and the debug logger for auditing and debugging purposes.

**Parameters**
- `op_name` (str): The name of the arithmetic operation (e.g., "multiply", "subtract", "mode")
- `*operands` (any): The input operands for the operation
- `result` (any): The result of the operation

**Returns**
None

**Raises**
- `Exception`: If an error occurs while recording the operation (e.g., logger failure or history update failure)

**Examples**
```python
calc._log_op("multiply", 5, 3, 15)
```

**See also**
- `calculator.core.ArithmeticOperations.multiply`
- `calculator.core.ArithmeticOperations.subtract`
- `calculator.core.ArithmeticOperations.mode`
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->
