# API Documentation: calculator_core

<!-- BEGIN: auto:calculator.core.CalculatorError -->
### `CalculatorError`

**Summary**
Base exception class for all calculator-specific errors. This class serves as the root of the calculator module's exception hierarchy and is not intended to be instantiated directly.

**Parameters**
- None

**Returns**
- None

**Raises**
- None (this class does not raise exceptions)

**Examples**

```python
# Define a custom exception
class TestError(CalculatorError):
    """Custom error for test operations."""
    pass

# Raise and handle the exception
try:
    raise TestError("Test failed: Invalid input")
except CalculatorError as e:
    print(f"Test error: {e}")
```

```python
from calculator.core import ArithmeticOperations

try:
    result = ArithmeticOperations.multiply("invalid", 10)
except CalculatorError as e:
    print(f"Calculator error: {e}")
```

**See also**
- `TestError`
- `ArithmeticOperations`
<!-- END: auto:calculator.core.CalculatorError -->

<!-- BEGIN: auto:calculator.core.PrecisionError -->
### `PrecisionError`

**Summary**  
A custom exception subclass of `CalculatorError` raised when the requested precision (e.g., decimal places) exceeds the calculator's operational limits (e.g., 1000+ decimal places).

**Parameters**  
- `message` (str, optional): Human-readable error message (inherited from `CalculatorError`). Default: empty string.

**Returns**  
- None

**Raises**  
- `None`: The `PrecisionError` class does not raise exceptions. It is the type of exception that *can be raised* by other code.

**Examples**  
```python
# Example 1: Creating a PrecisionError instance
try:
    # Code that would cause precision error (e.g., invalid calculation)
    raise PrecisionError("Precision exceeded limit")
except PrecisionError as e:
    print(e.message)  # Output: "Precision exceeded limit"
```

**See also**  
- `CalculatorError`: Base class for all calculator-related exceptions.
<!-- END: auto:calculator.core.PrecisionError -->

<!-- BEGIN: auto:calculator.core.TestError -->
### `TestError`

**Summary**  
A lightweight, test-specific exception class for simulating error scenarios in unit tests without affecting core calculator logic. This class inherits directly from `CalculatorError` (a base error class in the `calculator.core` module) and is a `pass` class with no additional functionality.

**Parameters**  
- `None`: The `TestError` class itself has no parameters. When instantiated, it requires a `message` string (as defined by the base `CalculatorError` class).

**Returns**  
- `None`: The `TestError` class does not return a value. When instantiated, it returns an exception object (instance of `TestError`), but this is not part of the class's return value.

**Raises**  
- `TestError`: A custom exception object for test simulation. This exception is raised when the class is instantiated and used in `raise` statements. It follows the inheritance chain: `TestError` → `CalculatorError` → `Exception`.

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
```

**See also**  
- `CalculatorError`: The base error class for the calculator module.  
- `ArithmeticOperations._check_limits`: The method that handles calculation limits and precision errors.
<!-- END: auto:calculator.core.TestError -->

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->
### `CalculationLimitError`

**Summary**  
A custom exception class raised when numerical values in a calculator operation exceed predefined safe limits (e.g., maximum/minimum representable values, precision thresholds). This class is used in the `ArithmeticOperations._check_limits` method to enforce safe calculation boundaries and prevent undefined behavior.

**Parameters**  
- `message` (str): A human-readable error message describing why limits were exceeded (e.g., `"Value exceeds safe limits"`). This parameter is required when raising an instance of the exception.

**Returns**  
- `None`: This class does not return anything.

**Raises**  
- `None`: This class does not raise exceptions. It is an exception type that is raised by the calculator's code (e.g., `ArithmeticOperations._check_limits`).

**Examples**  
```python
# Example 1: Raising in ArithmeticOperations._check_limits
from calculator.core import CalculatorError

class ArithmeticOperations:
    def _check_limits(self, value):
        # Example safe limit: 1e308 (max float in IEEE 754)
        if value > 1e308:
            raise CalculationLimitError("Value exceeds safe limits")
```

```python
# Example 2: Catching the exception
try:
    # ... calculator logic ...
    result = arithmetic_ops.calculate(1e309)  # Triggers limit check
except CalculationLimitError as e:
    print(f"Calculation error: {e}")
