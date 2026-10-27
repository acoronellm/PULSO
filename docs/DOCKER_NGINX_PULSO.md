# PULSO — Guía de infraestructura Docker y NGINX

## 1. Objetivo

Documentar la contenerización del frontend React + Vite y la implementación de NGINX como proxy inverso de PULSO.

Esta configuración permite ejecutar localmente los servicios principales mediante Docker Compose y acceder al sistema desde un único punto de entrada.

## 2. Arquitectura

La infraestructura contiene cuatro servicios:

| Servicio | Tecnología | Función |
|---|---|---|
| frontend | React, Vite y NGINX | Servir la interfaz compilada |
| nginx | NGINX | Proxy inverso y punto de entrada |
| backend | Python y FastAPI | Procesar solicitudes de la aplicación |
| ml-service | Python, XGBoost y SHAP | Predicción, explicación y simulación |

El servicio RAG funciona mediante un contenedor independiente de n8n.

### Flujo de comunicación

1. El navegador accede a NGINX mediante el puerto 80.
2. NGINX dirige las solicitudes `/` al frontend.
3. NGINX dirige las solicitudes `/api/` al backend.
4. El backend se comunica con ML Service mediante `http://ml-service:8001`.
5. El backend utiliza la dirección configurada en `RAG_SERVICE_URL` para consultar n8n.

NGINX conserva el prefijo `/api/` al reenviar las solicitudes a FastAPI.

## 3. Archivos principales

- `docker-compose.yml`: orquestación de servicios.
- `frontend/Dockerfile`: construcción y ejecución del frontend.
- `frontend/.dockerignore`: exclusión de archivos innecesarios.
- `infrastructure/nginx/default.conf`: configuración del proxy inverso.
- `backend/Dockerfile`: imagen del backend.
- `ml_service/Dockerfile`: imagen de ML Service.
- `.env.example`: referencia para configurar variables de entorno.

## 4. Requisitos

- Docker Desktop instalado y funcionando.
- Docker Compose disponible.
- Repositorio PULSO descargado.
- Artefactos del modelo disponibles en las rutas esperadas.
- Variables de entorno correctamente configuradas.
- Contenedor de n8n disponible para ejecutar el flujo que requiera RAG.

## 5. Construcción y ejecución

Desde la raíz del repositorio:

```powershell
docker compose --env-file .env.docker up -d --build
```

Comprobar el estado de los servicios:

```powershell
docker compose --env-file .env.docker ps
```

Acceder a la interfaz:

```text
http://localhost
```

El frontend se entrega como una compilación de producción de Vite, servida mediante NGINX.

## 6. Puertos

| Servicio | Acceso |
|---|---|
| NGINX principal | `http://localhost:80` |
| Backend | `http://127.0.0.1:8000` |
| ML Service | `http://127.0.0.1:8001` |
| Frontend | Puerto 80 interno |
| n8n | Puerto 5678, contenedor independiente |

Los puertos del backend y ML Service se restringen a la interfaz local del computador. El frontend no publica directamente su puerto al host.

La comunicación entre servicios de Compose utiliza la red interna creada por Docker.

## 7. Variables de entorno

El archivo `.env.docker` contiene configuración local y está excluido del control de versiones mediante `.gitignore`.

El backend utiliza variables como:

- `ML_SERVICE_URL`
- `ML_TIMEOUT_SECONDS`
- `RAG_SERVICE_URL`
- `RAG_TIMEOUT_SECONDS`

Para el frontend compilado mediante Docker se utiliza una URL base vacía, de forma que las solicitudes a `/api/` se envían al mismo origen y son gestionadas por NGINX.

No deben incorporarse credenciales ni valores sensibles al repositorio.

## 8. Pruebas realizadas

Se verificó:

- Construcción correcta de las imágenes Docker.
- Ejecución de los cuatro servicios mediante Docker Compose.
- Estado saludable de ML Service.
- Validación de la configuración de NGINX.
- Acceso al frontend desde `http://localhost`.
- Respuesta HTTP 200 del endpoint `/api/health`.
- Enrutamiento correcto de `/api/analyze` y `/api/simulate`.
- Predicción con XGBoost v1.
- Explicación SHAP.
- Simulación de escenarios.
- Comunicación con n8n mediante `host.docker.internal:5678`.
- Ejecución del análisis completo utilizando una respuesta RAG simulada.

La prueba RAG utilizó un workflow MOCK. No constituye una validación del sistema documental de producción.

## 9. Comandos de mantenimiento

Consultar registros:

```powershell
docker compose --env-file .env.docker logs --tail 100
```

Reiniciar los servicios:

```powershell
docker compose --env-file .env.docker restart
```

Detener la infraestructura:

```powershell
docker compose --env-file .env.docker down
```

Reconstruir después de modificar archivos de construcción o código incluido en imágenes:

```powershell
docker compose --env-file .env.docker up -d --build
```

Estas operaciones no gestionan automáticamente el contenedor independiente de n8n.

## 10. Consideraciones y limitaciones

- La infraestructura corresponde a un entorno de desarrollo e integración local.
- La configuración HTTP actual no incorpora TLS/HTTPS.
- El RAG debe estar disponible de forma independiente.
- Las pruebas documentales de producción del RAG están pendientes.
- Los cambios posteriores en los contratos de API deberán validarse conjuntamente con frontend y backend.
- La contenerización no modifica los parámetros del modelo, SHAP ni la simulación.
- El despliegue público requiere configuración adicional de seguridad, dominio, HTTPS y operación.

## 11. Resultado

La infraestructura local de PULSO permite ejecutar el frontend, el backend y ML Service mediante Docker Compose, utilizando NGINX como punto de entrada único para el navegador.

Las pruebas confirmaron la integración del frontend con la API, la predicción, SHAP, la simulación y la comunicación técnica con el RAG MOCK.

## 12. Mejoras de robustez y validación automatizada

### Configuración del frontend

Se incorporó un valor predeterminado para `VITE_API_URL` en `frontend/src/services/api.js`, permitiendo utilizar rutas relativas cuando la variable no se encuentre definida.

### Resolución de nombres en NGINX

Se implementó la resolución dinámica de los servicios `backend` y `frontend` mediante el DNS interno de Docker (`127.0.0.11`).

Este cambio reduce la dependencia de la resolución de nombres durante el arranque de NGINX y facilita la recuperación ante reinicios de los contenedores.

### Automatización mediante GitHub Actions

Se añadió el workflow `.github/workflows/infrastructure-ci.yml`, encargado de:

1. Validar Docker Compose.
2. Construir las imágenes Docker del frontend, backend y ML Service.
3. Verificar la configuración de NGINX.
4. Comprobar el enrutamiento HTTP hacia servicios simulados.
5. Verificar que el proxy permanece en ejecución.

Las pruebas automatizadas de enrutamiento utilizan mocks y no ejecutan el modelo XGBoost ni el workflow RAG real.

Las pruebas funcionales de los servicios reales deben verificarse mediante las pruebas de integración correspondientes.

La ejecución exitosa del workflow debe confirmarse en GitHub Actions antes de aprobar su integración.