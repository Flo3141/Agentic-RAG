# API Documentation: calculator_core



<!-- BEGIN: auto:calculator.core.CalculatorError -->
### `SymbolName`

**Summary**
Returns the full name of a financial symbol.

**Parameters**
- `symbol` (str): The financial symbol to look up (e.g., "AAPL" for Apple Inc.)

**Returns**
- (str): The full name of the symbol.

**Raises**
- `ValueError`: If the symbol is not found in the symbol database.

**Examples**
```python
symbol_name = SymbolName("AAPL")
print(symbol_name)  # Output: "Apple Inc."
```

**See also**
- `SymbolInfo`: Provides more detailed information about a symbol.
<!-- END: auto:calculator.core.CalculatorError -->

---

<!-- BEGIN: auto:calculator.core.PrecisionError -->
### `PrecisionError`

**Summary**
A custom exception class raised when a requested precision exceeds the calculator's maximum allowed precision. This error occurs during precision validation in arithmetic operations and signals that the requested precision is too high for the calculator to handle accurately.

**Parameters**
- `message` (str, optional): Optional error message (default: `"Requested precision is too high"`). Used to provide context for the error.

**Returns**
- `None`: The `PrecisionError` class itself does not return a value. It is an exception class.

**Raises**
- `PrecisionError`: Raised when the requested precision exceeds the calculator's maximum allowed precision (e.g., `precision > max_precision`).

**Examples**
```python
from calculator.core import ArithmeticOperations

# Initialize calculator with max precision = 100
calc = ArithmeticOperations(max_precision=100)

try:
    # Attempt high-precision calculation (exceeds limit)
    result = calc.calculate(1.0, 2.0, precision=1000)
except PrecisionError as e:
    print(f"Precision error: {e}")  # Output: "Precision error: Requested precision 1000 exceeds maximum 100"
```

**See also**
- `calculator.core.CalculatorError`: Base class for all calculator errors.
- `calculator.core.ArithmeticOperations._check_limits`: Method that validates precision before computation and raises `PrecisionError` when necessary.
<!-- END: auto:calculator.core.PrecisionError -->

---

<!-- BEGIN: auto:calculator.core.CalculationLimitError -->
### `CalculationLimitError`

**Summary**  
A custom exception subclass designed to be raised when calculator operations produce results that exceed predefined safe computational limits (e.g., integer overflow, floating-point precision boundaries, or arbitrary-precision constraints). This exception is explicitly raised by the calculator's internal logic when unsafe values are detected.

**Parameters**  
- `message` (str, optional): Human-readable error message (e.g., `"Value exceeds safe limit: 1e300"`). *Required when raising the exception*.

**Returns**  
- `None`: The class itself does not return a value.

**Raises**  
- `None`: This class does not raise exceptions.

**Examples**  
```python
from calculator.core import ArithmeticOperations

# Simulate unsafe subtraction (e.g., large floating-point values)
try:
    calc = ArithmeticOperations()
    result = calc.subtract(1e300, 1e-10)  # 1e300 is unsafe
except CalculationLimitError as e:
    print(f"Calculation limit error: {e}")
```

```python
try:
    raise CalculationLimitError("Custom limit error: Value too large")
except CalculatorError as e:
    print(f"Caught: {e}")
```

**See also**  
- `PrecisionError`: Handles precision issues (e.g., floating-point rounding errors).  
- `CalculatorError`: The root exception class for all calculator errors.
<!-- END: auto:calculator.core.CalculationLimitError -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations -->
### `ArithmeticOperations`

**Summary**  
A robust calculator implementation for performing basic arithmetic operations (`add`, `subtract`) with configurable precision (max 10 decimal places), input validation, and audit logging.

**Parameters**  
- `precision` (int): Number of decimal places for rounding results (default: `4`). Must be between `0` and `10` (inclusive).

**Returns**  
- `None`: The class initializes without returning a value.

**Raises**  
- `PrecisionError`: If `precision` is greater than `10` (max precision is `10`).  
- `CalculationLimitError`: If an operand value exceeds the defined limits (`MIN_VALUE` or `MAX_VALUE`).

