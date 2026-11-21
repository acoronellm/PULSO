# Manual de desarrollo — PULSO

**Proyecto:** PULSO — Plataforma web educativa de prevención cardiovascular  
**Fecha de actualización:** 20 de noviembre de 2026  
**Repositorio:** https://github.com/acoronellm/PULSO  
**Alcance:** MVP académico con XGBoost v1, explicabilidad SHAP, simulación de escenarios y componente RAG educativo.

> **Base de revisión.** Las rutas, scripts, contratos HTTP, configuración de Docker Compose y seis workflows de GitHub Actions se contrastaron con la rama `magaarb204-patch-1`, commit `25d460f`, sincronizada con `origin/magaarb204-patch-1` al momento de la revisión. El equipo informó que las últimas ejecuciones de los seis workflows estaban en estado exitoso; esta constancia no sustituye los enlaces y registros específicos de esas ejecuciones. Para el componente RAG, el manual toma como referencia el workflow operativo actualizado cuya exportación se incorporará al repositorio antes de cerrar la entrega. No se ha verificado el procedimiento interno de despliegue utilizado por la universidad.

## 1. Propósito del documento

Este documento proporciona una guía técnica de continuidad para los equipos responsables de comprender, mantener, probar y extender PULSO. Describe la organización del repositorio, los límites entre componentes, los contratos de las APIs, la configuración de contenedores, las automatizaciones de integración y entrega, las dependencias externas, las convenciones y las decisiones técnicas relevantes. Se complementa con `Instalación.md`, que desarrolla los procedimientos de instalación y despliegue, y con `Informe_final.md`, que expone los fundamentos, experimentos y resultados académicos.

Su destinatario es una persona desarrolladora con conocimientos básicos de Python, TypeScript, Git, Docker y APIs HTTP. El sistema **no es un instrumento de diagnóstico clínico**; esta restricción debe mantenerse en modificaciones de código, interfaz, modelos y generación documental.

## 2. Descripción general del proyecto desde la perspectiva de desarrollo

PULSO es una aplicación web que recibe un perfil de variables cardiovasculares, consulta un clasificador XGBoost, devuelve la clasificación junto con contribuciones SHAP, permite simular cambios hipotéticos en variables seleccionadas y solicita explicaciones o recomendaciones educativas mediante un workflow RAG. La integración está desacoplada: la API FastAPI gestiona los casos de uso y los contratos, el servicio ML ejecuta inferencia y SHAP, y n8n gestiona la recuperación documental y la generación con Gemini.

### 2.1 Tecnologías principales

| Área | Tecnologías verificadas o documentadas | Propósito |
|---|---|---|
| Cliente web | TypeScript, React, Vite, Tailwind CSS | Captura de perfiles y presentación de resultados |
| Backend | Python 3.11, FastAPI, Pydantic, Uvicorn | API, validación, coordinación, adaptación de respuestas |
| Servicio predictivo | Python 3.11, XGBoost, SHAP, Joblib | Inferencia, contribuciones de variables y simulación |
| Integración RAG | n8n, Google Gemini | Recuperación documental y redacción educativa |
| Base documental | Supabase, PostgreSQL, pgvector | Embeddings y recuperación por similitud |
| Contenedores | Docker y Docker Compose v2 | Construcción y ejecución reproducible local |
| Proxy inverso | NGINX | Exposición del frontend y rutas `/api/` |
| Calidad y entrega | GitHub Actions, pytest, Vitest, oxlint, TypeScript | Pruebas, verificaciones, publicación de imágenes |
| Repositorio y artefactos | Git, GitHub, GHCR | Versionado de código y entrega de imágenes |

El dataset original es `cardio_train.csv` del *Cardiovascular Disease Dataset*, procesado para el entrenamiento del clasificador. Para el MVP se seleccionó XGBoost v1 con umbral global **0,38**. La salida es una clasificación estadística respecto a la variable `cardio` de los datos, no una probabilidad clínica validada de un evento cardiovascular futuro.

### 2.2 Componentes principales

1. **Frontend:** formulario, resultado predictivo, factores SHAP, simulación y visualización de información documental.
2. **Backend FastAPI:** valida perfiles, invoca casos de uso, coordina ML y RAG y conserva temporalmente el contexto de cada análisis.
3. **ML Service:** carga el artefacto oficial de XGBoost, calcula probabilidades y contribuciones SHAP, y evalúa escenarios modificados.
4. **NGINX:** punto de entrada HTTP en la ejecución de referencia con Docker Compose; sirve el cliente a través del contenedor frontend y enruta `/api/` al backend.
5. **n8n externo:** recibe solicitudes validadas del backend, consulta el corpus documental y elabora la información preventiva mediante Gemini.
6. **Supabase/pgvector externo:** almacena la base documental de 15 fuentes, dividida en 160 fragmentos con embeddings de 3.072 dimensiones.

La universidad facilitó la publicación de PULSO mediante una URL pública a partir del repositorio proporcionado por el equipo. Se exigió disponer de las imágenes y configuración Docker preparadas, pero no se ha confirmado si la institución utiliza Docker Compose ni cuál es su plataforma de orquestación.

## 3. Estructura del repositorio

### 3.1 Árbol general del repositorio

