# PULSO: plataforma de predicción explicable y educación preventiva cardiovascular

## Informe de avance para la Entrega 1 Backend

**Curso:** Proyecto Final Backend  
**Integrantes:** Miguel Angel Márquez Coronel, María Gabriela Rey Barrios y Andrés Felipe Serrano Mendoza  
**Fecha:** 13/11/2026 

## Resumen

PULSO es una plataforma web propuesta para apoyar la prevención y la educación cardiovascular mediante una estimación generada por aprendizaje automático, explicaciones de las variables que influyen en la salida del modelo, simulación de escenarios e información recuperada de fuentes confiables. El público principal son personas no especializadas. La plataforma no tiene como propósito diagnosticar, prescribir tratamientos ni sustituir la atención de profesionales de la salud.

El componente de Machine Learning utiliza el *Cardiovascular Disease Dataset* de Kaggle y aborda una tarea de clasificación binaria sobre la variable `cardio`. Por ello, su salida representa una probabilidad estimada de pertenecer a la clase `cardio = 1`; no representa el riesgo de sufrir un evento cardiovascular futuro en un horizonte temporal definido. El modelo final documentado es XGBoost, con umbral de clasificación 0.38 y sin calibración adicional. SHAP describe el comportamiento del modelo, mientras que las simulaciones muestran cómo cambia su salida ante entradas alternativas; ninguno de estos resultados demuestra causalidad clínica.

El repositorio integra una interfaz React/Vite, un backend FastAPI, PostgreSQL, un servicio Python de Machine Learning y una integración RAG. La interfaz permite registrarse e iniciar sesión antes de enviar factores, visualizar una predicción, consultar factores SHAP, solicitar información preventiva y explorar una simulación. El backend guarda las cuentas en PostgreSQL, almacena las contraseñas mediante hashes Argon2 y protege las rutas de análisis con JWT bearer. No se implementan roles, consentimiento de privacidad ni eliminación de cuenta. Este informe presenta esas diferencias como características y límites del estado actual, no como funcionalidades ya realizadas.

## 1. Contexto y problema

Las herramientas de evaluación cardiovascular suelen estar dirigidas a profesionales, dependen de poblaciones específicas y pueden presentar resultados difíciles de interpretar para el público general. El problema que aborda PULSO es la dificultad de comprender información personalizada sobre factores asociados con enfermedades cardiovasculares, así como las limitaciones de las estimaciones y de los escenarios hipotéticos.

La propuesta integra predicción, explicabilidad, simulación e información educativa en una experiencia web. El modelo utilizado en el MVP se entrena con datos públicos. Su variable objetivo identifica la presencia o ausencia de enfermedad cardiovascular en los registros de origen. Por tanto, el sistema no debe describirse como una calculadora clínica de riesgo futuro ni como un instrumento diagnóstico.

La procedencia del conjunto de datos no permite asumir representatividad para Colombia o América Latina. Los resultados deben comunicarse con esa limitación, sin atribuirles validez clínica poblacional que no haya sido demostrada.

## 2. Objetivos y alcance

### 2.1 Objetivo general

Diseñar e implementar un MVP web que facilite a personas no especializadas la comprensión de factores asociados con enfermedades cardiovasculares mediante un clasificador de Machine Learning, explicaciones SHAP, simulaciones de escenarios e información educativa sustentada en fuentes confiables.

### 2.2 Alcance funcional

El alcance funcional de PULSO comprende:

1. Ingreso y validación de los factores requeridos por el modelo.
2. Estimación de la probabilidad de pertenecer a la clase `cardio = 1`.
3. Presentación de la clasificación, la probabilidad, el umbral y la versión del modelo.
4. Explicación local de la predicción mediante los factores SHAP principales.
5. Comparación de la predicción original con escenarios hipotéticos admitidos por el modelo.
6. Solicitud de información educativa mediante RAG, basada en fuentes médicas seleccionadas.
7. Interfaz web orientada al público general, con mensajes sobre las limitaciones del resultado.

La gestión de cuentas, los roles, el consentimiento, la eliminación de datos y el almacenamiento persistente no forman parte de las funcionalidades demostrables en el estado revisado del repositorio. Se mencionan más adelante como aspectos transversales de la pauta que deben distinguirse del alcance implementado de PULSO.

### 2.3 Fuera del alcance

PULSO no diagnostica enfermedades, no prescribe ni modifica tratamientos, no reemplaza la consulta profesional y no certifica clínicamente sus modelos. La simulación es una exploración matemática de las salidas del clasificador, no una recomendación de intervención ni una demostración de causalidad.

## 3. E1. Contextualización y definición del problema

### 3.1. Contexto del proyecto

PULSO es una plataforma web orientada a la prevención y educación cardiovascular que integra técnicas de aprendizaje automático (*Machine Learning*), inteligencia artificial explicable (*Explainable AI*, XAI) y generación aumentada por recuperación (*Retrieval-Augmented Generation*, RAG).

El proyecto surge de la necesidad de facilitar el acceso a herramientas tecnológicas que permitan explorar factores asociados con las enfermedades cardiovasculares y comprender los resultados de modelos predictivos mediante explicaciones accesibles para personas sin conocimientos especializados en medicina o inteligencia artificial.

La plataforma permite introducir información relacionada con características físicas, presión arterial y determinados hábitos de vida. A partir de estos datos, un modelo supervisado de clasificación binaria genera una estimación probabilística de pertenencia a la clase asociada con enfermedad cardiovascular en el conjunto de datos utilizado para su entrenamiento.

Adicionalmente, PULSO incorpora mecanismos de explicabilidad mediante SHAP (*SHapley Additive exPlanations*), simulación de escenarios y generación de recomendaciones educativas fundamentadas en documentos de referencia recuperados mediante RAG.

La solución tiene un propósito exclusivamente educativo y preventivo. Sus resultados no constituyen diagnósticos médicos, no permiten determinar con certeza la presencia de una enfermedad cardiovascular y no sustituyen la evaluación de profesionales de la salud.

### 3.2. Descripción del problema

Las enfermedades cardiovasculares representan un problema relevante de salud pública. Su prevención está relacionada con la identificación y comprensión de distintos factores, entre ellos la presión arterial, las características antropométricas y determinados hábitos de vida.

Aunque existen modelos de aprendizaje automático capaces de identificar patrones estadísticos asociados con enfermedades cardiovasculares, sus resultados pueden resultar difíciles de interpretar para usuarios sin formación técnica.

Presentar únicamente una probabilidad o una clasificación puede generar confusión, especialmente cuando no se explica qué variables influyeron en el resultado, cuáles son las limitaciones del modelo o cómo interpretar adecuadamente la información.

Asimismo, una predicción estadística no proporciona por sí sola orientación educativa fundamentada ni permite comprender cómo cambiaría el resultado del modelo ante modificaciones hipotéticas de determinadas variables.

En consecuencia, se identifica la necesidad de una solución que integre predicción, explicabilidad, simulación y acceso a información educativa respaldada por fuentes documentales, mediante una interfaz comprensible y accesible.

PULSO busca atender esta necesidad mediante una plataforma que permita interpretar los resultados de un modelo predictivo sin confundirlos con diagnósticos clínicos o estimaciones causales.

### 3.3. Objetivo general

Desarrollar una plataforma web educativa orientada a la prevención cardiovascular que integre un modelo de clasificación supervisada, técnicas de inteligencia artificial explicable, simulación de escenarios y generación de recomendaciones educativas basadas en recuperación documental, con el propósito de facilitar la comprensión de factores asociados con enfermedades cardiovasculares.

### 3.4. Objetivos específicos

1. Implementar una interfaz web que permita registrar y validar las variables requeridas por el modelo predictivo.

2. Integrar un modelo de aprendizaje automático que genere una probabilidad estimada de pertenencia a la clase positiva del conjunto de datos cardiovascular utilizado.

3. Incorporar técnicas de explicabilidad mediante SHAP para identificar las variables que contribuyen al resultado de una predicción individual.

4. Implementar una funcionalidad de simulación que permita modificar determinadas variables y comparar las respuestas del modelo frente a distintos escenarios hipotéticos.

5. Integrar un sistema RAG que recupere información de un corpus documental seleccionado para generar recomendaciones educativas respaldadas por fuentes identificables.

6. Desarrollar una arquitectura modular que permita integrar el frontend, el backend, el servicio de Machine Learning y el sistema RAG, manteniendo responsabilidades diferenciadas.

7. Comunicar de forma clara las limitaciones del modelo y garantizar que los resultados se presenten con una finalidad educativa, sin atribuirles validez diagnóstica.

### 3.5. Necesidades funcionales identificadas

A partir del problema planteado, se identificaron cinco necesidades funcionales principales.

**NF-01. Registro y validación de variables de entrada**

El sistema debe permitir que el usuario introduzca la información necesaria para ejecutar la predicción, incluyendo edad, sexo codificado según el conjunto de datos, altura, peso, presión arterial sistólica y diastólica, consumo de tabaco, consumo de alcohol y actividad física.

El índice de masa corporal (IMC) debe calcularse automáticamente a partir del peso y la altura, evitando que sea ingresado como un valor independiente.

**NF-02. Predicción mediante aprendizaje automático**

El sistema debe procesar las variables introducidas y obtener una probabilidad mediante un modelo de clasificación binaria.

La interpretación del resultado debe considerar el umbral de decisión establecido para el modelo y comunicar que la probabilidad corresponde a la clasificación aprendida a partir de los datos de entrenamiento.

**NF-03. Explicabilidad de resultados**

El sistema debe presentar información que permita comprender cuáles variables contribuyeron al resultado individual del modelo.

Para ello, debe integrar SHAP y mostrar los factores relevantes de manera comprensible, sin interpretar automáticamente las contribuciones estadísticas como relaciones causales.

**NF-04. Simulación de escenarios**

El sistema debe permitir modificar determinadas variables de entrada para observar cómo cambia el resultado del modelo.

Las simulaciones deben conservar la coherencia de los datos derivados y mostrar comparaciones entre el escenario original y el escenario modificado.

Los resultados deben interpretarse como variaciones en la respuesta del modelo y no como predicciones clínicas del efecto que tendría una intervención.

**NF-05. Recomendaciones educativas fundamentadas**

El sistema debe proporcionar información educativa relacionada con los factores identificados, utilizando un sistema RAG que recupere contenido de un corpus documental previamente seleccionado.

Las recomendaciones deben estar vinculadas con fuentes identificables y respetar las limitaciones del alcance educativo de la plataforma.

### 3.6. Alcance funcional del proyecto

El alcance principal de PULSO comprende el desarrollo de una aplicación web que permita realizar un proceso de análisis educativo a partir de variables cardiovasculares.

Este proceso incluye la captura y validación de datos, la ejecución de la predicción, la interpretación de factores mediante SHAP, la simulación de escenarios y la presentación de recomendaciones educativas mediante RAG.

La solución está organizada en componentes tecnológicos diferenciados:

- **Frontend:** aplicación desarrollada con React y TypeScript, responsable de la interacción con el usuario y la presentación de resultados.
- **Backend:** API desarrollada con Python y FastAPI, encargada de coordinar los casos de uso, validar solicitudes y gestionar la comunicación entre los servicios.
- **Servicio de Machine Learning:** componente independiente encargado de cargar el modelo predictivo, ejecutar inferencias y obtener explicaciones mediante SHAP.
- **Sistema RAG:** flujo implementado mediante n8n que recupera información documental almacenada en una base vectorial y genera contenido educativo fundamentado.
- **Infraestructura:** servicios contenerizados mediante Docker, con NGINX como proxy inverso para centralizar el acceso a la aplicación.

La delimitación funcional prioriza las capacidades de análisis y educación cardiovascular. Las funcionalidades de autenticación, gestión de usuarios, almacenamiento de historiales personales y administración de cuentas no forman parte del alcance funcional original de PULSO y su eventual incorporación dependerá de los requisitos académicos acordados y de futuras decisiones de desarrollo.

### 3.7. Decisiones técnicas y restricciones

Durante la definición y desarrollo de PULSO se establecieron las siguientes decisiones:

**DT-01. Separación de responsabilidades**

Se adoptó una arquitectura que diferencia las responsabilidades de presentación, coordinación de casos de uso, inferencia mediante Machine Learning y generación de contenido educativo.

Esta separación facilita el mantenimiento, las pruebas y la evolución independiente de los servicios.

**DT-02. Uso de un modelo de clasificación supervisada**

El componente predictivo utiliza un modelo XGBoost entrenado con el conjunto de datos cardiovascular seleccionado para el proyecto.

Se establece un umbral de clasificación de 0.38 con el objetivo de priorizar la sensibilidad del modelo y reducir la proporción de falsos negativos, considerando el compromiso con la especificidad.

**DT-03. Incorporación de explicabilidad**

Se utiliza SHAP como mecanismo de explicación local para identificar las contribuciones de las variables a las predicciones individuales.

**DT-04. Simulaciones sin interpretación causal**

Los escenarios simulados permiten comparar resultados del modelo, pero no representan estimaciones validadas de los efectos reales de intervenciones clínicas o cambios de hábitos.

**DT-05. Recuperación documental para recomendaciones educativas**

La generación de recomendaciones se apoya en información recuperada de un corpus documental seleccionado. Se busca mantener trazabilidad entre las recomendaciones y sus fuentes.

**DT-06. Minimización de datos personales**

La plataforma prioriza el procesamiento de información necesaria para las funciones educativas y predictivas, sin establecer como requisito original la conservación de historiales personales.

**DT-07. Limitaciones clínicas**

PULSO no se considera un dispositivo médico ni una herramienta diagnóstica. Sus resultados están condicionados por las características del conjunto de datos utilizado, el desempeño del modelo y las limitaciones propias de los métodos de aprendizaje automático.

### 3.8. Resultado de la definición del proyecto

La definición del problema permitió establecer el propósito, las necesidades funcionales, el alcance y las principales restricciones técnicas de PULSO.

Como resultado, se identificaron cinco capacidades funcionales principales: captura y validación de variables, predicción mediante Machine Learning, explicabilidad mediante SHAP, simulación de escenarios y generación de recomendaciones educativas mediante RAG.

Estas capacidades constituyen la base para la elaboración de las historias de usuario, la identificación de los casos de uso y el diseño de la arquitectura del sistema, desarrollados en los apartados siguientes del informe.

