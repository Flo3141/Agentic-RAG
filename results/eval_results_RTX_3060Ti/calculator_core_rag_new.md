# API Documentation: calculator_core

<!-- BEGIN: auto:calculator.core.CalculatorError -->
**Summary**  
`CalculatorError` is a base class for calculator exceptions. It is **not intended to be instantiated or raised directly**. Instead, it serves as a parent class for specific exception subclasses like `CalculationLimitError` and `PrecisionError`. This design ensures proper error handling in calculator operations.

**Parameters**  
- `None`: This class has no parameters.

**Returns**  
- `None`: This class does not return any value.

**Raises**  
- `None`: This class does not raise exceptions. It is designed to be inherited by specific exception classes.

**Examples**  
```python
# Example 1: Raising a specific subclass
from calculator.core import CalculationLimitError

try:
    raise CalculationLimitError("Exceeded maximum calculation iterations")
except CalculationLimitError as e:
    print(f"Calculation error: {e}")
```

```python
# Example 2: Catching the base exception (rare)
try:
    raise CalculatorError("Base error for demonstration")
except CalculatorError as e:
    print(f"Base calculator error: {e}")
```

```python
# Example 3: Error in ArithmeticOperations.mode
from calculator.core import ArithmeticOperations

try:
    result = ArithmeticOperations.mode(10.0, 20.0, precision=3)
except PrecisionError as e:
    print(f"Precision error: {e}")
```

**See also**  
- `TestError` (for test-related errors)  
- `CalculationLimitError` (for calculation limit exceeded errors)  
- `PrecisionError` (for precision requirement unmet errors)
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
**Parameters**  
- None: The `TestError` class has no constructor parameters. The string message is handled by the base class `CalculatorError`.

**Returns**  
- None: The `TestError` class is an exception class and does not return any value.

**Raises**  
- `TestError`: When the exception is raised (e.g., `raise TestError("message")`).  
- `TypeError`: If non-string arguments are passed to the constructor (handled by the base class `CalculatorError`).

**Examples**  
```python
from calculator.core import TestError

try:
    raise TestError("This is a test error")
except TestError as e:
    print(f"Caught test error: {e}")
```
<!-- END: auto:calculator.core.TestError -->

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->
### `CalculationLimitError`

**Summary**
A custom exception type raised when numerical calculations (e.g., arithmetic operations) produce values that exceed safe computational limits, such as overflow or underflow.

**Parameters**
None

**Returns**
None

**Raises**
- `CalculationLimitError`: This exception is raised when numerical calculations (e.g., arithmetic operations) produce values that exceed safe computational limits.

**Examples**
```python
from calculator.core import ArithmeticOperations, CalculationLimitError

try:
    # Subtraction with values exceeding safe limits (e.g., 1e300)
    result = ArithmeticOperations.subtract(1e300, 1e300)
except CalculationLimitError as e:
    print(f"Calculation error: {e}")  # Output: "Calculation error: Values exceed safe limits"
```

**See also**
- `CalculatorError`: Base class for all calculator-related exceptions.
- `PrecisionError`: Handles precision constraints (e.g., rounding errors).
<!-- END: auto:calculator.core.CalculationLimitError -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `ArithmeticOperations`

**Summary**  
A robust calculator implementation for performing basic arithmetic operations (`add`, `subtract`, `multiply`) with configurable precision and operation history logging.

**Parameters**  
- `precision` (int): Number of decimal places for rounding (default: `DEFAULT_PRECISION`).

**Returns**  
- `None`: The class does not return a value.

**Raises**  
- `PrecisionError`: Raised when `precision` exceeds the maximum allowed (10 decimal places).  
- `CalculationLimitError`: Raised when an operand exceeds the defined limits (`MIN_VALUE` or `MAX_VALUE`).  
- `CalculatorError`: Base class for all calculator errors (not directly raised by methods).

**Examples**  
```python
from calculator.core import ArithmeticOperations

# Create an instance with default precision (2 decimal places)
op = ArithmeticOperations()

# Add two numbers
print(op.add(2, 3))  # Output: 5.0

# Multiply two numbers (placeholder method returns 0)
print(op.multiply(2, 3))  # Output: 0.0
```

