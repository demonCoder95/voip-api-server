"""This module implements the custom exceptions for the common package.

Author: Noor
Date: January 3, 2022
License: None
"""

# Exception to indicate invalid configuration parameter
class InvalidConfigError(Exception):
    pass

# Exception to indicate unsupported payload
class UnsupportedPayload(Exception):
    pass