La definición del proyecto se realizó como parte del trabajo académico del equipo desarrollador. Conforme a la adaptación del enunciado autorizada por el docente, no se requirió realizar una reunión formal de Inception con un equipo externo.

## 4. E2. Historias de usuario y requisitos funcionales

### 4.1. Definición del backlog del producto

El backlog de PULSO se estructura a partir de las necesidades funcionales identificadas durante la definición y evolución del proyecto. Su propósito es organizar los requisitos de la plataforma en historias de usuario verificables, relacionadas con la gestión de usuarios, la captura de variables cardiovasculares, la clasificación mediante Machine Learning, la explicabilidad, la simulación, la generación de recomendaciones educativas y la consulta del historial de análisis.

Las historias se expresan utilizando el formato «Como [rol], quiero [funcionalidad], para [beneficio]» y cuentan con criterios de aceptación basados en el esquema Dado/Cuando/Entonces.

Cada historia incorpora una prioridad y una estimación de complejidad en puntos, utilizando la escala de Fibonacci. Estas estimaciones son referenciales y deberán corresponder con la planificación técnica documentada por el equipo.

El backlog diferencia las funcionalidades dirigidas al usuario final de los requisitos operativos, de seguridad y de calidad necesarios para el funcionamiento de la plataforma.

### 4.2. Historias de usuario

#### HU-01. Ingreso de factores cardiovasculares

**Historia:** Como usuario autenticado, quiero introducir mis factores cardiovasculares mediante un formulario, para solicitar un análisis educativo personalizado.

**Criterios de aceptación:**

- Dado que accedo al formulario, cuando ingreso los datos requeridos, entonces puedo identificar claramente cada variable y su unidad de medida.
- Dado que completo los campos obligatorios con valores válidos, cuando envío el formulario, entonces el sistema procesa la solicitud.

**Prioridad:** Alta.  
**Puntos:** 5.

#### HU-02. Validación de datos de entrada

**Historia:** Como usuario, quiero que el sistema valide mis datos, para evitar análisis realizados con información incompleta o inconsistente.

**Criterios de aceptación:**

- Dado que introduzco un valor fuera de los límites admitidos, cuando intento solicitar el análisis, entonces el sistema identifica el campo inválido.
- Dado que la presión arterial sistólica no supera a la diastólica, cuando intento enviar los datos, entonces el sistema rechaza la solicitud e informa la inconsistencia.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-03. Cálculo automático del IMC

**Historia:** Como usuario, quiero que el sistema calcule automáticamente mi índice de masa corporal a partir del peso y la altura, para evitar cálculos manuales y mantener la coherencia de los datos.

**Criterios de aceptación:**

- Dado que proporciono un peso y una altura válidos, cuando se prepara el perfil para el modelo, entonces el sistema calcula el IMC utilizando ambas variables.
- Dado que modifico el peso durante una simulación, cuando se prepara el escenario, entonces el IMC se recalcula manteniendo la altura del perfil original.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-04. Predicción mediante Machine Learning

**Historia:** Como usuario autenticado, quiero obtener una estimación generada por el modelo predictivo, para explorar la clasificación asociada con mis factores cardiovasculares.

**Criterios de aceptación:**

- Dado un perfil válido y una sesión autenticada, cuando solicito el análisis, entonces el sistema devuelve la probabilidad estimada, la clasificación, el umbral y la versión del modelo.
- Dado que el servicio de Machine Learning no está disponible, cuando solicito el análisis, entonces el sistema informa el fallo sin generar resultados ficticios.

**Prioridad:** Alta.  
**Puntos:** 5.

#### HU-05. Visualización e interpretación de la predicción

**Historia:** Como usuario, quiero visualizar la estimación y su clasificación mediante una presentación comprensible, para interpretar correctamente la información proporcionada por el modelo.

**Criterios de aceptación:**

- Dado que el análisis finaliza correctamente, cuando accedo a los resultados, entonces puedo consultar la probabilidad y la clasificación obtenidas.
- Dado que se muestra la clasificación, cuando consulto su interpretación, entonces puedo identificar el umbral utilizado para determinarla.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-06. Comunicación de las limitaciones del modelo

**Historia:** Como usuario, quiero conocer las limitaciones del resultado, para evitar interpretarlo como un diagnóstico médico.

**Criterios de aceptación:**

- Dado que consulto una predicción, cuando se presenta el resultado, entonces se comunica que corresponde a la clase positiva del conjunto de datos y no a una predicción clínica de eventos cardiovasculares futuros.
- Dado que consulto la interpretación, cuando reviso sus advertencias, entonces se informa que el modelo no sustituye la valoración profesional y que su representatividad poblacional no está clínicamente validada.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-07. Explicabilidad mediante SHAP

**Historia:** Como usuario, quiero conocer los factores que contribuyeron a mi predicción, para comprender mejor el comportamiento del modelo.

**Criterios de aceptación:**

- Dado un análisis exitoso, cuando consulto la explicación, entonces se muestran los principales factores identificados mediante SHAP.
- Dado que se presenta un factor, cuando consulto su contribución, entonces puedo identificar si aumenta o disminuye la salida del modelo, sin atribuirle automáticamente una relación causal.

**Prioridad:** Alta.  
**Puntos:** 5.

#### HU-08. Modificación de variables para simulación

**Historia:** Como usuario, quiero modificar determinadas variables de mi perfil, para explorar escenarios hipotéticos mediante el mismo modelo predictivo.

**Criterios de aceptación:**

- Dado un análisis original, cuando modifico una variable permitida, entonces puedo solicitar una nueva predicción utilizando el escenario modificado.
- Dado que introduzco un cambio inválido, cuando intento realizar la simulación, entonces el sistema rechaza el escenario sin alterar los datos originales.

**Prioridad:** Alta.  
**Puntos:** 5.

#### HU-09. Comparación de escenarios

**Historia:** Como usuario, quiero comparar los resultados del escenario original y el simulado, para comprender cómo cambian las salidas del modelo.

**Criterios de aceptación:**

- Dado que ejecuto una simulación válida, cuando obtengo el resultado, entonces puedo visualizar las probabilidades originales y simuladas.
- Dado que comparo ambos escenarios, cuando se presenta la diferencia, entonces se informa que el cambio representa una variación matemática del modelo y no una estimación causal de una intervención.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-10. Recomendaciones educativas mediante RAG

**Historia:** Como usuario, quiero recibir recomendaciones educativas relacionadas con mi análisis, para consultar información preventiva respaldada por documentos seleccionados.

**Criterios de aceptación:**

- Dado un análisis válido, cuando solicito información educativa, entonces el sistema consulta el servicio RAG y presenta la respuesta recibida.
- Dado que el sistema genera recomendaciones, cuando estas se presentan, entonces su contenido debe fundamentarse en las fuentes documentales recuperadas y no ofrecer diagnósticos ni prescripciones.

**Prioridad:** Alta.  
**Puntos:** 5.

#### HU-11. Consulta de fuentes educativas

**Historia:** Como usuario, quiero identificar las fuentes utilizadas para elaborar las recomendaciones, para conocer su procedencia y consultar la información de referencia.

**Criterios de aceptación:**

- Dado que recibo una recomendación respaldada documentalmente, cuando consulto sus fuentes, entonces puedo identificar las referencias asociadas.
- Dado que una recomendación no cuenta con evidencia documental suficiente, cuando se genera la respuesta, entonces no se presentan fuentes ficticias ni afirmaciones como si estuvieran verificadas.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-12. Manejo de indisponibilidad del servicio RAG

**Historia:** Como usuario, quiero recibir información clara cuando el servicio educativo no esté disponible, para comprender por qué no se muestran recomendaciones.

**Criterios de aceptación:**

- Dado que el servicio RAG presenta un fallo, cuando solicito recomendaciones, entonces el sistema informa la indisponibilidad sin inventar contenido.
- Dado que la predicción ya se realizó correctamente, cuando falla la solicitud educativa, entonces el resultado predictivo permanece disponible.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-13. Accesibilidad y adaptabilidad de la interfaz

**Historia:** Como usuario, quiero interactuar con una interfaz clara y adaptable a diferentes tamaños de pantalla, para utilizar las funcionalidades principales de PULSO de manera comprensible.

**Criterios de aceptación:**

- Dado que accedo a PULSO desde un navegador, cuando modifico el tamaño de la ventana, entonces los componentes principales se reorganizan para adaptarse al espacio disponible sin superponerse ni perder legibilidad.
- Dado que introduzco información incorrecta o incompleta, cuando intento realizar un análisis, entonces el sistema presenta mensajes comprensibles que permiten identificar y corregir los errores.

**Prioridad:** Alta.  
**Puntos:** 3.

**Alcance de validación:** Se ha observado adaptabilidad visual del formulario de evaluación en diferentes anchos de pantalla. La compatibilidad funcional completa con dispositivos móviles requiere pruebas adicionales.

#### HU-14. Gestión operativa del corpus documental

**Historia:** Como responsable técnico del sistema, quiero mantener actualizado el corpus documental utilizado por RAG, para conservar la pertinencia y trazabilidad de la información educativa.

**Criterios de aceptación:**

- Dado un documento previamente seleccionado y aprobado, cuando se incorpora mediante el flujo de ingesta, entonces sus fragmentos y metadatos quedan disponibles para recuperación.
- Dado que un documento debe actualizarse o reemplazarse, cuando se ejecuta el procedimiento de mantenimiento, entonces se evita conservar fragmentos obsoletos o duplicados del documento sustituido.

**Prioridad:** Media.  
**Puntos:** 5.

**Nota:** Esta historia corresponde a una operación técnica de mantenimiento del corpus. No implica la existencia de un panel administrativo ni de un sistema de roles.

#### HU-15. Gestión de errores de la API

**Historia:** Como usuario, quiero recibir mensajes de error comprensibles cuando una solicitud falla, para identificar el problema y continuar utilizando la plataforma.

**Criterios de aceptación:**

- Dada una solicitud inválida, cuando la API la procesa, entonces devuelve una respuesta de error estructurada que permite identificar la causa.
- Dado un fallo interno, cuando el sistema responde, entonces no expone contraseñas, secretos, trazas internas ni información sensible de configuración.

**Prioridad:** Alta.  
**Puntos:** 3.

#### HU-16. Verificación de disponibilidad de servicios

**Historia:** Como responsable técnico del sistema, quiero comprobar la disponibilidad de los servicios principales, para verificar que la infraestructura se encuentra operativa.

**Criterios de aceptación:**

- Dado que el backend está funcionando, cuando se consulta su endpoint de salud, entonces devuelve una respuesta que permite comprobar su disponibilidad.
- Dado que se inicia la infraestructura mediante Docker Compose, cuando se verifica el estado de los servicios, entonces es posible identificar cuáles se encuentran ejecutándose y si los servicios con comprobaciones de salud están operativos.

**Prioridad:** Media.  
**Puntos:** 3.

#### HU-17. Registro de usuarios

**Historia:** Como persona interesada en utilizar PULSO, quiero crear una cuenta mediante un correo electrónico y una contraseña, para acceder a las funcionalidades de la plataforma.

**Criterios de aceptación:**

- Dado que no tengo una cuenta registrada, cuando proporciono un correo electrónico válido y una contraseña que cumple los requisitos establecidos, entonces el sistema crea mi cuenta y almacena la contraseña utilizando hashing seguro.
- Dado que intento registrar un correo electrónico que ya existe, cuando envío la solicitud, entonces el sistema rechaza el registro e informa que la cuenta ya está registrada.

**Prioridad:** Alta.  
**Puntos:** 5.

**Implementación relacionada:** `RegisterUser`, `POST /api/auth/register`, PostgreSQL y Argon2.

#### HU-18. Inicio de sesión

**Historia:** Como usuario registrado, quiero iniciar sesión mediante mis credenciales, para acceder a las funcionalidades protegidas de PULSO.

**Criterios de aceptación:**

- Dado que tengo una cuenta registrada, cuando proporciono credenciales válidas, entonces el sistema verifica mi identidad y emite un token JWT de acceso.
- Dado que proporciono credenciales incorrectas, cuando intento iniciar sesión, entonces el sistema rechaza la autenticación sin conceder acceso a las funcionalidades protegidas.

**Prioridad:** Alta.  
**Puntos:** 5.

**Implementación relacionada:** `AuthenticateUser`, `POST /api/auth/login`, JWT y `Argon2PasswordHasher`.

#### HU-19. Protección de funcionalidades mediante autenticación

**Historia:** Como usuario registrado, quiero que las operaciones de análisis y consulta de información personal estén protegidas mediante autenticación, para evitar accesos no autorizados.

**Criterios de aceptación:**

- Dado que no proporciono un token de acceso válido, cuando intento utilizar una operación protegida, entonces el sistema rechaza la solicitud con una respuesta de autenticación apropiada.
- Dado que tengo una sesión autenticada, cuando consulto información personal o resultados persistentes, entonces el sistema utiliza mi identidad para determinar a qué registros puedo acceder.

**Prioridad:** Alta.  
**Puntos:** 5.

**Implementación relacionada:** `get_current_user`, HTTP Bearer, PyJWT y dependencias de autenticación de FastAPI.

#### HU-20. Consulta del historial de análisis

**Historia:** Como usuario autenticado, quiero consultar los resultados de mis análisis anteriores, para revisar las evaluaciones que he realizado en PULSO.

**Criterios de aceptación:**

- Dado que tengo análisis almacenados, cuando accedo al historial, entonces el sistema presenta los registros asociados con mi cuenta, incluyendo la fecha y la probabilidad correspondiente.
- Dado que consulto el historial, cuando solicito más resultados, entonces el sistema utiliza paginación y devuelve únicamente registros asociados con mi identidad autenticada.

**Prioridad:** Alta.  
**Puntos:** 5.

**Implementación relacionada:** `ListAnalysisHistory`, `SQLAlchemyAnalysisHistoryRepository`, `GET /api/analyses` y `HistoryPage`.

### 4.3. Clasificación del backlog

Las historias se organizan en siete grupos funcionales y técnicos.

