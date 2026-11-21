# Instalación y despliegue de PULSO

**Proyecto:** PULSO — Plataforma web educativa de prevención cardiovascular  
**Fecha de actualización:** 20 de noviembre de 2026 (diferenciación de instalación local y despliegue público universitario)  
**Repositorio:** https://github.com/acoronellm/PULSO  
**Alcance:** instalación y operación del MVP académico, con modelo XGBoost v1, explicación SHAP, simulación y recomendaciones documentales mediante RAG.

> **Nota de alcance.** PULSO puede utilizarse mediante dos modalidades diferentes: **(1) instalación local reproducible**, preferentemente con Docker Compose, para desarrollo, pruebas o demostraciones; y **(2) acceso al despliegue público**, que fue realizado por la universidad a partir del repositorio entregado por el equipo y está disponible tanto para usuarios dentro como fuera de la institución. El equipo recibió la URL pública, pero **no dispone de información verificada sobre la infraestructura ni el procedimiento interno de publicación de la universidad**. Por consiguiente, los comandos de Docker de esta guía describen la instalación local y una alternativa de autodespliegue, **no el procedimiento efectivamente seguido por la universidad**. En ambas modalidades, la generación documental utiliza n8n alojado en un servidor externo y una base vectorial Supabase/pgvector. No se deben publicar credenciales ni presumir que el servidor universitario tiene Docker, NGINX o una topología concreta sin evidencia.

**Modalidades resumidas**

| Modalidad | ¿Quién realiza la instalación? | Acceso del usuario | Alcance de esta guía |
|---|---|---|---|
| Local con Docker Compose | Desarrollador o evaluador | `http://localhost/` | Procedimiento reproducible de construcción y ejecución |
| Local sin Docker | Desarrollador | Dirección de Vite informada por la terminal | Procedimiento de desarrollo y depuración |
| Despliegue público universitario | Universidad, a partir del repositorio proporcionado | URL pública entregada al equipo | Uso y verificación desde navegador; infraestructura y operación internas no verificadas |
| Autodespliegue opcional en servidor propio | Administrador técnico | Dominio o IP configurados por quien despliega | Procedimientos de referencia; no equivalen al despliegue universitario |

## 1. Descripción general de la solución

PULSO permite ingresar variables cardiovasculares y recibir una clasificación del modelo XGBoost v1, explicaciones de contribución mediante SHAP, escenarios simulados y, mediante un servicio RAG, información educativa respaldada por documentos. No constituye un instrumento diagnóstico ni sustituye la consulta con profesionales de la salud.

### 1.1 Lenguajes y tecnologías utilizadas

| Capa | Tecnologías | Función |
|---|---|---|
| Interfaz | TypeScript/JavaScript, React, Vite | Formulario, visualización, explicaciones y simulación |
| Backend | Python 3.11, FastAPI, Uvicorn | Validación, coordinación de servicios y exposición de API |
| Inferencia | Python 3.11, XGBoost y SHAP | Predicción, explicación y simulación |
| RAG | n8n, Google Gemini | Orquestación de recuperación y generación educativa |
| Almacén RAG | Supabase, PostgreSQL, pgvector | Almacenamiento y consulta vectorial de las fuentes |
| Proxy y frontend compilado | NGINX | Publicación de la interfaz y enrutamiento `/api/` |
| Contenedorización | Docker y Docker Compose | Construcción y ejecución coordinada |
| Versionamiento | Git y GitHub | Control de versiones y trazabilidad |

Las imágenes Docker publicadas en el repositorio utilizan Python 3.11 para los dos servicios Python y Node.js 22 durante la compilación del frontend. Si se desarrolla sin contenedores, se recomienda utilizar versiones compatibles con estos entornos.

### 1.2 Componentes de la solución

Para **la ejecución de referencia con Docker Compose**, el archivo `docker-compose.yml` define cuatro servicios. Esta topología no debe atribuirse automáticamente a la infraestructura universitaria:

| Servicio Compose | Contenedor | Puerto accesible desde el equipo | Responsabilidad |
|---|---|---|---|
| `nginx` | `pulso-nginx` | `80` | Entrada pública local; enruta interfaz y API |
| `frontend` | `pulso-frontend` | Interno `80` | Sirve los archivos compilados de React |
| `backend` | `pulso-backend` | `127.0.0.1:8000` | API FastAPI y coordinación de inferencia y RAG |
| `ml-service` | `pulso-ml-service` | `127.0.0.1:8001` | Carga XGBoost v1 y ejecuta predicciones, SHAP y simulaciones |

