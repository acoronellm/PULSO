"""Verifica la regla de dependencias de Clean Architecture.

Las capas internas no pueden importar capas externas ni frameworks:
dominio <- aplicación <- infraestructura / interfaces.
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"

LAYERS = {"domain", "application", "infrastructure", "interfaces"}

FORBIDDEN = {
    "domain": {"application", "infrastructure", "interfaces", "fastapi", "pydantic", "httpx", "starlette"},
    "application": {"infrastructure", "interfaces", "fastapi", "pydantic", "httpx", "starlette"},
    "infrastructure": {"interfaces", "fastapi", "starlette"},
}

# Formas absolutas de referirse al paquete de la aplicación
APP_PREFIXES = (("backend", "app"), ("app",))


def _within_app(parts: tuple[str, ...]) -> tuple[str, ...] | None:
    """Partes del módulo relativas a app/, o None si el módulo es externo."""
    for prefix in APP_PREFIXES:
        if parts[: len(prefix)] == prefix:
            return parts[len(prefix):]
    return None


def imported_names(source: str, package: tuple[str, ...]) -> set[str]:
    """Capas internas y paquetes externos que importa un módulo.

    `package` es la ubicación del módulo dentro de app/ (por ejemplo
    ("application", "use_cases")) y sirve para resolver los imports relativos.
    """
    names: set[str] = set()

    def add_module(parts: tuple[str, ...], imported: tuple[str, ...] = ()) -> None:
        inner = _within_app(parts)
        if inner is None:
            names.add(parts[0])
        elif inner:
            names.add(inner[0])
        else:
            # "from backend.app import infrastructure": la capa es el nombre importado
            names.update(imported)

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                add_module(tuple(alias.name.split(".")))
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            imported = tuple(alias.name for alias in node.names)
            if node.level:
                base = package[: len(package) - (node.level - 1)]
                target = (*base, *module)
                names.update(target[:1] if target else imported)
            elif module:
                add_module(module, imported)

    return names


def layer_violations(app_root: Path, layer: str) -> dict[str, list[str]]:
    violations = {}
    for path in (app_root / layer).rglob("*.py"):
        package = path.relative_to(app_root).parts[:-1]
        source = path.read_text(encoding="utf-8")
        forbidden = sorted(imported_names(source, package) & FORBIDDEN[layer])
        if forbidden:
            violations[str(path.relative_to(app_root))] = forbidden
    return violations


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_respects_dependency_rule(layer):
    violations = layer_violations(APP, layer)

    assert violations == {}, f"La capa {layer} depende de capas externas: {violations}"


# -------------------------------------------------------------
# Regresión: el verificador debe reconocer cada forma de import
# -------------------------------------------------------------

@pytest.mark.parametrize(
    ("layer", "package", "source", "expected"),
    [
        # Absolutos con el prefijo "app"
        ("domain", ("domain",), "from app.infrastructure.ml_service_client import MLServiceClient", "infrastructure"),
        ("domain", ("domain",), "import app.interfaces.http.schemas", "interfaces"),
        ("application", ("application", "use_cases"), "from app.infrastructure import config", "infrastructure"),
        # Absolutos con el prefijo "backend.app"
        ("domain", ("domain",), "from backend.app.application.use_cases.analyze_profile import AnalyzeProfile", "application"),
        ("application", ("application", "use_cases"), "import backend.app.interfaces.http.schemas", "interfaces"),
        ("infrastructure", ("infrastructure",), "from backend.app.interfaces.http import schemas", "interfaces"),
        # La capa como nombre importado desde la raíz del paquete
        ("domain", ("domain",), "from backend.app import infrastructure", "infrastructure"),
        ("application", ("application", "use_cases"), "from app import interfaces", "interfaces"),
        # Relativos
        ("domain", ("domain",), "from ..infrastructure.config import Settings", "infrastructure"),
        ("domain", ("domain",), "from .. import interfaces", "interfaces"),
        ("application", ("application", "use_cases"), "from ...infrastructure.ml_service_client import MLServiceClient", "infrastructure"),
        ("infrastructure", ("infrastructure",), "from ..interfaces.http.errors import register_exception_handlers", "interfaces"),
        # Frameworks
        ("domain", ("domain",), "from pydantic import BaseModel", "pydantic"),
        ("application", ("application", "use_cases"), "import httpx", "httpx"),
        ("infrastructure", ("infrastructure",), "from fastapi import APIRouter", "fastapi"),
    ],
)
def test_detects_forbidden_imports(layer, package, source, expected):
    assert expected in imported_names(source, package) & FORBIDDEN[layer]


@pytest.mark.parametrize(
    ("layer", "package", "source"),
    [
        ("application", ("application", "use_cases"), "from ...domain.ports import CardiovascularModel"),
        ("application", ("application", "use_cases"), "from app.domain.entities import Prediction"),
        ("infrastructure", ("infrastructure",), "from backend.app.domain.errors import ModelServiceError"),
        ("infrastructure", ("infrastructure",), "import httpx"),
        ("domain", ("domain",), "from .errors import InvalidProfileError"),
        ("domain", ("domain",), "from typing import Protocol"),
    ],
)
def test_allows_inward_and_standard_imports(layer, package, source):
    assert imported_names(source, package) & FORBIDDEN[layer] == set()


def test_rule_fails_when_an_inner_layer_depends_on_an_outer_one(tmp_path):
    (tmp_path / "domain").mkdir()
    (tmp_path / "domain" / "entities.py").write_text("from typing import Protocol\n", encoding="utf-8")
    (tmp_path / "domain" / "bad.py").write_text(
        "from app.infrastructure.ml_service_client import MLServiceClient\n",
        encoding="utf-8",
    )

    assert layer_violations(tmp_path, "domain") == {
        str(Path("domain") / "bad.py"): ["infrastructure"]
    }