Estructura de referencia contrastada con el listado de archivos de la rama `magaarb204-patch-1` (commit `25d460f`):

```text
PULSO/
├── .github/
│   └── workflows/                 # CI, infraestructura, ML y entrega de imágenes
├── .vscode/                       # Configuración auxiliar del editor
├── backend/
│   ├── app/
│   │   ├── application/           # Casos de uso
│   │   ├── domain/                # Entidades, reglas y errores del dominio
│   │   ├── infrastructure/        # Adaptadores y configuración
│   │   ├── interfaces/http/       # Rutas, esquemas, dependencias y errores HTTP
│   │   └── main.py                # App FastAPI
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/                      # Componentes, integración y pruebas del frontend
│   ├── Dockerfile
│   ├── package.json
│   └── package-lock.json
├── ml_service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── ml/                            # Desarrollo y análisis ML
├── models/pulso/v1/               # Artefacto oficial versionado
│   └── pulso_xgboost.joblib
├── rag/workflows/                  # Exportaciones del workflow RAG
├── infrastructure/nginx/
│   └── default.conf
├── data/                           # Insumos de datos del proyecto
├── notebooks/                      # Exploración y experimentación
├── tests/                          # Pruebas adicionales/integración
├── docs/                           # Material técnico complementario
├── .env.example
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── requirements-ml.txt
├── Informe_final.md
├── Instalación.md
├── Desarrollo.md                  # Manual de desarrollo a incorporar
└── README.md
```

Este árbol es una vista de las rutas relevantes, **no un inventario exhaustivo**. Los nombres reales confirmados en Git son `Informe_final.md` e `Instalación.md`. `Desarrollo.md` es el presente manual y debe agregarse al repositorio como parte de la entrega.

### 3.2 Descripción de directorios y archivos relevantes

| Ruta | Responsabilidad |
|---|---|
| `backend/app/domain/` | Reglas de negocio independientes de HTTP y proveedores externos |
| `backend/app/application/use_cases/` | Orquestación de análisis, recomendaciones y simulación |
| `backend/app/interfaces/http/` | Contratos HTTP, validación Pydantic, rutas y dependencias |
| `backend/app/infrastructure/` | Configuración, acceso al servicio ML y cliente del RAG |
| `backend/tests/` | Pruebas automatizadas del backend, contratos y adaptadores |
| `frontend/src/` | Componentes React, utilidades, integración y tests |
| `ml_service/` | API de inferencia y dependencias del modelo |
| `models/pulso/v1/pulso_xgboost.joblib` | Artefacto oficial de ML usado al construir la imagen |
| `rag/workflows/` | Exportación actualizada de referencia del RAG operativo en n8n; conservar la versión equivalente a la del servidor |
| `infrastructure/nginx/default.conf` | Enrutamiento HTTP de la ejecución con Compose |
| `.github/workflows/` | Definición de verificaciones automáticas y Continuous Delivery |
| `docker-compose.yml` | Topología local reproducible de cuatro servicios |
| `.env.example` | Inventario de variables configurables, sin secretos reales |
| `README.md` | Presentación y enlaces principales del proyecto |

## 4. Organización de la solución a nivel de código

### 4.1 Organización por módulos o capas

El backend sigue una adaptación de **Clean Architecture**:

- **Dominio:** entidades (`CardiovascularProfile`, `Prediction`, `Explanation`, `ScenarioChanges` y reportes documentales), validaciones y errores de negocio. No debería depender de FastAPI, n8n o detalles de Docker.
- **Aplicación:** casos de uso `AnalyzeProfile`, `RequestRecommendations` y `SimulateScenario`. Coordina acciones sin codificar detalles de presentación o protocolos externos.
- **Infraestructura:** adaptadores de comunicación con el servicio ML, cliente HTTP n8n, configuración y administración de contexto temporal.
- **Interfaces HTTP:** rutas FastAPI, esquemas Pydantic, inyección de dependencias y traducción de errores a respuestas HTTP.

El frontend no ejecuta el modelo predictivo ni debe guardar el secreto de n8n. El ML Service es la fuente de predicciones y explicaciones SHAP; el RAG **no** recalcula la clasificación ni debe atribuir causalidad a las contribuciones SHAP.

### 4.2 Relación entre componentes del sistema y código fuente

| Componente / responsabilidad | Ubicación o interfaz |
|---|---|
| Entrada HTTP de backend | `backend/app/main.py` |
| Rutas de análisis, RAG y simulación | `backend/app/interfaces/http/routes/analysis.py` |
| Validación de perfiles y contratos JSON | `backend/app/interfaces/http/schemas.py` |
| Dependencias de casos de uso | `backend/app/interfaces/http/dependencies.py` |
| Caso de uso de análisis | `backend/app/application/use_cases/analyze_profile.py` |
| Caso de uso RAG | `backend/app/application/use_cases/request_recommendations.py` |
| Caso de uso de simulación | `backend/app/application/use_cases/simulate_scenario.py` |
| Cliente RAG HTTP | `backend/app/infrastructure/n8n_rag_client.py` |
| Variables y ajustes de backend | `backend/app/infrastructure/config.py` |
| Frontend | `frontend/src/` |
| Servicio ML | `ml_service/app/` |
| Definición de servicios Docker | `docker-compose.yml` |
| Proxy inverso | `infrastructure/nginx/default.conf` |