**See also**  
- `calculator.core` (module)
<!-- END: auto:calculator.core.ArithmeticOperations -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `Calculator.__init__`

**Summary**
This method initializes a calculator instance with **precision constraints** and **operation history tracking**. It:
- Validates that the precision (decimal places) does not exceed 10
- Sets the precision attribute for rounding operations
- Initializes an empty history list to record all calculator operations
- Logs initialization details using Python's `logging` module
- Ensures the calculator operates within defined precision boundaries (critical for financial/technical calculations where precision errors can cause significant drift)

**Parameters**
- `precision` (`int`): Number of decimal places for rounding operations. **Default**: `DEFAULT_PRECISION` (a module constant, typically `4` or `8` based on common financial standards). Must be a non-negative integer.

**Returns**
- `None`: `__init__` methods in Python always return `None`.

**Raises**
- `PrecisionError`: When `precision > 10`. Message: `"Max precision is 10."`. Root cause: Invalid precision value (exceeds 10 decimals).

**Examples**
```python
# Example 1: Default Precision Initialization
from sample_project.src.calculator.core import Calculator

calculator = Calculator()
print(calculator.precision)  # Output: 4 (or DEFAULT_PRECISION value)

# Example 2: Custom Precision Initialization
calculator = Calculator(precision=5)
print(calculator.precision)  # Output: 5

# Example 3: Precision Validation (Error Case)
try:
    calculator = Calculator(precision=11)
except PrecisionError as e:
    print(e)  # Output: "Max precision is 10."

# Example 4: Full Workflow (with history)
calculator = Calculator(precision=3)
calculator.multiply(2.5, 3.2)  # Adds to history
print(calculator.history)  # Output: ["2.5 * 3.2 = 8.0"]
```

**See also**
- `Calculator.multiply`: Performs multiplication with precision rounding.
- `Calculator.history`: List of operation strings.
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `mode`

**Summary**  
A getter method that returns the current operation mode of the calculator as a string without any side effects. This method simply retrieves the pre-defined `CURRENT_MODE` class-level constant from the calculator's core context.

**Parameters**  
- None: The method does not accept any explicit parameters beyond the implicit `self` instance reference.

**Returns**  
- `str`: A string representing the current operation mode (e.g., `"add"`, `"subtract"`, `"multiply"`, `"divide"`).

**Raises**  
- `NameError`: If the class-level constant `CURRENT_MODE` is not defined in the calculator's core module.  
- `TypeError`: If the class-level constant `CURRENT_MODE` is not a string.

**Examples**  
```python
from calculator.core import Calculator

# Initialize calculator
calculator = Calculator()

# Get current mode
current_mode = calculator.mode()

print(f"Current operation mode: {current_mode}")  # Output: "add" (or other mode)
```

```python
from calculator.core import Calculator

calculator = Calculator()

while True:
    mode = calculator.mode()
    
    if mode == "add":
        print("Performing addition...")
    elif mode == "subtract":
        print("Performing subtraction...")
    # ... handle other modes
```

```python
from calculator.core import Calculator

calculator = Calculator()

try:
    current_mode = calculator.mode()
    assert current_mode in ["add", "subtract", "multiply"], "Invalid mode"
    print(f"Valid mode: {current_mode}")
except NameError as e:
    print(f"Error: {e} - CURRENT_MODE is not defined in the class context")
except TypeError as e:
    print(f"Error: {e} - CURRENT_MODE must be a string")
```

**See also**  
- `calculator.core.ArithmeticOperations`: Defines the arithmetic operations (e.g., `add`, `subtract`, `multiply`) that the mode string values correspond to.  
- `calculator.core.Calculator`: The main calculator class that uses `CURRENT_MODE` as a class-level constant.
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `Calculator.add`

**Summary**
Safely performs floating-point addition with input validation, precision control, and operation logging. Ensures operands are within acceptable limits, rounds the result to `self.precision` decimal places, and records the operation for auditability.

**Parameters**
- `a` (float): First operand (must be a valid floating-point number)
- `b` (float): Second operand (must be a valid floating-point number)

**Returns**
- (float): Rounded sum of `a + b` to `self.precision` decimal places

