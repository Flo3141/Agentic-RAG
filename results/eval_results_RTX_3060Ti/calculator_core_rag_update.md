# API Documentation: calculator_core

<!-- BEGIN: auto:calculator.core.CalculatorError -->
### `calculator.core.CalculatorError`

**Summary**
A base exception class for all calculator-specific errors. This class serves as the root of the exception hierarchy in the calculator module, enabling consistent error handling for operations such as arithmetic calculations and test scenarios.

**Parameters**
None. This class has no parameters.

**Returns**
None. Exception classes do not return values; they are used to raise errors during execution.

**Raises**
None. This class is a base exception class and does not raise exceptions. Its subclasses (e.g., `TestError`) are raised by calculator operations.

**Examples**
```python
from calculator.core import TestError

try:
    raise TestError("Invalid input in test case")
except CalculatorError as e:
    print(f"Calculator error: {e}")
```

```python
from calculator.core import ArithmeticOperations

try:
    result = ArithmeticOperations.multiply(5, 0)
except CalculatorError as e:
    print(f"Arithmetic error: {e}")
```

```python
class CustomCalculatorError(CalculatorError):
    def __init__(self, message="Custom error"):
        super().__init__(message)

try:
    raise CustomCalculatorError("Invalid operation")
except CalculatorError as e:
    print(e)
```

**See also**
- `calculator.core.TestError`: A subclass of `CalculatorError` used for test-specific failures.
- `calculator.core.ArithmeticOperations`: The class that handles arithmetic operations and may raise exceptions derived from `CalculatorError`.
<!-- END: auto:calculator.core.CalculatorError -->

<!-- BEGIN: auto:calculator.core.PrecisionError -->
### `calculator.core.PrecisionError`

**Summary**  
A custom exception subclass of `CalculatorError` raised when a requested precision value (e.g., decimal places) exceeds the calculator's operational limits. This error indicates that the precision requirement is unreasonably high (e.g., 1000+ decimal places), which the calculator cannot process due to computational constraints.

**Parameters**  
- None (the class has no constructor parameters; exception instances inherit `message` from base class `CalculatorError`)

**Returns**  
- None (the class itself has no return value; exception instances propagate up the call stack)

**Raises**  
- None (the class does not raise exceptions; it is an exception type)

**Examples**  
```python
from calculator.core import ArithmeticOperations

# Initialize calculator with max precision 100
calc = ArithmeticOperations()

try:
    # Attempt to calculate with precision 1000 (exceeds max)
    result = calc.calculate(1.0, 2.0, "add", precision=1000)
except PrecisionError as e:
    print(f"Precision error: {e.message}")
```

**See also**  
- `calculator.core.CalculatorError`: Base class for all calculator exceptions.  
- `calculator.core.ArithmeticOperations`: The calculator class that raises `PrecisionError` when precision is too high.
<!-- END: auto:calculator.core.PrecisionError -->

<!-- BEGIN: auto:calculator.core.TestError -->
### `calculator.core.TestError`

**Summary**  
A lightweight, test-specific exception class for simulating error scenarios in unit tests. Inherits from `CalculatorError` and is designed to be used exclusively in testing contexts without affecting production code.

**Parameters**  
- None: The `TestError` class has no parameters. When instantiated, it requires a `message` string (inherited from the base `CalculatorError` class).

**Returns**  
- None: The `TestError` class itself does not return a value. When instantiated, it returns an exception object (instance of `TestError`).

**Raises**  
- `TestError`: A custom exception object that is raised when the class is instantiated and used in error simulation. This exception is a subclass of `CalculatorError`.

**Examples**  
```python
# Example 1: Basic Test Error Simulation (Unit Test)
from calculator.core import CalculatorError

class TestError(CalculatorError):
    """TestError for simulation purposes."""
    pass

def test_calculator_error():
    try:
        raise TestError("Test failed: Invalid input")
    except TestError as e:
        assert str(e) == "Test failed: Invalid input"
        print(f"Test passed! Error: {e}")

# Example 2: Error Handling in Calculator Logic
from calculator.core import ArithmeticOperations

class TestError(CalculatorError):
    pass

def validate_input(value):
    if value < 0:
        raise TestError("Negative values not allowed")

try:
    ArithmeticOperations._check_limits(10)
    validate_input(5)
except TestError as e:
    print(f"Validation failed: {e}")

# Example 3: Error Hierarchy Check
print("Is TestError a subclass of CalculatorError? ", issubclass(TestError, CalculatorError))
print("Does TestError inherit from Exception? ", issubclass(TestError, Exception))
```