| Grupo | Historias |
|---|---|
| Captura y preparación de información | HU-01, HU-02, HU-03 |
| Predicción e interpretación | HU-04, HU-05, HU-06 |
| Explicabilidad y simulación | HU-07, HU-08, HU-09 |
| Información educativa mediante RAG | HU-10, HU-11, HU-12 |
| Interfaz y manejo de errores | HU-13, HU-15 |
| Operación y mantenimiento | HU-14, HU-16 |
| Gestión de usuarios, autenticación e historial | HU-17, HU-18, HU-19, HU-20 |

El grupo de gestión de usuarios incorpora las capacidades implementadas de registro, autenticación, protección de operaciones y consulta del historial persistente.

### 4.4. Priorización

Se establece una prioridad alta para las funcionalidades directamente relacionadas con el análisis cardiovascular, la interpretación de resultados, la seguridad de acceso y la consulta de información personal.

La autenticación se considera una capacidad transversal necesaria para el funcionamiento de las operaciones protegidas.

La gestión operativa del corpus y la verificación de disponibilidad de servicios se clasifican con prioridad media, sin que ello implique que las condiciones técnicas indispensables puedan omitirse.

Los puntos representan estimaciones relativas de complejidad y no duraciones expresadas en horas o días.

### 4.5. Delimitación del backlog

El backlog comprende las capacidades funcionales originales de PULSO y las funcionalidades incorporadas posteriormente para la gestión de usuarios y el historial de resultados.

El alcance implementado contempla:

- Captura y validación de variables cardiovasculares.
- Predicción mediante Machine Learning.
- Explicabilidad mediante SHAP.
- Simulación y comparación de escenarios.
- Generación de recomendaciones educativas mediante RAG.
- Consulta de fuentes documentales.
- Registro e inicio de sesión.
- Autenticación mediante JWT.
- Protección de operaciones que requieren identidad autenticada.
- Persistencia y consulta del historial de análisis.

El historial conserva resultados seleccionados de las evaluaciones realizadas, sin almacenar permanentemente el perfil cardiovascular completo ni las explicaciones SHAP.

Se mantiene una separación entre la persistencia relacional de cuentas e historiales, el almacenamiento temporal del contexto de análisis y el corpus documental almacenado en Supabase.

Las funcionalidades de administración de múltiples roles, renovación mediante refresh tokens, gestión específica de consentimientos y eliminación de cuentas no forman parte de las capacidades implementadas descritas en este backlog.

Su eventual incorporación requerirá ampliar las historias de usuario y definir sus correspondientes criterios de aceptación.

### 4.6. Relación con la implementación

Las historias de usuario constituyen la referencia funcional para los casos de uso, endpoints, componentes de interfaz y pruebas automatizadas.

Las funcionalidades de autenticación e historial se relacionan con componentes específicos del backend y del frontend:

| Historia | Componente principal | Endpoint |
|---|---|---|
| HU-17 | `RegisterUser` | `POST /api/auth/register` |
| HU-18 | `AuthenticateUser` | `POST /api/auth/login` |
| HU-19 | `get_current_user` y autenticación JWT | Endpoints protegidos |
| HU-20 | `ListAnalysisHistory` | `GET /api/analyses` |

La implementación del historial utiliza PostgreSQL mediante adaptadores SQLAlchemy, mientras que la autenticación emplea JWT y protección de contraseñas mediante Argon2.

El cumplimiento de cada historia debe respaldarse mediante pruebas automatizadas y verificaciones funcionales de sus criterios de aceptación.

La existencia de un componente o endpoint permite establecer su relación con el requisito, pero no sustituye las evidencias correspondientes a su correcto funcionamiento.
## 5. E3. Modelo de dominio

### 5.1. Descripción general del dominio

El dominio de PULSO se centra en el análisis educativo de factores asociados con enfermedades cardiovasculares mediante un modelo de clasificación supervisada, la interpretación de sus resultados, la simulación de escenarios y la generación de recomendaciones educativas respaldadas por fuentes documentales.

El proceso principal comienza con un perfil cardiovascular que contiene las variables requeridas por el modelo de Machine Learning. A partir de este perfil, el sistema obtiene una predicción y una explicación individual mediante SHAP.

Los resultados se agrupan en un contexto de análisis que puede conservarse temporalmente para permitir posteriores consultas educativas sin necesidad de repetir la inferencia.

Adicionalmente, el sistema permite ejecutar simulaciones mediante modificaciones controladas de determinadas variables del perfil, comparando los resultados originales con los obtenidos en escenarios hipotéticos.

La generación de recomendaciones educativas constituye un proceso independiente de la inferencia predictiva. Este proceso utiliza el contexto del análisis previamente calculado y recupera información de fuentes documentales seleccionadas.

El dominio no presupone la existencia de cuentas de usuario, roles administrativos ni almacenamiento persistente de historiales personales, ya que estas capacidades no forman parte del alcance funcional original definido para PULSO.

### 5.2. Objetos y conceptos principales del dominio

El backend representa los datos y resultados del análisis mediante objetos de dominio inmutables definidos en Python.

Para fines de documentación, se distinguen objetos de valor, estructuras de contexto y contratos de acceso a servicios externos.

#### 5.2.1. Perfil cardiovascular (`CardiovascularProfile`)

Representa el conjunto de variables utilizadas como entrada del modelo predictivo.

Contiene las siguientes diez variables:

| Atributo | Descripción |
|---|---|
| `gender` | Sexo codificado según el conjunto de datos |
| `height` | Altura en centímetros |
| `weight` | Peso en kilogramos |
| `ap_hi` | Presión arterial sistólica |
| `ap_lo` | Presión arterial diastólica |
| `smoke` | Indicador de consumo de tabaco |
| `alco` | Indicador de consumo de alcohol |
| `active` | Indicador de actividad física |
| `age_years` | Edad expresada en años |
| `bmi` | Índice de masa corporal calculado |

El IMC se obtiene utilizando el peso y la altura, por lo que no debe solicitarse como una entrada independiente del usuario.

El perfil constituye la unidad de información sobre la cual se realizan las operaciones de predicción y simulación.

#### 5.2.2. Predicción (`Prediction`)

Representa el resultado producido por el modelo de clasificación cardiovascular.

Contiene cuatro atributos:

- `probability`: probabilidad estimada de pertenecer a la clase positiva `cardio = 1`.
- `classification`: clasificación binaria obtenida mediante el umbral.
- `threshold`: umbral de decisión utilizado.
- `model_version`: versión del modelo responsable de la predicción.

La predicción representa una salida estadística del clasificador y no una evaluación clínica diagnóstica.

#### 5.2.3. Factor explicativo (`ShapFactor`)

Representa la contribución de una variable a la salida del modelo mediante SHAP.

Contiene:

- `feature`: variable analizada.
- `value`: valor de la variable.
- `shap_value`: contribución SHAP calculada.
- `direction`: dirección de la contribución, expresada como `increase` o `decrease`.

Los factores explicativos describen el comportamiento matemático del modelo y no establecen relaciones causales clínicas.

#### 5.2.4. Explicación (`Explanation`)

Agrupa los factores explicativos más relevantes de una predicción individual mediante la colección `top_factors`.

Cada elemento de la colección corresponde a un objeto `ShapFactor`.

#### 5.2.5. Contexto de análisis (`AnalysisContext`)

Representa la información necesaria para reutilizar los resultados de un análisis previamente ejecutado.

Agrupa tres elementos:

- `profile`: perfil cardiovascular utilizado.
- `prediction`: resultado del modelo.
- `explanation`: explicación de los factores mediante SHAP.

El contexto puede almacenarse temporalmente mediante el repositorio de análisis.

Este almacenamiento no equivale a un historial persistente de usuario. Su finalidad es permitir que otras funcionalidades, especialmente el RAG, reutilicen la información obtenida sin ejecutar nuevamente el modelo predictivo.

#### 5.2.6. Cambios de escenario (`ScenarioChanges`)

Representa las modificaciones permitidas durante una simulación.

Las variables contempladas son:

- Peso (`weight`).
- Presión sistólica (`ap_hi`).
- Presión diastólica (`ap_lo`).
- Consumo de tabaco (`smoke`).
- Consumo de alcohol (`alco`).
- Actividad física (`active`).

Los atributos son opcionales porque una simulación puede modificar solo una parte de las variables permitidas.

#### 5.2.7. Resultado de escenario (`ScenarioResult`)

Representa el resultado predictivo de un escenario determinado mediante:

- `probability`.
- `classification`.

#### 5.2.8. Comparación de simulación (`SimulationOutcome`)

Agrupa los resultados necesarios para comparar el escenario original y el escenario hipotético.

Contiene:

- `original`: resultado del escenario de referencia.
- `simulated`: resultado del escenario modificado.
- `probability_difference`: diferencia entre ambas probabilidades.
- `model_version`: versión del modelo utilizado.
- `threshold`: umbral aplicado.
- `applied_changes`: modificaciones consideradas en la simulación.

Esta estructura permite comparar matemáticamente las respuestas del clasificador.

#### 5.2.9. Fuente documental (`DocumentSource`)

Representa una referencia documental recuperada por el sistema RAG.

Contiene el identificador de la fuente, su descripción, la puntuación de recuperación y el intervalo de líneas asociado mediante el objeto `SourceLines`.

#### 5.2.10. Recomendación educativa (`Recommendation`)

Representa una recomendación fundamentada en fuentes documentales.

Contiene:

- `factor`: factor al que se relaciona la recomendación.
- `recommendation`: contenido educativo.
- `source_ids`: identificadores de las fuentes utilizadas.
- `sources`: referencias documentales correspondientes.

#### 5.2.11. Informe educativo (`RecommendationReport`)

Representa la respuesta estructurada del sistema RAG.

Contiene un resumen, consideraciones adicionales, una nota informativa, un indicador de información insuficiente y una colección de recomendaciones educativas.

Su finalidad es ofrecer información respaldada documentalmente, sin modificar los resultados generados por el clasificador.

### 5.2.12. Usuario (`User`) — Propuesto

Representa una persona registrada en PULSO que puede autenticarse y acceder a las funcionalidades asociadas con su cuenta.

Sus atributos conceptuales son:

| Atributo | Descripción |
|---|---|
| `id` | Identificador único del usuario |
| `name` | Nombre del usuario |
| `email` | Correo electrónico |
| `password_hash` | Representación protegida de la contraseña |
| `is_active` | Estado de la cuenta |
| `created_at` | Fecha de creación |
| `updated_at` | Fecha de última actualización |

La entidad permitiría identificar usuarios registrados y relacionarlos con funcionalidades que requieran autenticación.

### 5.2.13. Rol (`Role`) — Propuesto

Representa un conjunto de permisos asignables a los usuarios de la plataforma.

Sus atributos conceptuales son:

| Atributo | Descripción |
|---|---|
| `id` | Identificador del rol |
| `name` | Nombre del rol |
| `description` | Descripción de sus responsabilidades |

Se podrían contemplar dos roles iniciales:

- **Usuario registrado:** persona que accede a las funcionalidades educativas y predictivas.
- **Administrador:** responsable de operaciones de administración autorizadas.

La relación entre usuarios y roles podría modelarse mediante una entidad intermedia `UserRole`, permitiendo que un usuario tenga uno o varios roles cuando el diseño de autorización así lo requiera.

La implementación de un sistema de roles no implica que deban incorporarse automáticamente nuevas funcionalidades administrativas.

### 5.2.14. Consentimiento (`Consent`) — Propuesto

Representa la decisión del usuario respecto al tratamiento de sus datos personales, cuando este resulte aplicable.

Sus atributos conceptuales son:

| Atributo | Descripción |
|---|---|
| `id` | Identificador del registro |
| `user_id` | Usuario asociado |
| `consent_type` | Tipo de consentimiento |
| `accepted` | Estado de aceptación |
| `policy_version` | Versión de la política presentada |
| `recorded_at` | Fecha y hora del registro |

Su finalidad sería documentar el consentimiento cuando corresponda, de acuerdo con las obligaciones de protección de datos personales aplicables.

### 5.2.15. Sesión de autenticación (`AuthSession`) — Propuesta

Representa una sesión autenticada y, si la estrategia de seguridad lo requiere, los datos necesarios para gestionar su renovación o revocación.

Podría incluir:

- `id`: identificador de sesión.
- `user_id`: usuario asociado.
- `created_at`: fecha de creación.
- `expires_at`: fecha de expiración.
- `revoked_at`: fecha de revocación, cuando corresponda.

La representación definitiva dependerá del mecanismo de autenticación elegido. No se presupone que los tokens de acceso deban almacenarse directamente en una base de datos.

### 5.2.16. Historial de análisis (`AnalysisRecord`) — Propuesto

Representa un análisis que podría conservarse de manera persistente y asociarse a un usuario registrado.

Sus atributos conceptuales serían:

| Atributo | Descripción |
|---|---|
| `id` | Identificador único del análisis |
| `user_id` | Identificador del usuario asociado |
| `created_at` | Fecha de ejecución |
| `model_version` | Versión del modelo |
| `probability` | Probabilidad estimada |
| `classification` | Clasificación obtenida |
| `threshold` | Umbral utilizado |

El almacenamiento del perfil cardiovascular completo, explicaciones SHAP u otros resultados requeriría una decisión adicional sobre necesidad, retención y protección de datos.

Esta entidad se diferencia de `AnalysisContext`, que permite reutilizar temporalmente un resultado sin establecer un historial permanente.

### 5.2.17. Relaciones del módulo de usuarios

Si se implementa este módulo, las relaciones propuestas serían:

1. Un `User` podría tener uno o varios `Role` mediante `UserRole`.
2. Un `User` podría registrar múltiples `Consent` a lo largo del tiempo.
3. Un `User` podría mantener varias `AuthSession`, dependiendo del mecanismo de autenticación.
4. Un `User` podría tener múltiples `AnalysisRecord`.
5. Cada `AnalysisRecord` pertenecería a un usuario y conservaría la referencia a la versión del modelo con la que se generó.

Estas relaciones son conceptuales y no deben interpretarse como evidencia de la existencia de tablas, migraciones o repositorios implementados.

### 5.3. Reglas de negocio adicionales del módulo de usuarios

**RN-13. Identificación de usuarios**

Si se implementa el registro de cuentas, cada usuario deberá contar con un identificador único y con mecanismos que impidan duplicidades de correo electrónico.

**RN-14. Protección de credenciales**

Las contraseñas deberán almacenarse mediante algoritmos seguros de hashing y no conservarse en texto plano.