**Contrato HTTP del backend** (rutas registradas con prefijo `/api`):

| Método / ruta | Entrada principal | Salida / función |
|---|---|---|
| `GET /api/health` | Ninguna | Estado del backend |
| `POST /api/analyze` | Perfil cardiovascular validado | `analysis_id`, `prediction`, `shap` |
| `POST /api/rag` | `{ "analysis_id": "UUID" }` | Explicaciones por factor, recomendaciones y fuentes |
| `POST /api/simulate` | `original`, `changes` | Predicción original y simulada, diferencia y cambios aplicados |

**Secuencia de análisis y RAG.** El frontend invoca `/api/analyze`; el backend valida el perfil y obtiene la predicción y factores SHAP desde ML. Almacena temporalmente el contexto validado e informa un `analysis_id`. Cuando el usuario solicita información documental, el frontend invoca `/api/rag` con ese identificador. El backend recupera el contexto correspondiente y construye la solicitud al webhook n8n. Esto evita que el navegador reenvíe y modifique por su cuenta la probabilidad o los factores SHAP. El RAG es independiente de la ejecución inicial de ML.

**Contexto temporal:** la implementación de referencia emplea caché en memoria con TTL de 900 segundos y capacidad máxima de 100 registros. Al reiniciarse el backend o expirar la entrada puede dejar de ser válido el `analysis_id`. Es una solución de MVP de una instancia, no persistencia de historial clínico. Para múltiples réplicas sería necesario diseñar un almacenamiento compartido y controles de privacidad apropiados.

**Perfil de entrada:** `gender`, `height`, `weight`, `ap_hi`, `ap_lo`, `smoke`, `alco`, `active`, `age_years`, `bmi`. El BMI es opcional en la API, se calcula de manera definitiva a partir de estatura y peso, y se valida si el cliente lo proporcionó. Debe cumplirse `ap_hi > ap_lo`, además de las restricciones de rango. La simulación modifica solamente las variables autorizadas por su contrato (`weight`, `ap_hi`, `ap_lo`, `smoke`, `alco`, `active`); no debe alterar arbitrariamente edad o sexo.

**Respuesta RAG:** incluye `summary`, `recommendations`, `factor_explanations`, `considerations`, `note` e `insufficient_information`. Cada explicación/recomendación puede incluir `source_ids` y metadatos documentales (`source`, `author`, `publication_year`, `source_url`, `pdf_url`, `score`, `lines`). La interfaz debe priorizar `factor_explanations` para presentar explicaciones específicas por factor y evitar duplicar innecesariamente el texto de `summary`.

## 5. Contenedores

### 5.1 Contenedores utilizados

En la topología **local de referencia** de Docker Compose existen cuatro servicios:

| Servicio | Contenedor de referencia | Función | Puerto |
|---|---|---|---|
| `nginx` | `pulso-nginx` | Proxy inverso y entrada al sistema | `80:80` |
| `frontend` | `pulso-frontend` | Servir la aplicación compilada | `80` interno |
| `backend` | `pulso-backend` | API y coordinación | `127.0.0.1:8000:8000` |
| `ml-service` | `pulso-ml-service` | Predicción, SHAP y simulación | `127.0.0.1:8001:8001` |

n8n y Supabase son **dependencias remotas** y no forman parte de estos cuatro contenedores. La configuración anterior no demuestra qué tecnología usa la universidad en su publicación pública. La institución solicitó previamente las imágenes y la configuración Docker, pero no se ha confirmado el método exacto de ejecución en sus servidores.

### 5.2 Archivos relacionados con contenedores

- `docker-compose.yml`: define servicios, construcción, variables, dependencias, puertos, verificación de salud y volumen del proxy.
- `frontend/Dockerfile`: construye la aplicación web y prepara su servicio HTTP.
- `backend/Dockerfile`: imagen Python del backend.
- `ml_service/Dockerfile`: imagen del servicio predictivo, que copia el artefacto de `models/pulso/v1/pulso_xgboost.joblib` a `/app/artifacts/final/model/pulso_xgboost.joblib`.
- `infrastructure/nginx/default.conf`: reglas del proxy inverso.
- `.dockerignore`: exclusión de archivos no requeridos en contextos de construcción.

### 5.3 Construcción y ejecución de contenedores

Desde la raíz del repositorio, con Docker Compose v2 y el archivo `.env` configurado:

```bash
docker compose config
```

```bash
docker compose build
```

```bash
docker compose up -d
```

```bash
docker compose ps
```

Para reconstruir servicios tras cambios de código o Dockerfile:

```bash
docker compose up -d --build
```

Para consultar errores:

```bash
docker compose logs --tail=100 backend ml-service nginx
```

Para detener y eliminar los contenedores de esta instalación local:

```bash
docker compose down
```

No ejecutar `down -v` ni limpiezas agresivas sobre entornos cuyo almacenamiento o dependencias no estén identificados.

### 5.4 Redes, puertos y volúmenes

En Compose, los nombres de servicio permiten la comunicación interna. El backend utiliza `http://ml-service:8001` para invocar al ML Service. El servicio `nginx` publica el puerto 80; el backend y ML solo se exponen en la interfaz local `127.0.0.1` de la máquina anfitriona. El frontend queda accesible internamente por el proxy.

Compose no declara una red personalizada, por lo cual utiliza la red predeterminada del proyecto. `ml-service` tiene un healthcheck HTTP a `/health` cada 10 s, con timeout de 5 s y cinco reintentos; el backend espera que ese servicio esté saludable (`condition: service_healthy`). NGINX depende de frontend y backend, aunque su `depends_on` no verifica por sí mismo la salud HTTP de ambos. Se monta únicamente el archivo `./infrastructure/nginx/default.conf` en `/etc/nginx/conf.d/default.conf` en modo solo lectura; no hay un volumen de datos persistente definido. `frontend` y `nginx` utilizan `restart: unless-stopped`; el backend y ML Service no tienen política explícita de reinicio en el Compose. No se despliegan n8n ni PostgreSQL localmente: los embeddings residen en Supabase y el contexto temporal de análisis se conserva en memoria del backend.

### 5.5 Recomendaciones para modificar contenedores

- Mantener el artefacto oficial versionado del modelo al modificar la imagen ML; una reconstrucción debe comprobar `model_loaded: true`.
- Cambiar con cuidado nombres DNS de servicios y rutas del proxy; ejecutar `docker compose config` y pruebas de NGINX.
- Mantener `RAG_WEBHOOK_API_KEY` solamente en el backend o en la configuración segura del servidor, no en JavaScript del cliente.
- Evitar publicar los puertos de backend y ML directamente a Internet si el proxy es la entrada prevista.
- Verificar contratos `/api/*`, pruebas automatizadas y health checks después de cualquier cambio.
- No asumir que la infraestructura pública de la universidad replica exactamente el Compose del repositorio.

## 6. Scripts y automatizaciones

### 6.1 Scripts principales

**Frontend** (`frontend/package.json`):

| Comando (desde `frontend/`) | Uso |
|---|---|
| `npm ci` | Instalar dependencias según lockfile |
| `npm run dev` | Iniciar Vite para desarrollo |
| `npm run build` | Comprobar TypeScript y compilar frontend |
| `npm run typecheck` | Validar tipos TypeScript |
| `npm run lint` | Ejecutar oxlint |
| `npm run test` | Ejecutar Vitest |
| `npm run preview` | Servir una vista previa de la compilación |

**Backend y servicios:**

```bash
python -m pytest -q backend/tests
```

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

```bash
python -m uvicorn ml_service.app.main:app --host 127.0.0.1 --port 8001
```

Los dos procesos Python deben iniciarse desde la raíz en entornos locales sin contenedores y con las dependencias instaladas; para instrucciones completas consultar `Instalación.md`.

**Automatizaciones de GitHub Actions:**

| Workflow | Responsabilidad principal |
|---|---|
| `.github/workflows/frontend-ci.yml` | Node.js 22, `npm ci`, Oxlint, comprobación de tipos, Vitest y build de Vite |
| `.github/workflows/backend-rag-ci.yml` | Python 3.11, instalación de dependencias y `python -m pytest -q backend/tests` |
| `.github/workflows/ml-service-ci.yml` | Python 3.11, Ruff y `python -m pytest -q ml_service/tests` |
| `.github/workflows/ml-training-ci.yml` | Python 3.11, Ruff y `python -m pytest -q tests`; utiliza datos sintéticos, no ejecuta un entrenamiento integral |
| `.github/workflows/infrastructure-ci.yml` | Validación de Compose, construcción de imágenes, verificación NGINX con upstreams simulados del frontend y backend |
| `.github/workflows/delivery.yml` | Entrega continua desde `main`: construye y publica imágenes de frontend, backend y ML Service en GHCR, valida etiquetas y digests y ejecuta smoke tests de las imágenes publicadas |

**Estado de ejecución comunicado por el equipo (20 de noviembre de 2026):** los seis workflows se encontraban en verde en sus últimas ejecuciones. Este estado fue revisado por el equipo en GitHub y comunicado para la documentación; no se adjuntaron aquí identificadores de ejecución ni enlaces individuales. Debe conservarse en la entrega evidencia trazable si se presenta como resultado formal de CI/CD.

**Alcance de la automatización:** `infrastructure-ci.yml` utiliza upstreams simulados para probar el enrutamiento de NGINX; no ejecuta el flujo clínico-educativo completo. En cambio, `delivery.yml` publica y vuelve a descargar imágenes reales, comprueba que el modelo está cargado en ML Service y realiza verificaciones de disponibilidad del frontend y backend. Tampoco ejecuta el flujo extremo a extremo con RAG real. La publicación en GHCR **no constituye un despliegue automático en los servidores universitarios**; el mecanismo interno de la universidad es desconocido.

### 6.2 Ubicación de scripts auxiliares

Además de los comandos definidos en `frontend/package.json`, el proyecto incluye archivos de investigación en `ml/`, `notebooks/` y `tests/`. Sus nombres, argumentos y entradas pueden variar entre commits experimentales; revisar las cabeceras de los archivos específicos antes de ejecutarlos. No se debe asumir que exista un script genérico `npm run migrate`, porque **no figura** entre los scripts de frontend verificados.