**Raises**
- `CalculatorError`: Raised by `_check_limits` if operands violate constraints (e.g., `a` or `b` is `inf`, `nan`, or exceeds a defined numerical limit).
- `TypeError`: If `a` or `b` is not a `float`.
- `OverflowError`: If `a + b` exceeds representable float range.

**Examples**
```python
from sample_project.src.calculator.core import Calculator

# Initialize calculator with 2 decimal places precision
calc = Calculator(precision=2)

# Add 1.234 and 5.678 → 6.91 (rounded to 2 decimals)
result = calc.add(1.234, 5.678)
print(result)  # Output: 6.91
```

```python
try:
    calc.add(float("inf"), 10)  # Invalid: inf is not allowed
except calculator.core.CalculatorError as e:
    print(f"Error: {e}")  # Output: "Operand 'inf' exceeds numerical limits"
```

```python
# Logs: "add: 1.234 + 5.678 = 6.91"
calc.add(1.234, 5.678)
```

**See also**
- `calculator.core.CalculatorError`: Custom exception for invalid operations
- `Calculator.precision`: Class attribute controlling rounding precision
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `subtract`

**Summary**  
Performs subtraction of `b` from `a`, validates inputs against operational constraints, rounds the result to the class's configured precision, and logs the operation for auditability.

**Parameters**  
- `a` (float): The **minuend** (first operand) to be subtracted from. Represents the value before subtraction.  
- `b` (float): The **subtrahend** (second operand). Represents the value to be subtracted from `a`.

**Returns**  
- (float): The result of `a - b` rounded to `self.precision` decimal places.

**Raises**  
- `CalculatorError`: Input values `a` or `b` violate operational limits (e.g., out-of-range values).  
- `TypeError`: If `self.precision` is not a numeric type (e.g., string) during rounding.  
- `ValueError`: If `self.precision` is negative or non-integer (e.g., fractional) during rounding.

**Examples**  
```python
from calculator.core import ArithmeticOperations

# Configure precision (float)
calculator = ArithmeticOperations()
calculator.precision = 2.0  # Round to 2 decimal places

# Perform subtraction
result = calculator.subtract(10.5, 2.3)  # Returns 8.2
print(result)  # Output: 8.2
```

```python
calculator = ArithmeticOperations()
calculator.precision = 3  # Round to 3 decimal places
result = calculator.subtract(-10.5, 2.3)  # Returns -12.8
print(result)  # Output: -12.8
```

```python
calculator = ArithmeticOperations()
calculator.min_value = 0  # Enforced lower bound
calculator.max_value = 100  # Enforced upper bound

try:
    calculator.subtract(-1, 2)  # Invalid: negative value
except calculator.core.CalculatorError as e:
    print(e)  # Output: "Value -1 is below minimum allowed value 0"
```

```python
calculator = ArithmeticOperations()
calculator.precision = 2.5  # Non-integer precision

result = calculator.subtract(10.5, 2.3)  # Returns 8.2 (not 8.20)
print(result)  # Output: 8.2
```

**See also**  
- `ArithmeticOperations` class: The class that handles arithmetic operations with precision and validation.  
- `precision` attribute: Configures the rounding precision for all operations.
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.multiply -->
### `multiply`

**Summary**
A stub implementation of multiplication that always returns `0.0` for testing purposes. This method is **not** intended for production use and does not perform actual arithmetic operations. It serves as a placeholder to avoid breaking workflows during development or testing phases.

**Parameters**
- `self` (object): The instance of the `ArithmeticOperations` class (required for instance methods in Python).
- `a` (float): First operand (floating-point number).
- `b` (float): Second operand (floating-point number).

**Returns**
- `float`: Always returns `0.0` (a floating-point zero). **No actual multiplication occurs**.

**Raises**
- No exceptions are raised by this method. However, if non-float inputs are provided, a `TypeError` will be raised at the caller level.

**Examples**
```python
from sample_project.src.calculator.core import ArithmeticOperations

# Create an instance of the calculator
calc = ArithmeticOperations()

# Call multiply (always returns 0.0)
result = calc.multiply(10.5, -3.2)  # Returns 0.0 (not 10.5 * -3.2)
print(result)  # Output: 0.0
```

