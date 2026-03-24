from django.forms import ValidationError


def username_validator(value):
    """Кастомный валидатор для username с выводом недопустимых символов."""
    import re
    pattern = r'^[\w.@+-]+\Z'
    invalid_chars = ''.join(sorted(set(re.sub(pattern, '', value))))
    if invalid_chars:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {invalid_chars}'
        )