El backend se conecta a `http://ml-service:8001` dentro de la red de Docker. Para obtener información educativa, **el backend se comunica por HTTPS con el webhook de n8n alojado en un servidor externo**: la dirección se configura mediante `RAG_SERVICE_URL` y la clave `RAG_WEBHOOK_API_KEY` viaja en la cabecera HTTP `X-PULSO-RAG-Key`. El frontend no recibe esta clave ni se comunica directamente con n8n. El workflow remoto usa Gemini y consulta la base documental final alojada en la tabla `public.documents_pulso_test` de Supabase/pgvector. Ni n8n ni PostgreSQL/Supabase deben instalarse en la máquina local para consumir este servicio ya desplegado.

El modelo XGBoost usa un umbral de clasificación de `0.38`. Sus entradas incluyen sexo codificado, estatura, peso, presiones sistólica y diastólica, tabaquismo, alcohol, actividad física, edad e IMC calculado. El sistema tiene un propósito exclusivamente educativo.

## 2. Requisitos previos

### 2.1 Software requerido

**Instalación local recomendada con contenedores:**

- Git para clonar el repositorio.
- Docker Desktop (Windows/macOS) o Docker Engine (Linux), con el complemento Docker Compose v2.
- En Windows, WSL2 habilitado y el motor de Docker Desktop integrado con la distribución WSL utilizada.
- Conexión a Internet para descargar imágenes y dependencias y acceso saliente **HTTPS (puerto 443)** desde el backend hasta el webhook RAG remoto cuando se requieran explicaciones y recomendaciones documentales.
- Acceso autorizado al webhook RAG de n8n: URL completa de producción y valor correspondiente a `RAG_WEBHOOK_API_KEY` facilitados de forma segura por el equipo administrador.
- n8n y Supabase ya operativos en sus respectivos servicios externos. No se exige instalarlos ni configurar una base de datos local.
- Puertos `80`, `8000` y `8001` disponibles. El puerto 80 es el único destinado a la entrada de usuarios.
- Recursos suficientes para compilar y ejecutar cuatro servicios. Los mínimos de CPU, RAM y disco no han sido medidos formalmente para esta entrega; deben dimensionarse según el equipo y los resultados de pruebas de carga.

**Desarrollo local sin contenedores:** Python 3.11, Node.js 22 con npm, Git y acceso a las dependencias especificadas en `backend/requirements.txt`, `ml_service/requirements.txt` y `frontend/package-lock.json`. El desarrollador tendrá que iniciar cada proceso por separado.

Para comprobar herramientas instaladas, ejecutar individualmente:

```bash
git --version
```

```bash
docker --version
```

```bash
docker compose version
```

```bash
python --version
```

```bash
node --version
```

```bash
npm --version
```

### 2.2 Variables de entorno

El repositorio incluye `.env.example`. Para la instalación con Docker Compose, crear un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

En PowerShell, el comando equivalente es:

```powershell
Copy-Item .env.example .env
```

Variables contempladas por la configuración examinada:

| Variable | Ejemplo / valor de referencia | Propósito |
|---|---|---|
| `ML_SERVICE_URL` | `http://127.0.0.1:8001` | URL de ML al ejecutar backend fuera de Docker; en Compose se usa `http://ml-service:8001` |
| `ML_TIMEOUT_SECONDS` | `30` | Tiempo límite de comunicación con ML |
| `RAG_SERVICE_URL` | `https://<servidor-n8n>/webhook/<ruta-real>` | URL **completa** del webhook de producción en n8n remoto (no el dominio raíz, editor ni URL de pruebas) |
| `RAG_TIMEOUT_SECONDS` | `90` | Tiempo límite en segundos de la llamada desde backend al webhook; Compose utiliza `90` por defecto si no se define |
| `RAG_WEBHOOK_API_KEY` | `<clave-secreta-del-entorno>` | **Requerida por Docker Compose**; se envía desde el backend en `X-PULSO-RAG-Key` y debe coincidir con el valor que valida el webhook remoto |
| `ANALYSIS_CACHE_TTL_SECONDS` | `900` | Tiempo de vida en segundos del contexto temporal de análisis |
| `ANALYSIS_CACHE_MAX_ENTRIES` | `100` | Máximo de contextos mantenidos temporalmente |

**Importante:** `RAG_SERVICE_URL` debe ser la URL **completa del webhook de producción**, no la URL del editor n8n ni una URL temporal `/webhook-test/`. En el despliegue del proyecto se ha utilizado un servidor n8n accesible mediante el dominio `n8n-1-121-0-g9hf.onrender.com`; ese dominio por sí solo **no es la URL del webhook** y su disponibilidad actual debe confirmarse antes de instalar. La ruta concreta del webhook se obtiene del workflow de n8n y se comparte por un canal autorizado.

La clave `RAG_WEBHOOK_API_KEY` debe corresponder a la que verifica el workflow remoto; el nombre de cabecera utilizado por el cliente Python es **`X-PULSO-RAG-Key`**. No se debe publicar la clave ni incluirla en código JavaScript del navegador, documentación pública, capturas de pantalla o repositorios. El archivo `.env` debe excluirse de Git. Las claves del proveedor Gemini y de Supabase permanecen del lado de la infraestructura RAG, no se requieren para arrancar los cuatro contenedores locales si n8n ya está configurado.