**RN-15. Autorización por roles**

Las operaciones que requieran privilegios específicos deberán comprobar los permisos correspondientes antes de ejecutarse.

**RN-16. Registro de consentimiento**

Cuando una operación requiera consentimiento, el sistema deberá permitir registrar su otorgamiento y aplicar las reglas de tratamiento de datos correspondientes.

**RN-17. Acceso a información personal**

Los análisis persistentes de un usuario solamente podrán ser consultados o modificados por sujetos autorizados.

**RN-18. Eliminación de información personal**

En caso de incorporar cuentas e historiales, deberán definirse mecanismos para gestionar las solicitudes de eliminación de datos conforme a los requisitos legales aplicables.

### 5.5. Casos de uso adicionales propuestos

| Caso de uso | Descripción |
|---|---|
| `RegisterUser` | Registrar una nueva cuenta |
| `AuthenticateUser` | Validar credenciales e iniciar sesión |
| `RefreshSession` | Renovar una sesión cuando el mecanismo lo permita |
| `LogoutUser` | Finalizar o revocar la sesión según la arquitectura |
| `GetUserProfile` | Consultar los datos autorizados de una cuenta |
| `UpdateUserProfile` | Actualizar información de la cuenta |
| `AssignUserRole` | Asignar permisos mediante roles |
| `RegisterConsent` | Registrar el consentimiento del usuario |
| `RevokeConsent` | Gestionar la revocación cuando corresponda |
| `SaveAnalysis` | Guardar un análisis asociado a un usuario |
| `GetAnalysisHistory` | Consultar el historial de análisis |
| `DeleteAnalysis` | Eliminar un análisis almacenado |
| `DeleteUserAccount` | Gestionar la eliminación de una cuenta y los datos correspondientes |

Estos casos de uso representan funcionalidades propuestas. Su inclusión definitiva dependerá de la decisión sobre el alcance del módulo de usuarios.

### Nota sobre el alcance del módulo de usuarios

**Estado: pendiente de decisión. Posible eliminación del alcance final.**

El módulo de usuarios se conserva provisionalmente en el modelo de dominio para documentar una posible ampliación de PULSO que contemple registro, autenticación, autorización por roles, consentimiento y persistencia de historiales personales.

Actualmente, estas capacidades no forman parte del alcance funcional original confirmado del proyecto y no deben presentarse como funcionalidades implementadas sin evidencia en el código.

Su permanencia está sujeta a la definición final de requisitos acordada con el profesor. En caso de determinarse que no son necesarias, se eliminarán del modelo de dominio las entidades, relaciones, reglas y casos de uso exclusivamente asociados a este módulo.

Esta decisión deberá reflejarse también en el backlog, el modelo de datos, la arquitectura y la documentación de funcionalidad para mantener la coherencia entre los entregables.

### 5.3. Reglas de negocio

Las reglas de negocio establecen las condiciones que deben respetarse durante el análisis y la interpretación de resultados.

**RN-01. Validación de variables**

Un perfil cardiovascular debe cumplir los rangos, tipos y relaciones de consistencia definidos por el contrato de entrada antes de ser procesado por el modelo.

**RN-02. Coherencia del IMC**

El índice de masa corporal debe calcularse a partir del peso y la altura utilizando la expresión:

\[
IMC = \frac{peso\;(kg)}{altura\;(m)^2}
\]

Si una simulación modifica el peso, el IMC correspondiente debe recalcularse.

**RN-03. Variables del modelo**

El modelo PULSO v1 utiliza diez variables de entrada definidas en `CardiovascularProfile`. Las entradas deben conservar las características y la estructura requeridas por el modelo entrenado.

**RN-04. Interpretación de la probabilidad**

La probabilidad producida por el modelo representa la estimación de pertenencia a `cardio = 1`, según el conjunto de datos de entrenamiento.

No debe presentarse como una probabilidad clínicamente validada de sufrir un evento cardiovascular futuro.

**RN-05. Clasificación binaria**

La clasificación se determina mediante el umbral de decisión asociado a la versión del modelo.

Para PULSO v1, el umbral seleccionado es 0.38.

**RN-06. Explicabilidad**

Las explicaciones SHAP describen las contribuciones de las variables a una salida individual del modelo.

No deben presentarse como evidencia de causalidad clínica.

**RN-07. Simulación de escenarios**

Las simulaciones solo pueden modificar variables autorizadas y deben conservar la coherencia de los datos del perfil.

Sus resultados representan comparaciones entre salidas del modelo, no efectos clínicos demostrados de intervenciones.

**RN-08. Reutilización del análisis**

La solicitud de recomendaciones educativas debe utilizar el contexto del análisis previamente calculado, evitando ejecutar nuevamente la inferencia únicamente para obtener información educativa.

**RN-09. Trazabilidad documental**

Las recomendaciones educativas deben asociarse con fuentes recuperadas del corpus documental y conservar la información necesaria para identificar su procedencia.

**RN-10. Información insuficiente**

Cuando no exista respaldo documental suficiente, el sistema debe comunicar esa limitación y evitar generar recomendaciones presentadas como fundamentadas sin evidencia.

**RN-11. Limitaciones clínicas**

Las respuestas educativas no deben constituir diagnósticos médicos ni prescribir modificaciones de medicamentos o tratamientos.

**RN-12. Almacenamiento temporal**

El contexto de un análisis puede conservarse temporalmente para dar continuidad a las funcionalidades de la plataforma.

El almacenamiento temporal no debe describirse como un historial personal permanente.

### 5.4. Glosario del dominio

| Término | Definición |
|---|---|
| Perfil cardiovascular | Conjunto de variables utilizadas para ejecutar el análisis |
| Variable predictora | Atributo empleado como entrada del modelo de Machine Learning |
| IMC | Índice de masa corporal calculado a partir del peso y la altura |
| Clasificador | Modelo que asigna probabilidades a las clases definidas en los datos |
| Probabilidad estimada | Salida del modelo correspondiente a la clase positiva |
| Umbral de decisión | Valor utilizado para transformar la probabilidad en una clasificación |
| Clasificación binaria | Asignación a una de dos clases posibles |
| SHAP | Técnica de atribución utilizada para explicar predicciones individuales |
| Factor explicativo | Variable con una contribución identificada mediante SHAP |
| Contexto de análisis | Agrupación del perfil, la predicción y la explicación previamente calculados |
| Escenario hipotético | Conjunto de modificaciones permitidas sobre un perfil |
| Simulación | Ejecución del modelo con variables modificadas para comparar resultados |
| RAG | Técnica que combina recuperación documental y generación de respuestas |
| Fuente documental | Referencia recuperada que permite respaldar contenido educativo |
| Recomendación educativa | Información orientativa asociada con factores y fuentes |
| Modelo versionado | Modelo identificado mediante una versión determinada |
| Almacenamiento temporal | Conservación transitoria de información necesaria para continuar un flujo |

### 5.5. Casos de uso del sistema

Los casos de uso principales se relacionan con las capacidades funcionales definidas para PULSO.

| Caso de uso | Descripción |
|---|---|
| ValidarPerfil | Comprobar que las variables cumplen los requisitos de entrada del modelo |
| AnalizarPerfil | Obtener una predicción y una explicación SHAP a partir de un perfil cardiovascular |
| ConsultarExplicacion | Presentar al usuario la explicación obtenida durante el análisis |
| SimularEscenario | Ejecutar una simulación con modificaciones permitidas y comparar resultados |
| SolicitarInformacionEducativa | Utilizar el contexto de un análisis previo para solicitar recomendaciones mediante RAG |
| ConsultarFuentesEducativas | Presentar las referencias documentales asociadas con las recomendaciones |

Estos nombres representan acciones funcionales documentadas. No todos corresponden necesariamente a clases independientes del backend.

En la implementación revisada, `AnalyzeProfile` constituye un caso de uso explícito de la capa de aplicación. Las demás acciones deben relacionarse con los casos de uso, adaptadores y componentes existentes, evitando presentar como clases implementadas aquellas que solo representan operaciones del sistema.

El mantenimiento del corpus documental, la supervisión de servicios y las verificaciones de infraestructura se consideran procesos técnicos de soporte, no entidades centrales del dominio cardiovascular.

### 5.6. Relaciones entre los objetos del dominio

Las principales relaciones identificadas son:

1. `AnalysisContext` agrupa un `CardiovascularProfile`, una `Prediction` y una `Explanation`.
2. `Explanation` contiene una colección de objetos `ShapFactor`.
3. `ScenarioChanges` expresa las modificaciones permitidas sobre el perfil de referencia.
4. `SimulationOutcome` contiene dos objetos `ScenarioResult`, correspondientes al escenario original y al simulado.
5. `RecommendationReport` agrupa una colección de objetos `Recommendation`.
6. Cada `Recommendation` puede referenciar múltiples objetos `DocumentSource`.
7. Cada `DocumentSource` contiene un objeto `SourceLines` que identifica un intervalo documental.

Estas relaciones constituyen la base del diagrama de clases del dominio.

### 5.7. Independencia del dominio

Los objetos del dominio se encuentran definidos mediante estructuras de Python que no requieren directamente FastAPI, Pydantic, SQLAlchemy ni la implementación de los servicios externos.

El dominio también define contratos o puertos que permiten desacoplar los casos de uso de sus implementaciones concretas.

Los principales puertos identificados son:

- `CardiovascularModel`: operaciones de predicción, explicación y simulación.
- `RecommendationGenerator`: generación de información educativa a partir del contexto del análisis.
- `AnalysisRepository`: almacenamiento y recuperación temporal del contexto de análisis.

Las implementaciones concretas de estos contratos pertenecen a la infraestructura, mientras que los casos de uso coordinan las operaciones de la aplicación.

Esta organización permite conservar las reglas y estructuras principales del dominio separadas de las tecnologías empleadas para exponer APIs, ejecutar modelos y recuperar información documental.

**Diagrama de dominio:** [Insertar aquí la figura exportada del diagrama de clases, con título y leyenda, al preparar la versión PDF.]

## 6. E4. Modelo de datos

### 6.1. Descripción general

El modelo de datos de PULSO responde a las necesidades de almacenamiento y recuperación de información relacionadas con las funcionalidades de predicción cardiovascular, explicabilidad, simulación y generación de recomendaciones educativas.

La arquitectura distingue entre información persistente, utilizada principalmente por el sistema RAG, e información temporal necesaria para coordinar las solicitudes de análisis.

Adicionalmente, se contempla un modelo de datos para la gestión de usuarios, autenticación, roles, consentimientos e historiales personales. Este módulo se conserva como una propuesta arquitectónica pendiente de decisión respecto a su incorporación definitiva al proyecto.

Por tanto, el modelo se organiza en tres categorías:

1. **Persistencia documental del sistema RAG:** almacenamiento vectorial de fragmentos documentales y metadatos en Supabase, basado en PostgreSQL y pgvector.
2. **Almacenamiento temporal de análisis:** conservación transitoria de los datos y resultados necesarios para continuar las operaciones de la plataforma.
3. **Persistencia de usuarios e historiales:** modelo relacional propuesto para gestionar cuentas, autorizaciones y datos asociados a usuarios registrados.

Esta separación permite representar la arquitectura de datos sin atribuir al sistema funcionalidades que no forman parte de su implementación confirmada.

### 6.2. Persistencia documental del sistema RAG

PULSO utiliza Supabase, basado en PostgreSQL y la extensión pgvector, como infraestructura de almacenamiento y recuperación semántica para el corpus documental del sistema RAG.

Durante la reconstrucción del corpus se implementó una tabla aislada de pruebas denominada `public.documents_pulso_test`, conservando la tabla `public.documents` correspondiente a una versión anterior del sistema.

#### 6.2.1. Estructura de almacenamiento

La tabla `public.documents_pulso_test` contiene los siguientes campos:

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | `BIGINT` | Identificador del fragmento almacenado |
| `content` | `TEXT` | Contenido textual del fragmento |
| `metadata` | `JSONB` | Información bibliográfica, documental y estructural |
| `embedding` | `VECTOR(3072)` | Representación vectorial del contenido |

El modelo utilizado para generar las representaciones vectoriales es `models/gemini-embedding-001`, con una dimensionalidad de 3072.

La información de los documentos se organiza mediante metadatos como `document_id`, `source_file`, `source`, `source_url`, `author`, `chunk_index`, `section_path` y `chunking_version`.

Estos metadatos permiten identificar la procedencia de los fragmentos y mantener su trazabilidad.

#### 6.2.2. Preparación y fragmentación documental

El corpus se compone de 15 documentos seleccionados y normalizados, relacionados con factores cardiovasculares y recomendaciones educativas.

Los documentos se procesaron mediante una estrategia de fragmentación estructural basada en Markdown, identificada como `markdown_structural_v1_3`.

Esta estrategia busca conservar la coherencia de títulos, secciones y párrafos.

Se estableció un tamaño objetivo de 650 caracteres por fragmento y un umbral de advertencia de 1200 caracteres. El tamaño objetivo no constituye un límite estricto.

El proceso produjo 160 fragmentos documentales.

#### 6.2.3. Vectorización e ingesta

La ingesta documental se realizó mediante un flujo de n8n que recupera los archivos normalizados, prepara los fragmentos y sus metadatos, genera embeddings mediante Google Gemini e inserta los registros en Supabase.

Los 160 fragmentos generaron embeddings de 3072 dimensiones y fueron almacenados en la tabla de pruebas.

Las auditorías estructurales reportadas confirmaron:

- 15 documentos distintos.
- 160 registros almacenados.
- 160 embeddings no nulos con dimensionalidad correcta.
- Ausencia de contenido vacío.
- Ausencia de faltantes en los metadatos obligatorios evaluados.
- Secuencias de fragmentos completas y sin duplicaciones de índices por documento.

#### 6.2.4. Recuperación semántica

La recuperación documental se realiza mediante la función `public.match_documents_pulso_test`, que permite efectuar búsquedas por similitud coseno y aplicar filtros opcionales mediante metadatos JSONB.

Las pruebas documentadas incluyeron nueve consultas relacionadas con presión arterial, actividad física, tabaquismo, alcohol, envejecimiento y diferencias cardiovasculares asociadas con sexo y género.

Los resultados mostraron recuperación temática y trazabilidad documental en los casos evaluados.