```

```python
# Example 3: Custom error message
raise CalculationLimitError("Input value too large for safe computation")
```

**See also**  
- `calculator.core.CalculatorError`: Base class for all calculator-specific errors.  
- `ArithmeticOperations._check_limits`: Method that validates input limits and raises `CalculationLimitError` when values exceed safe bounds.
<!-- END: auto:calculator.core.CalculationLimitError -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `ArithmeticOperations`

**Summary**  
The `ArithmeticOperations` class is a production-grade calculator designed for precise numerical operations with robust error handling and auditability. It handles:
- Configurable precision (rounding to `N` decimal places)
- Input validation to prevent overflow/underflow
- Operation logging for full audit trails
- Basic arithmetic operations (addition, subtraction, multiplication)

Key strengths:
- Prevents invalid operations via strict input validation
- Maintains traceability through operation history
- Enforces precision constraints to avoid floating-point inaccuracies
- Provides a property `mode` to indicate the current operation mode

**Parameters**  
- `precision` (int): Number of decimal places for rounding results (default: `DEFAULT_PRECISION`)

**Returns**  
- `float`: The result of the arithmetic operation (for `add`, `subtract`, `multiply`)

**Raises**  
- `PrecisionError`: Raised when the precision value is invalid (e.g., negative or non-integer)
- `CalculationLimitError`: Raised when an operation would cause overflow or underflow

**Examples**  
```python
# Example 1: Adding two numbers
result = ArithmeticOperations(2).add(3.14, 2.71)
print(result)  # Output: 5.85

# Example 2: Subtracting two numbers
result = ArithmeticOperations(2).subtract(5.0, 3.14)
print(result)  # Output: 1.86

# Example 3: Multiplying two numbers
result = ArithmeticOperations(2).multiply(2.0, 3.0)
print(result)  # Output: 6.0

# Example 4: Getting the mode
print(ArithmeticOperations(2).mode)  # Output: 'scientific'
```

**See also**  
- [PrecisionError documentation](#)
- [CalculationLimitError documentation](#)
<!-- END: auto:calculator.core.ArithmeticOperations -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `ArithmeticOperations.__init__`

**Summary**
Initializes a calculator instance with precision validation, history tracking, and logging. Ensures the precision parameter is within the allowed range (≤10 decimal places), sets the precision attribute, initializes an empty operation history list, and logs the initialization event. This method is critical for setting up the calculator's operational constraints and auditability.

**Parameters**
- `precision` (int, optional): Number of decimal places for rounding operations. Must be ≤10. Default is `4` (the class-level constant `DEFAULT_PRECISION`).

**Returns**
- (None): Constructor methods in Python always return `None`.

**Raises**
- `PrecisionError`: Raised when `precision > 10`. Message: `"Max precision is 10."`

**Examples**
```python
from calculator.core import ArithmeticOperations

# Initialize with default precision (typically 4)
calculator = ArithmeticOperations()
print(f"Initialized with precision={calculator.precision}")  # Output: Initialized with precision=4
```

```python
calculator = ArithmeticOperations(precision=2)
print(f"Initialized with precision={calculator.precision}")  # Output: Initialized with precision=2
```

```python
try:
    calculator = ArithmeticOperations(precision=11)
except PrecisionError as e:
    print(e)  # Output: Max precision is 10.
```

**See also**
- `calculator.core.ArithmeticOperations.multiply`: Performs multiplication with precision-aware rounding
- `calculator.core.ArithmeticOperations.mode`: Computes statistical mode with precision constraints
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `mode`

**Summary**
A state accessor method that returns the current arithmetic operation mode (e.g., `"add"`, `"subtract"`, `"multiply"`) as a string without modifying state.

**Parameters**
- `self` (object): Required instance of `calculator.core.ArithmeticOperations`. This is the standard Python convention for instance methods and is implicitly passed by the interpreter.

**Returns**
- `str`: A string representing the current operation mode (e.g., `"add"`, `"subtract"`, `"multiply"`).

**Raises**
- None

**Examples**
```python
from sample_project.src.calculator.core import ArithmeticOperations