**Examples**  
```python
from calculator.core import ArithmeticOperations

# Example 1: Basic initialization and addition
calc = ArithmeticOperations()
result = calc.add(1.2345, 2.3456)
print(f"Result: {result:.4f}")  # Output: 3.5801
print(f"History: {calc.history}")  # Output: ["add(1.2345, 2.3456) = 3.5801"]

# Example 2: Custom precision and subtraction
calc = ArithmeticOperations(precision=3)
result = calc.subtract(10.0, 2.5)
print(f"Result: {result:.3f}")  # Output: 7.500
print(f"History: {calc.history}")  # Output: ["sub(10.0, 2.5) = 7.500"]

# Example 3: Exception handling
try:
    calc = ArithmeticOperations(precision=11)
except PrecisionError as e:
    print(e)  # Output: "Max precision is 10."

try:
    calc = ArithmeticOperations(precision=4)
    calc.add(1e100, 0.0)
except CalculationLimitError as e:
    print(e)  # Output: "Value 1e+100 exceeds limits."
```

**See also**  
- `calculator.core` (module)
<!-- END: auto:calculator.core.ArithmeticOperations -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.__init__ -->
### `ArithmeticOperations.__init__`

**Summary**
Initializes a calculator instance with precision validation, history tracking, and logging. Ensures the precision parameter does not exceed 10 decimal places (the maximum allowed), sets the precision attribute, initializes an empty history list to store operation strings, and logs the initialization to the application logger.

**Parameters**
- `precision` (int): Number of decimal places for rounding calculations. **Default**: `DEFAULT_PRECISION` (a module-level constant, typically `4` in calculators).

**Returns**
- `None`: The `__init__` method does not return any value.

**Raises**
- `PrecisionError`: If `precision` exceeds 10 decimal places. The message is `"Max precision is 10."`.

**Examples**
```python
# Example 1: Initialize with default precision
from calculator.core import ArithmeticOperations

calculator = ArithmeticOperations()

# Output: Logs "Initialized with precision=4"
# calculator.precision = 4
# calculator.history = []

# Example 2: Initialize with custom precision (valid)
calculator = ArithmeticOperations(precision=5)

# Output: Logs "Initialized with precision=5"
# calculator.precision = 5
# calculator.history = []

# Example 3: Handle invalid precision (raises PrecisionError)
try:
    calculator = ArithmeticOperations(precision=11)
except PrecisionError as e:
    print(e)  # Output: "Max precision is 10."
```

**See also**
- `calculator.core.ArithmeticOperations`: The calculator class that manages operations and history.
<!-- END: auto:calculator.core.ArithmeticOperations.__init__ -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.mode -->
### `calculator.core.ArithmeticOperations.mode`

**Summary**
The `mode` method is a getter that returns the current operation mode of the calculator as a string. This method provides a standardized way to query the calculator's current mode without exposing internal state. The calculator operates exclusively in standard mode by default, and this method always returns the fixed string `"standard"`.

**Parameters**
- `self` (object): The instance of the `ArithmeticOperations` class. Required for all instance methods in Python.

**Returns**
- `str`: A string representing the current operation mode. Specifically, it returns the constant `MODE_STANDARD` (e.g., `"standard"`).

**Raises**
- No exceptions are raised by this method under normal circumstances. Any potential exceptions (e.g., `NameError` if `MODE_STANDARD` is undefined in `calculator/core.py`) are module-level configuration issues and not raised by this method.

**Examples**
```python
from calculator.core import ArithmeticOperations

# Create calculator instance
calculator = ArithmeticOperations()

# Get current mode (always returns "standard")
current_mode = calculator.mode()
print(f"Current mode: {current_mode}")  # Output: "standard"
```

```python
# Ensure calculator is in standard mode before operations
if calculator.mode() != "standard":
    raise ValueError("Calculator must be in standard mode")
    
# Proceed with operations (e.g., subtraction)
result = calculator.subtract(10, 5)  # Returns 5
```

**See also**
- `calculator.core.ArithmeticOperations.subtract`: Performs subtraction operations.
- `calculator.core.ArithmeticOperations._log_op`: Internal logging method (not directly used by mode).
<!-- END: auto:calculator.core.ArithmeticOperations.mode -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.add -->
### `calculator.core.ArithmeticOperations.add`