Estas pruebas respaldan el funcionamiento básico del mecanismo de recuperación, pero no constituyen una validación clínica de las recomendaciones generadas ni una evaluación comparativa exhaustiva frente a versiones anteriores.

#### 6.2.5. Estado de implementación y validación

El sistema RAG de PULSO utiliza actualmente en producción la tabla `public.documents_pulso_test`, alojada en Supabase mediante PostgreSQL y la extensión pgvector.

Esta tabla almacena el corpus documental normalizado, compuesto por 15 documentos y 160 fragmentos vectorizados mediante el modelo `models/gemini-embedding-001`, con representaciones de 3072 dimensiones.

La recuperación semántica se realiza mediante la función `public.match_documents_pulso_test`, que permite efectuar búsquedas por similitud coseno y aplicar filtros opcionales sobre los metadatos documentales.

La tabla fue creada originalmente para realizar pruebas de reconstrucción del corpus. Sin embargo, tras las verificaciones técnicas realizadas, fue adoptada como fuente documental de la versión productiva del sistema RAG, conservando su denominación original.

Las auditorías estructurales documentadas verificaron la integridad de los registros, la disponibilidad de los embeddings y la presencia de los metadatos obligatorios. Estas verificaciones respaldan la correcta ingesta del corpus, aunque no constituyen por sí solas una validación clínica de las recomendaciones generadas.

El almacenamiento vectorial se utiliza exclusivamente para organizar y recuperar contenido educativo. No constituye una base de datos de cuentas de usuarios ni un repositorio persistente de historiales personales.

### 6.3. Almacenamiento temporal de análisis

PULSO utiliza un mecanismo de almacenamiento temporal para conservar el contexto necesario durante determinadas operaciones.

El contexto agrupa:

- Perfil cardiovascular utilizado en la predicción.
- Probabilidad y clasificación obtenidas.
- Umbral y versión del modelo.
- Explicación de los factores mediante SHAP.

La finalidad de este mecanismo es permitir que el backend reutilice los resultados previamente calculados al solicitar información educativa mediante RAG.

De esta manera se evita ejecutar nuevamente la inferencia exclusivamente para generar recomendaciones.

El almacenamiento temporal no equivale a una base de datos persistente de historiales.

En consecuencia, no requiere representar cada contexto como una tabla relacional permanente dentro del modelo entidad-relación.

Su implementación actual utiliza memoria del proceso, por lo que la información está sujeta a las condiciones de expiración y disponibilidad establecidas por el repositorio temporal.

Este mecanismo tampoco debe presentarse como una solución de persistencia compartida entre múltiples instancias del backend.

### 6.4. Modelo relacional propuesto para usuarios

**Estado: propuesto y sujeto a decisión de alcance.**

Se conserva un modelo relacional destinado a permitir la incorporación futura de registro, autenticación, autorización, consentimiento y almacenamiento de historiales.

La existencia de este diseño no implica que todas sus tablas, migraciones o funcionalidades estén implementadas.

#### 6.4.1. Tabla `users`

Representa las cuentas registradas en la plataforma.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `id` | UUID | PK |
| `name` | VARCHAR(150) | NOT NULL |
| `email` | VARCHAR(254) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

La contraseña no debe almacenarse en texto plano. El campo `password_hash` conservaría el resultado de un algoritmo apropiado para el almacenamiento seguro de contraseñas.

#### 6.4.2. Tabla `roles`

Representa los roles utilizados para controlar las operaciones autorizadas.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `id` | SMALLSERIAL | PK |
| `name` | VARCHAR(50) | NOT NULL, UNIQUE |
| `description` | TEXT | NULL |

#### 6.4.3. Tabla `user_roles`

Representa la asociación entre usuarios y roles.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `user_id` | UUID | PK, FK → users |
| `role_id` | SMALLINT | PK, FK → roles |
| `assigned_at` | TIMESTAMPTZ | NOT NULL |

La clave primaria compuesta por `user_id` y `role_id` evita asignar repetidamente el mismo rol a una cuenta.

#### 6.4.4. Tabla `privacy_consents`

Conserva registros de consentimiento asociados con los usuarios.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users, NOT NULL |
| `consent_type` | VARCHAR(50) | NOT NULL |
| `accepted` | BOOLEAN | NOT NULL |
| `policy_version` | VARCHAR(30) | NOT NULL |
| `recorded_at` | TIMESTAMPTZ | NOT NULL |
| `withdrawn_at` | TIMESTAMPTZ | NULL |

Su finalidad es mantener evidencia de las decisiones del usuario respecto al tratamiento de datos cuando resulte aplicable.

#### 6.4.5. Tabla `auth_sessions`

Representa información de sesiones autenticadas cuando se requiera almacenamiento para renovación o revocación.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users, NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `expires_at` | TIMESTAMPTZ | NOT NULL |
| `revoked_at` | TIMESTAMPTZ | NULL |

Esta tabla es opcional y dependerá de la estrategia definitiva de autenticación. No implica almacenar tokens de acceso en texto plano.

#### 6.4.6. Tabla `analyses`

Representa los resultados de análisis que eventualmente podrían conservarse de forma persistente.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users, NOT NULL |
| `model_version` | VARCHAR(50) | NOT NULL |
| `probability` | NUMERIC(8,7) | NOT NULL |
| `classification` | SMALLINT | NOT NULL |
| `threshold` | NUMERIC(5,4) | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL |

La tabla propuesta no incluye automáticamente el perfil cardiovascular completo.

La persistencia del perfil, de las explicaciones SHAP o de otros datos asociados requeriría una decisión adicional sobre su necesidad, finalidad, consentimiento y conservación.

#### 6.4.7. Tabla `simulations`

Representa escenarios hipotéticos asociados con análisis almacenados.

| Columna | Tipo PostgreSQL | Restricción |
|---|---|---|
| `id` | UUID | PK |
| `analysis_id` | UUID | FK → analyses, NOT NULL |
| `changes` | JSONB | NOT NULL |
| `probability` | NUMERIC(8,7) | NOT NULL |
| `classification` | SMALLINT | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL |

El campo `changes` conservaría únicamente las modificaciones necesarias para reconstruir el escenario, sujetas a las políticas de tratamiento y retención correspondientes.

### 6.5. Relaciones del modelo relacional propuesto

Las relaciones principales serían:

| Entidad de origen | Entidad destino | Cardinalidad |
|---|---|---|
| `users` | `user_roles` | 1:N |
| `roles` | `user_roles` | 1:N |
| `users` | `privacy_consents` | 1:N |
| `users` | `auth_sessions` | 1:N |
| `users` | `analyses` | 1:N |
| `analyses` | `simulations` | 1:N |

La relación entre usuarios y roles es muchos a muchos, implementada mediante `user_roles`.

Este modelo constituye una propuesta lógica. Las cardinalidades deberán conservarse en el diagrama entidad-relación correspondiente si el módulo se mantiene dentro del alcance final.

### 6.6. Índices y optimización de consultas

Los índices se definen en función de las operaciones que las aplicaciones necesitan ejecutar.

Para el módulo de usuarios se proponen los siguientes:

| Tabla | Índice propuesto | Justificación |
|---|---|---|
| `users` | UNIQUE sobre `email` | Evitar duplicidades y localizar cuentas durante autenticación |
| `user_roles` | Índice sobre `role_id` | Consultar usuarios asociados con un rol |
| `privacy_consents` | `(user_id, recorded_at DESC)` | Consultar consentimientos por usuario y fecha |
| `auth_sessions` | `(user_id, expires_at)` | Localizar sesiones de un usuario |
| `analyses` | `(user_id, created_at DESC)` | Recuperar historiales ordenados cronológicamente |
| `simulations` | `(analysis_id, created_at DESC)` | Consultar simulaciones asociadas con un análisis |

Las claves primarias y las restricciones UNIQUE generan los índices correspondientes en PostgreSQL.

Los índices adicionales deben justificarse mediante los patrones reales de consulta y no incorporarse indiscriminadamente.

En el almacenamiento vectorial, la selección del índice de similitud y sus parámetros debe corresponder al tipo y dimensión efectiva de los embeddings, así como al volumen y las necesidades de consulta del corpus.

### 6.7. Tratamiento y minimización de datos

PULSO procesa variables relacionadas con características físicas, presión arterial y hábitos de vida.

Aunque estas variables son necesarias para ejecutar el modelo, su utilización no implica que deban almacenarse permanentemente.

En el diseño actual se prioriza el procesamiento de los datos proporcionados para producir un resultado y su reutilización temporal cuando es necesario continuar el flujo educativo.

Si se implementa el módulo de usuarios, se deberán establecer controles adecuados para:

1. Proteger las credenciales y la información identificable.
2. Restringir el acceso a registros personales mediante autenticación y autorización.
3. Registrar y gestionar el consentimiento cuando corresponda.
4. Definir periodos de conservación y eliminación.
5. Evitar almacenar datos relacionados con la salud que no sean necesarios para una finalidad justificada.
6. Prevenir la exposición de información sensible en registros de aplicación y respuestas de error.

Estas medidas deberán ajustarse a los requisitos aplicables de protección de datos personales, incluida la Ley 1581 de 2012 en Colombia.

### 6.8. Diagramas de datos

El modelo de datos debe representarse mediante diagramas que diferencien las estructuras persistentes existentes de las propuestas.

**Figura 6.1. Esquema de persistencia documental del RAG.**

Representa el almacenamiento vectorial en Supabase, la organización de fragmentos y metadatos y su utilización por el proceso de recuperación documental.

**Figura 6.2. Diagrama entidad-relación del módulo de usuarios (propuesto).**

Representa las tablas `users`, `roles`, `user_roles`, `privacy_consents`, `auth_sessions`, `analyses` y `simulations`, incluyendo claves primarias, claves foráneas, tipos y cardinalidades.

El diagrama del módulo de usuarios debe identificarse expresamente como diseño propuesto y no como esquema implementado, salvo que su integración se confirme mediante las migraciones correspondientes.

### 6.9. Nota sobre la permanencia del módulo de usuarios

**Estado del módulo: pendiente de decisión. Posible eliminación del alcance final.**

El modelo relacional de usuarios se conserva provisionalmente para documentar las estructuras necesarias en caso de incorporar autenticación, roles, consentimiento e historiales.

Su presencia en este informe no representa un compromiso definitivo de implementación ni demuestra la existencia de todas las tablas descritas.

La permanencia del módulo dependerá de los requisitos finales acordados con el profesor y de las necesidades funcionales aprobadas para PULSO.

En caso de decidirse su exclusión, se retirarán las tablas y relaciones exclusivamente asociadas con la gestión de usuarios, manteniendo la documentación de la persistencia documental del RAG y del almacenamiento temporal de análisis.

La decisión también deberá reflejarse en E2, E3, E5, E6 y E7 para garantizar la coherencia del informe.

**Diagrama entidad-relación:** [Insertar aquí la figura exportada con tipos PostgreSQL, claves y cardinalidades antes de generar el PDF.]

## 7. E5. Arquitectura del sistema mediante el modelo C4

### 7.1. Descripción general de la arquitectura

PULSO es una plataforma web educativa de prevención cardiovascular cuya arquitectura integra una interfaz de usuario, un backend de coordinación, un servicio independiente de Machine Learning y un sistema de generación de recomendaciones educativas mediante recuperación aumentada por generación (*Retrieval-Augmented Generation*, RAG).

La arquitectura está diseñada para separar las responsabilidades de presentación, coordinación de operaciones, inferencia predictiva y recuperación documental, facilitando el mantenimiento, las pruebas automatizadas y la evolución de los componentes.

El sistema utiliza las siguientes tecnologías:

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Frontend | React, TypeScript y Vite | Captura de variables, presentación de resultados, explicaciones y simulaciones |
| Backend | Python y FastAPI | Coordinación de casos de uso y comunicación con servicios |
| ML Service | Python, FastAPI, XGBoost y SHAP | Predicción, explicabilidad y simulación |
| Sistema RAG | n8n | Orquestación de recomendaciones educativas |
| Base vectorial | Supabase, PostgreSQL y pgvector | Almacenamiento y recuperación del corpus documental |
| Proveedor de IA | Google Gemini API | Servicios de embeddings y generación de contenido |
| Proxy inverso | NGINX | Punto de entrada y enrutamiento HTTP |
| Contenerización | Docker y Docker Compose | Ejecución coordinada de los servicios principales |

El backend está organizado siguiendo una adaptación de **Clean Architecture**, en la que las reglas del dominio y los casos de uso se mantienen desacoplados de las implementaciones tecnológicas.

Para documentar la solución se utiliza el modelo C4, que representa progresivamente el contexto general del sistema, sus contenedores de ejecución y los componentes internos del backend.

### 7.2. C4 Nivel 1 — Contexto del sistema

El diagrama de contexto presenta PULSO como una única unidad de software e identifica los actores que interactúan con la plataforma y sus dependencias externas.

#### 7.2.1. Actores

**Persona usuaria:** utiliza la plataforma para introducir factores cardiovasculares, obtener una estimación generada por el modelo predictivo, consultar explicaciones mediante SHAP, simular escenarios y acceder a recomendaciones educativas.

**Responsable técnico:** administra y supervisa la infraestructura de PULSO, verifica el funcionamiento de los servicios y realiza operaciones de mantenimiento sobre el corpus documental del sistema RAG.

Este actor no representa necesariamente un usuario autenticado dentro de la aplicación, sino una responsabilidad técnica de operación y mantenimiento.

#### 7.2.2. Sistema principal

**PULSO:** plataforma web educativa de orientación cardiovascular que integra predicción mediante Machine Learning, explicabilidad, simulación y recuperación documental para ofrecer información educativa.

Su finalidad es facilitar la comprensión de los factores considerados por el modelo y de sus resultados, sin constituir una herramienta de diagnóstico médico.

#### 7.2.3. Sistema externo

**Google Gemini API:** proveedor externo de servicios de inteligencia artificial utilizados para generar representaciones vectoriales durante la ingesta documental y para apoyar la generación de contenido educativo mediante el sistema RAG.

Los servicios de n8n y Supabase se consideran parte de la solución PULSO desde el punto de vista lógico, aunque se encuentren alojados fuera del stack local de Docker Compose.

Por esta razón, sus responsabilidades internas se detallan en el diagrama de contenedores del nivel 2.

#### 7.2.4. Relaciones

