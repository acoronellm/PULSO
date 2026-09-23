# Guía de entorno virtual para PULSO

## 1. Objetivo

Este documento explica cómo crear, configurar, usar y reutilizar el entorno virtual de Python del proyecto PULSO para ejecutar pruebas, entrenar modelos y trabajar con MLflow.

En este proyecto se utiliza un **entorno virtual de Python**, normalmente llamado `.venv`. No se trata de una máquina virtual completa: es un entorno aislado que permite instalar las dependencias del proyecto sin afectar otros proyectos de Python instalados en el computador.

## 2. Requisitos previos

Antes de crear el entorno virtual, verificar que estén instalados:

- Python.
- Git.
- Visual Studio Code o un editor equivalente.
- El repositorio de PULSO descargado localmente.

Para comprobar Python:

```powershell
python --version
```

Para comprobar Git:

```powershell
git --version
```

Los comandos de esta guía deben ejecutarse desde la **raíz del repositorio PULSO**, es decir, la carpeta donde se encuentran directorios como:

```text
PULSO/
├── data/
├── ml/
├── notebooks/
├── tests/
├── requirements-ml.txt
└── README.md
```

## 3. Crear el entorno virtual por primera vez

Abrir PowerShell o la terminal integrada de VS Code dentro de la raíz del proyecto.

Ejecutar:

```powershell
python -m venv .venv
```

Esto crea una carpeta llamada:

```text
.venv/
```

La carpeta contiene una instalación aislada de Python y será utilizada únicamente por PULSO.

No se debe subir `.venv/` a GitHub.

En `.gitignore` debe existir:

```gitignore
.venv/
```

## 4. Activar el entorno virtual

En PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si se activa correctamente, la terminal mostrará algo similar a:

```text
(.venv) PS C:\...\PULSO>
```

El texto `(.venv)` indica que los comandos de Python y `pip` utilizarán el entorno virtual de PULSO.

## 5. Si PowerShell bloquea la activación

En algunos equipos Windows, PowerShell puede impedir la ejecución del script de activación.

Una alternativa es ejecutar directamente Python desde el entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
```

Y para las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

## 6. Instalar las dependencias por primera vez

Una vez activado `.venv`, ejecutar:

```powershell
python -m pip install -r requirements-ml.txt
```

Este archivo instala las dependencias necesarias para el pipeline de Machine Learning, entre ellas:

- pandas
- NumPy
- scikit-learn
- MLflow
- PyYAML
- joblib
- matplotlib
- pytest

No es necesario volver a instalar estas dependencias cada vez que se abre el proyecto.

## 7. Ejecutar las pruebas automáticas

Con `.venv` activo y desde la raíz de PULSO:

```powershell
python -m pytest -q tests
```

Actualmente las pruebas verifican:

- Que las variables excluidas no entren al modelo.
- Que la división de datos sea reproducible.
- Que los conjuntos de entrenamiento, validación y prueba no se superpongan.
- Que regresión logística y árbol de decisión puedan entrenarse con datos sintéticos.
- Que las métricas principales puedan calcularse.

Un resultado como:

```text
.... [100%]
4 passed in 13.59s
```

significa que las pruebas automatizadas pasaron.

Estas pruebas utilizan **datos sintéticos**, no el CSV cardiovascular real.

## 8. Entrenar regresión logística con el dataset depurado

El archivo depurado esperado por defecto es:

```text
data/processed/cardio_clean_v1.csv
```

Para entrenar regresión logística:

```powershell
python -m ml.train --config ml/configs/logistic_regression.yaml
```

Si el CSV tiene otra ruta:

```powershell
python -m ml.train --config ml/configs/logistic_regression.yaml --data ruta/al/archivo.csv
```

La ejecución:

1. Carga el CSV depurado.
2. Selecciona las variables configuradas.
3. Divide los datos en entrenamiento, validación y prueba.
4. Entrena el modelo usando solamente entrenamiento.
5. Evalúa el modelo con validación.
6. Registra parámetros, métricas y artefactos en MLflow.
7. Mantiene el conjunto de prueba reservado.

## 9. Entrenar árbol de decisión

Ejecutar:

```powershell
python -m ml.train --config ml/configs/decision_tree.yaml
```

## 10. Iniciar MLflow

Para visualizar los experimentos registrados:

```powershell
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

La terminal mostrará una dirección local, normalmente:

```text
http://127.0.0.1:5000
```

Abrir esa dirección en el navegador.

## 11. Detener MLflow

En la terminal donde MLflow está ejecutándose:

```text
Ctrl + C
```

Esto detiene el servidor, pero no elimina experimentos, métricas ni artefactos.

## 12. Salir del entorno virtual

Ejecutar:

```powershell
deactivate
```

Esto no elimina el entorno ni desinstala las dependencias.

## 13. Volver a utilizar el proyecto otro día

No es necesario crear nuevamente `.venv` ni reinstalar todas las dependencias.

Abrir una terminal en PULSO y ejecutar:

```powershell
.\.venv\Scripts\Activate.ps1
```

Después pueden ejecutarse directamente las pruebas:

```powershell
python -m pytest -q tests
```

O entrenar un modelo:

```powershell
python -m ml.train --config ml/configs/logistic_regression.yaml
```

O:

```powershell
python -m ml.train --config ml/configs/decision_tree.yaml
```

Para consultar MLflow:

```powershell
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## 14. Cuándo volver a ejecutar `pip install`

Debe ejecutarse nuevamente cuando:

- Se elimina `.venv`.
- Se trabaja en otro computador.
- Se clona el repositorio por primera vez.
- Se agregan nuevas dependencias a `requirements-ml.txt`.
- Se actualizan versiones de las librerías.

## 15. Archivos locales que no deben subirse a GitHub

El `.gitignore` debe excluir:

```gitignore
.venv/
mlflow.db
mlflow.db-*
mlruns/
mlartifacts/
artifacts/
__pycache__/
.pytest_cache/
.env
.env.*
```

## 16. Flujo recomendado de trabajo diario

```text
Abrir repositorio PULSO
        ↓
Activar .venv
        ↓
Actualizar código si corresponde
        ↓
Modificar código o configuración
        ↓
Ejecutar pytest
        ↓
Entrenar modelo si corresponde
        ↓
Revisar ejecución en MLflow
        ↓
Comparar resultados
        ↓
Commit y pull request
        ↓
deactivate
```

## 17. Resumen de comandos

### Crear el entorno por primera vez

```powershell
python -m venv .venv
```

### Activar

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar dependencias

```powershell
python -m pip install -r requirements-ml.txt
```

### Ejecutar pruebas

```powershell
python -m pytest -q tests
```

### Entrenar regresión logística

```powershell
python -m ml.train --config ml/configs/logistic_regression.yaml
```

### Entrenar árbol de decisión

```powershell
python -m ml.train --config ml/configs/decision_tree.yaml
```

### Abrir MLflow

```powershell
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

### Salir del entorno virtual

```powershell
deactivate
```

## 18. Consideración final

El entorno virtual garantiza que los experimentos de PULSO puedan ejecutarse con un entorno de dependencias controlado.

Para una reproducibilidad más estricta, después de validar el pipeline conviene fijar versiones exactas de las dependencias utilizadas en los experimentos oficiales.
