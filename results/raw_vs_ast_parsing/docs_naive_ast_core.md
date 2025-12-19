# Doku core (Phase 2: AST Structure)
> Code was semantically segmented in functions/classes.



### `CalculatorError`

**Summary**  
A base exception class for calculator applications, serving as the root of a hierarchy of calculator-specific exceptions (e.g., `CalculatorValueError`, `CalculatorDivisionByZeroError`). This class does not perform any computation or logic and is designed to be inherited by specific error types.

**Parameters**  
- `message` (str): Optional error message (default: `None`). Used to provide context when raising the exception.

**Returns**  
- `None`: The class itself does not return any value (it is a class object).

**Raises**  
- `None`: This class does not raise exceptions itself.

**Examples**  
```python
# Example 1: Raising a base exception
try:
    raise CalculatorError("Invalid input: value must be positive")
except CalculatorError as e:
    print(f"Caught base calculator error: {e}")

# Example 2: Inheriting for a specific error
class CalculatorDivisionByZeroError(CalculatorError):
    pass

try:
    raise CalculatorDivisionByZeroError("Cannot divide by zero")
except CalculatorError as e:
    print(f"Calculator error: {e}")
```

**See also**  
- `CalculatorValueError`: Error when input value is invalid.  
- `CalculatorDivisionByZeroError`: Division by zero error.
---


### `PrecisionError`

**Summary**  
A custom exception class raised when a calculation operation requires a precision level exceeding the capabilities of the calculator module.

**Parameters**  
None

**Returns**  
None

**Raises**  
- `None`: This class does not raise exceptions. It is an exception class that is raised by user code.

**Examples**  
```python
class Calculator:
    MAX_PRECISION = 10  # Maximum allowed precision

    def calculate(self, value, precision):
        if precision > self.MAX_PRECISION:
            raise PrecisionError(f"Requested precision {precision} exceeds max {self.MAX_PRECISION}")
        # ... rest of calculation logic
```

```python
try:
    calculator = Calculator()
    calculator.calculate(10.5, 15)  # Precision 15 > MAX_PRECISION (10)
except PrecisionError as e:
    print(f"Precision error: {e}")
```

```python
try:
    raise PrecisionError("User requested 100 decimal places — impossible for this calculator")
except PrecisionError as e:
    print(f"Error: {e}")
```

**See also**  
- `CalculatorError`: Base exception class for all calculator-related errors.
---


### `CalculationLimitError`

**Summary**
This class defines a custom exception type that signals when calculation operations exceed predefined safe limits (e.g., numerical thresholds, memory constraints, or resource boundaries). It inherits from `CalculatorError` and is designed to be raised during runtime when safe limits are violated. This class follows Python's exception design principles with minimalism and extensibility.

**Parameters**
- None (this class does not accept parameters at definition time)

**Returns**
- None (exception classes do not return values; they propagate up the call stack when raised)

**Raises**
- `CalculationLimitError`: Raised when calculation operations exceed safe limits (e.g., `value > MAX_SAFE_LIMIT`)

**Examples**
```python
class Calculator:
    class CalculatorError(Exception):
        pass

    MAX_SAFE_LIMIT = 1000

    def calculate(self, value):
        if value > self.MAX_SAFE_LIMIT:
            raise self.CalculationLimitError(f"Value {value} exceeds safe limit")
        return value * 2

# Usage
calc = Calculator()
result = calc.calculate(1500)  # Raises CalculationLimitError
```

**See also**
- `CalculatorError`: Base exception class for calculator-related errors
- `Exception`: Base class for all exceptions in Python
---


### `ArithmeticOperations`

**Summary**  
A robust calculator for basic arithmetic operations with configurable precision and audit logging. Supports addition and subtraction with rounding to a specified number of decimal places, while maintaining a history of operations for traceability.

**Parameters**  
- `precision` (int): Number of decimal places for rounding (default: `DEFAULT_PRECISION` constant). Must be between 0 and 10 (inclusive).

**Returns**  
- (None): The class initializes without returning a value.

**Raises**  
- `PrecisionError`: Raised when `precision` is greater than 10.
- `CalculationLimitError`: Raised when an operand exceeds the `[MIN_VALUE, MAX_VALUE]` bounds.

**Examples**  
```python
# Example 1: Creating a calculator with 2 decimal places and using add
calc = ArithmeticOperations(precision=2)
result = calc.add(1.234, 5.678)
print(result)  # Output: 6.91

# Example 2: Using subtract
result = calc.subtract(10.5, 3.2)
print(result)  # Output: 7.3

# Example 3: Accessing the history log
print(calc.history)  # Output: ['1.234 + 5.678 = 6.91', '10.5 - 3.2 = 7.3']
```

**See also**  
- `DEFAULT_PRECISION`: Default rounding precision value (typically 2)
- `MIN_VALUE` and `MAX_VALUE`: Bounds for operand validation (implementation-specific)
---


### `Calculator.__init__`

**Summary**
Initializes a calculator instance with precision validation, operation history tracking, and configuration logging. This method ensures the precision parameter adheres to a maximum of 10 decimal places (the default value is a class constant `DEFAULT_PRECISION`), initializes an empty history list to store operation strings, and logs the configuration for auditability.

**Parameters**
- `precision` (int): Number of decimal places for rounding operations. **Default**: `DEFAULT_PRECISION` (a class-level constant, e.g., `4` or `10`). This parameter must be an integer and must not exceed 10.

**Returns**
- (None): Constructor methods in Python always return `None`.

**Raises**
- `PrecisionError`: If `precision` exceeds 10 decimal places. The error message is `"Max precision is 10."`.

**Examples**
```python
# Example 1: Use default precision (e.g., 4)
from my_calculator import Calculator

calc = Calculator()  # Uses DEFAULT_PRECISION (e.g., 4)

# Example 2: Explicitly set precision to 2
calc = Calculator(precision=2)

# Example 3: Invalid precision (raises PrecisionError)
try:
    Calculator(precision=11)
except PrecisionError as e:
    print(e)  # Output: "Max precision is 10."
```

**See also**
- `Calculator.history`: The list of operation strings (e.g., `"1 + 2 = 3"`).
- `Calculator.logger`: The logging module used for configuration logging.
---


**Parameters**
- None

**Returns**
- `str`: The string value of the class constant `MODE_STANDARD` (e.g., `"standard"`).

**Raises**
None

**Examples**
```python
class Device:
    MODE_STANDARD = "standard"

    def mode(self) -> str:
        return Device.MODE_STANDARD

device = Device()
print(device.mode())  # Output: "standard"
```
---


### `add`

**Summary**
Safely adds two floating-point numbers while enforcing input validation, precision control, and audit logging. The method ensures operands comply with predefined limits before computation, rounds the result to the class's configured precision (e.g., 2 decimal places for financial calculations), and records the operation for traceability.

**Parameters**
- `a` (float): First operand (e.g., monetary value, sensor reading)
- `b` (float): Second operand (e.g., another monetary value, measurement)

**Returns**
- (float): Rounded sum of `a` and `b` to `self.precision` decimal places (e.g., `12.8` if `self.precision=1`)

**Raises**
- `ValueError`: If operands violate predefined limits (e.g., `a > 1e10`, negative values in financial context)
- `TypeError`: If `self.precision` is not a `float` (e.g., `self.precision = "2"` instead of `2.0`)
- `AttributeError`: If `self.precision` is undefined (e.g., class not initialized properly)

**Examples**
```python
# Financial Calculation (Precision = 2)
class Money:
    def __init__(self, precision: int = 2):
        self.precision = precision

    def _check_limits(self, a: float, b: float) -> None:
        if a < 0 or b < 0 or a > 1e9 or b > 1e9:
            raise ValueError("Invalid monetary values")

    def _log_op(self, op: str, a: float, b: float, result: float) -> None:
        print(f"Logged {op}({a}, {b}) → {result:.{self.precision}f}")

    def add(self, a: float, b: float) -> float:
        self._check_limits(a, b)
        result = round(a + b, self.precision)
        self._log_op("add", a, b, result)
        return result

money = Money()
print(money.add(10.5, 2.3))  # Output: 12.8
```

```python
# Scientific Measurement (Precision = 4)
class Sensor:
    def __init__(self, precision: int = 4):
        self.precision = precision

    def add(self, a: float, b: float) -> float:
        result = round(a + b, self.precision)
        return result

sensor = Sensor()
print(sensor.add(1.2345, 5.6789))  # Output: 6.9134
```

**Edge Case Example**
```python
try:
    money = Money()
    money.add(-1.0, 2.0)
except ValueError as e:
    print(e)
# Output: Invalid monetary values
```

**See also**
- `Money` class
- `Sensor` class
---


### `subtract`

**Summary**  
Performs precision-controlled subtraction of two floating-point numbers (`a` and `b`), validates input constraints via a private `_check_limits` method, rounds the result to the class's `precision` decimal places, and logs the operation for auditing/tracing purposes.

**Parameters**  
- `a` (float): The minuend (the number from which another number is subtracted).  
- `b` (float): The subtrahend (the number to be subtracted from `a`).  