```python
# Test interaction with add/subtract (for validation)
calc = ArithmeticOperations()
assert calc.multiply(2.0, 3.0) == 0.0  # Always passes (stub)
assert calc.add(2.0, 3.0) == 5.0       # Real add works (non-stub)
assert calc.subtract(5.0, 2.0) == 3.0   # Real subtract works (non-stub)
```

```python
# This would raise TypeError (not from multiply, but from caller)
try:
    calc.multiply("a", "b")  # Non-float inputs
except TypeError as e:
    print(f"Error: {e}")  # Output: "unsupported operand type(s) for *: 'str' and 'str'"
```

**See also**
- `ArithmeticOperations.add`
- `ArithmeticOperations.subtract`
- `calculator.core.CalculatorError`
<!-- END: auto:calculator.core.ArithmeticOperations.multiply -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
# `_check_limits` Method

This method validates that all provided values fall within the defined range (`MIN_VALUE` to `MAX_VALUE`). If any value exceeds these bounds, it raises a `CalculationLimitError` with the specific invalid value.

## Parameters
- `*args`: The values to check (any number of positional arguments)

## Returns
- None

## Examples
```python
# Example 1: Valid input (no exception)
self._check_limits(10.0, 20.0)

# Example 2: Invalid input (raises exception)
self._check_limits(1000.0)  # Raises CalculationLimitError: Value 1000.0 exceeds limits.

# Example 3: Edge case (empty input)
self._check_limits()  # No exception (loop does nothing)
```

## See also
- `MAX_VALUE` (calculator.core): The upper bound of valid values
- `MIN_VALUE` (calculator.core): The lower bound of valid values
- `CalculationLimitError` (calculator.core): The exception type raised when input values exceed defined limits
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `_log_op`

**Summary**  
Internal helper method for recording the history of arithmetic operations performed by the calculator. Formats a human-readable string describing the operation (e.g., `add(2.0, 3.0) = 5.0`), appends it to the class's `history` list, and logs the entry at the `debug` level using Python's built-in `logging` module.

**Parameters**  
- `op` (str): Name of the arithmetic operation (e.g., `"add"`, `"subtract"`, `"mode"`). This string must match the operation names defined in the `ArithmeticOperations` class.  
- `a` (float): First operand (numeric value) for the operation.  
- `b` (float): Second operand (numeric value) for the operation.  
- `res` (float): Result of the operation (numeric value). This is the exact result of the operation, not an intermediate value.  

**Returns**  
- (None): This method does not return any value.  

**Raises**  
- `TypeError`: If `self.history` is not a list (or a mutable sequence).  
- `AttributeError`: If `logger` is not defined or not accessible (e.g., missing logging configuration).  
- `RuntimeError`: If the logging system is misconfigured (no handlers) and `logger.debug` fails.  
- `ValueError`: If `res` is not a valid float (e.g., `NaN`, `inf`).  

**Examples**  
This method is **never called directly by users**. It is invoked internally by the `ArithmeticOperations` class's arithmetic operation methods (e.g., `add`, `subtract`, `mode`).  

```python
# After a successful add operation
result = calc.add(2.5, 3.7)
# Internally calls: calc._log_op("add", 2.5, 3.7, 6.2)
```

**Log Entry**: `add(2.5, 3.7) = 6.2`  
**History**: `["add(2.5, 3.7) = 6.2"]`

```python
# After a subtract operation
result = calc.subtract(10.0, 4.2)
# Internally calls: calc._log_op("subtract", 10.0, 4.2, 5.8)
```

**Log Entry**: `subtract(10.0, 4.2) = 5.8`  
**History**: `["add(2.5, 3.7) = 6.2", "subtract(10.0, 4.2) = 5.8"]`

```python
# After a mode operation (modular arithmetic)
result = calc.mode(17, 5)  # 17 % 5 = 2
# Internally calls: calc._log_op("mode", 17, 5, 2)
```

**Log Entry**: `mode(17, 5) = 2`  
**History**: `["add(2.5, 3.7) = 6.2", "subtract(10.0, 4.2) = 5.8", "mode(17, 5) = 2"]`

**See also**  
- `ArithmeticOperations.add`  
- `ArithmeticOperations.subtract`  
- `ArithmeticOperations.mode`
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->