### 6.3 Consideraciones para su uso

- Utilizar Python 3.11 y Node.js compatible con el Dockerfile (Node.js 22 en las compilaciones verificadas).
- No ejecutar scripts de entrenamiento sobre artefactos de producción sin versionar las salidas.
- No utilizar el conjunto Test oficial para ajuste de umbrales o hiperparámetros.
- Aislar pruebas de infraestructura con mocks de las pruebas reales de integración.
- Registrar versiones de dependencias, commit y variables no sensibles al adjuntar evidencia de ejecución.

## 7. Variables de entorno

### 7.1 Variables requeridas

La configuración de backend utiliza Pydantic Settings (`backend/app/infrastructure/config.py`), con lectura opcional de `.env`. La referencia pública es `.env.example`:

| Variable | Valor de ejemplo o referencia | Uso |
|---|---|---|
| `ML_SERVICE_URL` | `http://127.0.0.1:8001` fuera de Docker | Dirección del servicio predictivo |
| `ML_TIMEOUT_SECONDS` | `30` | Tiempo de espera para ML |
| `RAG_SERVICE_URL` | URL HTTPS completa del webhook | Ubicación del servicio RAG remoto |
| `RAG_TIMEOUT_SECONDS` | `90` | Tiempo límite de la solicitud RAG |
| `RAG_WEBHOOK_API_KEY` | Secreto, sin valor público | Autenticación entre backend y n8n |
| `ANALYSIS_CACHE_TTL_SECONDS` | `900` | Caducidad del contexto temporal de análisis |
| `ANALYSIS_CACHE_MAX_ENTRIES` | `100` | Máximo de contextos en memoria |

En el Compose vigente, `RAG_WEBHOOK_API_KEY` se declara **obligatoria** mediante sustitución de variables. El backend la envía al webhook n8n a través de `X-PULSO-RAG-Key`. La URL debe identificar el webhook de producción `/webhook/...` y no el editor ni la ruta temporal `/webhook-test/...`.

### 7.2 Variables por ambiente

- **Desarrollo local sin Docker:** `ML_SERVICE_URL=http://127.0.0.1:8001`; el frontend se ejecuta con Vite y requiere que sus llamadas `/api/` alcancen al backend según el proxy o configuración vigente.
- **Desarrollo/pruebas con Docker Compose:** el contenedor backend recibe `ML_SERVICE_URL=http://ml-service:8001`, `ML_TIMEOUT_SECONDS=30` y los ajustes de RAG de `.env`.
- **Pruebas automatizadas:** emplear datos de prueba y mocks cuando el workflow así lo define. Un servicio RAG simulado no demuestra disponibilidad del webhook real.
- **Publicación institucional:** la configuración la administra el responsable de infraestructura de la universidad. Solo deben documentarse variables y revisiones reales cuya utilización esté confirmada; no publicar valores secretos.
- **n8n remoto:** mantiene por separado la configuración de Gemini, Supabase y del webhook. Estas credenciales no deben inyectarse en el frontend.

### 7.3 Archivos de configuración

Crear `.env` desde `.env.example` en el directorio raíz. En Bash/WSL:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Ejemplo con marcadores no operativos:

```dotenv
RAG_SERVICE_URL=https://SERVIDOR-N8N/webhook/RUTA-REAL
RAG_TIMEOUT_SECONDS=90
RAG_WEBHOOK_API_KEY=REEMPLAZAR_POR_SECRETO_COMPARTIDO
```

El archivo `.env` debe mantenerse fuera del repositorio; comprobar su exclusión mediante `.gitignore`. No añadir archivos `.env.production` o equivalentes al control de versiones si contienen secretos.

### 7.4 Manejo seguro de secretos

- Compartir la clave RAG por un medio autorizado y de acceso restringido, nunca por commits, issues o capturas públicas.
- Rotar claves coordinadamente entre backend y webhook n8n. La rotación unilateral interrumpe el acceso al RAG.
- Registrar errores de integración sin volcar payloads de salud ni encabezados de autenticación.
- Mantener Gemini y Supabase del lado de n8n; no suministrar sus tokens al navegador.
- Si se sospecha una filtración, revocar o cambiar la credencial y revisar la exposición en logs e historial.

## 8. Flujo de trabajo de desarrollo

### 8.1 Preparación del entorno

1. Clonar el repositorio y seleccionar la rama o commit asignado.
2. Instalar Git, Docker Compose o el entorno Python/Node necesario.
3. Crear `.env` a partir de `.env.example` y completar valores obtenidos de manera segura.
4. Validar la configuración con `docker compose config` y construir los servicios.
5. Comprobar `/api/health`, el estado del servicio ML y un caso de análisis, simulación y RAG si el webhook está autorizado y operativo.

El procedimiento completo de instalación se documenta en `Instalación.md`.

### 8.2 Desarrollo de nuevas funcionalidades

Trabajar en una rama específica creada a partir de una revisión actualizada y aprobada. Localizar el requerimiento y modificar la capa propietaria de la responsabilidad. Para una nueva regla de validación, priorizar el dominio y su contrato HTTP; para un cambio en el mensaje visible, el frontend; para cambios documentales, el workflow remoto y la trazabilidad de las fuentes.