**Summary**  
Performs safe addition of two floating-point numbers with precision control and operational auditing. Validates inputs against operational limits, computes the sum rounded to `self.precision` decimal places, and logs the operation for audit compliance.

**Parameters**  
- `a` (float): First operand (e.g., `1.234`)  
- `b` (float): Second operand (e.g., `5.678`)  

**Returns**  
- `float`: Rounded sum of `a` and `b` to `self.precision` decimal places (e.g., `6.91` when `self.precision = 2`)

**Raises**  
- `ValueError`: Inputs exceed calculator's operational limits (e.g., `a > 1e300`, `b < -1e300`)  
- `RuntimeError`: Logging system failure (e.g., disk full, invalid log path)  
- `TypeError`: Non-serializable log data (e.g., `a` is `None`)  

**Examples**  
```python
# Example 1: Basic addition with precision control
from calculator.core import ArithmeticOperations

calc = ArithmeticOperations(precision=2)
result = calc.add(1.234, 5.678)
print(f"Result: {result:.2f}")
```

```python
# Example 2: Handling invalid inputs (via _check_limits)
from calculator.core import ArithmeticOperations

calc = ArithmeticOperations(precision=3)
try:
    calc.add(1e300, 2e300)
except ValueError as e:
    print(f"Invalid input: {e}")
```

```python
# Example 3: Logging operation (audit trail)
from calculator.core import ArithmeticOperations

calc = ArithmeticOperations(precision=1)
calc.add(1.2, 3.4)
```

```python
# Example 4: Real-world financial use case
from calculator.core import ArithmeticOperations

calc = ArithmeticOperations(precision=4)
total = calc.add(123.4567, 89.0123)
print(f"Total: {total:.4f} USD")
```

**See also**  
- `calculator.core.ArithmeticOperations.subtract`: Subtraction operation  
- `calculator.core.ArithmeticOperations._log_op`: Operation logging  
- `calculator.core.ArithmeticOperations.mode`: Operation mode (e.g., "financial", "scientific")  
- `calculator.core.ArithmeticOperations._check_limits`: Input validation
<!-- END: auto:calculator.core.ArithmeticOperations.add -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations.subtract -->
### `ArithmeticOperations.subtract`

**Summary**
Performs arithmetic subtraction of `b` from `a` (i.e., `a - b`), with critical safety and precision handling. Validates input limits before computation, rounds the result to `self.precision` decimal places, and logs the operation for auditability.

**Parameters**
- `a` (float): Minuend (the number being subtracted from)
- `b` (float): Subtrahend (the number to subtract)

**Returns**
- (float): Result of `a - b` rounded to `self.precision` decimal places.

**Raises**
- `CalculatorError`: If input limits are violated (e.g., numbers too large, invalid types, overflow). This exception is raised by the `_check_limits` method.
- `TypeError`: *Indirectly* if `_check_limits` attempts to compare non-numeric types (e.g., `int` vs `float`). Note: This exception is raised by the `_check_limits` method.
- `ValueError`: *Indirectly* if `self.precision` is non-numeric (e.g., `str` passed to `round`). Note: This exception is raised by the `round` function, but the method ensures `self.precision` is numeric via `_check_limits`.

**Examples**
```python
from calculator.core import ArithmeticOperations

# Initialize with precision = 2
calc = ArithmeticOperations(precision=2)

result = calc.subtract(10.555, 2.333)  # 8.222 → rounded to 2 decimals
print(result)  # Output: 8.22
```

```python
try:
    calc = ArithmeticOperations(precision=1)
    result = calc.subtract(1e300, 0.0)  # Exceeds max representable float
except calculator.core.CalculatorError as e:
    print(f"Operation failed: {e}")  # Output: "Number too large for precision"
```

```python
calc = ArithmeticOperations(precision=1)
result = calc.subtract(5.5, 2.2)
# Logs: {"op": "sub", "a": 5.5, "b": 2.2, "result": 3.3}
```

