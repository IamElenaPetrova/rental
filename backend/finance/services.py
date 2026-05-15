from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError


# =========================
# Payment (income) validation
# =========================


def validate_payment_currency(payment, contract_currency: str) -> None:
    if payment.currency == contract_currency:
        return
    if not payment.exchange_rate:
        raise ValidationError(
            {
                'exchange_rate': (
                    'Please provide an exchange rate when paying in '
                    'a different currency.'
                )
            }
        )


# =========================
# Payment (income) apply on save
# =========================


def apply_payment_currency(payment, contract_currency: str) -> None:
    if payment.currency == contract_currency:
        payment.exchange_rate = Decimal('1')
        payment.amount_in_booking_currency = payment.amount
        return

    payment.amount_in_booking_currency = (
        Decimal(payment.amount) / Decimal(payment.exchange_rate)
    ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