Ejemplo de creación de rama:

```bash
git switch main
```

```bash
git pull --ff-only origin main
```

```bash
git switch -c feature/nombre-cambio
```

Agregar o actualizar pruebas antes de proponer la integración. Evitar cambios no relacionados dentro de un mismo pull request.

### 8.3 Ejecución de pruebas y validaciones

Desde `frontend/`:

```bash
npm ci
```

```bash
npm run lint
```

```bash
npm run typecheck
```

```bash
npm run test
```

```bash
npm run build
```

Desde la raíz, con las dependencias Python del backend instaladas:

```bash
python -m pytest -q backend/tests
```

Para infraestructura:

```bash
docker compose config
```

```bash
docker compose build
```

Para una prueba funcional local, consultar también `docker compose ps` y ejecutar un análisis válido, una simulación y una consulta RAG. Distinguir siempre resultados de pruebas unitarias, pruebas con mocks y pruebas reales de extremo a extremo. Los tests deben revisarse en el commit de destino; no se asume que una ejecución histórica siga siendo válida para otro commit.

### 8.4 Integración de cambios

Antes de abrir un pull request: comprobar `git diff --check`, ejecutar pruebas pertinentes, documentar cambios de contrato y verificar que no se agregaron secretos ni datasets sensibles. Crear commit descriptivo y enviar la rama:

```bash
git status -sb
```

```bash
git diff --check
```

```bash
git add RUTA_DEL_ARCHIVO_MODIFICADO
```

```bash
git commit -m "feat(area): describe cambio"
```

```bash
git push -u origin HEAD
```

Solicitar revisión por pull request. Contrastar los cambios con la guía interna `GUIA_CI_CD_MLOPS_TESTING_PULSO` cuando esté disponible, incluyendo cobertura, ejecuciones reales de GitHub Actions, diferencias entre mocks y servicios reales, regresiones y evidencia del commit. No aprobar únicamente por ver una marca verde aislada. Respetar las reglas de protección de ramas, sin bypass.

El workflow `delivery.yml` se ejecuta sobre `main` y publica imágenes Docker en GHCR con etiquetas vinculadas al commit y la ejecución; valida su descarga e incorpora digests y smoke tests. **No se ha confirmado que estos artefactos activen automáticamente el despliegue público universitario.**

## 9. Dependencias y servicios externos

### 9.1 Servicios externos integrados

| Dependencia | Rol | Dónde se administra |
|---|---|---|
| n8n | Orquestación RAG y webhook de recomendaciones | Servidor externo al Compose de PULSO |
| Google Gemini | Modelo generativo y embeddings del corpus | Credenciales y workflows del servicio RAG |
| Supabase/pgvector | Almacenamiento y recuperación semántica | Proyecto externo de Supabase |
| GitHub | Repositorio, revisión y automatizaciones | Organización/cuenta del proyecto |
| GitHub Container Registry (GHCR) | Publicación de imágenes Docker de entrega | GitHub Packages |
| Universidad | Publicación de la aplicación por URL pública | Infraestructura institucional no administrada directamente por el equipo |

### 9.2 Requisitos de acceso

Para desarrollar el backend, frontend y ML en modo local se necesita acceso al repositorio y herramientas de ejecución. Para probar **RAG real** se requieren la URL completa de producción del webhook n8n y `RAG_WEBHOOK_API_KEY` válidos. Para mantener el contenido documental o el workflow remoto se necesitan permisos independientes sobre n8n, el proyecto Supabase y el proveedor de Gemini. No deben utilizarse credenciales compartidas de forma pública.

La publicación pública de la universidad puede probarse desde un navegador con su URL, pero esto no implica acceso administrativo al servidor. Solicitudes de reinicio, actualización o revisión de logs institucionales deben coordinarse con el personal autorizado.

### 9.3 Consideraciones de desarrollo y pruebas

**Gestión de la versión del RAG.** El archivo JSON de `rag/workflows/` se considera la exportación de referencia del workflow operativo actualizado de n8n. La versión definitiva de dicho archivo debe incorporarse al repositorio antes de etiquetar la entrega y debe excluir credenciales, tokens, secretos y cualquier dato personal. El estado activo del servicio se administra en n8n, no por GitHub Actions; por tanto, un cambio del JSON no actualiza automáticamente el workflow remoto. Una modificación del RAG exige comprobar compatibilidad de entrada/salida con `backend/app/infrastructure/n8n_rag_client.py`, especialmente `factor_explanations`, `recommendations`, las fuentes y sus metadatos.


