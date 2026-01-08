# Doku core (Phase 2: AST Structure)
> Code was semantically segmented in functions/classes.



### `CalculatorError`

**Summary**
Base exception class for calculator-specific errors. This class serves as the root of an exception hierarchy for calculator operations (e.g., arithmetic errors, invalid inputs). It is intentionally empty to act as a placeholder for domain-specific exceptions (e.g., `CalculatorDivisionByZeroError`).

**Parameters**
- This class has no parameters.

**Returns**
- This class does not return a value.

**Raises**
- None: This class does not raise exceptions. It is a base class for calculator-specific exceptions.

**Examples**
```python
# Example 1: Defining a domain-specific exception
class CalculatorDivisionByZeroError(CalculatorError):
    """Error when division by zero is attempted."""
    pass

# Example 2: Raising and catching the base exception
try:
    # Simulate calculator operation
    result = divide(10, 0)
except CalculatorError as e:
    print(f"Calculator error: {e}")

# Example 3: Raising the base exception
try:
    raise CalculatorError("Invalid calculator state")
except CalculatorError as e:
    print(f"Critical calculator failure: {e}")
```

**See also**
- `CalculatorDivisionByZeroError`: A domain-specific exception for division by zero.
---


### `PrecisionError`

**Summary**
A custom exception class for the calculator module that is raised when a precision request exceeds the maximum allowable precision level (e.g., due to computational constraints, floating-point limitations, or resource constraints).

**Parameters**
- `None` (type): The `PrecisionError` class has no constructor parameters. It is an empty class (defined via `pass`).

**Returns**
- (type): Not applicable (this is a class, not a function or method).

**Raises**
- `PrecisionError`: This exception is raised when the requested precision exceeds the maximum allowable precision level (e.g., due to computational constraints).

**Examples**
```python
# Example 1: Precision validation in a Calculator
class Calculator:
    MAX_PRECISION = 10

    def calculate(self, value, precision):
        if precision > self.MAX_PRECISION:
            raise PrecisionError("Requested precision exceeds maximum allowed")
        # ... rest of calculation logic

# Example 2: Explicit error handling
try:
    raise PrecisionError("Precision too high for this operation")
except PrecisionError as e:
    print(f"Precision error: {e}")

# Example 3: Custom message in error handling
try:
    raise PrecisionError("Precision level 15 is not supported")
except PrecisionError as e:
    print(f"Error: {e}")
```

**See also**
- `CalculatorError`: The base exception class for calculator errors.
---


### `TestError`

**Summary**  
A minimal exception class for test-specific error handling in calculator operations, inheriting from `CalculatorError`. This class is intentionally empty to serve as a leaf exception in the calculator error hierarchy without adding unnecessary complexity.

**Parameters**  
- None: The class has no parameters for instantiation.

**Returns**  
- None: This class does not return values (it is a type definition, not a function).

**Raises**  
- `TestError`: A specific exception instance that can be raised via `raise TestError()` (a subclass of `CalculatorError`).

**Examples**  
```python
try:
    raise TestError()
except TestError as e:
    print(f"Test error occurred: {e}")
```

```python
try:
    if some_condition:
        raise TestError()
    result = calculate()
except TestError as e:
    print(f"Critical test error: {e}")
except CalculatorError as e:
    print(f"Generic calculator error: {e}")
```

**See also**  
- `CalculatorError`: The base exception class for calculator errors.
---


**CalculationLimitError**

An empty exception subclass that signals when calculation values exceed predefined safe limits. This class inherits from `CalculatorError` and is used to raise specific error messages for limit violations in calculation logic.

**Parameters**  
- `None`: This class does not accept parameters when instantiated.

**Returns**  
- `N/A`: This class is an exception type and does not return values.

**Raises**  
- `None`: This class does not raise exceptions. It is a type of exception that is raised by other code when calculation values exceed safe limits.

**Examples**  
```python
# Example: Raising the exception in a validation function
class Calculator:
    MAX_SAFE_VALUE = 1000000

    def calculate(self, value):
        if value > self.MAX_SAFE_VALUE:
            raise CalculationLimitError(f"Value {value} exceeds safe limit")
        return value * 2

# Usage
calculator = Calculator()
try:
    result = calculator.calculate(1500000)
except CalculationLimitError as e:
    print(f"Error: {e}")  # Output: Error: Value 1500000 exceeds safe limit
```
---


### `ArithmeticOperations`

**Summary**  
A robust calculator class for basic arithmetic operations with configurable precision, input validation, and audit logging.

**Parameters**  
- `precision` (int, optional): Number of decimal places for rounding (default: `DEFAULT_PRECISION`)

**Returns**  
- `None`: The class constructor returns `None`.

**Raises**  
- `ValueError`: If `precision` is not a non-negative integer.