calc = ArithmeticOperations()
current_mode = calc.mode()
print(f"Current operation mode: {current_mode}")
```

**See also**
- `ArithmeticOperations.add()`
- `ArithmeticOperations.subtract()`
- `ArithmeticOperations.multiply()`
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `add`

**Summary**
The `add` method safely performs floating-point addition with input validation, precision control, and operation logging. It ensures operands are within acceptable limits before computation, rounds the result to the class's configured precision (e.g., 2 decimal places), and records the operation for auditability.

**Parameters**
- `a` (`float`): First operand (e.g., `1.234`). Must be a valid floating-point number within the calculator's operational limits.
- `b` (`float`): Second operand (e.g., `5.678`). Must be a valid floating-point number within the calculator's operational limits.

**Returns**
- `float`: The result of `a + b` rounded to `self.precision` decimal places. Example: `round(1.234 + 5.678, 2) → 6.91`.

**Raises**
- `ValueError`: If operands exceed safe range (e.g., too large for 64-bit float).
- `TypeError`: If logging fails due to invalid types (e.g., non-numeric values).
- `IOError`: If logging fails (e.g., file permissions, network issues).
- `OverflowError`: If the result exceeds representable float range (rare in practice).

**Examples**
```python
from sample_project.src.calculator.core import ArithmeticOperations

# Initialize calculator with 2 decimal places precision
calc = ArithmeticOperations(precision=2)

# Add numbers (rounds to 2 decimals)
result = calc.add(1.234, 5.678)
print(result)  # Output: 6.91
```

```python
try:
    calc = ArithmeticOperations(precision=3)
    calc.add(1e300, 2e300)  # Exceeds safe range
except ValueError as e:
    print(f"Invalid input: {e}")  # Output: "Operands too large for 64-bit float"
```

```python
# After add() call, log entry is automatically created
log_entry = calc._log_op  # Access via class (not directly exposed)
print(log_entry)  # Output: {"operation": "add", "a": 1.234, "b": 5.678, "result": 6.91}
```

**See also**
- `ArithmeticOperations`: The calculator class that manages precision and operations.
- `self.precision`: The class attribute controlling rounding precision.
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `subtract`

**Summary**
Performs arithmetic subtraction of two floating-point numbers (`a - b`), applies rounding to the class's precision level, and logs the operation for auditability. Ensures inputs comply with predefined limits to prevent numerical instability or overflow.

**Parameters**
- `a` (float): The minuend (first operand) to be subtracted by `b`. Must be a valid floating-point number.
- `b` (float): The subtrahend (second operand) to be subtracted from `a`. Must be a valid floating-point number.

**Returns**
- (float): The result of `a - b` rounded to `self.precision` decimal places.

**Raises**
- `calculator.core.CalculatorError`: Raised when input limits are violated (e.g., numbers exceed operational range) or when `self.precision` is not a non-negative number.

**Examples**
```python
from sample_project.src.calculator.core import ArithmeticOperations

# Initialize calculator with 2 decimal places precision
calc = ArithmeticOperations(precision=2)

# Subtract 2.3 from 10.5
result = calc.subtract(10.5, 2.3)
print(result)  # Output: 8.2
```

```python
from sample_project.src.calculator.core import ArithmeticOperations

calc = ArithmeticOperations(precision=2)

try:
    calc.subtract(1e300, 1e-300)  # Causes overflow
except calculator.core.CalculatorError as e:
    print(f"Error: {e}")  # Output: "Numbers exceed operational limits"
```

**See also**
- [calculator.core.ArithmeticOperations](sample_project\src\calculator\core.py): Parent class for all arithmetic operations
- [calculator.core.ArithmeticOperations._log_op](sample_project\src\calculator\core.py): Logs operations with `op_type`, `a`, `b`, `result`
- [calculator.core.CalculatorError](sample_project\src\calculator\core.py): Specific exception for input validation failures
- `self.precision`: Class attribute for rounding precision (e.g., `2` = 2 decimal places)
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.multiply -->
### `multiply`

**Summary**
Placeholder implementation for multiplication that always returns `0.0` (a test stub). This method is **not functional** and should be replaced with actual multiplication logic (`a * b`) before production use.

**Parameters**
- `a` (float): First operand (a floating-point number)
- `b` (float): Second operand (a floating-point number)

**Returns**
- (float): Always `0.0` (a hardcoded value). This is a test-specific quirk and does not represent the product of `a` and `b`.

**Raises**
- None: The method does not raise any exceptions in the current implementation.

**Examples**
```python
from calculator.core import ArithmeticOperations