Crear el archivo `.env` a partir de `.env.example` y **rellenar** estos valores (los marcadores son ejemplos, no valores operativos):

```dotenv
RAG_SERVICE_URL=https://<servidor-n8n>/webhook/<ruta-real>
RAG_TIMEOUT_SECONDS=90
RAG_WEBHOOK_API_KEY=<clave-secreta-compartida-con-n8n>
```

**Validación de variables:** `docker compose config` falla si `RAG_WEBHOOK_API_KEY` está sin configurar, porque `docker-compose.yml` la declara obligatoria. El servicio `backend` recibe explícitamente `RAG_SERVICE_URL`, `RAG_TIMEOUT_SECONDS` y `RAG_WEBHOOK_API_KEY` desde Docker Compose.

**Artefacto XGBoost:** el Dockerfile vigente de `ml-service` incluye el modelo oficial desde `models/pulso/v1/pulso_xgboost.joblib` y lo copia a `/app/artifacts/final/model/pulso_xgboost.joblib` durante la construcción de la imagen. **Para el arranque con Docker Compose no se requiere una copia manual en `artifacts/`.** En cambio, al ejecutar ML sin Docker desde la raíz del repositorio, se debe asegurar que esté disponible la ruta de artefactos que espera el cargador Python; si es necesario copiar el modelo, verificar previamente que sea el artefacto oficial v1.

## 3. Instalación para ambiente de desarrollo

### 3.1 Desarrollo sin contenedores

La ejecución sin Docker es útil para depuración. Se realiza mediante tres terminales, desde la raíz del repositorio, y presupone que existe el archivo del modelo.

#### 3.1.1 Clonar el repositorio

```bash
git clone https://github.com/acoronellm/PULSO.git
```

```bash
cd PULSO
```

La rama `main` corresponde al estado público consultado para esta guía. Si se solicita una versión entregable concreta, cambiar a su etiqueta o commit antes de instalar.

#### 3.1.2 Instalar dependencias

Crear un entorno virtual Python desde la raíz:

```bash
python -m venv .venv
```

Activarlo en Linux/macOS o WSL:

```bash
source .venv/bin/activate
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias de ambos servicios Python:

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install -r backend/requirements.txt
```

```bash
python -m pip install -r ml_service/requirements.txt
```

Instalar dependencias del frontend:

```bash
cd frontend && npm ci && cd ..
```

Los requisitos de entrenamiento o experimentación, cuando sean necesarios, son diferentes de los mínimos de ejecución del MVP. No deben instalarse automáticamente para una simple demostración.

#### 3.1.3 Configurar variables de entorno

Crear `.env` a partir de `.env.example` como se indica en la sección 2.2 y configurar `RAG_SERVICE_URL`, `RAG_TIMEOUT_SECONDS` y `RAG_WEBHOOK_API_KEY`. Para ejecuciones fuera de Docker, `pydantic-settings` admite lectura de `.env` cuando se ejecuta desde la raíz del repositorio. Si el proceso se inicia desde otra ubicación o no encuentra dicho archivo, exportar las variables explícitamente.

Para la terminal de backend en Bash, una forma explícita de configurar las URL básicas es:

```bash
export ML_SERVICE_URL=http://127.0.0.1:8001
```

```bash
export RAG_SERVICE_URL='https://SERVIDOR_N8N/webhook/RUTA_REAL'
```

```bash
export RAG_WEBHOOK_API_KEY='CLAVE_PRIVADA_DEL_ENTORNO'
```

```bash
export RAG_TIMEOUT_SECONDS=90
```

En PowerShell:

```powershell
$env:ML_SERVICE_URL='http://127.0.0.1:8001'
```

```powershell
$env:RAG_SERVICE_URL='https://SERVIDOR_N8N/webhook/RUTA_REAL'
```

```powershell
$env:RAG_WEBHOOK_API_KEY='CLAVE_PRIVADA_DEL_ENTORNO'
```

```powershell
$env:RAG_TIMEOUT_SECONDS=90
```

Sustituir los marcadores por la URL completa y la clave real que comparta el equipo de forma segura; **no guardar claves en un script versionado**.

#### 3.1.4 Ejecutar servicios requeridos

Para ejecutar ML sin Docker desde la raíz del repositorio, confirmar que existe `artifacts/final/model/pulso_xgboost.joblib`, que es la ubicación usada en la imagen del servicio. Si solo existe el artefacto versionado `models/pulso/v1/pulso_xgboost.joblib`, puede prepararse la ruta local antes de iniciar ML:

```bash
mkdir -p artifacts/final/model && cp models/pulso/v1/pulso_xgboost.joblib artifacts/final/model/pulso_xgboost.joblib
```

En PowerShell:

```powershell
New-Item -ItemType Directory -Force artifacts/final/model | Out-Null; Copy-Item models/pulso/v1/pulso_xgboost.joblib artifacts/final/model/pulso_xgboost.joblib
```

Esta copia solo corresponde a la **ejecución local sin contenedores**; Docker la incorpora automáticamente durante `docker compose build`. Comprobar también que n8n remoto esté accesible con HTTPS y que la clave compartida esté configurada correctamente; no enviar perfiles sensibles a servicios de comprobación externos.

#### 3.1.5 Iniciar la aplicación

En la **primera terminal**, desde la raíz y con el entorno Python activado:

```bash
python -m uvicorn ml_service.app.main:app --host 127.0.0.1 --port 8001
```

En la **segunda terminal**, desde la raíz y con el entorno Python activado y variables disponibles:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

En la **tercera terminal**, desde el directorio `frontend`:

```bash
npm run dev
```

La interfaz Vite suele anunciar una URL local de desarrollo, habitualmente `http://localhost:5173`. Si al abrirla las llamadas a `/api/` no llegan al backend, se debe comprobar la configuración del proxy de Vite o la variable `VITE_API_URL` de esa revisión del frontend. El enrutamiento relativo `/api/` sí está configurado explícitamente en la ruta recomendada con NGINX y Docker.

### 3.2 Desarrollo local con contenedores

#### 3.2.1 Construcción de contenedores

Desde la raíz, con Docker activo, `.env` configurado (incluida la clave RAG) y el archivo `models/pulso/v1/pulso_xgboost.joblib` presente:

```bash
docker compose config
```

Este comando verifica la estructura y sustitución de variables del Compose. A continuación:

```bash
docker compose build
```

#### 3.2.2 Ejecución del entorno

```bash
docker compose up -d
```

Para reconstruir y arrancar en una sola operación:

```bash
docker compose up -d --build
```

Comprobar el estado:

```bash
docker compose ps
```

Consultar los mensajes de los servicios cuando sea necesario:

```bash
docker compose logs --tail=100
```

#### 3.2.3 Servicios disponibles

| Recurso | Dirección prevista |
|---|---|
| Aplicación web | `http://localhost/` |
| API mediante NGINX | `http://localhost/api/` |
| Estado del backend | `http://localhost/api/health` |
| Documentación FastAPI directa | `http://127.0.0.1:8000/docs` |
| Estado del ML Service | `http://127.0.0.1:8001/health` |

En el Compose verificado, NGINX escucha en el puerto 80 y la API y el ML Service solo publican sus puertos hacia `127.0.0.1`. El RAG no se publica desde Compose: n8n se ejecuta en un **servidor externo** y es invocado por el backend mediante HTTPS y la cabecera `X-PULSO-RAG-Key`.

#### 3.2.4 Apagado del entorno

```bash
docker compose down
```

Este comando detiene y elimina los contenedores y la red creada por Compose, sin eliminar las imágenes ni los archivos del repositorio. Para detener sin eliminar:

```bash
docker compose stop
```

No utilizar `docker compose down -v` ni comandos de limpieza destructiva sin evaluar previamente qué datos podrían verse afectados.

## 4. Despliegue y publicación de la plataforma

Esta sección distingue expresamente el **despliegue público universitario existente** de los procedimientos de **instalación local** descritos en la sección 3 y de un **autodespliegue opcional**. No se debe considerar el acceso público como prueba de que se utiliza la misma infraestructura o los mismos comandos de la instalación local.

### 4.1 Arquitectura de despliegue

#### 4.1.1 Despliegue público administrado por la universidad

PULSO se encuentra publicado en Internet mediante un despliegue realizado con el apoyo de la universidad. Para llevarlo a cabo, el equipo de desarrollo proporcionó el repositorio del proyecto, incluyendo los archivos necesarios para la construcción y configuración de los contenedores Docker, cuya preparación fue solicitada previamente por la institución. Una vez recibidos estos elementos, la universidad realizó el despliegue de la aplicación y proporcionó una dirección URL pública, permitiendo su utilización desde navegadores web tanto dentro como fuera de la red universitaria, sin necesidad de instalar localmente los componentes de PULSO.

**Dirección pública:** utilizar la URL facilitada oficialmente por la universidad. No se reproduce una dirección concreta en esta guía porque no se ha proporcionado aquí una URL verificada de la aplicación publicada. Este enlace deberá insertarse en la versión de entrega una vez confirmado por el equipo.

**Límites de la información disponible:** aunque la preparación de las imágenes y configuraciones Docker fue un requisito solicitado por la universidad, no se ha confirmado si el despliegue público utiliza directamente Docker Compose u otra herramienta de ejecución y administración de contenedores. Tampoco se dispone de información verificada sobre el sistema operativo del servidor, la infraestructura utilizada, la topología de red o los procedimientos internos de actualización. Por esta razón, los comandos y configuraciones descritos para la instalación local se presentan como una referencia reproducible del proyecto y no como una descripción confirmada de la infraestructura universitaria.