| Origen | Destino | Interacción |
|---|---|---|
| Persona usuaria | PULSO | Ingresa datos, consulta predicciones, simula escenarios y recibe información educativa |
| Responsable técnico | PULSO | Administra, verifica y mantiene los servicios y recursos documentales |
| PULSO | Google Gemini API | Utiliza servicios externos de IA para procesamiento documental y generación educativa mediante HTTPS/API |

#### 7.2.5. Diagrama de contexto

**Figura 7.1. Diagrama C4 de nivel 1 — Contexto del sistema PULSO.**

**[INSERTAR AQUÍ LA IMAGEN `C4_N1_Contexto.png`]**

*Figura 7.1. Representación de los actores que interactúan con PULSO y de su relación con el proveedor externo de servicios de inteligencia artificial.*

El diagrama permite identificar el propósito general de la plataforma, sus actores y su dependencia externa principal sin introducir detalles internos de implementación.

### 7.3. C4 Nivel 2 — Contenedores del sistema

El segundo nivel del modelo C4 descompone PULSO en sus principales aplicaciones, servicios y almacenes de datos, mostrando sus tecnologías, responsabilidades y relaciones.

En el modelo C4, el término *contenedor* se refiere a una unidad de ejecución o almacenamiento, y no necesariamente a un contenedor Docker.

#### 7.3.1. Proxy inverso NGINX

NGINX funciona como punto de entrada a la plataforma.

Recibe las solicitudes provenientes del navegador y las dirige hacia el servidor del frontend o hacia el backend, según la ruta solicitada.

En la configuración local, el servicio expone el puerto 80 y permite centralizar el acceso a la aplicación.

#### 7.3.2. Frontend web

El frontend está desarrollado con React, TypeScript y Vite.

Es responsable de:

- Presentar el formulario de evaluación cardiovascular.
- Capturar las variables requeridas por el modelo.
- Mostrar la probabilidad y clasificación obtenidas.
- Presentar los principales factores explicativos mediante SHAP.
- Permitir modificaciones de variables para simular escenarios.
- Mostrar recomendaciones educativas y referencias documentales.

La interfaz utiliza una distribución adaptable a diferentes anchos de pantalla. La validación funcional completa en dispositivos móviles constituye una comprobación independiente de esta característica visual.

#### 7.3.3. Backend API

El backend está desarrollado en Python mediante FastAPI y expone una API REST.

Su responsabilidad principal consiste en coordinar las funcionalidades de la plataforma.

Realiza las siguientes operaciones:

- Validación de solicitudes.
- Construcción de objetos del dominio.
- Ejecución de casos de uso.
- Comunicación con ML Service.
- Almacenamiento temporal del contexto de análisis.
- Solicitud de recomendaciones al workflow RAG.
- Coordinación de simulaciones.
- Traducción de errores del dominio a respuestas HTTP.

El backend mantiene separadas las reglas de negocio de las implementaciones concretas de infraestructura.

#### 7.3.4. Servicio de Machine Learning

ML Service es un servicio independiente desarrollado con Python y FastAPI.

Integra el modelo XGBoost de PULSO y la biblioteca SHAP.

Sus funciones principales son:

- Procesar los perfiles cardiovasculares.
- Generar probabilidades y clasificaciones.
- Obtener explicaciones individuales mediante SHAP.
- Ejecutar inferencias sobre escenarios hipotéticos.
- Proporcionar resultados estructurados al backend.

El backend se comunica con ML Service mediante HTTP/JSON.

#### 7.3.5. Sistema RAG

La generación de recomendaciones educativas se implementa mediante workflows de n8n.

El sistema recibe información estructurada proveniente del backend, que incluye los datos del perfil cardiovascular, la predicción y los principales factores explicativos de SHAP.

El workflow coordina la recuperación documental y la generación de contenido educativo fundamentado.

Una decisión importante de la arquitectura es que **el RAG reutiliza la predicción y la explicación previamente calculadas**, sin realizar una nueva inferencia del modelo cardiovascular.

#### 7.3.6. Base vectorial Supabase

El sistema RAG utiliza Supabase, basado en PostgreSQL y pgvector, para almacenar y recuperar información documental.

La configuración productiva utiliza la tabla:

`public.documents_pulso_test`

La recuperación semántica se realiza mediante la función:

`public.match_documents_pulso_test`

El corpus está compuesto por 15 documentos normalizados y 160 fragmentos vectorizados mediante `models/gemini-embedding-001`, con embeddings de 3072 dimensiones.

La denominación de la tabla conserva el sufijo `_test` debido a su origen como entorno de pruebas, aunque actualmente forma parte de la arquitectura operativa de producción.

Supabase se utiliza para persistencia documental y no constituye una base de datos de historiales personales de usuarios.

#### 7.3.7. Almacenamiento temporal

El backend utiliza `InMemoryAnalysisRepository` como implementación del puerto `AnalysisRepository`.

Este mecanismo conserva temporalmente los contextos necesarios para continuar los flujos de análisis y recomendaciones educativas.

Su configuración establece:

- Tiempo de vida de los registros: 900 segundos.
- Capacidad máxima: 100 entradas.
- Almacenamiento local en memoria del proceso.

Este repositorio no es persistente ni compartido entre múltiples procesos del backend.

Por ello, se representa como una responsabilidad interna del backend y no como un contenedor independiente de base de datos.

#### 7.3.8. Comunicación entre contenedores

| Origen | Destino | Protocolo | Propósito |
|---|---|---|---|
| Navegador | NGINX | HTTP en entorno local | Acceso a la aplicación |
| NGINX | Frontend | HTTP | Entrega de archivos HTML, JavaScript y CSS |
| NGINX | Backend | HTTP/JSON | Enrutamiento de solicitudes `/api/*` |
| Backend | ML Service | HTTP/JSON | Predicción, explicación SHAP y simulación |
| Backend | n8n | HTTP/JSON | Solicitud de recomendaciones educativas |
| n8n | Supabase | HTTPS/API | Recuperación documental mediante similitud vectorial |
| n8n | Google Gemini API | HTTPS/JSON | Operaciones de IA utilizadas por el workflow |

La aplicación React se ejecuta en el navegador una vez cargados sus recursos.

Las solicitudes a la API se realizan a través de NGINX, que funciona como proxy inverso.

Los servicios NGINX, frontend, backend y ML Service forman parte del stack local definido mediante Docker Compose.

n8n y Supabase se consideran componentes lógicos de PULSO, aunque su infraestructura de ejecución se encuentre fuera de ese stack.

#### 7.3.9. Diagrama de contenedores

**Figura 7.2. Diagrama C4 de nivel 2 — Contenedores de PULSO.**

**[INSERTAR AQUÍ LA IMAGEN `C4_N2_Contenedores.png`]**

*Figura 7.2. Representación de los servicios principales de PULSO, sus tecnologías y sus comunicaciones. Se diferencian los componentes del stack Docker Compose de los servicios externos de infraestructura utilizados por el RAG.*

El diagrama permite comprender cómo se distribuyen las responsabilidades entre las aplicaciones y servicios que componen la plataforma.

### 7.4. C4 Nivel 3 — Componentes del backend

El tercer nivel del modelo C4 representa la estructura interna del contenedor Backend API.

El backend de PULSO implementa una adaptación de Clean Architecture basada en la separación de responsabilidades y la inversión de dependencias.

Su organización se divide en cuatro capas:

1. Dominio.
2. Aplicación.
3. Infraestructura.
4. Interfaces HTTP.

Las dependencias del código deben respetar la independencia del dominio respecto de las tecnologías externas.

#### 7.4.1. Capa de dominio

**Ubicación:** `backend/app/domain/`

Contiene los objetos centrales, las reglas de negocio, las excepciones y los contratos que utilizan los casos de uso.

Su estructura principal es:

| Archivo | Responsabilidad |
|---|---|
| `entities.py` | Define los objetos de dominio como `CardiovascularProfile`, `Prediction`, `Explanation`, `AnalysisContext`, `RecommendationReport` y `SimulationOutcome` |
| `rules.py` | Contiene reglas de coherencia del perfil y del IMC |
| `errors.py` | Define excepciones propias del dominio |
| `ports.py` | Establece los contratos que deben cumplir los servicios externos y repositorios |

Los puertos principales son:

**`CardiovascularModel`:** abstrae las operaciones de predicción, explicabilidad y simulación.

**`RecommendationGenerator`:** abstrae la generación de recomendaciones educativas.

**`AnalysisRepository`:** abstrae el almacenamiento y la recuperación temporal de contextos de análisis.

El dominio utiliza estructuras de Python y no depende de FastAPI, Pydantic, httpx ni de implementaciones concretas de infraestructura.

#### 7.4.2. Capa de aplicación

**Ubicación:** `backend/app/application/use_cases/`

Contiene los casos de uso responsables de coordinar los procesos principales.

**`AnalyzeProfile`**

Coordina el análisis cardiovascular.

Recibe el perfil, solicita una predicción y una explicación mediante el puerto `CardiovascularModel` y conserva el contexto obtenido a través de `AnalysisRepository`.

Devuelve los resultados y el identificador temporal asociado al análisis.

**`RequestRecommendations`**

Coordina la generación de información educativa.

Recupera el contexto previamente almacenado mediante `AnalysisRepository` y solicita las recomendaciones utilizando `RecommendationGenerator`.

Este caso de uso evita volver a ejecutar el modelo predictivo únicamente para obtener información educativa.

**`SimulateScenario`**

Coordina la simulación de escenarios.

Procesa las modificaciones permitidas y utiliza `CardiovascularModel` para obtener los resultados comparativos del escenario original y el modificado.

Los casos de uso dependen de contratos definidos en el dominio, sin conocer los detalles concretos de comunicación con ML Service o n8n.

#### 7.4.3. Capa de infraestructura

**Ubicación:** `backend/app/infrastructure/`

Contiene las implementaciones concretas de los contratos del dominio.

| Componente | Puerto implementado | Responsabilidad |
|---|---|---|
| `MLServiceClient` | `CardiovascularModel` | Comunicación HTTP con ML Service |
| `N8nRecommendationClient` | `RecommendationGenerator` | Comunicación HTTP con el workflow RAG |
| `InMemoryAnalysisRepository` | `AnalysisRepository` | Almacenamiento temporal de análisis |
| `Settings` | No aplica | Configuración del sistema mediante variables de entorno |

Los clientes externos utilizan httpx para comunicarse mediante HTTP.

La infraestructura depende de los contratos del dominio, mientras que el dominio permanece independiente de sus implementaciones concretas.

#### 7.4.4. Capa de interfaces HTTP

**Ubicación:** `backend/app/interfaces/http/`

Esta capa utiliza FastAPI y Pydantic para exponer las operaciones del sistema mediante una API REST.

Su estructura comprende:

| Archivo | Responsabilidad |
|---|---|
| `routes/analysis.py` | Endpoints `/api/analyze`, `/api/rag` y `/api/simulate` |
| `routes/health.py` | Endpoint `/api/health` |
| `schemas.py` | Validación y serialización de contratos JSON |
| `dependencies.py` | Composición e inyección de dependencias |
| `errors.py` | Conversión de errores del dominio a respuestas HTTP |

El archivo `dependencies.py` constituye el punto de composición de la arquitectura.

Su responsabilidad es construir los casos de uso, proporcionar las implementaciones concretas de los puertos y relacionar los componentes necesarios para procesar las solicitudes.

#### 7.4.5. Relaciones y regla de dependencias

La arquitectura utiliza inversión de dependencias para evitar que los casos de uso dependan directamente de los servicios externos.

Las relaciones principales son:

| Origen | Destino | Relación |
|---|---|---|
| Rutas FastAPI | Casos de uso | Ejecutan operaciones de aplicación |
| `AnalyzeProfile` | `CardiovascularModel` | Utiliza contrato de predicción |
| `AnalyzeProfile` | `AnalysisRepository` | Utiliza contrato de almacenamiento |
| `RequestRecommendations` | `AnalysisRepository` | Recupera contexto |
| `RequestRecommendations` | `RecommendationGenerator` | Solicita recomendaciones |
| `SimulateScenario` | `CardiovascularModel` | Solicita simulación |
| `MLServiceClient` | `CardiovascularModel` | Implementa contrato |
| `N8nRecommendationClient` | `RecommendationGenerator` | Implementa contrato |
| `InMemoryAnalysisRepository` | `AnalysisRepository` | Implementa contrato |
| `dependencies.py` | Casos de uso y adaptadores | Construye y conecta dependencias |

Debe diferenciarse entre una dependencia de código, la implementación de un contrato y una comunicación de ejecución.

Por ejemplo, `MLServiceClient` implementa `CardiovascularModel`, mientras que en ejecución realiza una solicitud HTTP hacia el servicio de Machine Learning.

#### 7.4.6. Verificación automatizada de dependencias

El backend dispone de una prueba automatizada de arquitectura ubicada en:

`backend/tests/test_architecture.py`

Esta prueba utiliza el módulo `ast` de Python para analizar instrucciones de importación y detectar dependencias prohibidas entre las capas.

Las restricciones contemplan:

- El dominio no debe depender de aplicación, infraestructura, interfaces HTTP ni frameworks externos utilizados en esas capas.
- La aplicación debe depender de los contratos y objetos del dominio, sin acoplarse directamente a los adaptadores de infraestructura.
- La infraestructura no debe depender de la capa HTTP.
- La capa de interfaces puede realizar la composición de los componentes concretos.

Este mecanismo contribuye a verificar que la organización del código conserve las reglas de dependencia establecidas.

La comprobación estática de imports complementa las pruebas unitarias y de integración, pero no garantiza por sí sola la ausencia de todas las formas posibles de acoplamiento.

#### 7.4.7. Diagrama de componentes

**Figura 7.3. Diagrama C4 de nivel 3 — Componentes internos del backend FastAPI.**

**[INSERTAR AQUÍ LA IMAGEN `C4_N3_Componentes.png`]**

*Figura 7.3. Organización interna del backend de PULSO conforme a Clean Architecture. Se representan los casos de uso, los puertos del dominio, las implementaciones de infraestructura y la composición de dependencias.*

El diagrama permite identificar los componentes centrales del backend y comprobar que las responsabilidades se encuentran distribuidas entre capas diferenciadas.

### 7.5. Flujo de análisis cardiovascular