**See also**  
- `calculator.core.CalculatorError`: The base error class for the calculator module.  
- `calculator.core.ArithmeticOperations`: The class that handles arithmetic operations and error checking.
<!-- END: auto:calculator.core.TestError -->

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->
### `CalculationLimitError`

**Summary**  
A custom exception class raised when numerical values in a calculator operation exceed predefined safe limits (e.g., maximum/minimum representable values, precision thresholds, or computational constraints). This class inherits from `CalculatorError` and enforces safe calculation boundaries by signaling invalid input ranges.

**Parameters**  
- `message` (str, optional): A human-readable error message describing why limits were exceeded (e.g., `"Value exceeds safe limits"`). Required when raising an instance of the exception.

**Returns**  
- None: This class does not return anything. It is an exception class, not a function or method.

**Raises**  
- `CalculationLimitError`: Instances of this class are raised by the calculator's code (specifically in `ArithmeticOperations._check_limits`) when input values exceed safe limits.

**See also**  
- `CalculatorError`: The base exception class for all calculator-specific errors.  
- `ArithmeticOperations`: The class that uses this exception during pre-calculation validation.
<!-- END: auto:calculator.core.CalculationLimitError -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `calculator.core.ArithmeticOperations`

**Summary**  
The `ArithmeticOperations` class is a configurable calculator designed for robust arithmetic operations with three key features:  
- **Precision control**: Rounds results to a user-specified number of decimal places (default: `DEFAULT_PRECISION`, max 10)  
- **Operation auditing**: Logs all operations to a history list (`self.history`) with debug-level logging  
- **Input validation**: Enforces bounds checks on operands using `MIN_VALUE`/`MAX_VALUE` (prevents overflow/underflow)  
- **Mode tracking**: Provides a read-only `mode` property for operation context (e.g., `"basic"`, `"scientific"`)

**Critical Note**  
The `multiply` method is **broken** (currently returns `0` instead of the actual product). This is a critical bug that must be fixed by implementing the multiplication operation.

**Parameters**  
- `precision` (int): Number of decimal places for rounding (default: `DEFAULT_PRECISION`). Must be between 0 and 10 (inclusive).

**Returns**  
- `None`: The `__init__` method initializes the calculator state and does not return a value.  
- `str`: The `mode` property returns the current operation mode (e.g., `"basic"`).  
- `float`: The `add` method returns the rounded sum of two operands to `self.precision` decimal places. The `subtract` method returns the rounded difference. The `multiply` method **currently returns `0`** (broken implementation; should return the product rounded to `self.precision` decimal places).

**Raises**  
- `PrecisionError`: Raised when the `precision` parameter in `__init__` exceeds 10 (max precision is 10).  
- `CalculationLimitError`: Raised when an operand exceeds the defined bounds (`MIN_VALUE` or `MAX_VALUE`).

**Examples**  
```python
from calculator.core import ArithmeticOperations

# Initialize with default precision (e.g., 4)
calc = ArithmeticOperations()

# Add two numbers (rounds to 4 decimals)
result = calc.add(1.23456, 2.78901)
print(f"Result: {result:.4f}")  # Output: 4.0236
print(f"History: {calc.history}")  # Output: ['add(1.23456, 2.78901) = 4.0236']

# Subtraction (valid)
result = calc.subtract(10.5, 3.2)
print(f"Result: {result:.2f}")  # Output: 7.30

# Multiplication (broken implementation - returns 0)
result = calc.multiply(2.0, 3.0)  # Output: 0.0 (should be 6.0)
print(f"Result: {result}")  # Output: 0.0

# Input validation (error handling)
try:
    calc.add(1e100, 0.0)  # Exceeds MAX_VALUE
except CalculationLimitError as e:
    print(e)  # Output: "Value 1e+100 exceeds limits."

# Precision validation
try:
    calc = ArithmeticOperations(precision=11)  # Exceeds max precision
except PrecisionError as e:
    print(e)  # Output: "Max precision is 10."

# Mode property
print(calc.mode)  # Output: "basic"
```