**Returns**  
(float): The result of `a - b` rounded to `self.precision` decimal places.

**Raises**  
- `ValueError`: Inputs `a` or `b` violate class-defined constraints (e.g., negative values, non-numeric inputs) or `self.precision` is negative (as per Python's `round` behavior).  
- `TypeError`: `self.precision` is not an integer.

**Examples**  

- Example 1: Valid Input with Precision Control  
  ```python
  calc = Calculator()
  result = calc.subtract(10.5, 3.2)
  print(result)  # Output: 7.3
  ```

- Example 2: Input with Negative Values  
  ```python
  calc = Calculator()
  result = calc.subtract(-5.0, 2.0)
  print(result)  # Output: -7.0
  ```

- Example 3: Input with Non-numeric Values  
  ```python
  calc = Calculator()
  try:
      result = calc.subtract("a", 3.2)
  except TypeError:
      print("TypeError: 'a' is not a number")
  ```

- Example 4: Negative Precision  
  ```python
  calc = Calculator()
  try:
      result = calc.subtract(10.5, 3.2)
  except ValueError:
      print("ValueError: precision is negative")
  ```

**See also**  
- `Calculator`
---


### `_check_limits`

**Summary**
This internal class method validates that all input values (passed as positional arguments) fall within a predefined numerical range `[MIN_VALUE, MAX_VALUE]`. If any value violates this range, it immediately raises a custom exception `CalculationLimitError`. The function serves as a pre-validation safety check for critical operations in the class.

**Parameters**
- `self` (object): The class instance (required for class methods)
- `*args` (tuple): Variable number of positional arguments (each is a single numeric value to validate)

**Returns**
- `None`: The function never returns a value in normal execution because it always raises an exception when a limit violation occurs. If all values are valid, the function completes without raising an exception (returning `None` implicitly).

**Raises**
- `CalculationLimitError`: Any input value violates the inclusive range `[MIN_VALUE, MAX_VALUE]`. The exception message is formatted as `"Value {val} exceeds limits."`.

**Examples**
```python
class Calculator:
    MIN_VALUE = 0
    MAX_VALUE = 100

    def _check_limits(self, *args):
        for val in args:
            if val > MAX_VALUE or val < MIN_VALUE:
                raise CalculationLimitError(f"Value {val} exceeds limits.")

# Example 1: Single Value Check (Valid)
calc = Calculator()
calc._check_limits(50)  # No exception

# Example 2: Multiple Values Check (Invalid)
calc._check_limits(150)  # Raises CalculationLimitError

# Example 3: Multiple Values Check (Mixed Valid/Invalid)
calc._check_limits(20, 150)  # Raises immediately on 150

# Example 4: Edge Case (Valid Range)
calc._check_limits(0, 100)  # No exception

# Example 5: Empty Input (No Validation)
calc._check_limits()  # No exception
```

**See also**
- `Calculator.MIN_VALUE` and `Calculator.MAX_VALUE` (class constants defining the valid range)
---


### `_log_op`

**Summary**
Internal helper method for recording operation history in a class context. This method is intended for internal use only and should not be called externally. It formats a string representing the operation (`op`), its two operands (`a`, `b`), and the computed result (`res`), then appends this string to the class instance's `history` list while simultaneously logging it at the `DEBUG` level using Python's `logging` module.

**Parameters**
- `self` (object): The class instance (required for method binding)
- `op` (str): Name of the operation (e.g., `"add"`, `"sub"`, `"mul"`, `"div"`)
- `a` (float): First operand in the operation (e.g., `2.5`, `3.7`)
- `b` (float): Second operand in the operation (e.g., `4.2`, `1.0`)
- `res` (float): Result of the operation (e.g., `6.2`, `4.0`)

**Returns**
- (None): The method does not return any value.

**Raises**
- `TypeError`: If `op` is not a string, or `a`, `b`, `res` are not floats
- `AttributeError`: If `self.history` is not a list (e.g., `None` or a non-list type)
- `logging.LoggerError`: If the `logger` object is misconfigured (e.g., no handlers set up)
- `ValueError`: If `res` is not a valid result for the operation (e.g., division by zero)

**Examples**
```python
class Calculator:
    def __init__(self):
        self.history = []
        self.logger = logging.getLogger(__name__)

    def add(self, a: float, b: float) -> float:
        res = a + b
        self._log_op(op="add", a=a, b=b, res=res)
        return res

calc = Calculator()
calc.add(2.5, 3.7)  # Logs: "add(2.5, 3.7) = 6.2"
```
---
