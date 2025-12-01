/**
 * US Phone Number Auto-Formatter
 * Auto-formats phone numbers to (XXX) XXX-XXXX as user types
 * Validates US phone number format
 */
(function() {
    'use strict';

    // Format phone number as user types
    function formatPhoneNumber(value) {
        // Remove all non-digits
        var cleaned = value.replace(/\D/g, '');

        // Limit to 10 digits
        cleaned = cleaned.substring(0, 10);

        // Format based on length
        if (cleaned.length <= 3) {
            return cleaned;
        } else if (cleaned.length <= 6) {
            return '(' + cleaned.substring(0, 3) + ') ' + cleaned.substring(3);
        } else {
            return '(' + cleaned.substring(0, 3) + ') ' + cleaned.substring(3, 6) + '-' + cleaned.substring(6);
        }
    }

    // Validate complete phone number
    function isValidPhoneNumber(value) {
        if (!value || value.trim() === '') return true; // Allow empty (unless required)
        var pattern = /^\(\d{3}\) \d{3}-\d{4}$/;
        return pattern.test(value);
    }

    // Apply formatting on input
    function applyFormatting() {
        $(document).on('input', 'input[type="tel"], input[name*="phone"]', function() {
            var input = $(this);
            var cursorPosition = this.selectionStart;
            var oldValue = input.val();
            var formatted = formatPhoneNumber(oldValue);

            // Only update if changed
            if (formatted !== oldValue) {
                input.val(formatted);

                // Attempt to maintain cursor position
                var newPosition = cursorPosition;
                if (formatted.length > oldValue.length) {
                    newPosition = cursorPosition + (formatted.length - oldValue.length);
                }
                this.setSelectionRange(newPosition, newPosition);
            }
        });
    }

    // Validate on blur
    function applyValidation() {
        $(document).on('blur', 'input[type="tel"], input[name*="phone"]', function() {
            var input = $(this);
            var value = input.val();
            var formGroup = input.closest('.form-group, .mb-3, .col-md-6');
            var feedback = formGroup.find('.invalid-feedback');

            // Create feedback element if it doesn't exist
            if (feedback.length === 0) {
                feedback = $('<div class="invalid-feedback">').insertAfter(input);
            }

            if (value && !isValidPhoneNumber(value)) {
                input.addClass('is-invalid');
                feedback.text('Please enter a valid phone number: (XXX) XXX-XXXX').show();
            } else {
                input.removeClass('is-invalid');
                feedback.hide();
            }
        });
    }

    // Prevent form submission with invalid phone
    function preventInvalidSubmission() {
        $(document).on('submit', 'form', function(e) {
            var form = $(this);
            var invalidPhones = form.find('input[type="tel"], input[name*="phone"]').filter(function() {
                var value = $(this).val();
                return value && !isValidPhoneNumber(value);
            });

            if (invalidPhones.length > 0) {
                e.preventDefault();
                invalidPhones.first().focus();

                // Trigger blur to show error
                invalidPhones.first().trigger('blur');

                return false;
            }
        });
    }

    // Initialize when DOM is ready
    $(document).ready(function() {
        applyFormatting();
        applyValidation();
        preventInvalidSubmission();
    });
})();