**See also**  
- [Calculator Core Module](index.md) for other components.
<!-- END: auto:calculator.core.ArithmeticOperations -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `calculator.core.ArithmeticOperations.__init__`

**Summary**
Initializes a calculator instance by validating and enforcing a maximum precision of 10 decimal places, setting the precision for all subsequent rounding operations, initializing an empty history list to track operation strings, and logging the initialization configuration.

**Parameters**
- `precision` (int): Number of decimal places for rounding calculations. Default value is `DEFAULT_PRECISION` (a module-level constant, typically `4` for financial calculators). The method validates that `precision` does not exceed `10`.

**Returns**
- (None): The `__init__` method returns `None`.

**Raises**
- `PrecisionError`: Raised when `precision` is greater than `10`. Message: `"Max precision is 10."`

**Examples**
```python
# Example 1: Initialize with default precision
from calculator.core import ArithmeticOperations

calculator = ArithmeticOperations()

# Behavior: Uses DEFAULT_PRECISION (e.g., 4 decimal places)
# History: []
# Log: "Initialized with precision=4"

# Example 2: Initialize with custom precision
calculator = ArithmeticOperations(precision=5)

# Behavior: Sets rounding to 5 decimal places
# Log: "Initialized with precision=5"

# Example 3: Handle invalid precision (raises exception)
try:
    calculator = ArithmeticOperations(precision=11)
except PrecisionError as e:
    print(e)  # Output: "Max precision is 10."

# Example 4: Full workflow with history tracking
calculator = ArithmeticOperations(precision=2)
calculator.add(2.34, 1.56)  # Adds with 2 decimals
calculator.multiply(3.14, 2)  # Multiplies with 2 decimals

print(calculator.history)  # Output: ["2.34 + 1.56", "3.14 * 2"]
```

**See also**
- `calculator.core.ArithmeticOperations.multiply`: Core operation method that uses the configured precision.
- `calculator.core.ArithmeticOperations.history`: List of operation strings (e.g., `"2.34 + 1.56"`).
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `calculator.core.ArithmeticOperations.mode`

**Summary**  
The `mode` method is a **read-only accessor** for the current operation mode of the `ArithmeticOperations` calculator instance. It returns a string representing the active mode (e.g., `"add"`, `"subtract"`, `"multiply"`, `"divide"`) without modifying the calculator's state.

**Parameters**  
- `self` (object): Required instance of `ArithmeticOperations`

**Returns**  
- `str`: A string representing the current operation mode (e.g., `"add"`, `"subtract"`, `"multiply"`, `"divide"`). The exact value depends on the calculator's internal state.

**Raises**  
- `NameError`: If `current_mode` is undefined in the class scope (e.g., missing initialization)  
- `AttributeError`: If `current_mode` is not an instance variable (e.g., class-level variable misconfiguration)

**Examples**  
```python
# Example 1: Basic usage
calculator = ArithmeticOperations()
print(calculator.mode)  # Output: "add"

# Example 2: Conditional operation
if calculator.mode == "add":
    result = calculator.add(2, 3)
else:
    result = calculator.multiply(2, 3)

# Example 3: Verify mode after state change
calculator.set_mode("multiply")
print(calculator.mode)  # Output: "multiply"

# Example 4: Handling potential exceptions
try:
    print(calculator.mode)
except NameError as e:
    print(f"NameError: {e}")
except AttributeError as e:
    print(f"AttributeError: {e}")
```

**See also**  
- `calculator.core.ArithmeticOperations`: Main calculator class  
- `calculator.core.ArithmeticOperations._current_mode`: Instance variable storing the active operation mode  
- `calculator.core.ArithmeticOperations._log_op`: Private method that logs operation details  
- `calculator.core.ArithmeticOperations.multiply`: Multiplication operation (only active in `"multiply"` mode)  
- `calculator.core.ArithmeticOperations.subtract`: Subtraction operation (only active in `"subtract"` mode)
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `calculator.core.ArithmeticOperations.add`

**Summary**
Safely performs floating-point addition with input validation, precision control, and operation logging. Ensures operands comply with predefined limits, computes the sum rounded to the instance's precision (`self.precision`), and records the operation in a structured log format.

**Parameters**
- `a` (`float`): First operand (e.g., `1.234`)
- `b` (`float`): Second operand (e.g., `5.678`)

**Returns**
- `float`: Rounded sum of `a` and `b` to `self.precision` decimal places.

**Raises**
- `ValueError`: If operands exceed the system-defined limits (e.g., numbers must be between `-1e10` and `1e10`)
- `TypeError`: If `self.precision` is not a non-negative integer (e.g., precision must be an integer)
- `Exception`: If logging fails (e.g., the logging system is down)

**Examples**
```python
from calculator.core import ArithmeticOperations

# Initialize with 2 decimal places (common for currency)
calc = ArithmeticOperations(precision=2)
result = calc.add(123.456, 78.901)
print(result)  # Output: 202.36 (rounded to 2 decimals)
```

```python
calc = ArithmeticOperations(precision=3)
try:
    calc.add(1e15, 1e15)  # Exceeds typical limits
except ValueError as e:
    print(f"Validation failed: {e}")  # Output: "Numbers exceed maximum allowed range (1e10)"
```

```python
calc = ArithmeticOperations(precision=1)
calc.add(3.1, 2.9)  # Logs: "add: 3.1 + 2.9 = 6.0"
# Log entry stored in `_log_op` (e.g., database/file)
```

**See also**
- `calculator.core.ArithmeticOperations`: The class that manages precision and logging
- `decimal`: For monetary calculations, use the `decimal` module to avoid floating-point rounding issues (this method uses standard floating-point rounding)
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `calculator.core.ArithmeticOperations.subtract`

**Summary**
The `subtract` method performs **floating-point subtraction** with **precision enforcement** and **operation logging**. It calculates `a - b`, rounds the result to the instance's precision level (`self.precision`), and records the operation in a structured log format. This method is part of a robust calculator class designed for financial/technical applications where precision control and auditability are critical.

**Parameters**
- `a` (float): Minuend (the number from which another number is subtracted)
- `b` (float): Subtrahend (the number to be subtracted from `a`)

**Returns**
- (float): Rounded result of `a - b` to `self.precision` decimal places

**Raises**
- `CalculatorError`: If `a` or `b` violate operational limits (e.g., values outside [0, 100] for financial calculations)

**Examples**
```python
# Example 1: Basic subtraction with rounding
from sample_project.src.calculator.core import ArithmeticOperations

calc = ArithmeticOperations(precision=2)
result = calc.subtract(10.123, 2.456)
print(result)  # Output: 7.67
```

```python
# Example 2: Handling invalid limits (raises CalculatorError)
calc = ArithmeticOperations(precision=2)

try:
    calc.subtract(100.5, 1.0)
except calculator.core.CalculatorError as e:
    print(f"Operation failed: {e}")  # Output: "Operand 'a' (100.5) exceeds maximum allowed value of 100.0"
```

```python
# Example 3: Edge case (precision=0)
calc = ArithmeticOperations(precision=0)
result = calc.subtract(1.234, 0.567)
print(result)  # Output: 1.0
```

**See also**
- `calculator.core.ArithmeticOperations.multiply`
- `calculator.core.ArithmeticOperations._log_op`
- `calculator.core.CalculatorError`
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.multiply -->
### `calculator.core.ArithmeticOperations.multiply`

**Summary**
Placeholder implementation for multiplication that always returns `0.0` (a hardcoded test value). This method is **not functional** and should be replaced with the standard multiplication logic (`a * b`). It is explicitly marked as a temporary placeholder for development purposes.

**Parameters**
- `a` (float): First operand (a numeric value to be multiplied).
- `b` (float): Second operand (a numeric value to be multiplied).

**Returns**
- (float): Always `0.0` (hardcoded test value). *This method does not perform actual multiplication and is not production-ready.*

**Raises**
- None (current implementation). *A production implementation should raise `TypeError` for non-numeric inputs.*

**Examples**
```python
from calculator.core import ArithmeticOperations

# Test usage (current behavior)
calc = ArithmeticOperations()
result = calc.multiply(2.5, 3.0)  # Always returns 0.0
print(result)  # Output: 0.0
```

**See also**
- `calculator.core.ArithmeticOperations.subtract`
- `calculator.core.ArithmeticOperations.mode`
<!-- END: auto:calculator.core.ArithmeticOperations.multiply -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
### `calculator.core.ArithmeticOperations._check_limits`

