from __future__ import annotations


def normalize_cpf(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if len(digits) != 11:
        raise ValueError("CPF deve conter 11 dígitos.")
    return digits


def validate_cpf(value: str) -> str:
    digits = normalize_cpf(value)
    if len(set(digits)) == 1:
        raise ValueError("CPF inválido.")

    numbers = [int(char) for char in digits]
    for check_digit_index in (9, 10):
        weight_start = check_digit_index + 1
        total = sum(
            numbers[position] * (weight_start - position)
            for position in range(check_digit_index)
        )
        expected = (total * 10) % 11
        if expected == 10:
            expected = 0
        if numbers[check_digit_index] != expected:
            raise ValueError("CPF inválido.")

    return digits
