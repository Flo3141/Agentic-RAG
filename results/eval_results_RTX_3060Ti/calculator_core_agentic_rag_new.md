# API Documentation: calculator_core

<!-- BEGIN: auto:calculator.core.CalculatorError -->
### `CalculatorError`

**Summary**
The base exception class for all calculator-related errors.

**Parameters**
- None

**Returns**
- None

**Raises**
- `CalculatorError`: This exception is raised when a calculator operation encounters an error that is not covered by specific subclasses (e.g., `CalculationLimitError`, `PrecisionError`, `TestError`).

**Examples**
```python
try:
    # Some calculator operation that might raise CalculatorError
    result = calculator.calculate(10, 20)
except CalculatorError as e:
    print(f"Calculator error: {e}")
```

**See also**
- `CalculationLimitError`
- `PrecisionError`
- `TestError`
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
A placeholder error class for test cases in the calculator module, inheriting from the base `CalculatorError` class.

**Parameters**
None

**Returns**
None

**Raises**
- `TestError`: This exception is raised when a test case fails in the calculator module.

**Examples**
```python
try:
    raise TestError()
except TestError as e:
    print(e)
```

**See also**
- `CalculatorError`: The base error class for the calculator module.
<!-- END: auto:calculator.core.TestError -->

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->
### `CalculationLimitError`

**Summary**
This exception is raised when numerical calculations in the calculator produce values that exceed predefined safe limits.

**Parameters**
- None

**Returns**
- None

**Raises**
- `CalculationLimitError`: This exception is raised by the calculator when a calculation exceeds safe limits.

**Examples**
```python
try:
    # Example of a calculation that would exceed safe limits
    result = 1e300
except CalculationLimitError as e:
    print(f"Calculation limit exceeded: {e}")
```

**See also**
- `CalculatorError`: The base exception class for all calculator errors.
- `PrecisionError`: Another subclass for precision-related errors.
- `TestError`: Another subclass for test-related errors.
<!-- END: auto:calculator.core.CalculationLimitError -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `ArithmeticOperations`

**Summary**
A class that implements basic arithmetic operations with configurable precision (up to 10 decimal places), maintaining operation history, and validating input values against class-defined `MIN_VALUE` and `MAX_VALUE` constants.

**Parameters**
- `name` (str): *Not applicable for class-level documentation*

**Returns**
- (None): *Class instances do not return values*

**Raises**
- `PrecisionError`: Raised when precision is set outside the valid range (0-10 decimal places).
- `CalculationLimitError`: Raised when input values exceed the class-defined `MIN_VALUE` or `MAX_VALUE` constraints.
- `CalculatorError`: Base exception class for all calculation-related errors.

**Examples**
```python
from arithmetic_operations import ArithmeticOperations

# Initialize with default precision
calc = ArithmeticOperations()

# Perform addition (logs to history)
result = calc.add(1.2345678901, 2.3456789012)
print(f"Addition result: {result}")

# Multiply (placeholder returns 0)
zero_result = calc.multiply(10, 20)
print(f"Multiplication result: {zero_result}")

# Access current mode
current_mode = calc.mode
print(f"Current mode: {current_mode}")
```

**See also**
- `PrecisionError`: Custom exception for invalid precision settings.
- `CalculationLimitError`: Custom exception for out-of-range values.
<!-- END: auto:calculator.core.ArithmeticOperations -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `Calculator.__init__`

**Summary**
Initializes the calculator with a specified precision.

**Parameters**
- `precision` (int): The number of decimal places for precision. Default value is 2.

**Returns**
- None

**Raises**
- `PrecisionError`: If the precision exceeds 10. The error message is "Max precision is 10."

**Examples**
```python
# Example 1: Initialize with default precision (2)
calc = Calculator()

# Example 2: Initialize with precision 5
calc = Calculator(precision=5)

# Example 3: Raises PrecisionError when precision is 11
try:
    calc = Calculator(precision=11)
except PrecisionError as e:
    print(e)  # Output: Max precision is 10.
```

**See also**
- `PrecisionError`: Custom error class for precision-related exceptions (inherits from `CalculatorError`).
- `Calculator`: The calculator class.
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `mode`

**Summary**
Returns the current operation mode of the calculator as a string.

**Parameters**
None