**Summary**  
Internal validation helper for the `ArithmeticOperations` class that ensures all input values passed to arithmetic operations (e.g., `subtract`, `multiply`) fall within predefined numerical bounds (`MIN_VALUE` to `MAX_VALUE`). This method iterates through each input value, checks if it exceeds the allowed range, and immediately raises a custom exception if any value is invalid.

**Parameters**  
- `self` (object): Instance of the `ArithmeticOperations` class (required for all instance methods)  
- `*args` (tuple): Variable-length positional arguments to be validated. **Expected type**: Numeric values (int or float). The method does not validate input types (e.g., strings) — this is intentional for performance and assumes inputs are pre-validated by higher-level methods.

**Returns**  
- `None`: The method does not return a value. It performs validation and raises exceptions if invalid inputs are detected.

**Raises**  
- `CalculationLimitError`: Raised when any value in `args` violates the range `[MIN_VALUE, MAX_VALUE]`. The exception message is formatted as `f"Value {val} exceeds limits."`. This exception is raised immediately upon the first invalid value (no further checks).

**Examples**  
```python
from calculator.core import ArithmeticOperations

class ArithmeticOperations:
    MIN_VALUE = -1000
    MAX_VALUE = 1000

op = ArithmeticOperations()

op._check_limits(500, -200)  # Passes validation (both within [-1000, 1000])
op._check_limits(2000)  # Raises CalculationLimitError: "Value 2000 exceeds limits."
op._check_limits(1500, -500)  # Raises immediately for 1500 (no check for -500)
```

**See also**  
- `calculator.core.ArithmeticOperations.subtract`  
- `calculator.core.ArithmeticOperations.multiply`
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `Calculator._log_op`

**Summary**  
Internal helper method for recording operation history in the calculator class. This method is **not intended for direct user calls**. It formats an operation string (e.g., `add(2.0, 3.0) = 5.0`), appends it to the class's `history` list, and logs it at the `DEBUG` level using Python's `logging` module. The method is **stateless** and **void** (does not return a value).

**Parameters**  
- `self` (object): Instance of the calculator class (required for class methods)  
- `op` (str): **Operation name** (e.g., `"add"`, `"subtract"`, `"multiply"`, `"mode"`). Must match valid operation names defined in `calculator.core.ArithmeticOperations`.  
- `a` (float): First operand (e.g., `2.0` for `add(2.0, 3.0)`)  
- `b` (float): Second operand (e.g., `3.0` for `add(2.0, 3.0)`)  
- `res` (float): Result of the operation (e.g., `5.0` for `add(2.0, 3.0)`)

**Returns**  
- (None): This method does not return any value (void method).

**Raises**  
- `TypeError`: If `a`, `b`, or `res` is not a `float` (e.g., `int`, `str`, `None`)  
- `ValueError`: If `op` is not a valid operation name (e.g., `"invalid_op"`). Valid `op` values must be one of `{"add"}`, `{"subtract"}`, `{"multiply"}`, `{"mode"}` as defined in `calculator.core.ArithmeticOperations`.  
- `AttributeError`: If `self.history` is not a list (e.g., `None`, `dict`, `int`)  
- `RuntimeError`: If the logging system is misconfigured (e.g., `logger` is not initialized or `logger.debug` fails)  
- `OSError`: In rare cases, if file I/O errors occur during logging (e.g., disk full)

**Examples**  
```python
# After a successful 'multiply' operation
result = self.multiply(4.0, 5.0)  # Returns 20.0
self._log_op("multiply", 4.0, 5.0, result)  # Logs: "multiply(4.0, 5.0) = 20.0"

# After a 'subtract' operation
result = self.subtract(10.0, 3.0)  # Returns 7.0
self._log_op("subtract", 10.0, 3.0, result)  # Logs: "subtract(10.0, 3.0) = 7.0"

# After a 'mode' (modulo) operation
result = self.mode(10.0, 3.0)  # Returns 1.0 (10 % 3)
self._log_op("mode", 10.0, 3.0, result)  # Logs: "mode(10.0, 3.0) = 1.0"
```

**See also**  
- `calculator.core.ArithmeticOperations`: Defines valid operation names (`"add"`, `"subtract"`, `"multiply"`, `"mode"`)  
- `Calculator.history`: The list where operation history is stored
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->