A nivel **funcional y lógico**, el código de PULSO comprende interfaz web, backend de coordinación y servicio de inferencia de XGBoost. La generación de información educativa se realiza mediante el **workflow RAG alojado en un servidor externo de n8n**; el backend consume su webhook por HTTPS, y el proceso RAG utiliza Google Gemini y el almacén documental en **Supabase/pgvector** (tabla `public.documents_pulso_test`). Este esquema describe las responsabilidades del sistema, no el mapa físico exacto del servidor universitario.

```text
Usuarios dentro o fuera de la universidad
                  |
                  | Navegador / Internet
                  v
          URL pública de PULSO
                  |
                  v
    Aplicación publicada por la universidad
  (infraestructura y mecanismo interno no verificados)
                  |
          Servicios lógicos de PULSO
        (interfaz / backend / inferencia)
                  |
                  | Webhook HTTPS protegido
                  v
        n8n en un servidor externo
                  |
            +-----+-----+
            |           |
        Gemini      Supabase / pgvector
                    documents_pulso_test
```

La disponibilidad pública de la interfaz no implica, por sí sola, que todos los servicios externos estén operativos en cada momento. La verificación debe incluir al menos una predicción válida, las explicaciones del modelo, una simulación y una solicitud de información al RAG.

#### 4.1.2 Instalación local reproducible de PULSO

Para desarrollo, pruebas y demostraciones en un equipo propio, se utiliza la topología **de referencia definida por `docker-compose.yml`**, cuyos servicios principales son NGINX, frontend, backend y ML Service. En esta modalidad la interfaz se accede normalmente desde `http://localhost/`, sin depender de la URL pública de la universidad. n8n y Supabase no forman parte de los cuatro contenedores locales y deben estar disponibles remotamente para utilizar las recomendaciones documentales.

```text
Navegador local --> http://localhost:80
                         |
                         v
                    NGINX local
                       |    \
                       |     --> Frontend local
                       v
                 Backend FastAPI local
                   |             |
                   v             | HTTPS + X-PULSO-RAG-Key
            ML Service local     v
                           n8n externo
                            |       |
                          Gemini  Supabase / pgvector
```

El frontend, backend y ML se ejecutan en el entorno local de la persona que instala PULSO. **La modalidad local con contenedores no constituye una réplica confirmada de la infraestructura de la universidad**; solo reproduce el entorno contemplado en el repositorio.

### 4.2 Proceso de actualización

El código fuente se administra mediante Git y GitHub. Las modificaciones deben registrarse en commits identificables y someterse a las verificaciones definidas por el proyecto antes de su integración.

- **Entorno local:** el desarrollador actualiza su copia del repositorio, revisa las variables de entorno, reconstruye los servicios modificados y ejecuta las verificaciones de la sección 5.
- **Entorno público universitario:** la actualización debe coordinarse con el personal de la universidad responsable de la publicación. Se desconoce si existe despliegue automático, sincronización con GitHub o actualización manual; no debe afirmarse ninguno de esos mecanismos como hecho.
- **Dependencias remotas RAG:** los cambios del workflow n8n, sus credenciales o la base documental en Supabase se administran separadamente de la instalación local o de la publicación del código de PULSO; requieren comprobar compatibilidad con el backend.

Una vez que la universidad comunique una actualización del entorno público, comprobar que la URL sigue disponible y ejecutar al menos las pruebas funcionales de la sección 5. Registrar el commit o versión publicada **solo si esa correspondencia se ha confirmado**.

### 4.3 Despliegue sin contenedores en infraestructura propia (alternativa)

Esta sección describe un **procedimiento genérico de referencia para un servidor administrado por el equipo o por otro operador**. No describe ni permite inferir la instalación que realizó la universidad. Para desarrollo puramente local, aplicar directamente la sección 3.1.

#### 4.3.1 Preparación del servidor

Disponer de un servidor con sistema operativo compatible, Python 3.11, Node.js 22, Git y conectividad hacia el webhook n8n. Configurar administración de procesos, proxy inverso, certificados HTTPS y medidas apropiadas de firewall. Las características mínimas de hardware no han sido establecidas mediante un estudio formal de dimensionamiento.

#### 4.3.2 Instalación de dependencias

Clonar el repositorio en una versión aprobada; crear el entorno Python e instalar las dependencias del backend y ML según la sección 3.1.2. Instalar dependencias del frontend mediante `npm ci` y construirlo con `npm run build` desde `frontend`.

#### 4.3.3 Configuración de la aplicación

Definir las variables indicadas en la sección 2.2, conservar el archivo del modelo oficial XGBoost v1 en la ruta esperada y configurar el proxy para servir el frontend y dirigir `/api/` al backend. Limitar la exposición de los puertos de servicios internos. Garantizar salida HTTPS hacia n8n y una clave RAG válida.

