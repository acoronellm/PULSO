
# PULSO

## Plataforma Inteligente para la Predicción Explicable y Simulación Personalizada del Riesgo Cardiovascular

PULSO es una plataforma web orientada a la prevención y educación en salud cardiovascular mediante técnicas de inteligencia artificial.

El sistema permite ingresar información básica de un perfil, obtener una clasificación mediante Machine Learning, identificar los factores asociados con la predicción utilizando SHAP, simular escenarios hipotéticos y recibir recomendaciones educativas generadas mediante un sistema RAG.

PULSO está desarrollado como un Producto Mínimo Viable (MVP) de carácter académico y experimental.

> **Aviso importante:** PULSO no es un dispositivo médico ni una herramienta de diagnóstico clínico. Sus resultados son estimaciones de un modelo entrenado con datos públicos y no sustituyen la valoración de profesionales de la salud.

---


## 1. Versión de entrega académica

La versión correspondiente a esta entrega académica se encuentra en la rama principal `main` del repositorio PULSO.

Repositorio:

https://github.com/acoronellm/PULSO

La versión específica evaluada se identifica mediante el tag `entrega-1`, que permite consultar el estado exacto del código y la documentación correspondiente a la entrega.

Para descargar el repositorio:

```powershell
git clone https://github.com/acoronellm/PULSO.git
```

Ingresar al directorio del proyecto:

```powershell
cd PULSO
```

Para consultar específicamente la versión etiquetada de la entrega, una vez publicado el tag:

```powershell
git fetch --tags
git switch --detach entrega-1
```

El tag conserva la referencia a la versión evaluada, incluso cuando posteriormente se introduzcan nuevos cambios en `main`.


---

## 2. Funcionalidades implementadas

### 2.1. Autenticación

- Registro de usuarios mediante correo electrónico y contraseña.
- Inicio de sesión.
- Autenticación mediante JSON Web Tokens (JWT).
- Almacenamiento de contraseñas mediante hashing Argon2.
- Protección de endpoints que requieren autenticación.
- Cierre de sesión desde la interfaz.

### 2.2. Predicción cardiovascular

- Ingreso de información básica del usuario.
- Validación de los datos introducidos.
- Cálculo automático del índice de masa corporal (IMC).
- Predicción mediante un modelo XGBoost.
- Obtención de una probabilidad estimada y clasificación binaria.
- Aplicación de un umbral de clasificación configurable en el servicio.

El modelo actual corresponde a PULSO v1 y utiliza un umbral de decisión de 0,38.

La probabilidad generada representa la salida del modelo para la clase positiva utilizada durante su entrenamiento. No constituye una probabilidad clínica validada de sufrir un evento cardiovascular futuro.

### 2.3. Explicabilidad con SHAP

El sistema proporciona factores explicativos que permiten identificar qué características del perfil contribuyeron a la predicción.

Estas explicaciones describen el comportamiento del modelo y no deben interpretarse como relaciones causales.

### 2.4. Simulación de escenarios

El usuario puede modificar variables de un perfil para comparar los resultados originales con los de un escenario hipotético.

La simulación permite:

- Comparar probabilidades.
- Observar cambios en la clasificación.
- Consultar la diferencia entre resultados.
- Validar la coherencia de los datos simulados.

Una simulación no predice necesariamente el efecto clínico real de modificar una variable.

### 2.5. Recomendaciones educativas mediante RAG

PULSO utiliza un sistema de generación aumentada por recuperación (RAG), integrado mediante n8n y Supabase.

Este componente permite:

- Generar resúmenes educativos.
- Proporcionar recomendaciones preventivas.
- Asociar recomendaciones con referencias documentales.
- Presentar advertencias sobre el alcance no diagnóstico del sistema.

La disponibilidad de esta funcionalidad depende de la conexión con el servicio n8n.

### 2.6. Historial de análisis

Los usuarios autenticados pueden consultar un historial de sus evaluaciones.

Se almacenan en PostgreSQL datos resumidos del análisis, como:

- Identificador.
- Usuario propietario.
- Probabilidad.
- Clasificación.
- Umbral utilizado.
- Versión del modelo.
- Fecha de creación.

El historial se encuentra asociado a cada usuario autenticado.

No se almacenan permanentemente en PostgreSQL todas las variables clínicas utilizadas para generar la predicción.

---

## 3. Arquitectura tecnológica