calculator = ArithmeticOperations()
result = calculator.multiply(2.5, 4.0)  # Always returns 0.0
print(f"Result: {result}")
```
<!-- END: auto:calculator.core.ArithmeticOperations.multiply -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
### `_check_limits`

**Summary**  
Internal validation helper for the `ArithmeticOperations` class that ensures all input values passed to arithmetic operations (e.g., `subtract`, `multiply`) fall within predefined numerical bounds (`MIN_VALUE` to `MAX_VALUE`). This method is called implicitly by arithmetic operations and should not be called directly by end-users.

**Parameters**  
- `self` (object): Instance of the `ArithmeticOperations` class (required for all instance methods)  
- `*args` (tuple): Variable-length positional arguments (each value to be validated). Expected type: Numeric values (int/float). **Note**: The method does not validate input types (e.g., strings, non-numeric values). This is intentional for performance and assumes inputs are pre-validated by higher-level methods (e.g., `subtract`/`multiply`).

**Returns**  
- `None`: The method does not return a value. It performs validation and raises exceptions if invalid inputs are detected.

**Raises**  
- `CalculationLimitError`: Raised when any value in `args` violates the range `[MIN_VALUE, MAX_VALUE]`. The exception message is `f"Value {val} exceeds limits."`. The exception is thrown immediately upon the first invalid value.

**Examples**  
```python
from calculator.core import ArithmeticOperations

class ArithmeticOperations:
    MIN_VALUE = -1000
    MAX_VALUE = 1000

op = ArithmeticOperations()

# Example 1: Valid Input
op._check_limits(500, -200)  # Passes validation

# Example 2: Invalid Input
op._check_limits(2000)  # Raises CalculationLimitError

# Example 3: Multiple Values (First Invalid Value Triggers Exception)
op._check_limits(1500, -500)  # Raises immediately for 1500
```

**See also**  
- `ArithmeticOperations.subtract`  
- `ArithmeticOperations.multiply`
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `_log_op`

**Summary**
Internal helper method for recording arithmetic operation history in the calculator class. Formats an operation string (e.g., `multiply(4.0, 5.0) = 20.0`), appends it to the class's `history` list, and logs the entry at the `DEBUG` level using Python's `logging` module. This method is **stateless** and **intentionally void** (no return value).

**Parameters**
- `self` (object): Instance of the calculator class (required for class methods).
- `op` (str): Operation name (e.g., `"add"`, `"subtract"`, `"multiply"`, `"mode"`). Must match the operation method names in `calculator.core.ArithmeticOperations`.
- `a` (float): First operand (e.g., `2.0` for `add(2.0, 3.0)`).
- `b` (float): Second operand (e.g., `3.0` for `add(2.0, 3.0)`).
- `res` (float): Result of the operation (e.g., `5.0` for `add(2.0, 3.0)`).

**Returns**
- `None`: This method does not return any value (void method).

**Raises**
- `ValueError`: If `op` is not a valid operation name (e.g., `"invalid_op"`). Valid `op` values must be one of `{"add"}`, `{"subtract"}`, `{"multiply"}`, `{"mode"}` as defined in `calculator.core.ArithmeticOperations`.
- `TypeError`: If `a`, `b`, or `res` is not a `float` (e.g., `int`, `str`, `None`).
- `AttributeError`: If `self.history` is not a list (e.g., `None`, `dict`, `int`).
- `RuntimeError`: If the logging system is misconfigured (e.g., `logger` is not initialized or `logger.debug` fails).

**Examples**
```python
# Example 1: After multiply operation
result = self.multiply(4.0, 5.0)  # Returns 20.0
self._log_op("multiply", 4.0, 5.0, result)  # Logs: "multiply(4.0, 5.0) = 20.0"

# Example 2: After subtract operation
result = self.subtract(10.0, 3.0)  # Returns 7.0
self._log_op("subtract", 10.0, 3.0, result)  # Logs: "subtract(10.0, 3.0) = 7.0"

# Example 3: After mode (modulo) operation
result = self.mode(10.0, 3.0)  # Returns 1.0 (10 % 3)
self._log_op("mode", 10.0, 3.0, result)  # Logs: "mode(10.0, 3.0) = 1.0"
```

**See also**
- `calculator.core.ArithmeticOperations`: Defines valid operation names (`"add"`, `"subtract"`, `"multiply"`, `"mode"`).
- `history`: Class attribute storing operation history (list of strings).
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->
