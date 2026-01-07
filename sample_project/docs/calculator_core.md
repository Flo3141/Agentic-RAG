# API Documentation: calculator_core

<!-- BEGIN: auto:calculator.core.CalculatorError -->
### `CalculatorError`

**Summary**
Base error class for calculator operations. This class now has a subclass `CalculationLimitError` for handling numerical limits.

**Parameters**
- None

**Returns**
- None

**Raises**
- `CalculatorError`: Base error class for calculator operations.

**Examples**
```python
try:
    # Example usage where CalculatorError might be raised
    result = calculate(10, 0)
except CalculatorError as e:
    print(f"Calculator error: {e}")
```

**See also**
- `CalculationLimitError`: Subclass for handling numerical limits.
<!-- END: auto:calculator.core.CalculatorError -->

<!-- BEGIN: auto:calculator.core.PrecisionError -->
### `PrecisionError`

**Summary**
An exception raised when the requested precision value exceeds the maximum allowable precision limit in the calculator system.

**Parameters**
None.

**Returns**
None.

**Raises**
- `PrecisionError`: This exception is raised when the requested precision value exceeds the maximum allowable precision limit.

**Examples**
```python
try:
    calculator.calculate(value=1.23456789, precision=20)
except PrecisionError as e:
    print(f"Precision error: {e}")
```

**See also**
- `CalculatorError`: The base class for all calculator-related exceptions.
<!-- END: auto:calculator.core.PrecisionError -->

<!-- BEGIN: auto:calculator.core.TestError -->
### `TestError`

**Summary**
A test-specific error class used to simulate error scenarios in calculator test cases without additional implementation. This class inherits from `CalculatorError` and is intentionally empty to facilitate test-driven development.

**Parameters**
None. This class has no constructor parameters.

**Returns**
None. This class does not return any values.

**Raises**
- `CalculatorError`: When an instance of `TestError` is raised, it is treated as a `CalculatorError` exception.

**Examples**
```python
try:
    raise TestError()
except CalculatorError as e:
    print(f"Caught error: {e}")
```

**See also**
- `CalculatorError`: The base class for all calculator errors.
- `PrecisionError`: A specific error for precision-related issues.
- `CalculationLimitError`: A specific error for calculation limit violations.
<!-- END: auto:calculator.core.TestError -->

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->
### `CalculationLimitError`

**Summary**
A specialized exception class raised when numerical values exceed safe operational limits during calculator calculations.

**Parameters**
- None

**Returns**
- None

**Raises**
- `CalculationLimitError`: Raised when numerical values exceed safe operational limits during calculator calculations.

**Examples**
```python
try:
    # Example: Attempting to calculate with a value that exceeds safe limits
    result = 1e300
except CalculationLimitError as e:
    print(f"Error: {e}")
```

**See also**
- `calculator.core.CalculatorError`: The base exception class for calculator errors.
- `ArithmeticOperations._check_limits`: The method that triggers this exception.
<!-- END: auto:calculator.core.CalculationLimitError -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `ArithmeticOperations`

**Summary**  
A calculator class that performs basic arithmetic operations (addition, subtraction, and multiplication) with configurable precision (up to 10 decimal places). The class validates input values against the range [MIN_VALUE, MAX_VALUE] (where MIN_VALUE = -1e300 and MAX_VALUE = 1e300), rounds results to the specified precision, and logs each operation to a history list. The class uses Python's logging module for auditing operations at the debug level.

**Constructor Parameters**  
- `precision` (int, optional): The number of decimal places for arithmetic operations. Default is 8. Must be an integer between 8 and 10 (inclusive).

**Returns**  
- (object): An instance of `ArithmeticOperations`.

**Raises**  
- `PrecisionError`: When the specified precision is not an integer in the range [8, 10].  
- `CalculationLimitError`: When input values are outside the range [MIN_VALUE, MAX_VALUE] (MIN_VALUE = -1e300, MAX_VALUE = 1e300).

**Methods**  
- `add(a, b)`: Adds two numbers with precision validation and logs the operation to the history list. The result is rounded to the specified precision. The operation is also logged via debug-level logging.  
- `subtract(a, b)`: Subtracts two numbers with precision validation and logs the operation to the history list. The result is rounded to the specified precision. The operation is also logged via debug-level logging.  
- `multiply(a, b)`: Placeholder method that returns 0 (not implemented for actual multiplication). This method is intentionally left as a test function.

**Properties**  
- `mode`: A string property that always returns `'standard'`.

**Examples**  
```python
from arithmetic_operations import ArithmeticOperations

# Initialize with default precision (8)
calc = ArithmeticOperations()

# Perform addition
result = calc.add(1.23456789, 2.3456789)
print(result)  # Output: 3.57924679

# Perform subtraction
result = calc.subtract(5.0, 3.0)
print(result)  # Output: 2.0

# Multiply (placeholder)
result = calc.multiply(10, 20)
print(result)  # Output: 0

# Get mode
print(calc.mode)  # Output: 'standard'
```