PULSO utiliza una arquitectura de servicios contenerizados mediante Docker Compose.

| Componente | Tecnología | Función |
|---|---|---|
| Frontend | React, TypeScript y Vite | Interfaz web |
| Backend | Python y FastAPI | Autenticación y orquestación |
| ML Service | Python, XGBoost y SHAP | Predicción, explicabilidad y simulación |
| Base de datos de usuarios | PostgreSQL 16 | Cuentas e historial |
| RAG | n8n | Orquestación de recomendaciones |
| Base vectorial | Supabase con pgvector | Recuperación documental |
| Proxy inverso | NGINX | Acceso unificado |
| Contenedores | Docker Compose | Ejecución de los servicios |

### Flujo general

1. El usuario accede al frontend.
2. El frontend se comunica con el backend mediante NGINX.
3. El backend valida los datos y la autenticación.
4. El backend solicita la inferencia al ML Service.
5. El ML Service ejecuta XGBoost y genera la explicación SHAP.
6. El backend entrega el resultado al frontend.
7. El análisis resumido se registra en PostgreSQL para el usuario autenticado.
8. Cuando se solicitan recomendaciones, el backend utiliza el contexto temporal del análisis y consulta el servicio RAG.
9. n8n recupera información documental de Supabase y genera una respuesta educativa.

El análisis y las recomendaciones RAG se solicitan mediante operaciones independientes.

---

## 4. Requisitos para ejecutar PULSO

Para ejecutar el sistema mediante Docker se recomienda disponer de:

- Git.
- Docker Desktop.
- Docker Compose v2 (incluido en las versiones actuales de Docker Desktop).
- Conexión a Internet para descargar las imágenes necesarias.
- Puertos locales disponibles.

En Windows, Docker Desktop debe estar instalado, iniciado y configurado para ejecutar contenedores Linux.

**No es necesario instalar manualmente XGBoost, PostgreSQL, React o FastAPI en el computador anfitrión para ejecutar la plataforma con Docker.**

Las dependencias de los servicios se instalan durante la construcción de sus imágenes.

### Puertos utilizados

| Puerto | Servicio |
|---|---|
| 80 | Aplicación web mediante NGINX |
| 8000 | Backend FastAPI |
| 8001 | ML Service |
| 5432 | PostgreSQL |

Los puertos 8000, 8001 y 5432 están vinculados a `127.0.0.1` en la configuración de Docker Compose.

Si alguno de estos puertos ya está ocupado, será necesario liberar el puerto o ajustar la configuración.

---

## 5. Instalación desde cero


### Paso 1. Clonar el repositorio

Abrir PowerShell y ejecutar:

```powershell
git clone https://github.com/acoronellm/PULSO.git
```

Ingresar al directorio:

```powershell
cd PULSO
```

Por defecto, se utilizará la rama principal configurada en GitHub (`main`).

Si se requiere reproducir exactamente la versión de la Entrega 1, ejecutar:

```powershell
git fetch --tags
git switch --detach entrega-1
```

Los pasos siguientes de configuración y ejecución mediante Docker Compose se realizan desde la raíz del repositorio.

### Paso 2. Crear el archivo de configuración

El repositorio incluye `.env.example`, que contiene las variables de entorno necesarias.

Crear el archivo `.env`:

```powershell
Copy-Item .env.example .env
```

El archivo `.env` contiene información de configuración local y no debe publicarse en GitHub.

### Paso 3. Configurar PostgreSQL

Abrir `.env` y revisar las siguientes variables:

```dotenv
POSTGRES_DB=pulso
POSTGRES_USER=pulso
POSTGRES_PASSWORD=pulso_dev_password
```

La contraseña mostrada es un valor de desarrollo.

Para una instalación fuera de un entorno local controlado, debe reemplazarse por una contraseña privada y segura.

El valor configurado debe conservarse mientras se utiliza el volumen existente de PostgreSQL.

### Paso 4. Configurar JWT

El backend exige una clave privada mediante la variable:

```dotenv
JWT_SECRET_KEY=
```

**No se debe iniciar el sistema con esta variable vacía.**

En Windows PowerShell, se puede generar una clave segura y escribirla en `.env` con el siguiente comando:

```powershell
$bytes=New-Object byte[] 32; $rng=[System.Security.Cryptography.RandomNumberGenerator]::Create(); $rng.GetBytes($bytes); $rng.Dispose(); $secret=[Convert]::ToBase64String($bytes); $path=(Resolve-Path .env).Path; $content=[System.IO.File]::ReadAllText($path); $content=[regex]::Replace($content,'(?m)^JWT_SECRET_KEY=.*$',"JWT_SECRET_KEY=$secret"); [System.IO.File]::WriteAllText($path,$content,(New-Object System.Text.UTF8Encoding($false))); Write-Output "JWT_SECRET_KEY configurada."
```

No es necesario instalar Python para generar esta clave.

La clave debe mantenerse privada. Si se cambia, los tokens emitidos anteriormente dejarán de ser válidos.

### Paso 5. Configurar el RAG

En `.env` se encuentra:

```dotenv
RAG_SERVICE_URL=
```

Esta variable contiene la URL del webhook de producción del servicio n8n.

Si todavía no se dispone del servicio RAG, puede permanecer vacía durante las pruebas de autenticación, predicción, explicabilidad, simulación e historial.

**Las recomendaciones educativas no estarán disponibles mientras `RAG_SERVICE_URL` permanezca vacía.**

La configuración de un túnel para n8n se explica posteriormente.

### Paso 6. Iniciar los servicios

Desde la raíz del proyecto:

```powershell
docker compose up -d --build
```

Docker construirá las imágenes y levantará los servicios correspondientes.

La primera ejecución puede requerir la descarga de imágenes y la instalación de dependencias.

### Paso 7. Verificar los contenedores

```powershell
docker compose ps
```

Deben encontrarse activos los servicios:

- `pulso-postgres`
- `pulso-ml-service`
- `pulso-backend`
- `pulso-frontend`
- `pulso-nginx`

PostgreSQL y el ML Service disponen de comprobaciones de salud en Docker Compose.

### Paso 8. Abrir la aplicación

Desde el navegador:

http://localhost

También se pueden comprobar los siguientes recursos:

- Backend: http://127.0.0.1:8000/docs
- Salud del backend: http://localhost/api/health
- Salud del ML Service: http://127.0.0.1:8001/health

La documentación interactiva del backend se encuentra disponible mediante Swagger UI.

---

## 6. Modelo XGBoost

PULSO incluye el modelo entrenado necesario para ejecutar sus predicciones.

Archivo:

```text
artifacts/final/model/pulso_xgboost.joblib
```

Este archivo está incluido en el repositorio PULSO y se distribuye junto con el código fuente de la aplicación.

**No es necesario volver a entrenar el modelo para ejecutar la aplicación.**

El ML Service carga el artefacto entrenado desde el directorio correspondiente.

Docker Compose monta:

```text
./artifacts
```

en:

```text
/app/artifacts
```

dentro del contenedor del ML Service.

### Datos del modelo

| Propiedad | Valor |
|---|---|
| Algoritmo | XGBoost |
| Tipo de problema | Clasificación binaria |
| Versión | v1 |
| Umbral de clasificación | 0,38 |
| Explicabilidad | SHAP |
| Archivo | pulso_xgboost.joblib |

El modelo fue entrenado utilizando un conjunto de datos cardiovasculares público, después de aplicar reglas de preparación, limpieza y separación de datos.

El umbral de clasificación fue seleccionado con una prioridad de sensibilidad (recall) de aproximadamente 80 %.

El modelo no debe utilizarse como sustituto de evaluación clínica.

---

## 7. PostgreSQL y persistencia

PULSO utiliza PostgreSQL 16 para administrar las cuentas y el historial resumido.

La configuración de Docker Compose incluye:

```text
backend/migrations/
```

Los archivos SQL principales son:

```text
001_create_users.sql
002_create_analysis_history.sql
```

Durante la primera inicialización de una base de datos vacía, PostgreSQL ejecuta automáticamente los scripts ubicados en:

```text
/docker-entrypoint-initdb.d
```

### Tablas principales

**users**

Almacena información de autenticación:

- `id`
- `email`
- `password_hash`
- `created_at`

**analyses**

Almacena información resumida de las evaluaciones:

- `id`
- `user_id`
- `probability`
- `classification`
- `threshold`
- `model_version`
- `created_at`

### Persistencia de datos

Docker Compose utiliza el volumen:

```text
pulso-postgres-data
```

Esto permite conservar los registros cuando se detienen o reinician los contenedores.

Para detener los servicios sin eliminar los datos:

```powershell
docker compose down
```

Para iniciarlos nuevamente:

```powershell
docker compose up -d
```