El flujo de análisis corresponde al endpoint `POST /api/analyze`.

Su ejecución comprende:

1. El usuario introduce sus factores cardiovasculares mediante el frontend.
2. La solicitud llega al backend a través de NGINX.
3. FastAPI valida el contrato JSON mediante Pydantic y las reglas correspondientes del dominio.
4. La ruta construye un objeto `CardiovascularProfile`.
5. El caso de uso `AnalyzeProfile` solicita la predicción y explicación al puerto `CardiovascularModel`.
6. `MLServiceClient` se comunica con ML Service para ejecutar la inferencia y obtener la explicación SHAP.
7. El contexto del análisis se conserva temporalmente mediante `AnalysisRepository`.
8. El backend devuelve el identificador del análisis, la predicción y los factores explicativos.
9. El frontend presenta los resultados al usuario.

Este flujo separa la coordinación del análisis de la ejecución del modelo predictivo.

### 7.6. Flujo de recomendaciones educativas

El endpoint `POST /api/rag` permite solicitar recomendaciones educativas utilizando un análisis previamente calculado.

El proceso comprende:

1. El frontend envía el identificador temporal del análisis.
2. El backend recupera el contexto mediante `AnalysisRepository`.
3. `RequestRecommendations` utiliza `RecommendationGenerator` para solicitar información educativa.
4. `N8nRecommendationClient` invoca el webhook correspondiente de n8n.
5. El workflow RAG consulta el corpus documental vectorizado en Supabase.
6. El sistema utiliza los servicios de IA configurados para generar recomendaciones educativas fundamentadas.
7. n8n devuelve una respuesta estructurada con información educativa y referencias documentales.
8. El backend entrega la respuesta al frontend.

El proceso no requiere ejecutar nuevamente ML Service para generar recomendaciones.

### 7.7. Flujo de simulación de escenarios

El endpoint `POST /api/simulate` permite evaluar escenarios hipotéticos a partir de modificaciones de determinadas variables.

La operación comprende:

1. El usuario selecciona las variables que desea modificar.
2. El frontend envía el escenario al backend.
3. FastAPI valida los datos recibidos.
4. El caso de uso `SimulateScenario` solicita la simulación mediante `CardiovascularModel`.
5. ML Service ejecuta el modelo considerando el escenario modificado y la coherencia de las variables derivadas.
6. Se obtiene el resultado comparativo entre el escenario de referencia y el escenario simulado.
7. El backend devuelve los resultados al frontend.

Las diferencias obtenidas representan cambios en la salida del clasificador y no estimaciones causales de intervenciones clínicas.

### 7.8. Módulo de gestión de usuarios — Propuesta provisional

**Estado: pendiente de decisión. Posible eliminación del alcance final.**

Se conserva como propuesta arquitectónica un módulo de gestión de usuarios que podría incorporar:

- Registro e inicio de sesión.
- Autenticación y renovación de sesiones.
- Autorización mediante roles.
- Gestión de cuentas.
- Registro de consentimientos.
- Persistencia de historiales de análisis.
- Eliminación de información personal almacenada.

En caso de implementarse, el módulo deberá organizarse respetando la separación de responsabilidades del backend.

**Dominio:** entidades y objetos de valor asociados con usuarios, roles y consentimiento, junto con sus contratos.

**Aplicación:** casos de uso de registro, autenticación, autorización y gestión de cuentas.

**Infraestructura:** repositorios de persistencia, almacenamiento seguro de contraseñas y mecanismos de autenticación.

**Interfaces HTTP:** endpoints y esquemas correspondientes a las operaciones de usuarios.

La incorporación de este módulo podría requerir una base de datos relacional destinada a las cuentas y sus relaciones.

No debe confundirse esta persistencia propuesta con el almacenamiento vectorial de Supabase utilizado actualmente por el sistema RAG.

El módulo de usuarios se excluye de los tres diagramas C4 principales, que representan la arquitectura implementada y verificada del sistema.

Si se decide incorporarlo definitivamente, deberán actualizarse el modelo de dominio, el modelo de datos, los diagramas arquitectónicos y los casos de uso.

### 7.9. Decisiones técnicas y justificación

| Decisión técnica | Justificación |
|---|---|
| React y TypeScript | Construcción de una interfaz web basada en componentes |
| FastAPI | Implementación de APIs y coordinación de operaciones en Python |
| Clean Architecture adaptada | Separación de responsabilidades e inversión de dependencias |
| ML Service independiente | Aislamiento de la inferencia predictiva |
| XGBoost | Implementación del modelo supervisado de clasificación |
| SHAP | Explicación local de las predicciones |
| n8n | Orquestación del sistema RAG |
| Supabase y pgvector | Persistencia y recuperación semántica documental |
| Google Gemini API | Generación de embeddings y contenido mediante servicios de IA |
| Repositorio temporal en memoria | Reutilización de resultados sin historial persistente |
| NGINX | Centralización del acceso a frontend y backend |
| Docker Compose | Ejecución coordinada y reproducible del stack principal |
| Pruebas de arquitectura | Verificación automatizada de las reglas de dependencias |

### 7.10. Limitaciones arquitectónicas

La arquitectura implementada presenta restricciones que deben considerarse durante su operación y evolución.

**Almacenamiento temporal:** el repositorio de análisis conserva información en memoria del proceso, por lo que no proporciona persistencia permanente ni almacenamiento compartido entre múltiples instancias.

**Dependencias externas:** el funcionamiento del sistema RAG depende de la disponibilidad de n8n, Supabase y los servicios de inteligencia artificial configurados.

**Disponibilidad:** la ejecución satisfactoria de los contenedores locales no garantiza automáticamente la disponibilidad de todas las integraciones externas.

**Seguridad del despliegue:** los mecanismos de comunicación y exposición pública deben configurarse de acuerdo con las condiciones del entorno de ejecución.

**Validación clínica:** los resultados del modelo y las recomendaciones educativas no constituyen diagnósticos médicos ni sustituyen una evaluación clínica.

**Gestión de usuarios:** el módulo de autenticación, roles e historiales permanece como una propuesta provisional, pendiente de definición en el alcance final.

### 7.11. Conclusión

La arquitectura de PULSO se fundamenta en una separación modular de responsabilidades entre la interfaz web, el backend, el servicio de Machine Learning y el sistema RAG.

El backend implementa una adaptación de Clean Architecture que utiliza entidades de dominio, casos de uso, puertos y adaptadores para reducir el acoplamiento entre la lógica principal y los servicios externos.

Los tres niveles del modelo C4 permiten representar la solución desde perspectivas complementarias:

- **Nivel 1:** contexto general, actores y dependencias externas.
- **Nivel 2:** aplicaciones, servicios, tecnologías y comunicaciones.
- **Nivel 3:** componentes internos del backend y reglas de dependencia.

Esta organización facilita la comprensión de la arquitectura existente, la identificación de responsabilidades y la evolución del sistema, manteniendo separadas las funcionalidades implementadas de aquellas que permanecen como propuestas futuras.
## 8. E6. Base técnica del repositorio y estado de implementación

### 8.1. Descripción general

La base técnica de PULSO está constituida por una arquitectura modular que integra una aplicación web, una API backend, un servicio independiente de Machine Learning, una base de datos relacional y un sistema RAG para la generación de recomendaciones educativas.

La solución utiliza React y TypeScript para la interfaz, Python y FastAPI para los servicios backend, XGBoost y SHAP para las operaciones predictivas y explicativas, PostgreSQL para cuentas e historiales de análisis, y n8n junto con Supabase para las recomendaciones educativas fundamentadas documentalmente.

El backend sigue una adaptación de Clean Architecture, con separación entre dominio, aplicación, infraestructura e interfaces HTTP.

La implementación incorpora mecanismos de autenticación mediante JWT, protección de contraseñas con Argon2 y persistencia de resultados de análisis asociados con usuarios registrados.

### 8.2. Organización del repositorio

PULSO está organizado en un repositorio que agrupa los componentes de aplicación, servicios, infraestructura, pruebas y documentación.

| Directorio o archivo | Responsabilidad |
|---|---|
| `frontend/` | Interfaz web React, TypeScript y Vite |
| `backend/` | API FastAPI, autenticación y casos de uso |
| `backend/app/domain/` | Entidades, reglas, errores y puertos |
| `backend/app/application/use_cases/` | Casos de uso de análisis, usuarios e historial |
| `backend/app/infrastructure/` | Adaptadores, seguridad, configuración y repositorios |
| `backend/app/interfaces/http/` | Rutas, esquemas e inyección de dependencias |
| `backend/migrations/` | Migraciones SQL de PostgreSQL |
| `backend/tests/` | Pruebas automatizadas |
| `ml_service/` | Servicio de Machine Learning |
| `ml/` | Preparación, entrenamiento y evaluación del modelo |
| `artifacts/` | Artefactos del modelo entrenado |
| `infrastructure/nginx/` | Configuración del proxy inverso |
| `.github/workflows/` | Workflows de integración continua |
| `docs/` | Documentación técnica |
| `docker-compose.yml` | Definición de servicios contenerizados |

La estructura permite separar las responsabilidades de presentación, lógica de aplicación, persistencia e inferencia predictiva.

### 8.3. Backend y API REST

El backend está desarrollado en Python mediante FastAPI.

Su función es coordinar las operaciones de análisis cardiovascular, autenticación, consulta de historiales y generación de recomendaciones educativas.

La API expone los siguientes endpoints principales:

| Método | Endpoint | Responsabilidad | Autenticación |
|---|---|---|---|
| GET | `/api/health` | Comprobar disponibilidad | No |
| POST | `/api/auth/register` | Registrar usuarios | No |
| POST | `/api/auth/login` | Iniciar sesión | No |
| GET | `/api/auth/me` | Consultar usuario autenticado | Sí |
| POST | `/api/analyze` | Predicción y explicación SHAP | Sí |
| POST | `/api/rag` | Recomendaciones educativas | Sí |
| POST | `/api/simulate` | Simulación de escenarios | Sí |
| GET | `/api/analyses` | Consultar historial de análisis | Sí |

Las solicitudes y respuestas se validan mediante esquemas Pydantic.

Los endpoints protegidos utilizan autenticación HTTP Bearer y validación del token JWT.

El backend transforma los errores de dominio, validación, autenticación y comunicación externa en respuestas HTTP estructuradas.

### 8.4. Gestión de usuarios y autenticación

PULSO incorpora funcionalidades de registro, inicio de sesión y consulta de información del usuario autenticado.

Estas operaciones se organizan mediante casos de uso y adaptadores de infraestructura que respetan la separación de responsabilidades del backend.

#### 8.4.1. Registro de usuarios

El caso de uso `RegisterUser` permite registrar una cuenta mediante correo electrónico y contraseña.

La implementación utiliza el repositorio de usuarios para conservar las credenciales protegidas en PostgreSQL y gestionar la unicidad de los correos electrónicos.

#### 8.4.2. Inicio de sesión

El caso de uso `AuthenticateUser` valida las credenciales proporcionadas.

Cuando la autenticación es satisfactoria, el sistema emite un token de acceso que permite utilizar las operaciones protegidas.

Las credenciales incorrectas generan una respuesta de autenticación fallida.

#### 8.4.3. Protección de contraseñas

La implementación utiliza Argon2 mediante `pwdlib`.

El puerto `PasswordHasher` permite desacoplar el proceso de protección de contraseñas de su implementación concreta, `Argon2PasswordHasher`.

Las contraseñas no se almacenan en texto plano.

#### 8.4.4. Autenticación JWT

La emisión y validación de tokens utiliza PyJWT.

El adaptador `JWTAccessTokens` encapsula la generación y validación de los tokens utilizados por el backend.

La configuración incluye `JWT_SECRET_KEY` y `ACCESS_TOKEN_EXPIRE_MINUTES`.

El tiempo predeterminado documentado para los tokens de acceso es de 60 minutos.

La solución utiliza autenticación basada en tokens de acceso. No se incluye un mecanismo de refresh tokens como funcionalidad implementada.

#### 8.4.5. Protección de endpoints

El componente `get_current_user` verifica las credenciales proporcionadas mediante el mecanismo HTTP Bearer.

Su utilización permite identificar al usuario y restringir el acceso a las operaciones que requieren autenticación.

Los resultados persistentes se asocian con el identificador del usuario correspondiente.

### 8.5. Base de datos relacional PostgreSQL

PULSO utiliza PostgreSQL 16 para almacenar cuentas y resultados de análisis.

La base se configura mediante `DATABASE_URL` y utiliza SQLAlchemy y psycopg para el acceso desde el backend.

#### 8.5.1. Tabla de usuarios

La migración `001_create_users.sql` establece la tabla `users`.

| Columna | Tipo | Restricción |
|---|---|---|
| `id` | UUID | Clave primaria |
| `email` | VARCHAR(254) | Único y no nulo |
| `password_hash` | VARCHAR(255) | No nulo |
| `created_at` | TIMESTAMPTZ | Fecha de creación |

Esta estructura conserva los datos necesarios para identificar cuentas y verificar credenciales.

#### 8.5.2. Tabla de análisis

La migración `002_create_analysis_history.sql` establece la tabla `analyses`.

| Columna | Tipo | Restricción |
|---|---|---|
| `id` | UUID | Clave primaria |
| `user_id` | UUID | Clave foránea |
| `probability` | DOUBLE PRECISION | Entre 0 y 1 |
| `classification` | SMALLINT | Valor binario |
| `threshold` | DOUBLE PRECISION | Entre 0 y 1 |
| `model_version` | VARCHAR(50) | No nulo |
| `created_at` | TIMESTAMPTZ | Fecha de creación |

La relación entre `users` y `analyses` es de uno a muchos.

Se utiliza el índice `ix_analyses_user_created_at` para optimizar las consultas de resultados por usuario y fecha.

#### 8.5.3. Repositorios de persistencia

Los adaptadores principales son:

- `SQLAlchemyUserRepository`: creación y consulta de usuarios.
- `SQLAlchemyAnalysisHistoryRepository`: almacenamiento y recuperación del historial.

Estos componentes implementan contratos del dominio y encapsulan las operaciones de SQLAlchemy.

#### 8.5.4. Migraciones

El repositorio contiene migraciones SQL versionadas para usuarios e historiales.

Docker Compose permite inicializar una base de datos nueva mediante los scripts montados en el directorio de inicialización de PostgreSQL.