**Examples**  
```python
from arithmetic import ArithmeticOperations

# Create an instance with precision 2
calc = ArithmeticOperations(precision=2)

# Add two numbers
result = calc.add(1.23, 4.56)
print(result)  # Output: 5.79

# Subtract two numbers
result = calc.subtract(10.0, 3.14)
print(result)  # Output: 6.86

# Get current mode
print(calc.mode)  # Output: "standard"
```

**See also**  
- `add`: Method for addition
- `subtract`: Method for subtraction
- `mode`: Current operation mode (e.g., "standard", "scientific")
---


### `Calculator.__init__`

**Summary**  
Initializes a calculator instance with precision validation, operation history tracking, and configuration logging. Ensures the precision parameter is within a safe range (≤ 10 decimal places), initializes an empty history list to store operation strings, and logs the configuration for auditability.

**Parameters**  
- `precision` (int): Number of decimal places for rounding calculations. **Default**: `DEFAULT_PRECISION` (a class-level constant, typically `4` or `10` depending on implementation context).

**Returns**  
- (None): Constructor methods in Python always return `None`.

**Raises**  
- `PrecisionError`: Raised when `precision > 10`. Message: `"Max precision is 10."`

**Examples**  
```python
from calculator import Calculator

# Example 1: Default Precision (Standard Financial Context)
calculator = Calculator()
print(f"Default precision: {calculator.precision}")  # Output: 4

# Example 2: Custom Precision (Scientific Context)
calculator = Calculator(precision=3)
print(f"Custom precision: {calculator.precision}")  # Output: 3

# Example 3: Invalid Precision (Error Handling)
try:
    calculator = Calculator(precision=11)
except PrecisionError as e:
    print(f"Error: {e}")  # Output: "Max precision is 10."

# Example 4: Negative Precision (No Error, but potentially invalid)
calculator = Calculator(precision=-1)
print(f"Precision: {calculator.precision}")  # Output: -1
```