**Advertencia:** ejecutar `docker compose down -v` elimina también los volúmenes administrados por ese proyecto, incluido el volumen persistente de PostgreSQL. No debe utilizarse si se desean conservar los usuarios y los análisis.

Las migraciones de inicialización se ejecutan automáticamente sobre un directorio de datos nuevo; no constituyen un sistema de migraciones incrementales para bases de datos ya existentes.

---

## 8. Configuración del servicio RAG mediante n8n

El RAG funciona como un servicio externo al conjunto principal de contenedores de PULSO.

Su implementación utiliza:

- n8n para ejecutar el workflow.
- Supabase con pgvector para la recuperación documental.
- Un modelo generativo para construir la respuesta educativa.
- El backend de PULSO para coordinar las solicitudes.

El corpus documental operativo contiene documentos normalizados sobre prevención y salud cardiovascular.

### Configuración mediante Cloudflare Tunnel

Para una demostración desde un equipo diferente, es posible utilizar un túnel que publique el webhook de n8n.

El procedimiento general es:

1. Iniciar n8n.
2. Verificar que el workflow de producción esté activo.
3. Iniciar el túnel de Cloudflare.
4. Obtener la URL pública asignada.
5. Identificar la dirección completa del webhook de producción.
6. Configurar esa dirección en `RAG_SERVICE_URL`.
7. Recrear el backend para aplicar la variable.
8. Ejecutar una predicción y solicitar recomendaciones.

Ejemplo ilustrativo de URL:

```dotenv
RAG_SERVICE_URL=https://DOMINIO-DEL-TUNEL/webhook/IDENTIFICADOR
```

Esta dirección debe reemplazarse por el webhook real.

No se deben utilizar direcciones ilustrativas ni endpoints de prueba en una demostración de producción.

### Aplicar cambios en la URL

Después de modificar `.env`:

```powershell
docker compose up -d --force-recreate --no-deps backend
```

La modificación de la variable no requiere necesariamente reconstruir la imagen.

### Consideraciones importantes

- El túnel debe permanecer activo mientras se utiliza el RAG.
- n8n debe permanecer ejecutándose.
- Si n8n se ejecuta en un computador local y ese computador se apaga o suspende, el servicio dejará de estar disponible.
- Una URL de túnel temporal puede cambiar cuando se reinicia.
- El webhook debe ser accesible desde el contenedor del backend.
- No deben publicarse claves de API, credenciales ni secretos del workflow.

Para una demostración sin RAG, las funcionalidades principales de predicción y simulación pueden utilizarse independientemente.

---

## 9. Flujo de análisis y recomendaciones

El endpoint:

```text
POST /api/analyze
```

recibe el perfil del usuario, valida los datos y solicita la predicción al ML Service.

La respuesta contiene información del modelo, explicación SHAP y un identificador del análisis.

La generación del RAG se solicita de manera independiente:

```text
POST /api/rag
```

En esta segunda operación, el frontend proporciona el `analysis_id`.

El backend recupera el contexto temporal del análisis sin volver a ejecutar innecesariamente el modelo predictivo.

### Caché temporal

El backend utiliza una caché en memoria para mantener el contexto necesario para el RAG.

Variables configurables:

```dotenv
ANALYSIS_CACHE_TTL_SECONDS=900
ANALYSIS_CACHE_MAX_ENTRIES=100
```

Esto significa que el contexto del RAG puede expirar después del tiempo configurado.

También se pierde si el proceso del backend se reinicia.

**Importante:** el historial persistido en PostgreSQL y el contexto temporal del RAG son mecanismos diferentes.

Un análisis puede seguir apareciendo en el historial del usuario aunque su contexto para solicitar recomendaciones ya haya expirado.

El mecanismo de caché actual está orientado al MVP con una única instancia del backend.

---

## 10. Endpoints principales

La documentación completa de los endpoints está disponible en Swagger UI:

http://127.0.0.1:8000/docs

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/health` | Estado del backend |
| POST | `/api/auth/register` | Registro de usuarios |
| POST | `/api/auth/login` | Inicio de sesión |
| GET | `/api/auth/me` | Consulta del usuario autenticado |
| POST | `/api/analyze` | Predicción y explicación |
| POST | `/api/simulate` | Simulación de escenarios |
| POST | `/api/rag` | Recomendaciones educativas |
| GET | `/api/analyses` | Historial del usuario |

Las rutas protegidas requieren autenticación mediante un token Bearer válido.

La implementación utiliza validaciones de los datos mediante los esquemas del backend.

---

## 11. Uso de la aplicación

### Crear una cuenta

1. Abrir http://localhost.
2. Acceder a la opción de registro.
3. Introducir un correo electrónico válido y una contraseña.
4. Completar el registro.

### Iniciar sesión

1. Introducir las credenciales.
2. Autenticarse.
3. Acceder a las funcionalidades protegidas.

### Generar una predicción

1. Ingresar los datos solicitados.
2. Verificar que las variables sean coherentes.
3. Ejecutar el análisis.
4. Consultar la probabilidad estimada, la clasificación y los factores explicativos.

El IMC se calcula automáticamente utilizando el peso y la altura.

### Simular un escenario

1. Partir de un perfil válido.
2. Modificar una o varias variables admitidas.
3. Ejecutar la simulación.
4. Comparar los resultados original y simulado.

### Consultar recomendaciones

1. Generar un análisis.
2. Solicitar las recomendaciones educativas.
3. Revisar el resumen, las recomendaciones y las referencias disponibles.

Esta funcionalidad requiere que n8n esté accesible y correctamente configurado.

### Consultar el historial

El usuario autenticado puede consultar los análisis asociados a su cuenta.

Los resultados históricos están disponibles mientras se conserven los registros correspondientes en PostgreSQL.

---

## 12. Pruebas y validaciones

PULSO incorpora pruebas automatizadas y procesos de integración continua mediante GitHub Actions.

Durante la validación funcional de esta versión se ejecutaron pruebas relacionadas con:

- Autenticación y protección de endpoints.
- Predicción cardiovascular.
- Explicabilidad SHAP.
- Validaciones de entrada.
- Cálculo automático del IMC.
- Simulación de escenarios.
- Persistencia del historial.
- Aislamiento de datos entre usuarios.
- Paginación del historial.
- Comunicación con el servicio RAG.
- Validaciones estructurales de las recomendaciones.

### Resultado de las pruebas del backend

En la validación realizada para esta entrega:

```text
88 passed
```

Se registraron dos advertencias de deprecación relacionadas con dependencias de pruebas, sin fallos en la suite.

### Ejecutar pruebas del backend localmente

Con Python y las dependencias necesarias disponibles en el entorno de desarrollo:

```powershell
python -m pytest backend/tests -q
```

Las dependencias del backend pueden instalarse mediante:

```powershell
python -m pip install -r backend/requirements.txt
```

Para las pruebas locales también se requiere disponer de pytest y de las dependencias de pruebas correspondientes.

### Integración continua

Los workflows de GitHub Actions permiten ejecutar comprobaciones automatizadas del proyecto.

Consultar:

https://github.com/acoronellm/PULSO/actions

Los resultados concretos de cada ejecución deben comprobarse directamente en GitHub Actions.

---

## 13. Documentación académica

La documentación correspondiente a esta entrega se encuentra en el directorio `docs/`.

| Entregable | Documento | Descripción |
|---|---|---|
| E1 | [inception.pdf](docs/inception.pdf) | Contextualización del proyecto |
| E2 | [backlog.pdf](docs/backlog.pdf) | Requisitos e historias de usuario |
| E3 | [modelo-dominio.pdf](docs/modelo-dominio.pdf) | Modelo de dominio |
| E4 | [modelo-datos.pdf](docs/modelo-datos.pdf) | Modelo de datos |
| E5 | [arquitectura.pdf](docs/arquitectura.pdf) | Arquitectura y diagramas C4 |
| E6 | [base-tecnica.pdf](docs/base-tecnica.pdf) | Base técnica y validaciones |

Además, el repositorio contiene documentación complementaria de entrenamiento del modelo, MLOps, Docker, backend y pruebas.

---

## 14. Limitaciones conocidas

PULSO se encuentra en una etapa de desarrollo académico y no debe considerarse un sistema clínico de producción.

Las principales limitaciones son:

- El modelo fue entrenado con un conjunto de datos público y no constituye una herramienta diagnóstica validada clínicamente.
- La plataforma no garantiza una experiencia completamente adaptada a dispositivos móviles.
- El RAG depende de servicios externos y de su disponibilidad.
- El contexto temporal del RAG puede expirar o perderse al reiniciar el backend.
- El historial de PostgreSQL conserva resultados resumidos, no el conjunto completo de datos de entrada.
- La solución actual no dispone de todas las funcionalidades habituales de gestión avanzada de usuarios, como recuperación de contraseñas y administración de roles.
- No se ha validado una instalación integral completa desde un segundo portátil independiente.
- Se identificó una limitación interna en el manejo de determinadas entradas inválidas enviadas directamente al ML Service; la API pública incorpora validaciones para evitar el caso detectado.

No deben interpretarse las recomendaciones o las simulaciones como instrucciones médicas personalizadas.

---

## 15. Solución de problemas frecuentes

### El backend no inicia porque falta JWT_SECRET_KEY

Comprobar que existe `.env` y que contiene una clave no vacía:

```dotenv
JWT_SECRET_KEY=CLAVE_PRIVADA_GENERADA
```

Después volver a iniciar los servicios.

### El ML Service no encuentra el modelo

Verificar que exista:

```text
artifacts/final/model/pulso_xgboost.joblib
```

El modelo XGBoost entrenado está incluido en el repositorio y no necesita descargarse ni entrenarse nuevamente.

Comprobar también el montaje de `artifacts/` en Docker Compose.

### PostgreSQL no responde inmediatamente

En la primera ejecución, PostgreSQL debe inicializar el directorio de datos y ejecutar las migraciones.

Consultar el estado:

```powershell
docker compose ps
```

Y los registros:

```powershell
docker compose logs postgres --tail 100
```

### El RAG indica que RAG_SERVICE_URL no está configurado

Configurar en `.env` la dirección real del webhook de producción de n8n.

Después recrear el backend:

```powershell
docker compose up -d --force-recreate --no-deps backend
```

### El RAG indica que el análisis no existe o expiró

Generar un nuevo análisis y solicitar las recomendaciones inmediatamente.

El contexto temporal puede haber expirado o desaparecido después de reiniciar el backend.

### Un puerto ya está ocupado

Comprobar los contenedores:

```powershell
docker ps
```

Cerrar servicios que utilicen los mismos puertos o ajustar las asignaciones de Docker Compose.

### Consultar errores del sistema

```powershell
docker compose logs backend --tail 100
```

```powershell
docker compose logs ml-service --tail 100
```

```powershell
docker compose logs postgres --tail 100
```

---

## 16. Seguridad y privacidad

PULSO emplea mecanismos básicos de seguridad adecuados para el alcance de su MVP:

- Contraseñas almacenadas mediante hashing.
- Autenticación JWT.
- Protección de rutas.
- Asociación del historial con el usuario autenticado.
- Archivos `.env` excluidos del control de versiones.
- Restricción de determinados puertos a la interfaz local.

Estas medidas no sustituyen una auditoría integral de seguridad.

Para un despliegue público sería necesario ampliar las medidas de protección, incluyendo HTTPS, gestión segura de secretos, controles de acceso, políticas de tratamiento de datos y procedimientos de operación.

No deben introducirse datos personales o clínicos reales en entornos de prueba sin las autorizaciones y garantías correspondientes.

---

## 17. Estudiantes

| Nombre | GitHub |
|---|---|
| Miguel Angel Márquez Coronell | [acoronellm](https://github.com/acoronellm) |
| María Gabriela Rey Barrios | [magaarb204](https://github.com/magaarb204) |
| Andrés Felipe Serrano Mendoza | [serranoaf23](https://github.com/serranoaf23) |

## 18. Tutor

José Duván Márquez Díaz.

---

## 19. Estado de la entrega

Esta versión de PULSO incluye:

- Aplicación web desarrollada en React.
- Backend desarrollado en FastAPI.
- Modelo XGBoost entrenado y versionado.
- Explicaciones mediante SHAP.
- Simulación de escenarios.
- Autenticación de usuarios.
- Historial persistente en PostgreSQL.
- Sistema RAG integrado mediante n8n.
- Documentación académica E1–E6.
- Pruebas automatizadas y workflows de GitHub Actions.

Para una demostración completa deben estar operativos los contenedores y el servicio RAG externo.


La versión correspondiente a la Entrega 1 se integra en la rama principal `main` mediante Pull Request.

El tag `entrega-1` identifica el commit seleccionado para la evaluación académica y permite consultar posteriormente esa versión sin alterar el historial de Git.

**Repositorio:** https://github.com/acoronellm/PULSO

**Rama principal:** `main`

**Referencia de entrega:** `entrega-1`