- **Corpus RAG definitivo:** 15 documentos normalizados y 160 chunks; tabla `public.documents_pulso_test`; función de consulta `match_documents_pulso_test`; embeddings generados con `models/gemini-embedding-001` de 3.072 dimensiones.
- **Pruebas aisladas:** la validación estructural del corpus y la recuperación semántica deben diferenciarse de la evaluación del contenido generado.
- **Mocks:** útiles para contratos y proxy, pero no sustituyen invocaciones a n8n, Gemini o Supabase reales.
- **RAG externo:** depende de la disponibilidad del hosting y de las cuotas/latencia de los proveedores. El archivo JSON del repositorio debe mantenerse sincronizado con el workflow activo; una exportación sin credenciales permite recuperar la configuración lógica, pero no sustituye la configuración de accesos y secretos. Comprobar reintentos, expiración de solicitudes y errores de autorización.
- **Datos personales:** utilizar perfiles sintéticos en demos, capturas, tests y logs. Evitar conservar información sensible más tiempo del necesario.
- **Calidad documental:** un `source_id` válido comprueba trazabilidad técnica, no garantiza por sí solo el respaldo semántico de cada afirmación.

## 10. Convenciones del proyecto

### 10.1 Convenciones de código

En Python, seguir el estilo y separación de responsabilidades existente: paquetes en `snake_case`, clases en `PascalCase`, nombres expresivos y tipado donde el código lo requiera. Las validaciones del dominio deben mantenerse fuera de rutas HTTP cuando sea viable; los esquemas Pydantic traducen entradas y salidas. En TypeScript/React, conservar componentes funcionales, tipos y utilidades reutilizables conforme a la estructura actual. Ejecutar `oxlint`, `tsc`, Vitest y pytest según el módulo modificado.

Mantener pruebas para entradas inválidas de presión arterial, consistencia de BMI, simulación, respuesta RAG y manejo de errores de los proveedores. No modificar el orden de features del modelo sin volver a entrenar o revisar el contrato del artefacto oficial.

### 10.2 Convenciones de repositorio

Usar ramas con intención identificable, por ejemplo `feature/...`, `fix/...`, `test/...` o `docs/...`; mensajes de commit como `feat(frontend): ...`, `fix(rag): ...`, `docs(development): ...`. Evitar subir `.env`, credenciales, archivos de resultados temporales o artefactos no aprobados. Proponer cambios mediante pull request y adjuntar evidencia de pruebas de la revisión efectiva.

Para ML, conservar explícitamente la identificación de versión (`PULSO v1`) y documentar la procedencia de dataset, particiones, hiperparámetros, umbral y artefacto. No sustituir el archivo oficial `.joblib` por uno experimental sin una decisión reproducible y evaluación independiente.

### 10.3 Convenciones de documentación

Actualizar `README.md`, `Instalación.md`, `Desarrollo.md` y, cuando corresponda, `Informe_final.md` al cambiar arquitectura, rutas, variables, contratos, dependencias o procedimientos de despliegue. Los diagramas deben representar la configuración implementada, no una propuesta obsoleta. Registrar fechas, versiones y enlaces a evidencia verificable; no presentar planes o ejecuciones simuladas como resultados completados.

## 11. Problemas frecuentes y recomendaciones

### 11.1 Problemas frecuentes

| Síntoma | Diagnóstico inicial | Acción sugerida |
|---|---|---|
| Compose falla por `RAG_WEBHOOK_API_KEY` | Secreto vacío o ausente | Configurar valor válido en `.env` y repetir `docker compose config` |
| `POST /api/rag` devuelve error | `analysis_id` expirado, URL incorrecta o autenticación RAG | Repetir análisis; revisar backend y webhook con acceso autorizado |
| `ml-service` no está saludable | Artefacto ausente/incompatible o fallo de dependencias | Revisar logs, ruta y versión de `pulso_xgboost.joblib` |
| Respuesta 422 en análisis o simulación | Rangos o restricciones incoherentes | Validar presión, peso, IMC y esquema de entrada |
| Frontend abre pero `/api/` falla | Backend o proxy no disponible | Revisar `default.conf`, `docker compose ps` y `/api/health` |
| n8n responde 503 | Servicio remoto en reinicio o suspensión | Revisar disponibilidad y estrategia de reintento configurada |
| RAG tarda demasiado | Latencia de hosting, red o Gemini | Consultar métricas de nodos y timeouts; no atribuirlo al ML sin evidencia |
| Un análisis previo deja de existir | Contexto temporal vencido o backend reiniciado | Crear un análisis nuevo; considerar caché compartida para escalamiento |
| El CI verde no reproduce la app completa | Prueba con mock o cobertura parcial | Revisar pasos del workflow y ejecutar caso real de integración |
| Cambio de código no aparece en URL pública | Publicación institucional no sincronizada aún | Coordinar con el administrador, verificar el commit efectivamente desplegado |

### 11.2 Deuda técnica conocida

- **Caché de contexto en memoria:** adecuada para un MVP de una instancia; requiere rediseño para múltiples réplicas o alta disponibilidad.
- **Dependencia de n8n externo:** disponibilidad, autenticación y latencia afectan las recomendaciones sin invalidar necesariamente la inferencia ML.
- **Calidad semántica RAG:** la validación de fuentes existentes no certifica el respaldo completo de las afirmaciones; requiere regresión y revisión documental continuas.
- **Variaciones por edad:** XGBoost v1 presenta sensibilidades y especificidades diferentes entre grupos; los experimentos de umbrales y modelos especializados no justificaron reemplazar el modelo global.
- **Representatividad del dataset:** no se dispone de validación clínica externa ni puede presumirse generalización a la población colombiana o a mayores de 65 años.
- **Despliegue universitario:** no está documentado el mecanismo interno de publicación, escalado o actualización. Evitar diseñar automatizaciones que presuman acceso inexistente.
- **Sincronización del workflow RAG:** mantener en `rag/workflows/` una exportación sin secretos equivalente al workflow de n8n utilizado en producción y actualizarla cada vez que cambien nodos, reglas, prompts o contratos.
- **Evidencia y trazabilidad:** conservar los enlaces a las ejecuciones exitosas de GitHub Actions y las comprobaciones de integración y usabilidad en el informe correspondiente, distinguiendo pruebas automáticas de verificaciones manuales.

