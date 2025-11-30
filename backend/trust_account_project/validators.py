"""
Centralized Security Validators
SECURITY FIX M3: Consolidate SQL injection checks across the application

This module provides centralized validation for security threats like SQL injection.
Used by: api_hardening.py, forms.py, security.py, threat_detection.py

Benefits:
- Single source of truth for SQL injection patterns
- Pre-compiled regex patterns for better performance
- Easier maintenance (update once, affects all)
- Consistency across all validators
"""

import re
import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SQLInjectionValidator:
    """
    Centralized SQL injection pattern detection

    This validator consolidates SQL injection checks that were previously
    duplicated across 4 different files. It provides comprehensive pattern
    matching with pre-compiled regex for optimal performance.
    """

    # Complete list of SQL injection patterns
    # Consolidated from: api_hardening.py, forms.py, security.py, threat_detection.py
    PATTERNS = [
        r'union\s+select',          # UNION SELECT attacks
        r'drop\s+table',             # Table deletion
        r'delete\s+from',            # Row deletion
        r'insert\s+into',            # Data insertion
        r'update\s+.*set',           # Data modification
        r'--\s*$',                   # SQL comment (line)
        r'/\*.*\*/',                 # SQL comment (block)
        r"'\s*or\s*'",               # OR tautology
        r'1\s*=\s*1',                # Tautology
        r'admin\'\s*--',             # Admin bypass attempt
        r'or\s+1\s*=\s*1',           # OR tautology variant
        r'information_schema',       # Schema enumeration
        r'load_file\s*\(',           # File reading
        r'into\s+outfile',           # File writing
    ]

    # Pre-compile patterns for performance
    # Regex compilation happens ONCE at startup instead of on every request
    COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PATTERNS]

    @classmethod
    def validate(cls, text, field_name='input'):
        """
        Check text for SQL injection patterns

        Args:
            text (str): Text to validate
            field_name (str): Name of field being validated (for logging)

        Returns:
            tuple: (is_valid, violations_list)
                - is_valid (bool): True if no SQL injection patterns found
                - violations_list (list): List of matched pattern strings

        Example:
            is_valid, violations = SQLInjectionValidator.validate("SELECT * FROM users")
            if not is_valid:
                print(f"SQL injection detected: {violations}")
        """
        if not isinstance(text, str):
            return (True, [])

        text_lower = text.lower()
        violations = []

        for pattern in cls.COMPILED_PATTERNS:
            if pattern.search(text_lower):
                violations.append(pattern.pattern)
                logger.warning(
                    f"SECURITY: SQL injection pattern detected in {field_name}: {pattern.pattern}"
                )

        is_valid = len(violations) == 0
        return (is_valid, violations)

    @classmethod
    def has_sql_injection(cls, text):
        """
        Simple boolean check for SQL injection

        Args:
            text (str): Text to check

        Returns:
            bool: True if SQL injection patterns found, False otherwise

        Example:
            if SQLInjectionValidator.has_sql_injection(user_input):
                raise ValidationError("SQL injection detected")
        """
        is_valid, _ = cls.validate(text)
        return not is_valid


class PasswordComplexityValidator:
    """
    Password complexity validator (existing from settings.py)
    Enforces: uppercase, lowercase, numbers, symbols
    """
    def validate(self, password, user=None):
        """Validate password complexity"""
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                'Password must contain at least one uppercase letter.',
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                'Password must contain at least one lowercase letter.',
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                'Password must contain at least one number.',
                code='password_no_number',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'Password must contain at least one special character.',
                code='password_no_symbol',
            )

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )
