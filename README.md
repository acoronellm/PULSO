# PULSO

**Plataforma Inteligente para la Predicción Explicable y Simulación Personalizada del Riesgo Cardiovascular mediante Machine Learning y Aprendizaje Continuo**

## Descripción

PULSO es un prototipo web de carácter **educativo y preventivo** que integra aprendizaje automático, explicabilidad y recuperación aumentada de información (*RAG*) para ayudar a comprender factores asociados con la clasificación cardiovascular estimada por un modelo.

El usuario puede crear una cuenta, introducir sus datos, consultar la predicción y los principales factores explicativos mediante SHAP, simular modificaciones de algunas variables y obtener recomendaciones educativas respaldadas por documentos incorporados al sistema RAG. También puede consultar un historial resumido de sus análisis.

> **Aviso importante:** PULSO no realiza diagnósticos médicos, no sustituye una valoración profesional y no predice de forma validada la ocurrencia de un evento cardiovascular individual en un periodo determinado. La probabilidad mostrada es la salida del clasificador entrenado con un conjunto de datos específico. La clasificación depende del umbral configurado.

## Funcionalidades implementadas

- **Registro e inicio de sesión:** cuentas almacenadas en PostgreSQL, contraseñas protegidas con Argon2 y autenticación mediante JWT.
- **Análisis cardiovascular:** captura y validación de variables del perfil; el IMC se calcula automáticamente a partir del peso y la estatura.
- **Predicción con aprendizaje automático:** modelo XGBoost v1 que produce una probabilidad y una clasificación según un umbral de decisión de **0,38**.
- **Explicabilidad:** identificación de los principales factores asociados con la predicción mediante valores SHAP.
- **Simulación de escenarios:** comparación entre la salida original y la correspondiente a cambios hipotéticos en variables admitidas, sin interpretar las diferencias como efectos causales.
- **Recomendaciones educativas:** servicio RAG externo, orquestado con n8n, que consulta un corpus documental vectorizado en Supabase y devuelve recomendaciones y referencias.
- **Historial de análisis:** almacenamiento persistente de resultados resumidos en PostgreSQL y consulta paginada por usuario autenticado.

## Arquitectura

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Interfaz web | React, TypeScript y Vite | Captura de datos y presentación de resultados |
| API backend | Python y FastAPI | Validación, autenticación y orquestación de servicios |
| Servicio ML | Python, XGBoost y SHAP | Inferencia, explicación y simulación |
| Base de datos de aplicación | PostgreSQL | Usuarios e historial resumido de análisis |
| RAG educativo | n8n | Orquestación de recuperación y generación de recomendaciones |
| Base vectorial | Supabase / pgvector | Almacenamiento y recuperación de fragmentos documentales |
| Proxy inverso | NGINX | Entrada HTTP y encaminamiento hacia frontend y backend |
| Contenedores | Docker Compose | Ejecución coordinada de los servicios locales |

El sistema RAG utiliza actualmente el corpus normalizado de **15 documentos y 160 fragmentos**, alojado en la tabla operativa `public.documents_pulso_test` de Supabase. El sufijo `_test` forma parte del nombre de la tabla utilizada por el entorno operativo actual; no implica que el corpus esté pendiente de pasar a producción.

El backend no solicita una nueva inferencia al RAG: primero obtiene la predicción y sus factores SHAP desde el servicio ML; posteriormente solicita las recomendaciones utilizando el `analysis_id` de ese análisis.

## Requisitos previos

- Git.
- Docker Desktop con Docker Compose habilitado.
- Acceso a los servicios externos requeridos para el RAG, si se desea utilizar esa funcionalidad.
- Archivo del modelo entrenado disponible en `artifacts/final/model/pulso_xgboost.joblib`.

Los recursos externos (n8n y Supabase) no se despliegan automáticamente mediante el `docker-compose.yml` de este repositorio. El archivo del modelo debe estar presente en la ruta esperada antes de iniciar el servicio ML.

## Configuración del entorno

1. Clona el repositorio y entra en su directorio:

   ```powershell
   git clone https://github.com/acoronellm/PULSO.git
   cd PULSO
   ```

2. Prepara el archivo `.env` en la raíz del repositorio. Si existe `.env.example`, utilízalo como referencia:

   ```powershell
   Copy-Item .env.example .env
   ```

   Si ya tienes un `.env`, **no lo sobrescribas**: incorpora únicamente las variables que falten.

3. Configura las siguientes variables para tu entorno:

   ```dotenv
   POSTGRES_DB=pulso
   POSTGRES_USER=pulso
   POSTGRES_PASSWORD=REEMPLAZAR_CON_CONTRASENA_SEGURA
   JWT_SECRET_KEY=REEMPLAZAR_CON_SECRETO_ALEATORIO_SEGURO
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   RAG_SERVICE_URL=
   ```

   Puedes generar un secreto JWT con Python:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Copia el valor generado en `JWT_SECRET_KEY`. No publiques el archivo `.env`, secretos, contraseñas ni URLs privadas de webhooks.

   `RAG_SERVICE_URL` debe apuntar al **webhook de producción** del workflow n8n activo, accesible **desde el contenedor backend**. Si n8n se publica en el equipo anfitrión mediante Docker Desktop, puede requerirse `host.docker.internal` en lugar de `localhost`. Si la variable queda vacía, las funcionalidades de análisis ML pueden operar, pero las recomendaciones RAG no estarán disponibles.

4. Levanta la aplicación:

   ```powershell
   docker compose up -d --build
   ```

5. Comprueba los servicios:

   ```powershell
   docker compose ps
   ```

6. Abre la aplicación desde un navegador en **http://localhost**.

Para detener los contenedores sin borrar los datos persistidos:

```powershell
docker compose down
```

