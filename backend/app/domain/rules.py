"""Reglas de negocio sobre el perfil cardiovascular."""

from .errors import InvalidProfileError

# Diferencia máxima admitida entre el IMC recibido y el calculado (redondeo)
BMI_TOLERANCE = 0.02


def expected_bmi(weight: float, height_cm: float) -> float:
    return weight / ((height_cm / 100) ** 2)


def validate_blood_pressure(ap_hi: float, ap_lo: float) -> None:
    if ap_hi <= ap_lo:
        raise InvalidProfileError("ap_hi debe ser mayor que ap_lo.")


def validate_bmi(bmi: float, weight: float, height_cm: float) -> None:
    if abs(bmi - expected_bmi(weight, height_cm)) > BMI_TOLERANCE:
        raise InvalidProfileError("bmi no coincide con el peso y la altura.")


def validate_profile(
    ap_hi: float,
    ap_lo: float,
    bmi: float,
    weight: float,
    height_cm: float,
) -> None:
    """Reglas que debe cumplir cualquier perfil antes de evaluarlo."""
    validate_blood_pressure(ap_hi, ap_lo)
    validate_bmi(bmi, weight, height_cm)


def validate_simulated_weight(weight: float, height_cm: float) -> None:
    """El ML Service recalcula el IMC con el peso simulado; debe ser positivo."""
    if expected_bmi(weight, height_cm) <= 0:
        raise InvalidProfileError("El IMC del escenario de simulación no es válido.")
