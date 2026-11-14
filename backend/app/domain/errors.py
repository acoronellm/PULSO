"""Errores del dominio.

La capa HTTP los traduce a códigos de estado; el dominio no conoce HTTP.
"""


class DomainError(Exception):
    """Error base del dominio de PULSO."""


class InvalidProfileError(DomainError):
    """El perfil no cumple las reglas de coherencia (presión arterial o IMC)."""


class AnalysisNotFoundError(DomainError):
    """El análisis solicitado no existe o ya expiró."""


class InvalidScenarioError(DomainError):
    """El servicio del modelo rechazó el escenario de simulación."""


class ExternalServiceError(DomainError):
    """Un servicio externo no respondió o incumplió su contrato."""


class ModelServiceError(ExternalServiceError):
    """Fallo del servicio del modelo (predicción, SHAP o simulación)."""


class RecommendationServiceError(ExternalServiceError):
    """Fallo del servicio de recomendaciones educativas (RAG)."""


class EmailAlreadyRegisteredError(DomainError):
    """Ya existe una cuenta con ese correo electrónico."""


class InvalidCredentialsError(DomainError):
    """El correo o la contraseña no son válidos."""
