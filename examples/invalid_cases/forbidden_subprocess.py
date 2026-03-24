"""
forbidden_subprocess.py — invalid example: subprocess usage.

This file demonstrates a FORBIDDEN pattern under the J-NIS non_interference contract.
Any code invoking subprocess violates inv_no_hidden_side_effect.
"""
import subprocess

# FORBIDDEN: subprocess.run call — violates inv_no_hidden_side_effect
result = subprocess.run(["ls"])