#### 4.3.4 Ejecución de la aplicación

Configurar un gestor de servicios del sistema (por ejemplo `systemd` en Linux) para ejecutar backend y ML Service con Uvicorn y recuperación ante fallos. Servir los archivos estáticos del frontend mediante un servidor HTTP o NGINX. Los comandos de desarrollo de 3.1.5 son útiles para depuración, pero por sí solos no constituyen un procedimiento de publicación pública endurecido.

#### 4.3.5 Actualización de versiones

Revisar los cambios y el commit aprobado, instalar dependencias modificadas, reconstruir el frontend si corresponde, reiniciar los procesos administrados y ejecutar las verificaciones de la sección 5. Mantener un mecanismo de reversión apropiado.

### 4.4 Despliegue con contenedores en infraestructura propia (alternativa)

Los siguientes procedimientos permiten desplegar PULSO mediante Docker Compose en un servidor administrado por el equipo de desarrollo o por un tercero autorizado. Se basan en las imágenes y configuraciones Docker preparadas en el repositorio, las cuales también fueron proporcionadas como parte de los requisitos solicitados por la universidad para la publicación de PULSO. Sin embargo, el procedimiento descrito corresponde a una alternativa de despliegue reproducible y no implica que la institución haya utilizado exactamente estos comandos o mecanismos de administración.

#### 4.4.1 Construcción de imágenes

Desde la raíz del repositorio, con Docker instalado y las variables necesarias configuradas:

```bash
docker compose config
```

```bash
docker compose build
```

#### 4.4.2 Ejecución en servidor

```bash
docker compose up -d
```

Esta configuración publica la aplicación mediante NGINX en el puerto definido en el repositorio (por defecto, 80). La exposición a Internet exige configurar HTTPS, seguridad de red y un dominio o dirección conforme a la infraestructura del administrador. No debe exponer directamente el backend ni el servicio ML a Internet.

#### 4.4.3 Variables de entorno y secretos

Mantener `.env` fuera del repositorio y restringir permisos de lectura. El backend necesita `RAG_SERVICE_URL`, `RAG_TIMEOUT_SECONDS` y **`RAG_WEBHOOK_API_KEY`**; la clave se envía al webhook externo en la cabecera **`X-PULSO-RAG-Key`**. La clave debe coincidir con la configurada en n8n y no debe aparecer en capturas, logs, comandos compartidos ni código del frontend. Las credenciales Gemini y Supabase pertenecen al entorno remoto de n8n.

#### 4.4.4 Persistencia y redes

El Compose de referencia no contiene n8n ni una base PostgreSQL local. El RAG utiliza un servidor n8n externo y los vectores documentales se almacenan en Supabase. Los servicios locales se comunican mediante los nombres de servicio de Docker Compose. Los contextos temporales del backend se mantienen en memoria: reiniciarlo puede invalidar consultas vinculadas a un `analysis_id` anterior. En caso de múltiples réplicas se requeriría revisar la gestión de ese estado temporal.

#### 4.4.5 Actualización del despliegue

En un servidor administrado por el equipo, confirmar primero la rama y el estado del repositorio:

```bash
git status -sb
```

Actualizar únicamente a la revisión aprobada, verificar configuración y ejecutar:

```bash
docker compose up -d --build
```

```bash
docker compose ps
```

```bash
docker compose logs --tail=100 backend ml-service nginx
```

Los comandos anteriores son de **autodespliegue opcional** y no documentan el procedimiento interno de actualización de la universidad.

## 5. Verificación de funcionamiento

### 5.1 Verificación de la instalación local

La comprobación debe cubrir tanto disponibilidad como comportamiento funcional. **La tabla siguiente se aplica a la instalación local con Docker Compose**. Para el despliegue público universitario, sustituir `http://localhost/` por la URL oficial y realizar las verificaciones de la subsección 5.2, sin suponer acceso a los contenedores o puertos internos de la universidad:

| Verificación | Procedimiento | Resultado esperado |
|---|---|---|
| Servicios Docker | `docker compose ps` | Cuatro servicios activos; `ml-service` saludable |
| Backend | Abrir `http://localhost/api/health` | Respuesta HTTP satisfactoria del backend |
| ML | Abrir `http://127.0.0.1:8001/health` | `status: ok` y `model_loaded: true` |
| Interfaz | Abrir `http://localhost/` | Formulario visible y navegable |
| Predicción | Completar un perfil válido y ejecutar análisis | Se presenta clasificación y resultado del modelo |
| Explicabilidad | Revisar el análisis generado | Aparecen contribuciones de variables SHAP |
| Simulación | Modificar una variable permitida y comparar | Se muestra el escenario simulado, sin afirmar causalidad |
| RAG remoto | Solicitar explicaciones/recomendaciones con `RAG_SERVICE_URL` y `RAG_WEBHOOK_API_KEY` válidos | El backend alcanza el webhook externo con HTTPS y devuelve información educativa con fuentes documentales |
| Secreto RAG | Comprobar que Compose acepta las variables y que la llamada RAG está autorizada | Sin error por clave ausente ni respuesta HTTP 401/403 al consultar el webhook |
| Integración | Comprobar flujo completo con un caso válido | No aparecen errores de comunicación inesperados |

