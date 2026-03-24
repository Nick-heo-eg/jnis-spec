"""
forbidden_silent_except.py — invalid example: silent except pattern.

This file demonstrates a FORBIDDEN pattern under the J-NIS non_interference contract.
Silent except (swallowing errors) violates inv_no_hidden_side_effect.
"""


def some_function():
    try:
        pass
    except Exception:
        pass  # FORBIDDEN: silent except — swallows all errors
