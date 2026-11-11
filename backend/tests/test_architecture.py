"""Verifica la regla de dependencias de Clean Architecture.

Las capas internas no pueden importar capas externas ni frameworks:
dominio <- aplicación <- infraestructura / interfaces.
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"

FORBIDDEN = {
    "domain": {"application", "infrastructure", "interfaces", "fastapi", "pydantic", "httpx", "starlette"},
    "application": {"infrastructure", "interfaces", "fastapi", "pydantic", "httpx", "starlette"},
    "infrastructure": {"interfaces", "fastapi", "starlette"},
}


def imported_names(path: Path) -> set[str]:
    """Primer componente de cada import; los relativos se resuelven dentro de app/."""
    names = set()
    package = path.relative_to(APP).parts[:-1]
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package[: len(package) - (node.level - 1)]
                target = (*base, *(node.module.split(".") if node.module else ()))
                names.add(target[0] if target else "")
            elif node.module:
                parts = node.module.split(".")
                # backend.app.<capa>...
                names.add(parts[2] if parts[:2] == ["backend", "app"] and len(parts) > 2 else parts[0])
    return names


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_respects_dependency_rule(layer):
    violations = {
        str(path.relative_to(APP)): sorted(imported_names(path) & FORBIDDEN[layer])
        for path in (APP / layer).rglob("*.py")
    }
    violations = {file: names for file, names in violations.items() if names}

    assert violations == {}, f"La capa {layer} depende de capas externas: {violations}"