**Precaución:** `docker compose down -v` elimina también los volúmenes de Docker Compose, incluido el almacenamiento local persistente de PostgreSQL. No lo utilices si deseas conservar cuentas e historial.

## Flujo de uso

1. Regístrate o inicia sesión.
2. Introduce las variables solicitadas en el formulario. El IMC se calcula a partir de peso y altura.
3. Ejecuta el análisis para consultar la probabilidad, clasificación y explicación SHAP.
4. Si lo deseas, modifica variables permitidas y compara la salida de una simulación con la original.
5. Solicita las recomendaciones educativas; requieren que el servicio RAG esté configurado y disponible.
6. Consulta el historial resumido asociado a tu cuenta.

La interfaz web está orientada principalmente a escritorio; **no se declara compatibilidad móvil completa**.

## API y documentación interactiva

La API FastAPI está disponible localmente en `http://127.0.0.1:8000` cuando se utiliza la configuración Docker Compose incluida. Su documentación OpenAPI se puede consultar en:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Esquema OpenAPI:** http://127.0.0.1:8000/openapi.json

Entre las rutas principales se encuentran:

| Método y ruta | Propósito |
|---|---|
| `POST /api/auth/register` | Registrar una cuenta |
| `POST /api/auth/login` | Iniciar sesión |
| `GET /api/auth/me` | Consultar la identidad autenticada |
| `POST /api/analyze` | Crear un análisis, obtener predicción y SHAP |
| `POST /api/simulate` | Comparar escenarios hipotéticos |
| `POST /api/rag` | Obtener recomendaciones para un `analysis_id` |
| `GET /api/analyses` | Consultar el historial paginado del usuario |
| `GET /api/health` | Verificar disponibilidad del backend |

Las rutas protegidas requieren el encabezado `Authorization: Bearer <token>`. La estructura exacta de solicitudes y respuestas debe consultarse en OpenAPI.

### Contexto de análisis y persistencia

El backend mantiene temporalmente el contexto necesario para solicitar recomendaciones RAG, con una caché en memoria configurada con **TTL de 900 segundos** y un máximo de **100 entradas** en el entorno Docker Compose. El análisis resumido se persiste por separado en PostgreSQL.

Esto significa que un análisis puede seguir apareciendo en el historial y, sin embargo, haber perdido su contexto temporal para consultar nuevamente el RAG. Reiniciar el backend también elimina los contextos de dicha caché. La estrategia actual está orientada a una instancia del backend; para escalar a varias instancias sería necesario un almacenamiento temporal compartido.

## Pruebas y validación

Para ejecutar las pruebas automatizadas del backend desde un entorno Python con las dependencias instaladas:

```powershell
python -m pytest backend/tests -q
```

Para ejecutar solamente las pruebas de esquemas HTTP:

```powershell
python -m pytest backend/tests/interfaces/test_http_schemas.py -q
```

En la validación local realizada el **13 de noviembre de 2026** se obtuvieron **88 pruebas aprobadas en la suite del backend**, incluidas **8 pruebas de esquemas HTTP**. También se comprobaron manualmente autenticación, predicción, SHAP, simulación, persistencia y paginación de historial, aislamiento básico entre cuentas, y conectividad y formato de respuesta del RAG. Estos resultados corresponden a las ejecuciones realizadas; no deben interpretarse como cobertura total de pruebas ni como garantía de ausencia de defectos.

Los controles automatizados de integración continua deben verificarse en la pestaña **Actions** del repositorio para cada rama o solicitud de incorporación (*pull request*).

## Documentación del proyecto

Los entregables se encuentran en `docs/`:

| Entregable | Documento |
|---|---|
| E1 — Contextualización / Inception | [docs/inception.pdf](docs/inception.pdf) |
| E2 — Backlog | [docs/backlog.pdf](docs/backlog.pdf) |
| E3 — Modelo de dominio | [docs/modelo-dominio.pdf](docs/modelo-dominio.pdf) |
| E4 — Modelo de datos | [docs/modelo-datos.pdf](docs/modelo-datos.pdf) |
| E5 — Arquitectura | [docs/arquitectura.pdf](docs/arquitectura.pdf) |
| E6 — Base técnica | [docs/base-tecnica.pdf](docs/base-tecnica.pdf) |

Otros materiales del proyecto pueden consultarse en los archivos de documentación disponibles en el repositorio.

## Alcance y limitaciones

- PULSO es un **prototipo educativo**, no un dispositivo médico ni una herramienta de diagnóstico clínico.
- La probabilidad del clasificador no equivale a una probabilidad clínica individual validada de sufrir un evento futuro.
- Los cambios en las simulaciones representan escenarios hipotéticos de entrada del modelo; **no demuestran causalidad**.
- La versión descrita no incorpora administración de roles, recuperación de contraseñas ni gestión integral de consentimientos como funcionalidades concluidas.
- El historial conserva resultados resumidos; no debe asumirse que se almacena permanentemente todo el perfil clínico de entrada.
- La experiencia de uso en pantallas móviles no está validada como completamente adaptable.
- La disponibilidad del RAG depende de la configuración y conectividad con n8n y Supabase.
- Está identificado un problema interno de serialización de errores del servicio ML cuando recibe directamente determinadas simulaciones inválidas; la API pública del backend ya valida y rechaza el escenario de presión arterial incoherente probado con HTTP 422.

## Equipo

| Integrante | GitHub |
|---|---|
| Miguel Angel Márquez Coronell | [@acoronellm](https://github.com/acoronellm) |
| María Gabriela Rey Barrios | [@magaarb204](https://github.com/magaarb204) |
| Andrés Felipe Serrano Mendoza | [@serranoaf23](https://github.com/serranoaf23) |

**Tutor:** José Duván Márquez Díaz.