**See also**  
- [Calculator class](#)
---


### `mode`

**Summary**
A simple getter method that returns the current operation mode as a string. This method is read-only and directly accesses the class-level variable `CURRENT_MODE` to provide the current mode value without any side effects. The implementation ensures minimal overhead and consistent state exposure across all instances.

**Parameters**
- `self` (object): The instance of the class (required for all instance methods in Python). This method does not accept any other parameters.

**Returns**
- (str): A string representing the current operation mode (e.g., `"production"`, `"debug"`, `"safemode"`). The value is immutable and sourced directly from the class-level variable `CURRENT_MODE`.

**Raises**
- (None): This method does not raise exceptions under normal operation. Any exceptions (e.g., `NameError`) would stem from class-level configuration issues (e.g., missing `CURRENT_MODE` in the class definition), not from the method itself.

**Examples**
```python
class DeviceController:
    CURRENT_MODE = "production"

    def mode(self) -> str:
        return CURRENT_MODE

device = DeviceController()
print(device.mode())  # Output: "production"
```

**See also**
- `switch_mode`: A method that updates the class-level mode value.
---


### `Calculator.add`

**Summary**
Adds two floating-point numbers, validates their range using an internal helper function (`_check_limits`), rounds the result to `self.precision` decimal places, and returns the rounded value.

**Parameters**
- `a` (float): First number to add (e.g., `1.234`).
- `b` (float): Second number to add (e.g., `5.678`).

**Returns**
- (float): The sum of `a` and `b` rounded to `self.precision` decimal places.

**Raises**
- `ValueError`: If `a` or `b` violates the constraints defined in `_check_limits` (e.g., negative values, values exceeding a maximum threshold).
- `TypeError`: If `self.precision` is not an integer (since Python's `round()` requires an integer for the number of decimal places).

**Examples**
```python
# Example 1: Basic usage (rounding to 2 decimal places)
class Calculator:
    def __init__(self, precision: int):
        self.precision = precision

    def add(self, a: float, b: float) -> float:
        result = a + b
        rounded_result = round(result, self.precision)
        return rounded_result

calc = Calculator(precision=2)
result = calc.add(1.234, 5.678)
print(result)  # Output: 6.91
```

```python
# Example 2: Handling invalid `self.precision` (during initialization)
calc = Calculator(precision=2.5)  # Raises TypeError
try:
    result = calc.add(1.234, 5.678)
except TypeError as e:
    print(f"Error: {e}")  # Output: "round() takes at most 2 arguments (3 given)"
```

```python
# Example 3: Handling invalid input via `_check_limits`
class Calculator:
    def __init__(self, precision: int):
        self.precision = precision

    def add(self, a: float, b: float) -> float:
        # Simulated _check_limits (enforces non-negative numbers)
        if a < 0 or b < 0:
            raise ValueError("Both numbers must be non-negative")
        result = a + b
        rounded_result = round(result, self.precision)
        return rounded_result

calc = Calculator(precision=2)
try:
    result = calc.add(-1.0, 5.678)
except ValueError as e:
    print(f"Error: {e}")  # Output: "Both numbers must be non-negative"
```

**See also**
- `Calculator.__init__`: Initializes the `Calculator` with a precision value.
---


### `subtract`

**Summary**  
The `subtract` method performs a controlled subtraction operation between two floating-point numbers (`a` and `b`). It ensures input validity through internal checks, rounds the result to the class's configured precision level, and logs the operation for auditability. This method is designed for financial or scientific contexts where precision control and input validation are critical.

**Parameters**  
- `a` (float): The **minuend** (the number from which another number is subtracted)  
- `b` (float): The **subtrahend** (the number to be subtracted)  

**Returns**  
- `float`: The result of `a - b` **rounded to `self.precision` decimal places**.  

**Raises**  
- `ValueError`: If `a` or `b` violate the class's numerical constraints (e.g., negative values for financial systems).  
- `TypeError`: If `self.precision` is not an integer (this exception may occur if the class was initialized with a non-integer precision value).  
- `RuntimeError`: If the logging operation fails (e.g., the logging subsystem is unavailable).  

**Examples**  
```python
# Example 1: Valid usage with precision = 2
calc = FinancialCalculator(precision=2)
result = calc.subtract(100.1234, 20.5678)  # Returns 79.55

# Example 2: Exception case (invalid input)
calc = FinancialCalculator(precision=2)
try:
    result = calc.subtract(-10.5, 5.0)
except ValueError as e:
    print(f"Input error: {e}")  # Output: "Negative balance not allowed"
```  

**See also**  
- `FinancialCalculator.__init__`: Initializes the precision level for the calculator.
---


### `multiply`

**Summary**  
A placeholder/test function that always returns `0.0` regardless of input values. This method is intended for development or testing purposes and does not perform actual multiplication.

**Parameters**  
- `a` (float): First operand (ignored in this implementation)  
- `b` (float): Second operand (ignored in this implementation)  

**Returns**  
- `float`: Always `0.0` (a constant value). The return value is independent of the input parameters.

**Raises**  
- No exceptions are raised by this method. It is exception-safe for all input types.

**Examples**  
```python
# Example 1: Basic call with valid floats
result = obj.multiply(2.5, 3.0)  # Returns 0.0

# Example 2: Call with non-float inputs (e.g., strings)
result = obj.multiply("hello", 10)  # Returns 0.0 (no exception)

# Example 3: Call with negative/zero values
result = obj.multiply(-1.0, 10.0)  # Returns 0.0
```

**See also**  
- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
---


Examples
```python
class Calculator:
    MIN_VALUE = -100
    MAX_VALUE = 100

    def _check_limits(self, *args):
        for val in args:
            if val < self.MIN_VALUE or val > self.MAX_VALUE:
                raise CalculationLimitError(f"Value {val} exceeds limits.")

    def calculate_sum(self, a, b):
        self._check_limits(a, b)
        return a + b
```
---


### `_log_op`

**Summary**  
Internal helper method for recording operation history in a class context. Formats a string representing a mathematical operation (e.g., `add(2.0, 3.0) = 5.0`), appends it to the class's `history` list, and logs it at the `DEBUG` level using Python's built-in `logging` module. This method is **non-blocking**, **stateful** (modifies `self.history`), and **idempotent** (repeated calls append new entries without interference). It is designed **exclusively for debugging/tracing purposes** and should **not** be used in production code without proper logging configuration.

**Parameters**  
- `op` (str): Operation name (e.g., `"add"`, `"subtract"`, `"multiply"`). Must be a valid string.  
- `a` (float): First operand (numeric value).  
- `b` (float): Second operand (numeric value).  
- `res` (float): Result of the operation (numeric value).

**Returns**  
- `None`: The method does not return any value (it is a void function).

**Raises**  
- `AttributeError`: If `self.history` is `None` (caller must initialize `self.history = []` in `__init__`).  
- `RuntimeError`: If the logging module is not configured (caller must ensure `logging.basicConfig()` is called before usage).  
- `TypeError`: If `op` is not a string, or if numeric inputs are invalid (e.g., non-numeric strings causing conversion errors during string formatting).

**Examples**  
```python
class Calculator:
    def __init__(self):
        self.history = []
    
    def _log_op(self, op: str, a: float, b: float, res: float):
        entry = f"{op}({a}, {b}) = {res}"
        self.history.append(entry)
        logger.debug(entry)

# Usage example
calc = Calculator()
calc._log_op("add", 2.5, 3.7, 6.2)  # Logs: "add(2.5, 3.7) = 6.2"
```

**See also**  
- `Calculator` class (for full implementation context)
---