Los cambios posteriores sobre una base inicializada requieren una estrategia de aplicación de migraciones que preserve los datos existentes.

### 8.6. Historial persistente de análisis

El sistema permite que los usuarios autenticados consulten sus resultados anteriores.

El caso de uso `ListAnalysisHistory` recupera los registros correspondientes al usuario identificado mediante JWT.

La consulta se realiza mediante `GET /api/analyses`, utilizando paginación.

| Parámetro | Valor predeterminado | Restricción |
|---|---|---|
| `limit` | 20 | Entre 1 y 100 |
| `offset` | 0 | Mayor o igual a 0 |

El frontend dispone de `HistoryPage`, que presenta los registros y permite consultar resultados adicionales.

El historial almacena los resultados técnicos de cada análisis, sin conservar permanentemente el perfil cardiovascular completo ni la explicación SHAP.

### 8.7. Almacenamiento temporal de análisis

Además de la persistencia PostgreSQL, PULSO utiliza `InMemoryAnalysisRepository`.

Este repositorio conserva temporalmente el contexto completo necesario para solicitar recomendaciones educativas.

| Parámetro | Configuración |
|---|---|
| TTL | 900 segundos |
| Capacidad máxima | 100 entradas |
| Almacenamiento | Memoria del proceso |
| Persistencia permanente | No |
| Compartido entre procesos | No |

La separación entre ambos mecanismos responde a responsabilidades distintas.

PostgreSQL conserva resultados históricos asociados con usuarios, mientras que el repositorio temporal permite reutilizar perfiles, predicciones y explicaciones durante el proceso RAG.

### 8.8. Frontend React

El frontend utiliza React, TypeScript y Vite.

La interfaz incorpora las siguientes vistas y funcionalidades:

- `AuthPage`: registro e inicio de sesión.
- `EvaluationPage`: formulario de evaluación.
- `ResultPage`: presentación de predicción y explicación.
- `SimulationPage`: simulación de escenarios.
- `HistoryPage`: consulta del historial.
- `Header`: navegación y acciones de autenticación.

La aplicación gestiona el estado de sesión y utiliza tokens de acceso para comunicarse con los endpoints protegidos.

El cierre de sesión debe limpiar las credenciales y la información de formulario y análisis asociada con la sesión anterior.

La interfaz presenta comportamiento adaptable a diferentes anchos de pantalla. La validación funcional completa en dispositivos móviles requiere comprobaciones específicas.

### 8.9. Servicio de Machine Learning

ML Service constituye un servicio independiente implementado mediante Python y FastAPI.

Utiliza XGBoost para clasificación binaria y SHAP para explicabilidad.

Las operaciones principales incluyen predicción, explicación individual y simulación.

El modelo PULSO v1 utiliza un umbral de clasificación de 0.38, seleccionado para priorizar la sensibilidad del clasificador.

La comunicación entre backend y ML Service se realiza mediante HTTP/JSON.

### 8.10. Sistema RAG y persistencia vectorial

El sistema RAG utiliza workflows n8n para generar recomendaciones educativas fundamentadas en documentos seleccionados.

La base vectorial utiliza Supabase, PostgreSQL y pgvector.

La tabla operativa de producción es `public.documents_pulso_test`, cuya recuperación se realiza mediante `public.match_documents_pulso_test`.

El corpus comprende 15 documentos normalizados y 160 fragmentos vectorizados con `models/gemini-embedding-001`, de 3072 dimensiones.

La infraestructura incorpora tres mecanismos de almacenamiento diferenciados:

| Mecanismo | Finalidad |
|---|---|
| PostgreSQL del backend | Persistencia de usuarios e historiales |
| Supabase/pgvector | Almacenamiento del corpus documental |
| Memoria del backend | Contextos temporales de análisis |

El sistema RAG utiliza predicciones y explicaciones previamente calculadas; no ejecuta nuevamente el modelo cardiovascular para generar recomendaciones.

### 8.11. Docker Compose e infraestructura

La infraestructura principal se ejecuta mediante Docker Compose.

La configuración contempla cinco servicios:

| Servicio | Tecnología | Responsabilidad |
|---|---|---|
| `postgres` | PostgreSQL 16 | Usuarios e historiales |
| `ml-service` | FastAPI, XGBoost y SHAP | Inferencia y explicabilidad |
| `backend` | FastAPI | API, autenticación y casos de uso |
| `frontend` | React/Vite | Aplicación web |
| `nginx` | NGINX | Proxy inverso |

La configuración utiliza healthchecks para comprobar la disponibilidad de PostgreSQL y ML Service.

El backend depende de la disponibilidad de estos servicios para ejecutar las operaciones correspondientes.

PostgreSQL dispone de un volumen persistente para conservar la información entre reinicios de los contenedores.

NGINX proporciona acceso a la aplicación mediante el puerto 80 en la configuración local.

El comando de construcción y ejecución es:

`docker compose up -d --build`

El sistema requiere la configuración previa de variables de entorno y la disponibilidad de las integraciones externas utilizadas por RAG.

### 8.12. Variables de entorno y seguridad

La configuración se gestiona mediante variables de entorno.

| Variable | Responsabilidad |
|---|---|
| `POSTGRES_DB` | Nombre de la base |
| `POSTGRES_USER` | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL |
| `DATABASE_URL` | Cadena de conexión |
| `JWT_SECRET_KEY` | Clave de firma de tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Vigencia de tokens |
| `ML_SERVICE_URL` | Dirección del servicio predictivo |
| `ML_TIMEOUT_SECONDS` | Tiempo máximo de espera del servicio ML |
| `RAG_SERVICE_URL` | Dirección del servicio RAG |
| `RAG_TIMEOUT_SECONDS` | Tiempo máximo de espera del RAG |
| `ANALYSIS_CACHE_TTL_SECONDS` | Tiempo de retención temporal |
| `ANALYSIS_CACHE_MAX_ENTRIES` | Capacidad del repositorio temporal |

El archivo `.env.example` proporciona una referencia de configuración sin publicar credenciales reales.

Las contraseñas, claves JWT y credenciales externas deben mantenerse fuera del código fuente y de los archivos versionados.

### 8.13. Pruebas automatizadas

El proyecto incorpora pruebas para diferentes componentes y niveles de la arquitectura.

| Categoría | Propósito |
|---|---|
| Dominio | Verificar reglas y objetos |
| Aplicación | Comprobar casos de uso |
| Infraestructura | Verificar clientes y repositorios |
| Interfaces HTTP | Validar endpoints y contratos |
| Autenticación | Comprobar registro, inicio de sesión y acceso protegido |
| Historial | Verificar persistencia, asociación y consulta |
| Arquitectura | Detectar dependencias prohibidas |

El archivo `backend/tests/test_architecture.py` analiza imports para comprobar las restricciones de dependencia entre capas.

Las pruebas de integración con servicios simulados se diferencian de las pruebas que requieren infraestructura real.

Durante la validación de la implementación de autenticación e historial se reportaron los siguientes resultados:

| Verificación | Resultado |
|---|---|
| Pruebas del backend | 84 aprobadas |
| Pruebas del frontend | 24 aprobadas |
| Comprobación de tipos TypeScript | Correcta |
| Lint frontend | Correcto |
| Build de frontend | Correcto |

Estos resultados corresponden a las ejecuciones técnicas reportadas y deben asociarse con las evidencias de ejecución pertinentes.

### 8.14. Integración continua

PULSO utiliza GitHub Actions para automatizar verificaciones relacionadas con frontend, backend, Machine Learning e infraestructura.

Los principales procesos de validación comprenden:

- Backend Validation.
- Frontend Validation.
- ML Service Validation.
- ML Training Validation.
- Infrastructure Validation.

Las verificaciones permiten comprobar pruebas automatizadas, análisis estático, compilación y configuraciones de infraestructura.

La configuración de CI contempla las variables necesarias para comprobar el entorno con autenticación JWT.

Las validaciones que emplean servicios simulados permiten verificar contratos y configuraciones de forma controlada, pero no deben confundirse con pruebas de extremo a extremo utilizando todas las integraciones reales.

### 8.15. Documentación técnica

El repositorio incorpora documentación que describe la organización, ejecución y mantenimiento del sistema.

Entre los documentos de referencia se encuentran:

- `README.md`.
- `docs/ARQUITECTURA_BACKEND.md`.
- Documentación del modelo de Machine Learning.
- Documentación de infraestructura y pruebas.
- Informes del proyecto y del corpus RAG.

FastAPI proporciona documentación OpenAPI de los endpoints disponibles.

La documentación técnica permite relacionar las funcionalidades implementadas con sus componentes, contratos y mecanismos de verificación.

### 8.16. Alcance del módulo de usuarios

La implementación actual incluye registro, inicio de sesión, autenticación JWT y consulta del historial persistente de análisis.

Sin embargo, se diferencian estas funcionalidades de otras capacidades de administración de usuarios no contempladas como implementadas en esta versión, entre ellas:

- Renovación de sesiones mediante refresh tokens.
- Administración de múltiples roles.
- Registro y gestión específica de consentimientos.
- Eliminación de cuentas mediante un caso de uso propio.
- Panel administrativo de permisos.

Estas capacidades constituyen posibles ampliaciones y no deben confundirse con las funcionalidades de autenticación y persistencia existentes.

### 8.17. Conclusión

La base técnica de PULSO integra una aplicación web React, un backend FastAPI organizado mediante Clean Architecture adaptada, un servicio independiente de Machine Learning, una base de datos PostgreSQL para cuentas e historiales y un sistema RAG conectado con Supabase.

La arquitectura incorpora mecanismos de autenticación JWT, almacenamiento seguro de contraseñas mediante Argon2, protección de endpoints y acceso a resultados persistentes asociados con cada usuario.

El almacenamiento temporal de análisis se mantiene separado de la persistencia relacional y del corpus vectorial, permitiendo conservar responsabilidades diferenciadas.

Docker Compose coordina los cinco servicios principales, mientras que las herramientas de pruebas automatizadas y GitHub Actions proporcionan mecanismos para verificar la calidad y consistencia de la implementación.

En conjunto, la base técnica ofrece una estructura modular, verificable y preparada para continuar la evolución funcional de PULSO, manteniendo la separación entre sus componentes predictivos, educativos, de persistencia y de seguridad.## 9. E7. Funcionalidad existente y brechas

### 9.1 Funcionalidad demostrable en el código actual

- El formulario web envía los datos de entrada al endpoint de análisis.
- El usuario puede crear una cuenta e iniciar sesión; el backend valida el JWT para las rutas de análisis.
- Las cuentas se almacenan en PostgreSQL y las contraseñas se guardan con hash Argon2, nunca en texto plano.
- `POST /api/analyze` ejecuta el caso de uso de análisis, solicita predicción y explicación al servicio ML, conserva temporalmente el contexto y devuelve un identificador de análisis.
- El servicio ML valida rangos y consistencia entre altura, peso e IMC.
- La interfaz muestra predicción y factores SHAP.
- La interfaz permite solicitar recomendaciones RAG usando el identificador de análisis; el caso de uso recupera el contexto del repositorio en memoria y consulta n8n sin repetir la inferencia.
- `POST /api/simulate` ejecuta el caso de uso de simulación, que solicita al servicio ML una comparación entre valores originales y simulados.
- La interfaz HTTP traduce errores del dominio a respuestas HTTP, incluidos los casos de análisis inexistente, entrada o escenario inválido y fallo de servicios externos.
- Docker Compose coordina ML, backend, frontend y Nginx.

### 9.2 Brechas para considerar funcionalidades terminadas según la pauta

La implementación descrita incluye PostgreSQL para cuentas y autenticación con JWT; no incluye gestión automatizada de migraciones posteriores, datos semilla, roles, consentimiento, eliminación de cuenta, rutas protegidas por rol ni historial paginado de análisis. Los análisis no se persisten. Estas capacidades no se atribuyen al alcance implementado; la pauta las incluye como referencias transversales y su pertinencia o prioridad para PULSO debe acordarse con el docente. Por la diferencia entre el alcance funcional de PULSO y los proyectos CLENA de la pauta, no se calcula un porcentaje de cumplimiento del 80 % a partir de las funcionalidades de esa tabla.

## 10. Evidencias de Scrum y GitHub Flow

La información verificable de los elementos siguientes debe incorporarse desde GitHub y las actas del equipo antes de cerrar el informe:

| Evidencia | Referencia que debe agregarse |
|---|---|
| Product Owner, Scrum Master y equipo de desarrollo | [Nombres y sección del README] |
| GitHub Project y estados del tablero | [URL del tablero] |
| Milestone Sprint 1 y objetivo | [URL del milestone] |
| Historias validadas | [URLs de Issues] |
| Dailies o Sprint Review | [Fechas reales, actas y enlaces a grabaciones] |
| Pull Requests, revisiones y CI | [URLs de PR y estado de checks] |
| Protección de `main` y colaborador del curso | [Evidencia o configuración verificable] |

No se completan fechas, asistentes, aprobaciones ni enlaces que no estén disponibles en el repositorio.

## 11. Conclusiones

PULSO cuenta con una base de producto demostrable para el flujo de análisis: formulario, predicción, explicación SHAP, simulación y consulta educativa RAG. El proyecto también dispone de un flujo MLOps documentado y un modelo XGBoost seleccionado con umbral 0.38. La documentación delimita que el clasificador estima la clase `cardio = 1`, no un evento futuro, y que SHAP y las simulaciones no prueban causalidad.

La pauta se utilizó como estructura para presentar el problema, el backlog, los modelos, la arquitectura, la base técnica, las funcionalidades y la gestión del trabajo. Debido a que sus ejemplos y requisitos funcionales fueron escritos para proyectos distintos, algunos apartados se adaptaron al alcance de PULSO y otros se reportan como no implementados o no aplicables al estado actual. La valoración del curso corresponde al docente; este informe no afirma cumplimiento total de todos los criterios de la pauta.

## Referencias internas del proyecto

- [Primer informe](../PrimerInforme.md)
- [Segundo informe](../SegundoInforme.md)
- [Documentación del modelo final y SHAP](MODELO_FINAL_Y_GUIA_SHAP.md)
- [Estructura MLOps](ESTRUCTURA_MLOPS_PULSO_ACTUALIZADA.md)