```python
calc = ArithmeticOperations(precision=3)
result = calc.subtract(1.0, 2.0)  # 1.0 - 2.0 = -1.0
print(result)  # Output: -1.0
```

**See also**
- `calculator.core.ArithmeticOperations._check_limits`: Pre-computation validation method
- `calculator.core.ArithmeticOperations._log_op`: Operation logging method
<!-- END: auto:calculator.core.ArithmeticOperations.subtract -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._check_limits -->
### `_check_limits`

**Summary**
Internal validation helper for the `ArithmeticOperations` class that ensures all input values adhere to predefined numerical boundaries (`MIN_VALUE` and `MAX_VALUE`). This method iterates through all positional arguments (`*args`), checks each value against the range constraints, and raises a `CalculationLimitError` if any value violates the limits. **This method is not intended for direct external use** but is designed to be called internally by arithmetic operations (e.g., `subtract`, `add`).

**Parameters**
- `self` (object): Instance of the `ArithmeticOperations` class (required for instance methods)
- `*args` (tuple): Variable number of positional arguments to validate (each value is checked)

**Returns**
- `None`: Returned **only if all values pass validation** (no exceptions raised). If validation fails, the method **raises an exception** and does not return.

**Raises**
- `CalculationLimitError`: If **any** value in `args` is outside the range `[MIN_VALUE, MAX_VALUE]`. The exception message includes the exact invalid value in the format: `f"Value {val} exceeds limits."`

**Examples**
```python
from calculator.core import ArithmeticOperations

# Example 1: Valid Input (No Exception)
calc = ArithmeticOperations()
calc._check_limits(50, 25)  # Passes validation → returns None

# Example 2: Invalid Input (Raises Exception)
try:
    calc._check_limits(150)
except CalculationLimitError as e:
    print(e)  # Output: "Value 150 exceeds limits."
```

**See also**
- `ArithmeticOperations`: The class that owns this method and uses it internally for arithmetic operations
- `CalculationLimitError`: The exception raised when input values exceed the defined limits
<!-- END: auto:calculator.core.ArithmeticOperations._check_limits -->

---

<!-- BEGIN: auto:calculator.core.ArithmeticOperations._log_op -->
### `_log_op`

**Summary**
Internal helper method for recording arithmetic operation history in the `ArithmeticOperations` class. Formats a string describing the operation (e.g., `subtract(5.0, 3.0) = 2.0`), appends it to the class's `history` list, and logs it at the `DEBUG` level using Python's `logging` module. This method is **exclusively called internally** by the `ArithmeticOperations` class and should never be used by external code.

**Parameters**
- `self` (object): Instance of `ArithmeticOperations`
- `op` (str): Operation name (e.g., `"add"`, `"subtract"`, `"multiply"`, `"divide"`)
- `a` (float): First operand in the operation
- `b` (float): Second operand in the operation
- `res` (float): Result of the operation (computed value)

**Returns**
- (None): This method does not return any value (void method). It only modifies the class's `history` list and logs the entry.

**Raises**
- `TypeError`: Non-`float` values for `a`, `b`, or `res` (violating type hints)
- `AttributeError`: `self.history` is not a list (e.g., uninitialized)
- `ValueError`: Invalid operation name (e.g., `op = "invalid_op"`)
- `RuntimeError`: Logger misconfiguration (e.g., no handlers for `DEBUG` level)
- `OSError`: File I/O errors during logging (unlikely for `logger.debug`)

**Examples**
This method is **exclusively called internally** by the `ArithmeticOperations` class (e.g., by `subtract`, `add`, `multiply`, `divide` methods). External code should never call it directly.

Example usage inside `subtract` method:
```python
def subtract(self, a: float, b: float) -> float:
    result = a - b
    self._log_op(op="subtract", a=a, b=b, res=result)
    return result
```

Example usage inside `mode` method (custom operation):
```python
def mode(self, a: float, b: float) -> float:
    result = (a + b) / 2  # Simplified example
    self._log_op(op="mode", a=a, b=b, res=result)
    return result
```

**See also**
- [ArithmeticOperations](https://example.com) (the class that uses this method)
<!-- END: auto:calculator.core.ArithmeticOperations._log_op -->

---