**Returns**
- `str`: The current operation mode (e.g., 'Standard', 'Scientific').

**Raises**
- `None`: This method does not raise exceptions.

**Examples**
```python
current_mode = calculator.mode()
print(f"Current mode: {current_mode}")
```

**See also**
- `calculator.core.CURRENT_MODE`: The module-level variable that stores the current operation mode.
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `calculator.core.ArithmeticOperations.add`

**Summary**
Safely adds two floating-point numbers with input validation, precision control, and operation logging to ensure numerical safety and auditability.

**Parameters**
- `a` (float): First number to add.
- `b` (float): Second number to add.

**Returns**
- float: The sum of `a` and `b`, rounded to `self.precision` decimal places.

**Raises**
- `calculator.core.CalculatorError`: Raised if either `a` or `b` is outside the valid range (e.g., NaN, infinity, or values exceeding precision limits).

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create an instance with precision 2
calc = ArithmeticOperations(precision=2)

# Add two numbers
result = calc.add(1.234, 2.567)
print(result)  # Output: 3.80
```

**See also**
- `calculator.core.ArithmeticOperations.subtract`
- `calculator.core.ArithmeticOperations.multiply`
- `calculator.core.ArithmeticOperations.divide`
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `ArithmeticOperations.subtract`

**Summary**
Subtracts two numbers and returns the result rounded to the class's precision.

**Parameters**
- `a` (float): First operand
- `b` (float): Second operand

**Returns**
- `float`: The result of `a - b` rounded to `self.precision` decimal places.

**Raises**
- `CalculatorError`: If the inputs are outside the valid limits (e.g., too large or too small numbers).

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create an instance with precision 2
calculator = ArithmeticOperations(2)

# Subtract 5.5 from 10.2
result = calculator.subtract(10.2, 5.5)
print(result)  # Output: 4.7
```

**See also**
- `ArithmeticOperations.add()`
- `ArithmeticOperations.multiply()`
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.multiply -->
### `calculator.core.ArithmeticOperations.multiply`

**Summary**
Placeholder implementation of the multiplication operation that currently returns 0. This method requires implementation to perform actual multiplication with the class's configurable precision (default 4).

**Parameters**
- `a` (float): First operand
- `b` (float): Second operand

**Returns**
- (float): The result of the multiplication (currently always 0)

**Raises**
- `CalculatorError`: This placeholder implementation does not raise errors. The actual implementation will raise `CalculatorError` for invalid operations.

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create an instance with default precision (4)
calculator = ArithmeticOperations()

# Multiply two numbers (placeholder returns 0)
result = calculator.multiply(2.5, 3.0)
print(result)  # Output: 0.0
```

**See also**
- `calculator.core.ArithmeticOperations.add`: Addition operation
- `calculator.core.ArithmeticOperations.subtract`: Subtraction operation
- `calculator.core.ArithmeticOperations.mode`: Mode operation
<!-- END: auto:calculator.core.ArithmeticOperations.multiply -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
### `_check_limits`

**Summary**
This internal helper method validates each input value against the predefined range [MIN_VALUE, MAX_VALUE]. If any value exceeds these limits, it raises a `CalculationLimitError` with a descriptive message.

**Parameters**
- `value` (number): The input value to be checked against the limits.

**Returns**
- (None): The method does not return a value (it raises an exception if limits are exceeded).

**Raises**
- `CalculationLimitError`: Raised when an input value exceeds the predefined limits [MIN_VALUE, MAX_VALUE].

**Examples**
```python
# Note: This method is internal and should not be called directly. This example is for demonstration purposes only.
try:
    Calculator._check_limits(1000000)
except CalculationLimitError as e:
    print(e)
```

**See also**
- `Calculator`: The main calculator class that uses this internal helper.
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `record_history`

Internal method that logs the history of an arithmetic operation by appending a formatted string to the class's `history` list and logging it at debug level. This method is called automatically by the `ArithmeticOperations` class after each operation.

**Parameters**  
None

**Returns**  
None

**Raises**  
None

**Examples**  
```python
# This method is called internally by the ArithmeticOperations class after each operation.
# It does not require any parameters.
instance.record_history()
```

**See also**  
- `ArithmeticOperations.add`  
- `ArithmeticOperations.subtract`
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->