Autenticación de usuarios e historial persistente no son requisitos bloqueantes del alcance académico actual; cualquier extensión que los incorpore requiere evaluación de privacidad, seguridad y almacenamiento de información personal.

### 11.3 Recomendaciones para continuidad

Priorizar la evaluación de las pruebas pendientes, mantener la compatibilidad entre frontend/backend/ML/RAG y automatizar pruebas de regresión que reproduzcan casos reales sin exponer secretos. Antes de cambiar el umbral del modelo, evaluar el costo de falsos negativos, la calibración y el desempeño por subgrupos sobre datos independientes. Para cambios de corpus, auditar normalización, chunking, vectores y trazabilidad. Para despliegue público, coordinar cambios con la universidad y verificar accesibilidad y flujos desde una red externa.

## 12. Historial de decisiones técnicas relevantes

| Decisión | Fundamento y consecuencia |
|---|---|
| Arquitectura separada frontend/backend/ML | Facilita pruebas, mantenimiento e intercambio de responsabilidades |
| Uso de Clean Architecture en backend | Aísla reglas de dominio de adaptadores y rutas HTTP |
| Selección de XGBoost v1 | Balance de desempeño predictivo y objetivo de sensibilidad en evaluación oficial |
| Umbral de clasificación 0,38 | Priorización de sensibilidad cercana al 80 %; no es un umbral clínico validado |
| Conservación del modelo global | Alternativas por edad no demostraron mejoras agregadas sólidas y podían producir saltos de clasificación en los límites etarios |
| BMI calculado en backend | Evita inconsistencias respecto de estatura y peso |
| SHAP como explicabilidad | Identifica contribuciones a predicción sin afirmar causalidad |
| Simulación sin inferencias causales | Permite comparar salidas del modelo bajo entradas modificadas |
| Separación `POST /api/analyze` y `POST /api/rag` | Evita recalcular ML y protege el contexto de inferencia validado mediante `analysis_id` |
| Reconstrucción corpus RAG | 15 documentos y 160 chunks estructurales, con metadatos trazables |
| Workflow RAG de producción | Gemini en n8n con recuperación, explicaciones por factor y referencias; la exportación versionada debe reflejar la revisión operativa actualizada |
| Contenerización mediante Docker Compose | Entorno local de referencia de cuatro servicios; facilita reproducibilidad |
| GHCR y Continuous Delivery | Publicación de imágenes con etiquetas, digests y smoke tests verificables |
| Despliegue público universitario | Acceso web para usuarios externos, con administración de infraestructura no verificada |

## 13. Referencias relacionadas

- Equipo de desarrollo de PULSO. (2026). *PULSO: repositorio del proyecto*. GitHub. https://github.com/acoronellm/PULSO
- Equipo de desarrollo de PULSO. (2026). *Instalación y despliegue de PULSO*. `Instalación.md`, documentación del proyecto.
- Equipo de desarrollo de PULSO. (2026). *Informe final del proyecto PULSO*. `Informe_final.md`, documentación del proyecto.
- Equipo de desarrollo de PULSO. (2026, 8 de noviembre). *PULSO: informe de normalización, chunking, vectorización e ingesta del corpus RAG*. Informe técnico interno.
- Equipo de desarrollo de PULSO. (2026, 12 de noviembre). *PULSO: informe técnico de evolución, comparación y selección de la arquitectura RAG*. Informe técnico interno.
- Docker, Inc. (s. f.). *Docker Compose documentation*. https://docs.docker.com/compose/
- FastAPI. (s. f.). *FastAPI documentation*. https://fastapi.tiangolo.com/
- GitHub. (s. f.). *GitHub Actions documentation*. https://docs.github.com/en/actions
- n8n. (s. f.). *n8n documentation*. https://docs.n8n.io/
- Supabase. (s. f.). *Supabase documentation*. https://supabase.com/docs
- Vite. (s. f.). *Getting started*. https://vite.dev/guide/

---

**Cierre documental:** el manual está completo en sus trece apartados para el MVP académico. Para declarar finalizada y reproducible la versión entregada, incorporar este archivo como `Desarrollo.md`, subir la exportación actualizada del workflow n8n a `rag/workflows/` (sin credenciales), comprobar que las rutas siguen siendo válidas en el commit final y conservar evidencia de las ejecuciones CI/CD reportadas como exitosas. La URL pública y la correspondencia exacta entre commit y versión desplegada se consignarán únicamente si el responsable de la universidad las confirma. Esta guía no afirma haber realizado un despliegue desde cero ni una nueva ejecución de pruebas que no se haya documentado.