Comandos de comprobación rápidos:

```bash
curl -i http://localhost/api/health
```

```bash
curl -i http://127.0.0.1:8001/health
```

```bash
docker compose logs --tail=100 ml-service backend
```

No se proporciona aquí un cuerpo JSON fijo para `POST /api/analyze` porque debe respetar el contrato de esquemas de la versión efectivamente instalada. Para pruebas automatizadas, utilizar los casos y fixtures del repositorio y verificar el contrato vigente en la documentación de la API.


### 5.2 Verificación del despliegue público universitario

La verificación del entorno universitario se realiza **como usuario final**, desde un navegador y utilizando la URL proporcionada por la institución. No requiere ni presume acceso SSH, Docker, repositorio alojado en servidor o configuración interna.

| Comprobación | Procedimiento desde un dispositivo conectado a Internet | Resultado esperado |
|---|---|---|
| Accesibilidad pública | Abrir la URL oficial desde una red externa a la universidad | Carga la interfaz web de PULSO |
| Formulario | Introducir un perfil de prueba válido | Se aceptan datos y validaciones conforme al formulario |
| Predicción y SHAP | Ejecutar el análisis | Se presenta el resultado y las contribuciones explicativas |
| Simulación | Modificar una variable permitida | Se muestra una comparación de escenarios |
| Información documental | Solicitar explicaciones o recomendaciones RAG | Se presenta información educativa con fuentes, si el servicio externo está disponible |
| Mensajes de error | Probar un valor inválido o un caso que active una validación prevista | La interfaz informa el problema sin revelar credenciales ni datos de configuración |

**Estado documentado:** el equipo ha confirmado que existe una URL pública accesible tanto dentro como fuera de la universidad. Esta guía no presenta una nueva ejecución de la batería anterior ni confirma la infraestructura del servidor universitario. Los resultados concretos y las capturas de la verificación pública deben registrarse cuando se realice la prueba para la entrega.


## 6. Solución de problemas frecuentes

**Diferencia operativa:** si el error ocurre en un **equipo local**, se pueden consultar los logs y la configuración de Docker siguiendo la tabla. Si ocurre exclusivamente en la **URL pública universitaria**, corresponde reportarlo al personal técnico responsable, aportando fecha, URL, operación realizada, mensaje observado y evidencia reproducible, sin intentar acceder a infraestructura para la que no se tienen permisos.

| Problema | Posible causa | Acción recomendada |
|---|---|---|
| La aplicación pública universitaria no abre | Incidencia de publicación, red, DNS o servicio institucional no verificable desde el equipo | Probar desde otra red y navegador; comunicar al responsable universitario la URL y el mensaje observado; no suponer causa interna |
| La interfaz pública abre pero falla una función | Dependencia externa o fallo de aplicación; causa aún no determinada | Registrar caso reproducible y comunicarlo al responsable del despliegue; revisar la integración externa solo con acceso autorizado |
| `docker` no se reconoce | Docker no instalado, daemon detenido o terminal sin acceso | Instalar/iniciar Docker; en WSL comprobar integración de Docker Desktop |
| Puerto 80 ocupado | Otro servidor o contenedor utiliza el puerto | Identificar el proceso; detenerlo o adaptar explícitamente el mapeo `ports` de NGINX |
| `ml-service` no saludable | El archivo `.joblib` falta o no se puede cargar | Revisar `docker compose logs ml-service` y la ruta `artifacts/final/model/pulso_xgboost.joblib` |
| El backend no responde | Dependencia ML indisponible o error de configuración | Consultar `docker compose logs backend`; comprobar la salud del ML Service |
| Interfaz visible, pero la API falla | Proxy NGINX o backend no disponible | Comprobar `/api/health`, `docker compose ps` y el archivo de NGINX |
| RAG no devuelve recomendaciones | URL incompleta, servidor n8n suspendido, timeout o error del proveedor | Confirmar URL completa de `/webhook/`, actividad del workflow, `RAG_TIMEOUT_SECONDS` y registros del backend/n8n |
| `docker compose config` informa que falta `RAG_WEBHOOK_API_KEY` | Clave vacía o no presente en `.env` | Solicitar la clave válida al administrador y definir `RAG_WEBHOOK_API_KEY` antes de iniciar Compose |
| HTTP 401 o 403 al solicitar recomendaciones | Clave RAG errónea o no enviada | Comprobar que backend tiene `RAG_WEBHOOK_API_KEY` y que coincide con la verificación del servidor n8n; no mostrarla en logs |
| RAG responde HTTP 503 al primer intento | Servidor remoto en arranque o temporalmente indisponible | Revisar disponibilidad de n8n; el cliente incorpora un segundo intento ante HTTP 503, sujeto al tiempo de espera y a la disponibilidad real |
| Error 422 al enviar datos | Campos fuera de rango, presión inconsistente o contrato inválido | Revisar el esquema de entrada; no alterar el contrato para hacer pasar un caso incorrecto |
| No se encuentra `analysis_id` | Contexto expirado o backend reiniciado | Generar un análisis nuevo; la caché es temporal |
| `npm ci` falla | Versión de Node incompatible o lockfile inconsistente | Utilizar una versión compatible con el Dockerfile; revisar el lockfile sin modificarlo arbitrariamente |
| Error de importación Python | Dependencias instaladas fuera del entorno virtual o ejecución fuera de la raíz | Activar `.venv`, instalar requirements y ejecutar `python -m uvicorn` desde la raíz |
| Recomendaciones lentas | Latencia de n8n o Gemini, reanudación del alojamiento o red | Revisar tiempos del workflow, configuración de timeout y disponibilidad externa; no asumir que es un fallo de ML |

