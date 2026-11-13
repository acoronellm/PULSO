# Arquitectura del backend de PULSO (Clean Architecture)

El backend FastAPI autentica las cuentas contra PostgreSQL y orquesta el análisis
cardiovascular: llama al ML Service para la predicción, la explicación SHAP y la
simulación, guarda temporalmente cada análisis y solicita las recomendaciones
educativas al workflow RAG de n8n.

Está organizado en cuatro capas. **Las dependencias apuntan siempre hacia adentro**:
el dominio no conoce FastAPI, Pydantic, httpx ni n8n.

```text
interfaces/http  ──►  application  ──►  domain  ◄──  infrastructure
(FastAPI)             (casos de uso)    (núcleo)     (ML Service, n8n, memoria)
```

## Capas

| Capa | Carpeta | Responsabilidad | Puede depender de |
|---|---|---|---|
| Dominio | `backend/app/domain/` | Entidades inmutables, reglas del perfil, errores del negocio y puertos (interfaces) | Solo Python estándar |
| Aplicación | `backend/app/application/use_cases/` | Casos de uso que coordinan el flujo | Dominio |
| Infraestructura | `backend/app/infrastructure/` | Implementaciones de los puertos: clientes HTTP, repositorio en memoria, acceso a PostgreSQL, hash de contraseñas y JWT | Dominio, SQLAlchemy, pwdlib, PyJWT, httpx, Pydantic |
| Interfaces | `backend/app/interfaces/http/` | Rutas FastAPI, contratos JSON, inyección de dependencias y traducción de errores a HTTP | Todas las anteriores |

`backend/tests/test_architecture.py` comprueba esta regla analizando los imports de cada capa.

## Estructura

```text
backend/app/
├── domain/
│   ├── entities.py        Perfil, Prediction, Explanation, AnalysisContext, RecommendationReport, SimulationOutcome…
│   ├── rules.py           ap_hi > ap_lo y coherencia del IMC (tolerancia 0,02)
│   ├── errors.py          AnalysisNotFoundError, InvalidScenarioError, ModelServiceError, RecommendationServiceError…
│   └── ports.py           CardiovascularModel, RecommendationGenerator, AnalysisRepository, UserRepository…
├── application/use_cases/
│   ├── authenticate_user.py       valida credenciales y emite un token de acceso
│   ├── register_user.py           crea una cuenta y emite un token de acceso
│   ├── analyze_profile.py          predicción + SHAP + guardar contexto → analysis_id
│   ├── request_recommendations.py  recupera el contexto y pide el RAG (sin repetir la inferencia)
│   └── simulate_scenario.py        compara perfil original y escenario hipotético
├── infrastructure/
│   ├── config.py                       variables de entorno (Settings)
│   ├── database.py                     motor PostgreSQL y sesiones SQLAlchemy
│   ├── user_model.py                   modelo persistente de la tabla users
│   ├── sqlalchemy_user_repository.py   implementación de UserRepository
│   ├── password_hasher.py              hash y verificación Argon2
│   ├── jwt_access_tokens.py            emisión y validación de JWT HS256
│   ├── ml_service_client.py            MLServiceClient       → puerto CardiovascularModel
│   ├── n8n_rag_client.py               N8nRecommendationClient → puerto RecommendationGenerator
│   └── in_memory_analysis_repository.py InMemoryAnalysisRepository → puerto AnalysisRepository
├── interfaces/http/
│   ├── routes/auth.py       POST /api/auth/register, /api/auth/login; GET /api/auth/me
│   ├── routes/analysis.py   POST /api/analyze, /api/rag, /api/simulate
│   ├── routes/health.py     GET /api/health (público)
│   ├── schemas.py           contratos JSON y conversión desde y hacia el dominio
│   ├── dependencies.py      composición: une casos de uso e implementaciones
│   └── errors.py            errores del dominio → 404 / 422 / 502
└── main.py                  create_app(); Uvicorn usa backend.app.main:app
backend/migrations/          SQL inicial de users, aplicado al crear el volumen PostgreSQL
```

## Flujo de una solicitud

`POST /api/analyze`:

1. FastAPI valida el JSON con `UserData`; las reglas de coherencia vienen de `domain/rules.py` (422 si fallan).
2. La ruta convierte el JSON en `CardiovascularProfile` y ejecuta `AnalyzeProfile`.
3. El caso de uso pide `predict` y `explain` al puerto `CardiovascularModel` (implementado por `MLServiceClient`) y guarda el contexto en `AnalysisRepository`.
4. La ruta convierte el resultado a `AnalysisResponse` (`analysis_id`, `prediction`, `shap`).

`POST /api/rag` recupera el contexto por `analysis_id` y lo envía a `RecommendationGenerator`; no vuelve a ejecutar el modelo.

`POST /api/auth/register` guarda el correo normalizado y el hash Argon2 de la
contraseña en PostgreSQL. `POST /api/auth/login` verifica las credenciales y
emite un JWT bearer firmado con HS256, válido por el tiempo configurado.
`GET /api/auth/me` valida el token y vuelve a consultar la cuenta. Las rutas de
análisis requieren el mismo bearer token y el repositorio temporal limita cada
contexto al usuario que lo creó; `/api/health` permanece público. El
frontend guarda el token en `localStorage` y lo elimina al cerrar sesión o al
recibir una respuesta 401.

## Errores

| Error del dominio | HTTP | Ejemplo |
|---|---|---|
| Validación de entrada (Pydantic y reglas del perfil) | 422 | `ap_hi debe ser mayor que ap_lo.` |
| `InvalidScenarioError` | 422 | El ML Service rechazó el escenario |
| `AnalysisNotFoundError` | 404 | `El análisis no existe o ya expiró.` |
| `ModelServiceError`, `RecommendationServiceError` | 502 | ML Service o RAG no disponibles, o respuesta fuera de contrato |
| Credenciales inválidas o token vencido | 401 | Se requiere iniciar sesión nuevamente. |
| Correo ya registrado | 409 | La cuenta ya existe. |

## Contratos que no cambiaron

Los contratos de análisis no cambian con la autenticación. Las cuentas sí se
persisten en PostgreSQL; el repositorio de contexto de análisis sigue siendo en
memoria: TTL de 900 s, máximo 100 entradas y un único proceso.

## Cómo extenderlo

- **Otro RAG o un modelo distinto:** crear una clase en `infrastructure/` que cumpla el puerto y registrarla en `interfaces/http/dependencies.py`.
- **Caché compartida (por ejemplo, Redis) para varios workers:** implementar `AnalysisRepository` en `infrastructure/` sin tocar los casos de uso.

## Pruebas

```powershell
python -m pytest -q backend/tests
```

| Carpeta | Qué prueba | Cómo |
|---|---|---|
| `tests/domain/` | Reglas del perfil | Python puro |
| `tests/application/` | Casos de uso | Dobles en memoria de los puertos (`conftest.py`) |
| `tests/infrastructure/` | Clientes del ML Service y n8n, repositorio | `httpx.MockTransport`, sin red |
| `tests/interfaces/` | Rutas y contratos JSON | `TestClient` con `app.dependency_overrides` |
| `tests/test_architecture.py` | Regla de dependencias entre capas | Análisis de imports |