**See also**  
- `PrecisionError`: Custom exception for precision validation.  
- `CalculationLimitError`: Custom exception for input range validation.
<!-- END: auto:calculator.core.ArithmeticOperations -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `Calculator`

**Summary**
A class for performing arithmetic calculations with configurable precision and maintaining a history of user operations.

**Parameters**
- `precision` (int): The number of decimal places for rounding calculations. Default value is 10. Must be ≤10.

**Returns**
- `Calculator`: The Calculator instance.

**Raises**
- `PrecisionError`: Raised if the provided precision exceeds 10.

**Examples**
```python
from calculator import Calculator

# Initialize calculator with precision 5
calc = Calculator(precision=5)

# Perform addition
result = calc.add(2.5, 3.7)
print(result)  # Output: 6.2

# Check history
print(calc.history)  # Output: ['2.5 + 3.7 = 6.2']
```

**See also**
- `PrecisionError`: Custom exception raised when precision validation fails.
- `logger`: Module for logging initialization events.
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `mode`

**Summary**
Returns the current operation mode as a string. This calculator always operates in standard mode, so the method returns the string "Standard".

**Parameters**
None

**Returns**
- `str`: The current operation mode string, which is always "Standard".

**Raises**
- `None`: This method does not raise any exceptions.

**Examples**
```python
calculator = Calculator()
current_mode = calculator.mode()
print(current_mode)  # Output: "Standard"
```

**See also**
- `Calculator.set_mode`: Method to change the operation mode.
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `ArithmeticOperations.add`

**Summary**
Adds two floating-point numbers with safety checks to prevent overflow/underflow and rounds the result to the instance's precision.

**Parameters**
- `a` (float): First operand
- `b` (float): Second operand

**Returns**
- (float): The sum of `a` and `b`, rounded to `self.precision` decimal places.

**Raises**
- `ValueError`: If either operand is outside the acceptable numerical range (e.g., causing potential overflow or underflow).

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create an instance with precision 2
calc = ArithmeticOperations(precision=2)
result = calc.add(1.234, 5.678)
print(result)  # Output: 6.91
```

**See also**
- `calculator.core.ArithmeticOperations._check_limits`: Validates input limits to prevent overflow/underflow.
- `calculator.core.ArithmeticOperations._log_op`: Logs the operation for audit purposes.
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `subtract`

**Summary**
Subtracts two numbers.

**Parameters**
- `a` (float): First number
- `b` (float): Second number

**Returns**
- (float): The result of subtracting `b` from `a`.

**Raises**
- `ValueError`: If the operation cannot be performed (e.g., division by zero)
- `CalculationLimitError`: If the value of `a` or `b` is outside the defined limits (MIN_VALUE and MAX_VALUE)

**Examples**
```python
# Example 1: Basic subtraction
result = subtract(10.5, 3.2)
print(result)  # Output: 7.3

# Example 2: Handling CalculationLimitError
try:
    subtract(float('inf'), 0)
except CalculationLimitError as e:
    print(e)
```

**See also**
None
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.multiply -->
### `multiply`

**Summary**
Multiplies two numbers.

**Parameters**
- `a` (float): First number
- `b` (float): Second number

**Returns**
- (float): The product of `a` and `b`

**Raises**
- `ValueError`: If the operation cannot be performed (e.g., division by zero)
- `CalculationLimitError`: If the values of `a` or `b` are outside the defined limits (MIN_VALUE and MAX_VALUE)

**Examples**
```python
result = multiply(2.5, 3.0)
print(result)  # Output: 7.5

try:
    multiply(1e300, 1e300)
except CalculationLimitError as e:
    print(e)
```

**See also**
- `add`: Adds two numbers.
- `subtract`: Subtracts two numbers.
<!-- END: auto:calculator.core.ArithmeticOperations.multiply -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
### `_check_limits`

**Summary**
A private method that validates input values against the class-defined `MAX_VALUE` and `MIN_VALUE` constants to prevent overflow or underflow during arithmetic operations.

**Parameters**
- `value` (float): The numerical value to validate.

**Returns**
- None: This method does not return a value; it raises an exception if validation fails.

**Raises**
- `CalculationLimitError`: Raised when a value exceeds the class-defined `MAX_VALUE` or `MIN_VALUE` constants.

**Examples**
```python
ArithmeticOperations._check_limits(1000)
```

**See also**
- `ArithmeticOperations`: The class that defines this method and its numerical constraints.
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `_log_op`

**Summary**
Records an arithmetic operation's input and result in the class history and logs the operation at debug level.

**Parameters**
- `op` (str): Name of the arithmetic operation (e.g., "multiply", "subtract").
- `a` (float): First operand.
- `b` (float): Second operand.
- `res` (float): Result of the operation.

**Returns**
- `None`: The method does not return any value.

**Raises**
- `None`: No exceptions are raised by this method.

**Examples**
```python
_log_op(op="multiply", a=2.0, b=3.0, res=6.0)
```

**See also**
- `ArithmeticOperations.multiply`
- `ArithmeticOperations.subtract`
- `ArithmeticOperations.mode`
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->