## 7. Mantenimiento y actualización

Para mantener el MVP operativo se recomienda distinguir responsabilidades: **en la instalación local**, el equipo controla los contenedores y sus variables; **en el despliegue universitario**, la institución controla la publicación de la aplicación y el equipo debe coordinar con ella los cambios; **en el servicio n8n y Supabase**, los responsables correspondientes mantienen el workflow, sus credenciales y el corpus documental.

Como prácticas generales:

1. Registrar las versiones de código mediante commit o etiqueta de Git. En el despliegue público, documentar qué revisión se encuentra publicada solo cuando lo confirme el responsable de la universidad; mantener la correspondencia entre backend, frontend, modelo XGBoost y workflow RAG.
2. Ejecutar pruebas automatizadas relevantes antes de actualizar. Una actualización exitosa de contenedores no sustituye pruebas funcionales.
3. En entornos administrados por el equipo, vigilar `/api/health`, `/health`, errores y latencia del RAG. En la plataforma pública, verificar las funciones desde la URL oficial y escalar las incidencias a la universidad cuando no haya acceso operativo al servidor.
4. Actualizar dependencias tras revisar compatibilidad, vulnerabilidades y cambios de contrato; no cambiar versiones del modelo sin revalidar sus métricas.
5. Conservar y auditar las fuentes documentales del RAG; toda actualización del corpus requiere comprobar fragmentación, embeddings, recuperación y trazabilidad.
6. Mantener secretos fuera del repositorio, usar HTTPS para n8n y despliegues públicos, restringir servicios internos y coordinar la rotación de `RAG_WEBHOOK_API_KEY` entre backend y webhook.
7. Documentar cualquier cambio de configuración en la guía, especialmente rutas de artefactos, variables, puertos y mecanismos de despliegue. No atribuir a la universidad la configuración local mientras no esté confirmada.

Para validar el frontend desde su directorio:

```bash
npm run test -- --run
```

```bash
npm run lint
```

Para verificar la sintaxis de Compose desde la raíz:

```bash
docker compose config
```

Las pruebas backend y de ML deben ejecutarse con los procedimientos CI definidos para la versión instalada, sin asumir que todos los test suites existentes requieren el mismo conjunto de variables externas.

## 8. Referencias relacionadas

- Equipo de desarrollo de PULSO. (2026). *PULSO: Repositorio del proyecto*. GitHub. https://github.com/acoronellm/PULSO
- Equipo de desarrollo de PULSO. (2026). *PULSO: Informe final del proyecto*. Archivo `InformeFinal.md` del repositorio.
- Equipo de desarrollo de PULSO. (2026). *PULSO: Documentación técnica del desarrollo*. Archivo `Desarrollo.md` del repositorio (si forma parte de la entrega definitiva).
- Docker, Inc. (s. f.). *Docker Compose documentation*. https://docs.docker.com/compose/
- FastAPI. (s. f.). *FastAPI documentation*. https://fastapi.tiangolo.com/
- Vite. (s. f.). *Getting started*. https://vite.dev/guide/
- n8n. (s. f.). *n8n documentation*. https://docs.n8n.io/

---

**Condiciones por verificar antes de calificar la guía como procedimiento reproducido:** ejecutar en la rama de entrega el arranque desde un clon limpio; confirmar la versión efectiva del `.joblib` empaquetado en la imagen, el endpoint de producción de n8n y la clave compartida; validar el flujo de análisis, simulación y RAG; registrar evidencia de las comprobaciones y actualizar rutas si el Compose final difiere del consultado.
