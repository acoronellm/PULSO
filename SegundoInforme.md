# Guía para el segundo informe del proyecto

## Resumen / Abstract

Las enfermedades cardiovasculares constituyen la principal causa de muerte en el mundo y están asociadas tanto con factores no modificables como modificables, entre ellas la hipertensión arterial, el colesterol elevado, la obesidad, el tabaquismo y la inactividad física. Aunque existen herramientas digitales para estimar el riesgo cardiovascular, muchas están orientadas a profesionales de la salud, emplean modelos calibrados para poblaciones específicas y presentan resultados cuya interpretación puede resultar compleja para personas sin formación médica. Este proyecto propone el diseño e implementación de PULSO (Plataforma Inteligente para la Predicción Explicable y Simulación Personalizada del Riesgo Cardiovascular mediante Machine Learning), un producto mínimo viable orientado a la prevención y educación en salud cardiovascular. La plataforma permitirá registrar factores de riesgo, generar una estimación mediante modelos de aprendizaje automático, explicar la influencia de las variables utilizadas y comparar el resultado inicial con escenarios hipotéticos construidos mediante la modificación de factores potencialmente controlables. Asimismo, integrará un sistema basado en Retrieval-Augmented Generation para presentar información preventiva sustentada en guías clínicas y fuentes médicas confiables, mediante un lenguaje comprensible para usuarios no especializados. El proyecto se desarrollará mediante una metodología iterativa e incremental que comprenderá la selección y preparación de datos clínicos públicos, el entrenamiento y comparación de modelos, el diseño de la arquitectura, la implementación de la plataforma web, la integración de explicabilidad y RAG, y la validación experimental del sistema. Como resultado, se espera obtener un MVP funcional que ayude a las personas a comprender sus factores de riesgo y favorezca decisiones informadas de prevención, sin sustituir la valoración realizada por profesionales de la salud.

En cuanto al estado actual del proyecto, se ha seleccionado el conjunto de datos Cardiovascular Disease Dataset, disponible en Kaggle, y se ha realizado un análisis exploratorio de datos (EDA). Asimismo, se ha iniciado la implementación y evaluación de diferentes algoritmos de clasificación. Los resultados de esta fase permitirán comparar el desempeño de los modelos y seleccionar el más adecuado para su integración en PULSO. Posteriormente, se continuará con el desarrollo y la integración de los componentes de explicabilidad mediante SHAP, simulación de escenarios y generación de información preventiva mediante RAG, así como con la validación del funcionamiento de la plataforma.

## 1. Introducción

El sector de la salud atraviesa un proceso de transformación impulsado por la digitalización de la información clínica, el crecimiento de la capacidad computacional y la aplicación de técnicas de inteligencia artificial al análisis de datos. En este contexto, el aprendizaje automático, la inteligencia artificial explicable, los sistemas de apoyo a la toma de decisiones y las plataformas digitales de salud ofrecen nuevas posibilidades para identificar patrones, estimar riesgos y comunicar información preventiva. Estas tecnologías adquieren especial relevancia frente a las enfermedades cardiovasculares, consideradas entre las principales causas de muerte en el mundo. Según la Organización Mundial de la Salud (OMS, 2025), aproximadamente 19,8 millones de personas murieron por enfermedades cardiovasculares en 2022, cifra equivalente al 32 % de las defunciones mundiales. La OMS también señala que muchas de estas enfermedades pueden prevenirse mediante la identificación y el manejo oportuno de factores conductuales y metabólicos, como el tabaquismo, la inactividad física, la alimentación poco saludable, la hipertensión arterial, la glucosa elevada, las alteraciones de los lípidos y el exceso de peso.

Actualmente existen herramientas como SCORE2, PREVENT, Framingham, Pooled Cohort y QRISK, diseñadas para estimar la probabilidad de que una persona presente un evento cardiovascular durante un periodo determinado. Sin embargo, estas soluciones difieren en las variables que emplean, la población para la cual fueron desarrolladas y la manera en que comunican sus resultados. Por ejemplo, SCORE2 fue diseñado para estimar el riesgo cardiovascular a diez años en poblaciones europeas, mientras que PREVENT utiliza información cardiovascular, renal y metabólica y está orientado principalmente a apoyar las conversaciones preventivas entre los profesionales de la salud y sus pacientes (American Heart Association [AHA], s. f.; European Society of Cardiology [ESC], s. f.-a). Además, algunas de estas herramientas presentan porcentajes y términos clínicos que pueden resultar difíciles de interpretar para personas no especializadas. Aunque generalmente permiten modificar los datos y repetir el cálculo, no siempre explican claramente la influencia de cada variable ni muestran una comparación comprensible entre el resultado original y los escenarios hipotéticos explorados.

Esta situación evidencia la necesidad de diseñar una solución tecnológica que no se limite a proporcionar un porcentaje, sino que facilite su comprensión y uso responsable. La oportunidad consiste en transformar una estimación probabilística en una experiencia educativa mediante la explicación de los factores considerados, la identificación de las variables que más influyen en el resultado y la comparación entre la condición inicial del usuario y diferentes escenarios hipotéticos.

En respuesta a esta necesidad, se desarrolla PULSO, una plataforma web orientada principalmente a personas no especializadas que busca facilitar la comprensión de los factores asociados con los problemas cardiovasculares. El sistema contempla la integración de modelos de Machine Learning de clasificación, mecanismos de explicabilidad mediante SHAP, simulación de escenarios hipotéticos y un componente basado en Retrieval-Augmented Generation (RAG) para proporcionar información preventiva sustentada en guías clínicas y fuentes médicas confiables. Para el componente predictivo se ha seleccionado el *Cardiovascular Disease Dataset*, disponible en Kaggle, cuya variable objetivo, `cardio`, identifica la presencia o ausencia de enfermedad cardiovascular en los registros. A partir de las características ingresadas por el usuario, el modelo buscará estimar la probabilidad de pertenecer a la clase `cardio = 1`. Esta salida representa una probabilidad estimada por el clasificador y no debe interpretarse como el riesgo de presentar un evento cardiovascular futuro durante un horizonte temporal determinado.

En cuanto al estado actual del proyecto, se ha completado la selección del conjunto de datos y se ha realizado un análisis exploratorio de datos (EDA) para examinar sus características y evaluar su pertinencia para el desarrollo del modelo predictivo. Asimismo, se ha iniciado la implementación y prueba de diferentes algoritmos de clasificación con el propósito de comparar su desempeño y seleccionar una alternativa para su integración en la plataforma.

## 2. Marco conceptual

El desarrollo de PULSO requiere integrar conceptos provenientes de la salud cardiovascular, el aprendizaje automático, la inteligencia artificial explicable y la ingeniería de software. Estos fundamentos permiten comprender tanto el problema que aborda el proyecto como el funcionamiento de los componentes que conformarán la plataforma. De la misma forma, proporcionan las bases necesarias para interpretar correctamente las estimaciones generadas por el modelo, explicar sus resultados y establecer los límites de su utilización en un contexto preventivo y educativo.
El marco conceptual se organiza alrededor de los fundamentos de la evaluación cardiovascular, los modelos de clasificación, la explicabilidad mediante SHAP, la simulación de escenarios hipotéticos, la generación aumentada por recuperación y las prácticas de desarrollo y operación de software. Estos conceptos se relacionan entre sí dentro de PULSO, pero cumplen funciones diferentes: el modelo genera una estimación, SHAP contribuye a explicar su comportamiento, la simulación permite explorar cambios en las entradas y RAG complementa los resultados con información documental.
La integración de estas tecnologías requiere considerar sus limitaciones. Una predicción estadística no constituye por sí misma un diagnóstico médico, una explicación de un modelo no demuestra causalidad y una respuesta generada mediante inteligencia artificial no garantiza que su contenido sea clínicamente correcto. Por esta razón, el diseño de PULSO debe fundamentarse en la interpretación responsable de las estimaciones y en la comunicación clara de sus condiciones de aplicación.

## 2.1. Enfermedades cardiovasculares y factores de riesgo
Las enfermedades cardiovasculares comprenden un conjunto de trastornos que afectan el corazón y los vasos sanguíneos, entre los que se encuentran la enfermedad coronaria y la enfermedad cerebrovascular. Su desarrollo puede relacionarse con diferentes características individuales, condiciones metabólicas y hábitos de vida. Entre los factores asociados se encuentran la hipertensión arterial, el tabaquismo, la inactividad física, la obesidad, las alteraciones del colesterol y los niveles elevados de glucosa. La identificación de estos factores constituye un elemento relevante para la prevención y la educación cardiovascular.
Los factores de riesgo pueden clasificarse en modificables y no modificables. Los primeros corresponden a características o comportamientos sobre los cuales pueden realizarse intervenciones, como el tabaquismo, la actividad física o determinadas condiciones metabólicas. Los segundos incluyen características como la edad y ciertos antecedentes personales o familiares. Esta clasificación permite distinguir entre factores que pueden ser objeto de acciones preventivas y aquellos que deben considerarse para contextualizar la condición de una persona.
En PULSO, estos factores constituyen parte de la información que podrá utilizarse como entrada del modelo predictivo. Sin embargo, su inclusión dependerá de las variables disponibles en el conjunto de datos seleccionado y de las características del modelo finalmente utilizado. Además, aunque una variable esté asociada estadísticamente con una condición cardiovascular, esto no significa que modificarla produzca necesariamente un cambio equivalente en la condición clínica de una persona.

## 2.2. Evaluación de riesgo cardiovascular y clasificación de enfermedad cardiovascular
El riesgo cardiovascular se refiere a la probabilidad de presentar un evento cardiovascular definido durante un periodo determinado. Herramientas como SCORE2, PREVENT y Framingham utilizan características individuales y factores clínicos para estimar este riesgo en poblaciones específicas. Sus resultados dependen del desenlace considerado, el horizonte temporal y las características de la población utilizada para desarrollar el modelo.
PULSO utiliza un enfoque diferente, basado en un problema de clasificación binaria. Para ello, se seleccionó el Cardiovascular Disease Dataset, publicado por sulianova en Kaggle, cuya variable objetivo cardio representa la presencia o ausencia de enfermedad cardiovascular en los registros. El modelo buscará estimar la probabilidad de pertenecer a la clase cardio = 1. Esta estimación no equivale a la probabilidad de presentar un evento cardiovascular futuro durante un horizonte temporal determinado ni constituye un diagnóstico médico.

## 2.3. Aprendizaje automático y modelos de clasificación
El aprendizaje automático (Machine Learning) es una disciplina de la inteligencia artificial que permite desarrollar modelos capaces de identificar patrones a partir de datos. En el aprendizaje supervisado, los algoritmos utilizan ejemplos con variables de entrada y una variable objetivo conocida para aprender relaciones que posteriormente pueden aplicarse a nuevas observaciones. La clasificación binaria constituye una modalidad de aprendizaje supervisado en la que se busca distinguir entre dos clases.
En PULSO se consideran algoritmos como regresión logística, árbol de decisión y Random Forest. La regresión logística modela la probabilidad de pertenecer a una clase, el árbol de decisión utiliza reglas de división sobre las características y Random Forest combina múltiples árboles para generar una predicción conjunta. Estos modelos serán comparados mediante métricas de evaluación para seleccionar uno que pueda integrarse al flujo de predicción, explicación y simulación de la plataforma.

## 2.4. Preparación de datos y evaluación de modelos
El análisis exploratorio de datos (Exploratory Data Analysis, EDA) permite examinar la estructura, distribución y características de un conjunto de datos antes del entrenamiento. A partir de sus resultados se pueden identificar inconsistencias, valores atípicos y relaciones entre variables. La preparación de datos comprende procesos como limpieza, transformación y selección de características, necesarios para adecuar la información al entrenamiento de los modelos.
La evaluación de los clasificadores permite determinar su comportamiento sobre datos no utilizados durante el entrenamiento. Entre las métricas consideradas se encuentran exactitud, precisión, sensibilidad, especificidad, F1-score y ROC-AUC. También resulta importante evaluar la calibración, que permite analizar la correspondencia entre las probabilidades estimadas y las frecuencias observadas. En PULSO, estas métricas permitirán comparar los modelos desarrollados y fundamentar la selección del clasificador definitivo.

## 2.5. IA explicable y SHAP
La inteligencia artificial explicable (Explainable Artificial Intelligence, XAI) comprende métodos que permiten interpretar el comportamiento de los modelos de inteligencia artificial. Su propósito es facilitar la comprensión de las predicciones y de las características que influyen en ellas. Esta capacidad resulta especialmente relevante para PULSO, debido a que sus usuarios no necesariamente tendrán conocimientos técnicos o médicos para interpretar una estimación probabilística.
SHAP (SHapley Additive exPlanations) es un método de explicabilidad basado en los valores de Shapley de la teoría de juegos cooperativos. Permite atribuir contribuciones a las variables utilizadas por un modelo para explicar una predicción respecto a un valor de referencia. En PULSO se utilizará para identificar los factores que más contribuyen a cada estimación y presentarlos de manera comprensible. Estas contribuciones explican el comportamiento del clasificador, pero no demuestran relaciones causales entre las variables y la condición cardiovascular.

## 2.6 Simulación de escenarios hipotéticos
La simulación de escenarios consiste en modificar determinadas variables de entrada de un modelo para observar cómo cambia su resultado bajo diferentes condiciones. Esta técnica permite comparar una estimación inicial con otras estimaciones generadas mediante combinaciones alternativas de características, facilitando la exploración del comportamiento del modelo predictivo.
En PULSO, el usuario podrá modificar factores potencialmente controlables y compatibles con el modelo seleccionado para obtener una nueva estimación y compararla con la original. Esta funcionalidad tendrá una finalidad educativa y exploratoria, ya que las variaciones observadas representan cambios en la salida del clasificador y no garantizan efectos equivalentes sobre la salud real de una persona.

## 2.7. Generación aumentada por recuperación (RAG)
a generación aumentada por recuperación (Retrieval-Augmented Generation, RAG) es una técnica que combina la recuperación de información documental con modelos generativos de lenguaje. Su funcionamiento consiste en recuperar fragmentos relevantes de un conjunto de documentos y utilizarlos como contexto para generar respuestas. Esto permite incorporar información procedente de fuentes seleccionadas sin necesidad de reentrenar el modelo generativo.
En PULSO, RAG utilizará guías clínicas y fuentes médicas confiables para proporcionar información preventiva relacionada con los factores cardiovasculares. Las respuestas se presentarán en un lenguaje comprensible y deberán mantener referencias a los documentos consultados. Sin embargo, esta técnica no elimina completamente el riesgo de generar información incorrecta, por lo que será necesario validar las respuestas y mantener las restricciones del alcance educativo del proyecto.

## 2.8. Arquitectura de software y servicios web
La arquitectura de software define la organización de los componentes de un sistema, sus responsabilidades y los mecanismos mediante los cuales interactúan. En una plataforma web, estos componentes pueden incluir frontend, backend, base de datos y servicios especializados. Su distribución influye en atributos como rendimiento, mantenibilidad, disponibilidad y capacidad de evolución. Las API permiten establecer interfaces de comunicación entre componentes, mientras que REST proporciona un estilo arquitectónico para diseñar servicios que interactúan mediante HTTP.
La contenerización permite empaquetar aplicaciones junto con sus dependencias para ejecutarlas en entornos aislados y reproducibles. Docker es una tecnología que facilita la construcción y ejecución de contenedores. Para PULSO se consideran alternativas monolíticas modulares, orientadas a servicios y basadas en microservicios, todas ellas contenerizadas. Su evaluación permitirá establecer una estructura para integrar el frontend, backend, Machine Learning y RAG de acuerdo con los requerimientos y recursos disponibles.

## 2.9. Integración continua y MLOps
La integración continua (Continuous Integration, CI) es una práctica de ingeniería de software que permite incorporar cambios al código de manera controlada mediante verificaciones automatizadas. Estas pueden incluir pruebas, análisis de calidad y comprobaciones de construcción. Herramientas como GitHub Actions permiten implementar flujos de trabajo que ejecutan estas verificaciones cuando se realizan cambios en el repositorio.
MLOps (Machine Learning Operations) comprende prácticas orientadas a gestionar el ciclo de vida de los modelos de aprendizaje automático, incluyendo la preparación de datos, el entrenamiento, la evaluación, el versionamiento y la integración. En PULSO se incorporarán prácticas básicas de MLOps para mantener la trazabilidad y reproducibilidad de los experimentos, permitiendo identificar qué datos, configuraciones y métricas corresponden a cada versión del modelo.



## 3. Planteamiento del problema

El problema central que aborda este trabajo es la dificultad que enfrentan las personas no especializadas para obtener, interpretar y utilizar de manera responsable información personalizada sobre los factores asociados con las enfermedades cardiovasculares. Aunque existen herramientas digitales que permiten estimar el riesgo cardiovascular, algunas presentan resultados cuya interpretación requiere conocimientos médicos, ofrecen explicaciones limitadas sobre la influencia de las variables y utilizan modelos desarrollados para poblaciones o contextos específicos.

Por tanto, el problema no se define como la inexistencia de una plataforma que integre Machine Learning, explicabilidad y RAG. Estas tecnologías representan componentes de la solución; lo que se pretende atender es la limitada capacidad de los usuarios para comprender qué significa una estimación, qué factores influyen en ella, cuáles podrían ser modificables y cuáles son los límites del resultado obtenido.

### 3.1 Descripción del problema

Las enfermedades cardiovasculares representan una problemática relevante de salud pública. Según la Organización Mundial de la Salud (OMS, 2025), aproximadamente 19,8 millones de personas murieron por estas enfermedades en 2022, lo que equivale al 32 % de las defunciones mundiales. Una parte importante del riesgo cardiovascular se relaciona con factores que pueden detectarse o modificarse, como el tabaquismo, la inactividad física, la alimentación poco saludable, la hipertensión arterial, la glucosa elevada, las alteraciones del colesterol y el exceso de peso. Por esta razón, la identificación temprana y la comprensión de estos factores son importantes para promover conductas preventivas y facilitar la búsqueda oportuna de orientación profesional.

Aunque existen herramientas como SCORE2, PREVENT, Framingham y QRISK para estimar la probabilidad de presentar eventos cardiovasculares, sus resultados no siempre son comprensibles para personas sin conocimientos médicos. Algunas presentan porcentajes y términos clínicos sin explicar suficientemente qué significa el resultado, cuáles variables tuvieron mayor influencia o cuáles son las limitaciones de la estimación. Además, varios modelos fueron desarrollados para poblaciones específicas: SCORE2 se diseñó principalmente con datos europeos, mientras que PREVENT está orientado al contexto estadounidense y al apoyo de conversaciones preventivas entre profesionales y pacientes (American Heart Association [AHA], 2026; European Society of Cardiology [ESC], s. f.-a). Esta situación limita su aplicación directa en otros contextos, ya que el desempeño de una estimación puede variar entre poblaciones. De hecho, actualmente se desarrolla SCORE2-LAC para adaptar este tipo de evaluación a América Latina y el Caribe (ESC, s. f.-b).

Como consecuencia, las personas no especializadas pueden tener dificultades para interpretar responsablemente la información relacionada con su condición cardiovascular, reconocer los factores que más influyen en las estimaciones y comprender el significado de los escenarios hipotéticos. Un resultado presentado sin suficiente contexto puede generar una falsa sensación de seguridad, preocupación innecesaria o decisiones sin acompañamiento profesional. Por tanto, el problema central corresponde a la limitada capacidad de los usuarios no especializados para obtener, comprender y utilizar información personalizada sobre los factores asociados con las enfermedades cardiovasculares, debido a la complejidad de las herramientas disponibles, la escasa explicación de sus resultados, la ausencia de comparaciones claras y las limitaciones de generalización de los modelos. Esta problemática evidencia la necesidad de presentar las estimaciones de manera comprensible, explicable y responsable, sin reemplazar la valoración de un profesional de la salud (OMS, 2021).

Desde la perspectiva social, esta problemática pone de manifiesto la necesidad de reducir la distancia existente entre la complejidad técnica de los modelos predictivos y la capacidad de interpretación del público general. No es suficiente comunicar que una persona presenta determinado porcentaje; también es necesario explicar qué representa ese valor, cuáles factores fueron considerados y cuáles influyeron con mayor intensidad. Esta forma de comunicación puede fortalecer la alfabetización en salud, entendida como la capacidad para acceder, comprender y utilizar información relacionada con el cuidado y la prevención.

La pertinencia social y práctica del proyecto también se relaciona con el contexto colombiano. El Ministerio de Salud y Protección Social (2023) plantea que el abordaje de las enfermedades no transmisibles requiere fortalecer la atención primaria, el empoderamiento de las personas y las comunidades y la aplicación de intervenciones que contribuyan a reducir la morbilidad, la mortalidad prematura y la discapacidad. En este contexto, una plataforma que presente información preventiva de manera accesible puede contribuir a la comprensión de los factores cardiovasculares, sin formar parte necesariamente de un servicio asistencial ni reemplazar las rutas institucionales de atención.

### 3.2 Restricciones y supuestos de diseño

El desarrollo de PULSO se encuentra condicionado por restricciones académicas, tecnológicas, metodológicas y relacionadas con el uso responsable de la inteligencia artificial en salud. Estas condiciones delimitan las funcionalidades que podrán implementarse, los datos utilizados para el entrenamiento de los modelos y el alcance de los resultados proporcionados por la plataforma.

La selección del *Cardiovascular Disease Dataset*, disponible en Kaggle, ha permitido concretar la fuente de datos y orientar el componente predictivo hacia un problema de clasificación binaria. No obstante, la selección del conjunto de datos no garantiza por sí misma que los modelos desarrollados presenten un desempeño adecuado ni que sus resultados puedan generalizarse a cualquier población. Por esta razón, será necesario evaluar experimentalmente los modelos y documentar las limitaciones de los datos utilizados.

Asimismo, el diseño de la plataforma deberá considerar que las estimaciones generadas por los modelos, las explicaciones proporcionadas mediante SHAP y los escenarios hipotéticos no constituyen diagnósticos médicos ni demuestran relaciones causales. PULSO mantendrá un propósito preventivo y educativo, por lo que sus funcionalidades deberán comunicar de manera comprensible las limitaciones de los resultados y evitar que estos sean interpretados como indicaciones clínicas.

**Restricciones**

1. **Tiempo y alcance académico.** El proyecto será desarrollado dentro del tiempo asignado para el Proyecto Final y por un equipo de tres estudiantes. Por esta razón, el resultado será un producto mínimo viable (MVP) y no una plataforma certificada para uso clínico.

2. **Disponibilidad y calidad de los datos.** Se ha seleccionado el *Cardiovascular Disease Dataset*, publicado por sulianova en Kaggle, como fuente de datos para el desarrollo del componente predictivo. Aunque ya se realizó un análisis exploratorio de datos (EDA), las características del conjunto de datos, su calidad, representatividad, distribución de las clases y posibles inconsistencias podrán limitar el desempeño de los modelos.

3. **Representatividad poblacional.** El conjunto de datos seleccionado podría no representar adecuadamente a la población colombiana o latinoamericana. Esta restricción es relevante porque el desempeño de los modelos predictivos puede variar al aplicarse a poblaciones diferentes de aquellas utilizadas durante su desarrollo. Por tanto, los resultados obtenidos no podrán considerarse automáticamente generalizables a cualquier población.

4. **Alcance preventivo y educativo.** PULSO no realizará diagnósticos médicos, no prescribirá medicamentos, no recomendará suspender tratamientos y no sustituirá la consulta con profesionales de la salud.

5. **Datos proporcionados por el usuario.** La plataforma dependerá parcialmente de información autodeclarada. Los errores de medición, desconocimiento, omisión o digitación podrán afectar el resultado. Por ello, las variables solicitadas deberán contar con unidades de medida, rangos válidos e instrucciones comprensibles.

6. **Interpretación de las simulaciones.** Los escenarios se construirán modificando determinadas variables de entrada del modelo. Una disminución en la probabilidad estimada por el clasificador no demostrará una relación causal ni garantizará que la condición cardiovascular real del usuario cambie. Las simulaciones tendrán una finalidad educativa y exploratoria y no serán utilizadas para recomendar modificaciones en medicamentos o tratamientos.

7. **Limitaciones de la inteligencia artificial generativa.** La utilización de RAG reduce, pero no elimina, el riesgo de generar respuestas incompletas, imprecisas o descontextualizadas. Las salidas deberán conservar vínculos con las fuentes consultadas y advertencias sobre su carácter informativo.

8. **Recursos tecnológicos.** El entrenamiento de los modelos, el almacenamiento de información, la ejecución de los componentes de inteligencia artificial y el despliegue de la plataforma estarán condicionados por la capacidad computacional, los servicios disponibles y el presupuesto del equipo.

9. **Privacidad y seguridad.** El MVP deberá minimizar la recopilación de información personal y proteger los datos almacenados. No se utilizarán historias clínicas identificables sin las autorizaciones, medidas de seguridad y procedimientos éticos correspondientes. La protección de la autonomía y la privacidad constituye un principio fundamental para el uso de la inteligencia artificial en salud (OMS, 2021).

10. **Delimitación de la predicción.** El componente predictivo se desarrollará como un problema de clasificación binaria utilizando la variable objetivo `cardio` del conjunto de datos seleccionado. El modelo buscará estimar la probabilidad de pertenecer a la clase `cardio = 1`, asociada con la presencia de enfermedad cardiovascular en los registros. Esta estimación no establece por sí misma la probabilidad de presentar un evento cardiovascular futuro durante un horizonte temporal determinado. La población de aplicación y las condiciones de interpretación de los resultados deberán delimitarse conforme a las características de los datos y los resultados de la evaluación experimental.

**Supuestos de diseño**

1. Se dispone de un conjunto de datos público seleccionado para el desarrollo del componente predictivo, cuyas características permiten iniciar la experimentación con modelos de clasificación. Su pertinencia definitiva para los objetivos del proyecto estará sujeta a los resultados de la evaluación experimental.

2. Los usuarios dispondrán de un dispositivo con navegador web y conexión a internet para acceder a la plataforma.

3. Los usuarios conocerán o podrán consultar la información solicitada por el sistema, como edad, peso, presión arterial y demás variables requeridas por el modelo seleccionado.

4. Las variables estarán definidas con unidades de medida, rangos válidos e instrucciones comprensibles para reducir errores en el ingreso de datos.

5. Será posible seleccionar guías clínicas y fuentes médicas confiables para construir un corpus documental controlado para el sistema RAG.

6. Los datos podrán dividirse adecuadamente en conjuntos de entrenamiento, validación y prueba, evitando que los mismos registros sean utilizados simultáneamente para entrenar y evaluar el modelo.

7. Los modelos se evaluarán mediante métricas de discriminación, calibración y clasificación apropiadas para la naturaleza y distribución de los datos. La selección del modelo definitivo dependerá de los resultados experimentales y de su pertinencia para los objetivos del proyecto.

8. La plataforma conservará el resultado inicial para compararlo con los escenarios hipotéticos y diferenciará visualmente los datos originales de los valores simulados.

9. Las variables modificadas durante la simulación estarán limitadas a factores potencialmente controlables y compatibles con el modelo seleccionado.

10. Las explicaciones generadas mediante SHAP indicarán la contribución de las variables a la predicción del modelo, pero no afirmarán que exista una relación causal entre dichas variables y la condición cardiovascular del usuario.

### 3.3 Alcance actualizado

El alcance de PULSO comprende el diseño e implementación de un producto mínimo viable (MVP) sobre una plataforma web orientada a la prevención y educación cardiovascular, dirigida principalmente a personas no especializadas. La solución busca facilitar la comprensión de los factores asociados con las enfermedades cardiovasculares mediante la integración de un modelo de Machine Learning de clasificación, mecanismos de explicabilidad, simulación de escenarios hipotéticos e información preventiva sustentada en fuentes médicas confiables. Este alcance delimita tanto las funcionalidades que serán desarrolladas como aquellas que quedan fuera del proyecto, en coherencia con las restricciones y supuestos de diseño descritos en la sección 3.2.

Respecto al planteamiento inicial, se ha concretado la selección del *Cardiovascular Disease Dataset*, publicado por sulianova en Kaggle, como fuente de datos para el desarrollo del componente predictivo. Este conjunto de datos contiene la variable objetivo `cardio`, que identifica la presencia o ausencia de enfermedad cardiovascular en los registros. En consecuencia, el modelo se desarrollará como un problema de clasificación binaria y buscará estimar la probabilidad de pertenecer a la clase `cardio = 1`. Esta estimación no debe interpretarse como la probabilidad de presentar un evento cardiovascular futuro durante un horizonte temporal determinado. La delimitación de la población de aplicación y las condiciones de interpretación de los resultados estarán sujetas a las características del conjunto de datos y a la evaluación experimental de los modelos.

En cuanto al avance actual, se ha completado la selección del conjunto de datos y se ha realizado un análisis exploratorio de datos (EDA). Asimismo, se ha iniciado la implementación y prueba de diferentes algoritmos de clasificación, entre ellos regresión logística y árbol de decisión. La selección del modelo definitivo se realizará a partir de la comparación de sus resultados, considerando métricas de desempeño, calibración y otros criterios pertinentes para el proyecto. Las funcionalidades de explicabilidad, simulación, RAG y los demás componentes de la plataforma se mantienen dentro del alcance previsto para el MVP, sin que su inclusión implique que ya se encuentren implementados.

**El proyecto incluye:**

1. El registro y la gestión de la información relacionada con los factores cardiovasculares ingresada por el usuario.

2. El entrenamiento, la comparación y la selección de modelos de Machine Learning de clasificación utilizando el conjunto de datos seleccionado, con el propósito de estimar la probabilidad de pertenecer a la clase `cardio = 1`.

3. La incorporación de mecanismos de explicabilidad mediante SHAP que permitan identificar los factores que más contribuyen a cada predicción generada por el modelo seleccionado.

4. Una funcionalidad de simulación que permita modificar variables potencialmente controlables y compatibles con el modelo seleccionado, como peso, presión arterial y otras variables pertinentes, para comparar la estimación inicial con la obtenida bajo un escenario hipotético.

5. Un sistema basado en Retrieval-Augmented Generation (RAG) que consulte guías clínicas y fuentes médicas confiables para generar información y recomendaciones preventivas de carácter educativo, utilizando un lenguaje sencillo y comprensible.

6. El diseño e implementación de una base de datos para la gestión de la información de la plataforma.

7. El diseño e implementación de una API que integre los diferentes servicios del sistema, incluyendo el modelo predictivo, la explicabilidad, la simulación y el componente RAG, con la interfaz web.

8. El diseño e implementación de una interfaz web orientada principalmente a personas no especializadas.

9. Una validación experimental que permita evaluar el desempeño de la plataforma y de los modelos utilizados mediante datos no empleados previamente durante el entrenamiento.

10. La implementación de un workflow de desarrollo basado en GitHub, utilizando ramas independientes, pull requests y revisión de código para controlar la incorporación de cambios al proyecto.

11. La configuración de un proceso de integración continua mediante GitHub Actions que ejecute automáticamente pruebas, validaciones de calidad y comprobaciones de integración antes de incorporar cambios a la rama principal.

12. El versionamiento de los modelos de Machine Learning, conservando información sobre las versiones utilizadas, los datos de entrenamiento, las métricas obtenidas y las condiciones bajo las cuales fueron generados.

13. La incorporación de prácticas básicas de MLOps para automatizar y hacer trazables los procesos relacionados con los datos, entrenamiento, evaluación, versionamiento e integración de los modelos dentro de la plataforma.

**El proyecto no incluye:**

1. La generación de diagnósticos médicos, la prescripción de medicamentos ni la recomendación de modificar o suspender tratamientos.

2. Una validación clínica certificada ni un proceso de aprobación regulatoria que permita utilizar PULSO como dispositivo médico.

3. La integración con historias clínicas electrónicas institucionales ni el uso de información identificable de pacientes reales sin las autorizaciones correspondientes.

4. La prestación de atención asistencial en tiempo real ni la sustitución de la consulta con profesionales de la salud.

5. La estimación del riesgo de presentar un evento cardiovascular futuro durante un horizonte temporal determinado, dado que el modelo de clasificación se desarrollará utilizando la variable `cardio` del conjunto de datos seleccionado. Tampoco se contempla la predicción independiente de todas las enfermedades o eventos cardiovasculares posibles.

6. El desarrollo de aplicaciones móviles nativas, dado que la solución se limitará a una plataforma web.

7. La recalibración exhaustiva de los modelos para todas las poblaciones latinoamericanas, aunque las limitaciones de generalización identificadas serán documentadas.

8. Un sistema completamente automatizado de aprendizaje continuo en producción. El MVP podrá incorporar mecanismos básicos de actualización, versionamiento y trazabilidad de los modelos como parte de las prácticas de MLOps, pero no contempla un ciclo autónomo de reentrenamiento y despliegue continuo en un entorno productivo.

## 4. Objetivos

A partir del problema planteado en la sección 3 y del alcance actualizado del proyecto, se establece el objetivo general y los objetivos específicos que orientan el desarrollo de PULSO. Estos objetivos contemplan la construcción de una plataforma web que integre un modelo de clasificación de Machine Learning, mecanismos de explicabilidad, simulación de escenarios e información preventiva sustentada en fuentes médicas confiables.

La selección del *Cardiovascular Disease Dataset* ha permitido concretar el enfoque del componente predictivo hacia la clasificación binaria, utilizando la variable objetivo `cardio` para estimar la probabilidad de pertenecer a la clase asociada con la presencia de enfermedad cardiovascular. Esta decisión permite delimitar el problema de aprendizaje automático y establecer actividades de entrenamiento, comparación y evaluación de modelos con resultados verificables.

Los objetivos se desarrollarán mediante un proceso iterativo e incremental que permita evaluar progresivamente los componentes del sistema. Su cumplimiento se verificará a través de los resultados del análisis de datos, las métricas de los modelos, la implementación de las funcionalidades y las pruebas técnicas, funcionales y de usabilidad del MVP.

### 4.1 Objetivo general

Diseñar e implementar, antes de noviembre de 2026, un MVP de una plataforma web orientada a personas no especializadas que permita estimar de manera explicable la probabilidad de pertenecer a la clase asociada con la presencia de enfermedad cardiovascular, mediante un modelo de Machine Learning de clasificación entrenado con el *Cardiovascular Disease Dataset*, integrando funcionalidades de explicabilidad mediante SHAP, simulación personalizada de escenarios y generación de información y recomendaciones preventivas mediante RAG basado en guías clínicas y fuentes médicas confiables.

### 4.2 Objetivos específicos

1. **Seleccionar y analizar**, antes de finalizar septiembre de 2026, un conjunto de datos clínicos público y pertinente para el desarrollo del modelo predictivo, mediante un análisis exploratorio de datos (EDA) que permita examinar su estructura, calidad, disponibilidad de variables y distribución de la variable objetivo, documentando los resultados obtenidos y las limitaciones identificadas.

2. **Desarrollar y comparar**, antes de octubre de 2026, al menos dos modelos de Machine Learning de clasificación utilizando el conjunto de datos seleccionado, evaluándolos mediante métricas de desempeño, discriminación y calibración, con el propósito de seleccionar un modelo y documentar los resultados que justifican su integración en el MVP.

3. **Implementar**, antes de octubre de 2026, un mecanismo de explicabilidad basado en SHAP sobre el modelo seleccionado, de manera que el MVP permita identificar y presentar los principales factores que contribuyen a cada estimación generada por el clasificador.

4. **Diseñar e implementar**, antes de octubre de 2026, una funcionalidad de simulación que permita modificar variables potencialmente controlables y compatibles con el modelo seleccionado, conservando el resultado inicial para compararlo con la estimación obtenida bajo al menos un escenario hipotético.

5. **Integrar**, antes de noviembre de 2026, un sistema basado en Retrieval-Augmented Generation (RAG) que utilice guías clínicas y fuentes médicas confiables previamente seleccionadas para generar información y recomendaciones preventivas de carácter educativo, en un lenguaje sencillo y comprensible para personas no especializadas.

6. **Diseñar e implementar**, antes de noviembre de 2026, la arquitectura de software, la base de datos, la API y los mecanismos de integración necesarios para incorporar los componentes del MVP, estableciendo un workflow de desarrollo basado en GitHub que permita gestionar, probar y versionar de manera controlada los cambios realizados durante el desarrollo del proyecto.

7. **Validar**, antes de noviembre de 2026, el funcionamiento del MVP mediante pruebas técnicas, funcionales y de usabilidad, utilizando datos de evaluación no empleados durante el entrenamiento de los modelos y usuarios no involucrados en su desarrollo, con el fin de verificar el cumplimiento de los requerimientos, evaluar la comprensión de los resultados e identificar oportunidades de mejora.

8. **Implementar**, antes de noviembre de 2026, prácticas básicas de MLOps que permitan automatizar y mantener la trazabilidad de los procesos de preparación de datos, entrenamiento, evaluación, versionamiento e integración de los modelos de Machine Learning desarrollados para el MVP.

## 5. Estado del arte / soluciones relacionadas

### 5.1 Modelos clínicos de estimación del riesgo cardiovascular

La estimación del riesgo cardiovascular ha sido abordada mediante diferentes modelos desarrollados a partir de cohortes poblacionales y registros clínicos. Aunque estas herramientas comparten el propósito general de apoyar la prevención cardiovascular, existen diferencias importantes en las poblaciones utilizadas para su desarrollo, los desenlaces considerados, los horizontes temporales de predicción, las variables empleadas y los procesos de validación. Estas características condicionan la interpretación de sus resultados y la posibilidad de aplicarlos a poblaciones diferentes de aquellas en las que fueron desarrollados.

Entre los modelos más representativos se encuentran el **Framingham General Cardiovascular Disease Risk Score**, las **Pooled Cohort Equations (PCE)**, **SCORE2**, **QRISK3** y **PREVENT**. En términos generales, todos incorporan factores de riesgo cardiovascular tradicionales, como edad, sexo, presión arterial y tabaquismo; sin embargo, algunos amplían la evaluación mediante variables metabólicas, renales, clínicas o sociales. Asimismo, aunque gran parte de estos modelos estima riesgo a diez años, existen diferencias importantes en la definición del evento cardiovascular que cada uno busca predecir.

| Modelo | Población de desarrollo | Tamaño de muestra | Desenlace principal | Horizonte temporal | Variables principales | Validación y generalización |
|---|---|---:|---|---|---|---|
| **Framingham General CVD Risk Score** | Adultos de 30 a 74 años de las cohortes Original y Offspring de Framingham, Massachusetts, EE. UU., sin enfermedad cardiovascular previa | La fuente revisada identifica las cohortes utilizadas, pero no especifica en el material recopilado un tamaño único de muestra para esta versión del modelo | Enfermedad cardiovascular global: muerte coronaria, infarto de miocardio, insuficiencia coronaria, angina, ictus, ataque isquémico transitorio, enfermedad arterial periférica e insuficiencia cardíaca | 10 años | Edad, sexo, colesterol total, colesterol HDL, presión arterial sistólica, tratamiento antihipertensivo, tabaquismo y diabetes. Existe una versión simplificada que sustituye el perfil lipídico por IMC | Desarrollado principalmente en una población blanca de una localidad estadounidense. Su aplicación en otras poblaciones puede requerir recalibración y se ha señalado posible sobreestimación del riesgo en cohortes contemporáneas (D'Agostino et al., 2008) |
| **Pooled Cohort Equations (PCE)** | Adultos de 40 a 79 años de EE. UU. sin enfermedad cardiovascular previa, provenientes de ARIC, CHS, CARDIA y Framingham; incluye población blanca y afroamericana | 24.626 participantes | Primer evento ateroesclerótico cardiovascular grave (*hard ASCVD*): infarto de miocardio no fatal, muerte por enfermedad coronaria o ictus fatal/no fatal | 10 años | Edad, sexo, raza, colesterol total, colesterol HDL, presión arterial sistólica, tratamiento antihipertensivo, diabetes y tabaquismo | Validación interna y externa. Se reportaron valores del estadístico C entre 0,713 y 0,818 según sexo y raza. La generalización a poblaciones como hispanos o asiáticos requiere precaución y posible recalibración (Goff et al., 2014) |
| **SCORE2** | Adultos europeos, principalmente entre 40 y 69 años, sin enfermedad cardiovascular previa ni diabetes conocida, procedentes de 45 cohortes de 13 países | 677.684 participantes en derivación y más de 1,13 millones en validación externa | Primer evento cardiovascular fatal o no fatal: muerte cardiovascular, infarto de miocardio no fatal o ictus no fatal | 10 años | Edad, sexo, tabaquismo, presión arterial sistólica y colesterol no-HDL | Validado externamente en 25 cohortes de 15 países europeos. Se reportaron valores de C-index entre aproximadamente 0,67 y 0,81. El modelo fue recalibrado para cuatro regiones europeas de riesgo y requiere adaptación para su utilización fuera de Europa (SCORE2 Working Group & ESC Cardiovascular Risk Collaboration, 2021) |
| **QRISK3** | Pacientes de 25 a 84 años registrados en atención primaria en Inglaterra, sin enfermedad cardiovascular previa ni uso de estatinas al inicio | 7,89 millones en derivación y 2,67 millones en validación | Enfermedad cardiovascular compuesta: enfermedad coronaria, ictus isquémico o ataque isquémico transitorio | 10 años | Edad, etnia, privación social, presión arterial sistólica, variabilidad de presión arterial, IMC, colesterol, tabaquismo, diabetes, antecedentes familiares, enfermedad renal, fibrilación auricular y otras condiciones clínicas y farmacológicas | Validación en una cohorte independiente de 2,67 millones de pacientes. Se reportaron valores del C-statistic de aproximadamente 0,88 en mujeres y 0,86 en hombres. Su utilización fuera del Reino Unido requiere validación y posible recalibración (Hippisley-Cox et al., 2017) |
| **PREVENT** | Adultos de 30 a 79 años de EE. UU. provenientes de cohortes poblacionales y grandes bases de datos clínicas, con representación de diferentes grupos étnicos y sin enfermedad cardiovascular al inicio | 3,28 millones en derivación y 3,33 millones en validación externa | Enfermedad cardiovascular total, compuesta por ASCVD e insuficiencia cardíaca; también dispone de modelos específicos para ASCVD e insuficiencia cardíaca | 10 y 30 años | Edad, sexo, presión arterial sistólica, colesterol no-HDL, colesterol HDL, función renal estimada mediante eGFR, tabaquismo, diabetes, tratamiento antihipertensivo y estatinas. Puede incorporar UACR, HbA1c y deprivación social | Validado externamente en aproximadamente 3,33 millones de personas. Para enfermedad cardiovascular total se reportaron valores medianos del C-statistic de 0,794 en mujeres y 0,757 en hombres, además de una adecuada calibración. Fue desarrollado para población estadounidense y requiere validación antes de utilizarse en otros países (Khan et al., 2024) |

### 5.2 Explicabilidad en modelos de predicción cardiovascular

El incremento en el uso de modelos de Machine Learning para la predicción de enfermedades y eventos cardiovasculares ha generado la necesidad de incorporar mecanismos que permitan comprender cómo se producen sus resultados. Esta necesidad resulta especialmente relevante cuando se utilizan modelos complejos, como Random Forest, XGBoost o redes neuronales, cuyo comportamiento no siempre puede interpretarse directamente a partir de sus parámetros internos. En este contexto, diferentes investigaciones han utilizado técnicas de inteligencia artificial explicable (XAI) para identificar las variables que influyen en las predicciones, analizar relaciones entre factores clínicos y proporcionar explicaciones tanto a nivel global como individual.

#### Aplicación de SHAP en modelos cardiovasculares

Una de las técnicas utilizadas con mayor frecuencia es SHAP (*SHapley Additive exPlanations*), que permite atribuir a cada variable una contribución sobre la predicción generada por un modelo. Zhu et al. (2026) desarrollaron un modelo para estimar el riesgo de enfermedad cardiovascular incidente a nueve años en adultos chinos de 45 años o más utilizando datos longitudinales del estudio CHARLS. La investigación comparó diez algoritmos de Machine Learning y seleccionó Random Forest como modelo final, con un AUC de 0,829. Posteriormente, SHAP fue utilizado tanto para explicaciones globales como individuales, permitiendo jerarquizar las variables según su influencia y representar predicciones específicas mediante gráficos como *summary plots*, *dependence plots* y *force plots*. Entre los factores con mayor influencia se encontraron la circunferencia de cintura, los triglicéridos, la edad y la hipertensión. Los autores también identificaron relaciones no lineales entre algunas variables y la predicción y desarrollaron una calculadora web para presentar los resultados de manera interactiva.

Otro estudio realizado por Chen et al. (2022) utilizó SHAP para interpretar modelos orientados a la estratificación del riesgo de enfermedad coronaria y accidente cerebrovascular isquémico en población china. La investigación analizó 8.624 registros médicos electrónicos y utilizó un *Balanced Bagging Classifier* basado en Random Forest para manejar el desequilibrio de clases. SHAP permitió identificar variables relevantes tanto de manera global como individual y analizar diferencias entre los factores asociados con enfermedad coronaria y accidente cerebrovascular. Entre las características con mayor influencia común se encontraron la edad, la rigidez arterial medida mediante velocidad de onda de pulso, la hipertensión y el colesterol LDL. La técnica también fue utilizada para reducir el número de variables de los modelos manteniendo un desempeño elevado, alcanzando valores de AUC de 0,905 para enfermedad coronaria y 0,889 para accidente cerebrovascular isquémico.

Estos estudios muestran que SHAP puede cumplir diferentes funciones dentro de los modelos cardiovasculares. Además de generar una jerarquía global de variables, puede utilizarse para explicar predicciones individuales, estudiar relaciones no lineales e interacciones entre características y apoyar la selección de predictores. No obstante, los resultados obtenidos mediante SHAP deben interpretarse como explicaciones del comportamiento estadístico del modelo. Zhu et al. señalan explícitamente que las contribuciones SHAP no representan efectos causales ni mecanismos biológicos directos, sino contribuciones estadísticas marginales asociadas con la salida del modelo.

#### Otras técnicas de explicabilidad

La explicabilidad en modelos cardiovasculares no se limita al uso de SHAP. También se han utilizado técnicas como LIME (*Local Interpretable Model-Agnostic Explanations*), importancia por permutación (*Permutation Feature Importance*, PFI) y gráficos de dependencia parcial (*Partial Dependence Plots*, PDP), entre otros enfoques. Estas técnicas pueden ofrecer diferentes niveles de interpretación y utilizarse de manera complementaria para explicar tanto el comportamiento general de un modelo como predicciones particulares.

Ansari et al. (2026) propusieron un marco dual de explicabilidad que combina LIME y PFI para la predicción de enfermedad cardíaca utilizando el conjunto de datos Cleveland de UCI. El estudio comparó siete algoritmos de clasificación y utilizó PFI para determinar la importancia global de las variables, mientras que LIME proporcionó explicaciones locales a nivel de cada paciente. Entre las características identificadas como relevantes se encontraron la depresión del segmento ST inducida por ejercicio, el tipo de dolor torácico, la frecuencia cardíaca máxima, la talasemia y otras variables clínicas. Los autores destacan que esta combinación permite disponer simultáneamente de una perspectiva global y una explicación local del comportamiento del modelo, con un menor costo computacional que otros métodos como SHAP. Sin embargo, también reconocen que LIME puede presentar variaciones en las explicaciones cuando cambia el muestreo utilizado para generar las perturbaciones locales.

Salah y Srinivas (2022) utilizaron técnicas de explicabilidad para analizar modelos destinados a estimar el riesgo cardiovascular a largo plazo a partir de factores observados durante la adolescencia. El estudio empleó información longitudinal de 14.083 participantes del estudio estadounidense Add Health y comparó diferentes algoritmos de Machine Learning. La importancia por permutación permitió identificar factores globalmente relevantes, mientras que los gráficos de dependencia parcial fueron utilizados para analizar relaciones lineales y no lineales entre determinadas características y la predicción. Entre las variables más importantes se encontraron la edad, el índice de masa corporal, el ingreso de los padres, la actividad física y el consumo de comida rápida. El estudio también complementó estas técnicas con SHAP para comparar diferentes formas de interpretar la importancia de los predictores.

La diversidad de técnicas utilizadas evidencia que no existe un único mecanismo de explicabilidad adecuado para todos los propósitos. Algunas técnicas se orientan principalmente a identificar la importancia global de las variables, mientras que otras buscan explicar casos particulares o visualizar relaciones entre las características y las predicciones. Por esta razón, diferentes investigaciones combinan métodos globales y locales para proporcionar una representación más completa del comportamiento de los modelos.

#### Limitaciones de la explicabilidad en salud

Aunque las técnicas XAI pueden aumentar la transparencia de los modelos, la literatura señala diferentes limitaciones que deben considerarse cuando se utilizan en contextos de salud. Una de las principales corresponde a la diferencia entre asociación predictiva y causalidad. Métodos como SHAP o LIME pueden identificar qué variables influyen en la salida de un modelo, pero estas contribuciones no demuestran que modificar una variable produzca necesariamente un cambio clínico equivalente. De manera similar, una característica con alta importancia predictiva no debe interpretarse automáticamente como un factor causal de la enfermedad.

Mienye et al. (2024), en una revisión sobre inteligencia artificial explicable en salud, señalan desafíos relacionados con la estabilidad de las explicaciones, la fidelidad con respecto al comportamiento real del modelo, los sesgos, la dificultad de integración en flujos clínicos y la ausencia de causalidad en muchos métodos post-hoc. Los autores también destacan que pequeñas variaciones en los datos pueden modificar las explicaciones obtenidas y que una representación simplificada puede generar una falsa sensación de transparencia si no refleja adecuadamente el funcionamiento del modelo subyacente. Asimismo, resaltan que las necesidades de explicación varían entre desarrolladores, profesionales de la salud y pacientes, por lo que el formato y nivel de detalle deben adaptarse al público objetivo.

Las limitaciones de XAI también se relacionan con la manera en que las personas interpretan las explicaciones. Rosenbacke et al. (2024), mediante una revisión sistemática sobre la confianza de los profesionales de la salud en aplicaciones de inteligencia artificial, encontraron que proporcionar explicaciones no garantiza necesariamente un aumento de la confianza. Las explicaciones complejas, contradictorias o extensas pueden aumentar la carga cognitiva y ser ignoradas durante la toma de decisiones. Por otra parte, una explicación aparentemente convincente puede generar sobreconfianza y llevar al usuario a aceptar una recomendación incorrecta del sistema. Los autores plantean que el propósito de la explicabilidad no debe ser maximizar la confianza en la inteligencia artificial, sino contribuir a establecer un nivel de confianza adecuadamente calibrado.

En conjunto, los trabajos revisados muestran que la explicabilidad puede aportar valor al análisis de modelos cardiovasculares al permitir identificar variables influyentes, examinar relaciones entre predictores y explicar resultados individuales. Sin embargo, también evidencian que una explicación técnicamente correcta no garantiza una interpretación clínica adecuada ni una comprensión efectiva por parte del usuario. La utilidad de XAI depende tanto de la fidelidad y estabilidad de la técnica empleada como de la forma en que las explicaciones son presentadas, del público al que están dirigidas y de la claridad con la que se comuniquen sus limitaciones. Por esta razón, la incorporación de mecanismos de explicabilidad en aplicaciones de salud debe acompañarse de una presentación responsable que distinga entre contribución predictiva, asociación y causalidad.

### 5.3 Comunicación y visualización del riesgo cardiovascular

La utilidad de una herramienta de estimación cardiovascular no depende únicamente de la capacidad del modelo para producir una estimación, sino también de la manera en que dicha información es presentada al usuario. La comunicación del riesgo puede incluir porcentajes, categorías, explicaciones textuales, recomendaciones, comparaciones entre escenarios o representaciones complementarias que permitan contextualizar el resultado. Estas características adquieren especial importancia cuando las herramientas pueden ser utilizadas por personas sin formación médica, ya que un porcentaje aislado puede resultar difícil de interpretar si no se acompaña de información que explique su significado, alcance y limitaciones.

Para analizar cómo se comunica actualmente el riesgo cardiovascular, se revisaron cuatro herramientas: **CVD Risk Estimator Plus** del American College of Cardiology, **PREVENT Calculator** de la American Heart Association, la calculadora **Framingham Risk Score** de la Canadian Cardiovascular Society y **QRISK3 Lifetime**. Aunque estas herramientas se basan en modelos y poblaciones diferentes, permiten observar distintas estrategias para presentar y contextualizar estimaciones cardiovasculares.

| Herramienta | Resultado principal | Forma de contextualización | Factores modificables | Comparación de escenarios | Recomendaciones | Limitaciones de comunicación identificadas |
|---|---|---|---|---|---|---|
| **ACC CVD Risk Estimator Plus** | Riesgo porcentual y categorías de riesgo | Recursos explicativos, categorías y revisión de valores previos | Parcialmente diferenciados | Sí, mediante funciones clínicas y escenarios proyectados | Generales, personalizadas, clínicas y preventivas | Orientación principalmente clínica; no se confirmó una explicación individual de la contribución de cada variable ni una representación uniforme de la incertidumbre |
| **AHA PREVENT Calculator** | Riesgo porcentual a 10 y 30 años | Explicación mediante frecuencias naturales y percentiles según edad y sexo | Reconocidos conceptualmente, aunque no se confirmó una separación visual completa | Permite recalcular, pero no está diseñada para estimar directamente el efecto real de una intervención | Preventivas y clínicas | La interpretación puede requerir conocimientos clínicos; el recálculo hipotético no debe interpretarse como beneficio clínico validado |
| **CCS Framingham Risk Score** | Riesgo cardiovascular a 10 años y edad cardíaca | Categorías de riesgo y edad cardíaca | Parcialmente identificables | Principalmente recálculo; no se confirmó comparación automática entre valor inicial y nuevo | Preventivas y clínicas en documentación complementaria | Parte de la orientación se encuentra fuera de la interfaz y no se confirmó una representación explícita de incertidumbre o contribución individual de variables |
| **QRISK3 Lifetime** | Riesgo cardiovascular a lo largo de la vida | Comparación entre situación actual y escenario hipotético de buen control | Sí, diferenciados explícitamente | Sí, mediante campos paralelos *Current* y *What if?* | Preventivas de forma indirecta mediante el escenario de control | No se confirmaron recomendaciones personalizadas detalladas ni representación explícita de incertidumbre; el escenario hipotético podría interpretarse erróneamente como garantía de beneficio |

El **CVD Risk Estimator Plus** combina resultados cuantitativos con categorías de riesgo, recomendaciones y recursos dirigidos tanto a profesionales como a pacientes. La herramienta permite introducir y modificar diferentes variables clínicas, consultar estimaciones previas y, en determinadas funciones, proyectar escenarios asociados con diferentes estrategias de tratamiento. Además, proporciona acceso a la metodología y a los modelos utilizados. Sin embargo, la revisión realizada no permitió confirmar que la herramienta muestre una descomposición individual de la contribución de cada variable comparable con técnicas de explicabilidad como SHAP, ni que presente una visualización uniforme de la incertidumbre asociada con cada estimación. 

La herramienta **PREVENT** presenta estimaciones porcentuales para horizontes de diez y treinta años y cuenta con documentación específica para apoyar la interpretación del resultado. Una característica relevante de su estrategia de comunicación es la recomendación de expresar el porcentaje mediante frecuencias naturales, por ejemplo indicando que determinado número de cada cien personas con características similares podría desarrollar enfermedad cardiovascular durante el periodo evaluado. Esta forma de expresión permite contextualizar el porcentaje mediante una representación potencialmente más intuitiva. La documentación también permite contextualizar el riesgo mediante percentiles de edad y sexo. No obstante, la American Heart Association advierte que modificar valores y recalcular el riesgo no permite estimar directamente cuánto disminuiría el riesgo real de una persona como consecuencia de una intervención específica. 

La calculadora **Framingham Risk Score** de la Canadian Cardiovascular Society utiliza como resultado principal un porcentaje de riesgo cardiovascular a diez años y lo complementa mediante el concepto de **edad cardíaca**. Esta medida permite contextualizar el resultado comparando el perfil cardiovascular de la persona con el correspondiente a una determinada edad equivalente. Además, la documentación complementaria incorpora categorías de riesgo y orientación preventiva y clínica. Aunque esta forma de presentación puede facilitar la interpretación del resultado, parte de la información necesaria para comprenderlo se encuentra fuera de la interfaz principal y no se confirmó que exista una comparación automática entre el valor original y un escenario modificado ni una representación explícita de la incertidumbre de la estimación. 

Por su parte, **QRISK3 Lifetime** incorpora una estrategia de comunicación basada explícitamente en la comparación de escenarios. La herramienta diferencia entre la situación actual del usuario y un escenario hipotético asociado con un mejor control de determinados factores modificables, utilizando columnas paralelas identificadas como *Current* y *What if?*. Además, distingue de manera explícita los factores modificables y permite cambiar valores relacionados con tabaquismo, índice de masa corporal, colesterol y presión arterial. Esta estructura facilita observar cómo cambia la estimación al modificar determinadas entradas. Sin embargo, el resultado obtenido bajo un escenario hipotético no debe interpretarse automáticamente como una garantía del efecto clínico real de modificar dichos factores. 

La comparación muestra que las herramientas revisadas utilizan diferentes estrategias para facilitar la interpretación del riesgo. Algunas complementan el porcentaje mediante categorías o recomendaciones, otras utilizan conceptos adicionales como la edad cardíaca, y QRISK3 Lifetime incorpora directamente una comparación entre el estado actual y un escenario hipotético. También existen diferencias en la manera en que se presentan los factores modificables, las advertencias, las limitaciones y la metodología utilizada para realizar el cálculo.

A pesar de estas diferencias, se identifican algunas limitaciones comunes. En las herramientas revisadas no se confirmó de manera consistente la presentación de intervalos de incertidumbre asociados con la estimación individual ni una explicación específica de cuánto contribuye cada variable al resultado. Asimismo, la posibilidad de modificar valores y recalcular el riesgo puede generar interpretaciones equivocadas si el usuario considera que la diferencia entre ambos resultados representa necesariamente el efecto clínico que produciría una intervención real. Estas observaciones muestran que la comunicación del riesgo requiere no solo presentar una estimación numérica, sino también explicar su significado, sus condiciones de aplicación y las limitaciones asociadas con la interpretación de escenarios hipotéticos.
### 5.4 Síntesis y posicionamiento de la propuesta

La revisión realizada muestra que las soluciones existentes para la evaluación cardiovascular abordan el problema desde perspectivas diferentes. Los modelos clínicos como Framingham, Pooled Cohort Equations, SCORE2, QRISK3 y PREVENT estiman riesgo cardiovascular utilizando poblaciones, desenlaces, horizontes temporales y conjuntos de variables específicos. Estas diferencias hacen que sus resultados no sean directamente intercambiables y resaltan la importancia de considerar el contexto poblacional y metodológico en el que cada modelo fue desarrollado y validado.

Asimismo, la literatura reciente evidencia un creciente interés por incorporar mecanismos de inteligencia artificial explicable en modelos de predicción cardiovascular. Técnicas como SHAP, LIME, Permutation Feature Importance y Partial Dependence Plots han sido utilizadas para identificar variables relevantes, analizar relaciones entre predictores y proporcionar explicaciones tanto globales como individuales. Sin embargo, estos trabajos también muestran que la explicabilidad presenta limitaciones importantes: una contribución predictiva no implica causalidad, la importancia de una variable no equivale necesariamente a un efecto clínico y las explicaciones pueden variar dependiendo del modelo, los datos y la técnica utilizada.

Por otra parte, las herramientas de riesgo cardiovascular revisadas muestran distintas estrategias para comunicar sus resultados. Algunas integran categorías, comparaciones o explicaciones dentro de la interfaz, mientras que otras dependen en mayor medida de documentos complementarios, guías clínicas o de la interpretación realizada por un profesional de la salud. Esto evidencia que la comunicación del riesgo no se limita a mostrar un porcentaje, sino que requiere contextualizar el resultado, explicar sus limitaciones y facilitar su interpretación dentro de un proceso preventivo o clínico.

En conjunto, el estado del arte permite identificar cuatro elementos relevantes para el diseño de soluciones orientadas a la evaluación cardiovascular: una estimación basada en datos, mecanismos de explicabilidad, herramientas para explorar escenarios y estrategias adecuadas de comunicación del resultado. Sin embargo, estos elementos no siempre se encuentran integrados de la misma manera en una única solución, y su implementación depende del propósito específico de cada herramienta, del público objetivo y del contexto clínico o educativo en el que será utilizada.

En este contexto, PULSO se posiciona como una propuesta de carácter educativo y preventivo que busca integrar en una misma plataforma un modelo de Machine Learning de clasificación, mecanismos de explicabilidad mediante SHAP, simulación de escenarios hipotéticos y generación de información preventiva mediante RAG. A diferencia de las calculadoras clínicas analizadas, el componente predictivo de PULSO no fue desarrollado a partir de una cohorte longitudinal orientada a estimar la probabilidad de un evento cardiovascular durante un horizonte temporal determinado. En su lugar, utiliza el *Cardiovascular Disease Dataset* y plantea un problema de clasificación binaria en el que la variable `cardio` representa la presencia o ausencia de enfermedad cardiovascular en los registros.

Por esta razón, la probabilidad generada por PULSO no debe interpretarse como equivalente a las estimaciones de riesgo a diez o treinta años proporcionadas por modelos clínicos como SCORE2, PREVENT, Framingham, Pooled Cohort Equations o QRISK. La propuesta tampoco pretende sustituir estas herramientas ni reemplazar la valoración de un profesional de la salud. Su aporte se encuentra principalmente en la integración de diferentes mecanismos orientados a facilitar la comprensión del comportamiento del modelo, explorar de manera controlada escenarios hipotéticos y complementar la estimación con información preventiva sustentada en fuentes seleccionadas.

La revisión realizada también permite identificar una limitación fundamental para la generalización de PULSO: el desempeño y significado de su clasificador dependen directamente de las características y representatividad del conjunto de datos utilizado. Por tanto, cualquier interpretación de sus resultados debe considerar las restricciones poblacionales y metodológicas del *Cardiovascular Disease Dataset*. En consecuencia, el valor del MVP debe evaluarse principalmente por su capacidad para integrar predicción, explicabilidad, simulación y comunicación responsable dentro de una experiencia educativa, y no por una equivalencia clínica con calculadoras cardiovasculares validadas para poblaciones específicas.

## 6. Solución propuesta

Se propone desarrollar PULSO, un producto mínimo viable (MVP) de una plataforma web orientada a la prevención y educación cardiovascular, cuyo propósito es facilitar que las personas no especializadas comprendan la información relacionada con sus factores cardiovasculares. La solución busca superar las limitaciones identificadas en el planteamiento del problema mediante la integración de un modelo predictivo de Machine Learning, mecanismos de explicabilidad, simulación de escenarios hipotéticos y un sistema de generación de información preventiva sustentada en fuentes médicas confiables. De esta manera, PULSO pretende ofrecer una experiencia que no se limite a presentar un resultado numérico, sino que permita comprender su significado, identificar los factores que influyen en él y explorar cómo varía la estimación bajo diferentes condiciones.

La plataforma estará dirigida principalmente a personas sin formación especializada en salud que deseen conocer y comprender información relacionada con sus características, hábitos y factores cardiovasculares. Para ello, el usuario ingresará los datos solicitados mediante una interfaz web diseñada para facilitar la comprensión de las variables y sus unidades de medida. Esta información será procesada por un modelo de Machine Learning de clasificación, entrenado utilizando el *Cardiovascular Disease Dataset*, publicado por sulianova en Kaggle. El modelo buscará estimar la probabilidad de pertenecer a la clase `cardio = 1`, asociada con la presencia de enfermedad cardiovascular en los registros del conjunto de datos. El resultado se presentará como una probabilidad estimada por el clasificador, acompañada de información que permita comprender su alcance y limitaciones. Esta estimación no constituye un diagnóstico médico ni representa la probabilidad de presentar un evento cardiovascular futuro durante un periodo determinado.

Para facilitar la interpretación del resultado, PULSO incorporará un mecanismo de explicabilidad basado en SHAP (SHapley Additive exPlanations), que permitirá identificar la contribución de las variables utilizadas por el modelo a cada predicción. A través de este componente, el usuario podrá conocer qué características tuvieron mayor influencia en la estimación obtenida y cómo contribuyeron al resultado. Las explicaciones se presentarán mediante un lenguaje comprensible para personas no especializadas, diferenciando los factores potencialmente modificables de aquellos que no pueden modificarse. No obstante, las contribuciones identificadas por SHAP describirán el comportamiento del modelo y no demostrarán relaciones causales entre las variables y la condición cardiovascular del usuario.

Adicionalmente, la plataforma contará con una funcionalidad de simulación que permitirá modificar determinadas variables potencialmente controlables y compatibles con el modelo seleccionado, con el propósito de explorar escenarios hipotéticos. El sistema conservará la estimación inicial y generará una nueva predicción a partir de los valores modificados, permitiendo comparar directamente ambos resultados. Esta funcionalidad tendrá un propósito educativo y exploratorio, ya que permitirá observar cómo responde el modelo ante diferentes combinaciones de características. Sin embargo, las variaciones observadas en la estimación no deberán interpretarse como una predicción del efecto clínico real de modificar un hábito, recibir un tratamiento o cambiar una condición de salud. La simulación tampoco sustituirá las recomendaciones proporcionadas por profesionales de la salud.

Como complemento, PULSO integrará un sistema basado en Retrieval-Augmented Generation (RAG), que utilizará un conjunto previamente seleccionado de guías clínicas y fuentes médicas confiables para proporcionar información preventiva relacionada con los factores cardiovasculares. Este componente combinará la recuperación de información documental con la generación de respuestas en lenguaje natural, buscando presentar explicaciones y recomendaciones preventivas de carácter educativo de manera sencilla y comprensible. Las respuestas deberán mantener referencias a las fuentes consultadas y respetar los límites establecidos para el proyecto, evitando generar diagnósticos, prescripciones médicas o indicaciones para modificar tratamientos. De esta manera, el componente RAG complementará la estimación del modelo y sus explicaciones sin reemplazar la valoración profesional.

Desde el punto de vista técnico, la solución se desarrollará como una plataforma web que integrará una interfaz de usuario, una API, una base de datos y los componentes de Machine Learning, explicabilidad, simulación y RAG. La API permitirá establecer la comunicación entre la interfaz y los diferentes servicios del sistema, mientras que la base de datos permitirá gestionar la información necesaria para el funcionamiento de la plataforma. Asimismo, el proyecto incorporará un workflow de desarrollo basado en GitHub, integración continua mediante GitHub Actions y prácticas básicas de MLOps para mantener la trazabilidad de los datos, los experimentos y las versiones de los modelos. La definición detallada de los componentes, sus responsabilidades y sus mecanismos de interacción se desarrollará en la sección de diseño y arquitectura.

En cuanto al estado actual del desarrollo, se ha seleccionado el *Cardiovascular Disease Dataset* y se ha realizado un análisis exploratorio de datos (EDA) para examinar sus características y evaluar su pertinencia para el componente predictivo. También se ha iniciado la implementación y prueba de diferentes algoritmos de clasificación, entre ellos regresión logística y árbol de decisión. La selección del modelo definitivo dependerá de la comparación de sus resultados mediante métricas apropiadas para el problema. Posteriormente, se continuará con la integración de los componentes de explicabilidad, simulación y RAG, el desarrollo de la plataforma web y la ejecución de las pruebas necesarias para verificar el funcionamiento conjunto del MVP. Así, la propuesta busca integrar en una misma solución la estimación probabilística, la explicación de resultados, la exploración de escenarios y el acceso a información preventiva, manteniendo un alcance educativo y sin sustituir la atención médica profesional.

## 7. Metodología de desarrollo

El desarrollo de PULSO se lleva a cabo mediante una metodología iterativa e incremental, orientada a construir, evaluar y perfeccionar progresivamente los componentes del MVP. Este enfoque responde a la naturaleza del proyecto, que integra análisis de datos, modelos de Machine Learning, explicabilidad, simulación, generación de información mediante RAG y desarrollo de software. Cada componente presenta desafíos técnicos que requieren experimentación y validación antes de su integración definitiva.

La metodología combina el prototipado iterativo con las etapas de CRISP-DM para el componente de datos y Machine Learning. Adicionalmente, contempla un workflow de desarrollo basado en GitHub, prácticas de integración continua mediante GitHub Actions y principios básicos de MLOps para mantener la trazabilidad de los experimentos y las versiones de los modelos. Estos mecanismos permitirán organizar el trabajo del equipo, evaluar los resultados de cada iteración y controlar la incorporación de cambios al sistema.

Hasta el momento, el trabajo desarrollado ha permitido seleccionar el *Cardiovascular Disease Dataset*, realizar un análisis exploratorio de datos (EDA) e iniciar la implementación y prueba de diferentes algoritmos de clasificación, entre ellos regresión logística y árbol de decisión. Las siguientes iteraciones estarán orientadas a completar la evaluación y selección del modelo, incorporar los mecanismos de explicabilidad y simulación, integrar el componente RAG y desarrollar y validar la plataforma web.

### 7.1 Enfoque metodológico

El desarrollo de PULSO se realiza mediante un enfoque de prototipado iterativo e incremental. Esta elección responde a la naturaleza del proyecto, el cual integra componentes con distintos niveles de incertidumbre: la calidad y pertinencia de los datos, el desempeño real de los modelos de Machine Learning, el comportamiento del mecanismo de explicabilidad y la pertinencia de las respuestas generadas por el sistema RAG no pueden determinarse completamente antes de construir y probar cada componente. Un enfoque estrictamente lineal dificultaría corregir oportunamente errores en los datos, modelos con desempeño insuficiente o funcionalidades que no comuniquen adecuadamente los resultados al usuario.

El proyecto avanza mediante ciclos sucesivos de diseño, construcción, prueba y ajuste. En cada ciclo se define un alcance acotado de trabajo, se desarrolla un entregable parcial y se evalúan sus resultados frente a los criterios establecidos. Cuando se identifican problemas o resultados insatisfactorios, se realizan ajustes antes de continuar con las siguientes actividades. De esta manera, cada entregable se considera un prototipo susceptible de perfeccionamiento, en lugar de esperar hasta el final del proyecto para verificar si la solución cumple los objetivos planteados.

Para el componente de datos y Machine Learning, las iteraciones toman como referencia las etapas de CRISP-DM, especialmente la comprensión de los datos, su preparación, el modelado y la evaluación. Estas etapas no se desarrollan necesariamente de forma secuencial, ya que los resultados obtenidos durante la experimentación pueden requerir regresar a fases anteriores para revisar variables, modificar transformaciones o ajustar los modelos. La selección del conjunto de datos, el EDA realizado y las pruebas iniciales con algoritmos de clasificación constituyen los primeros avances de este proceso.

Adicionalmente, el desarrollo contempla un workflow de ingeniería de software orientado a mantener la trazabilidad y calidad de los cambios. Las tareas se gestionarán mediante un backlog y se desarrollarán en ramas independientes de GitHub, posteriormente integradas mediante pull requests y revisión por parte de otro integrante del equipo. Este proceso estará acompañado por prácticas de CI/CD mediante GitHub Actions, con el propósito de automatizar la ejecución de pruebas, las validaciones de calidad y la integración de cambios. Para los componentes de Machine Learning se incorporarán prácticas básicas de MLOps relacionadas con el registro de los datos utilizados, las configuraciones de entrenamiento, las métricas obtenidas y las versiones de los modelos.

### 7.2 Iteraciones o fases de desarrollo

El desarrollo de PULSO se organiza mediante un proceso iterativo compuesto por diferentes fases, tomando como referencia CRISP-DM para el componente de datos y Machine Learning. Sobre esta estructura se incorporarán progresivamente las funcionalidades de explicabilidad, simulación y generación de información mediante RAG. Cada fase tiene un propósito específico y sus resultados sirven como base para las actividades posteriores, permitiendo realizar ajustes cuando los resultados obtenidos no sean satisfactorios.

Durante las primeras etapas se ha avanzado en la comprensión del problema predictivo, la selección del conjunto de datos y su análisis exploratorio. La elección del *Cardiovascular Disease Dataset* permitió orientar el componente de Machine Learning hacia un problema de clasificación binaria, utilizando la variable objetivo `cardio`. Asimismo, se ha iniciado la experimentación con diferentes algoritmos de clasificación para estudiar su comportamiento y determinar posteriormente cuál se integrará en la plataforma.

Las siguientes fases contemplan completar la preparación y evaluación de los datos, comparar los modelos desarrollados, seleccionar el clasificador definitivo e incorporar las funcionalidades restantes. Aunque las fases se presentan en un orden lógico, podrán ejecutarse de manera parcialmente paralela o revisarse cuando los hallazgos de una iteración hagan necesario modificar decisiones anteriores.

#### 1. Comprensión de los datos (Data Understanding)

Se identificaron y revisaron conjuntos de datos disponibles para determinar su pertinencia respecto al objetivo del proyecto. Como resultado de este proceso, se seleccionó el *Cardiovascular Disease Dataset*, publicado por sulianova en Kaggle, para el desarrollo del componente predictivo.

Posteriormente, se realizó un análisis exploratorio de datos (EDA) para examinar las características del conjunto de datos y evaluar su pertinencia para el proyecto. Este análisis constituye la base para identificar aspectos que deben considerarse durante la preparación de los datos y el entrenamiento de los modelos.

La comprensión de los datos continuará durante las siguientes iteraciones, especialmente cuando los resultados de los modelos permitan identificar posibles problemas relacionados con las variables utilizadas, la distribución de las clases o las características de los registros.

#### 2. Preparación de los datos (Data Preparation)

Los datos seleccionados serán sometidos a los procesos de limpieza y transformación necesarios para adecuarlos al entrenamiento de los modelos. Estas actividades podrán incluir el tratamiento de valores faltantes, la revisión de valores atípicos, la transformación de variables, la selección de características y la normalización o estandarización cuando corresponda.

La preparación deberá considerar la naturaleza de la variable objetivo `cardio` y las características de los algoritmos de clasificación que serán evaluados. Las transformaciones se definirán de acuerdo con los hallazgos del EDA y los requerimientos de cada modelo, procurando mantener la consistencia entre los datos utilizados durante el entrenamiento y aquellos que posteriormente ingresarán los usuarios de la plataforma.

Asimismo, los datos deberán dividirse en conjuntos de entrenamiento, validación y prueba, según el diseño experimental establecido. Se verificará que las transformaciones que aprenden parámetros de los datos se ajusten únicamente con la información de entrenamiento, evitando la fuga de información y conservando un conjunto independiente para la evaluación final.

#### 3. Modelado (Modeling)

Se desarrollarán y entrenarán diferentes modelos de Machine Learning de clasificación utilizando los datos previamente preparados. Entre los algoritmos considerados se encuentran regresión logística y árbol de decisión, cuyas pruebas iniciales ya han comenzado. También podrán evaluarse otros algoritmos, como Random Forest, de acuerdo con los resultados obtenidos y los recursos disponibles.

El modelado se orientará a estimar la probabilidad de pertenecer a la clase `cardio = 1`, asociada con la presencia de enfermedad cardiovascular en los registros del conjunto de datos. Esta salida deberá interpretarse como una estimación producida por el clasificador, sin atribuirle un horizonte temporal de predicción que no se encuentra definido en los datos.

Durante esta fase se experimentará con las configuraciones de los algoritmos y se documentarán las condiciones de entrenamiento y los resultados obtenidos. La finalidad será disponer de modelos comparables que puedan evaluarse posteriormente bajo criterios comunes.

#### 4. Evaluación (Evaluation)

Se analizará el desempeño de los modelos mediante métricas apropiadas para un problema de clasificación binaria. La evaluación considerará la capacidad de discriminación, el comportamiento de las probabilidades estimadas y las diferencias entre los resultados obtenidos por los algoritmos desarrollados.

Los modelos serán comparados utilizando conjuntos de datos y procedimientos de evaluación consistentes. Entre las métricas consideradas se encuentran precisión, sensibilidad, especificidad, F1-score y ROC-AUC, complementadas con métricas de calibración cuando corresponda. La selección del modelo no dependerá exclusivamente de una métrica individual, sino de una evaluación conjunta de su desempeño, estabilidad, interpretabilidad y pertinencia para el MVP.

Los resultados obtenidos se documentarán para facilitar la comparación entre experimentos y mantener la trazabilidad del proceso. Cuando se identifiquen resultados insatisfactorios, podrán realizarse ajustes en las etapas de preparación o modelado antes de seleccionar el clasificador definitivo.

#### 5. Explicabilidad mediante SHAP

Una vez seleccionado el modelo, se incorporará SHAP (SHapley Additive exPlanations) como mecanismo de explicabilidad. Esta etapa permitirá identificar la contribución de las diferentes variables a las predicciones realizadas por el clasificador.

Las explicaciones se adaptarán para que los usuarios no especializados puedan comprender cuáles características tuvieron mayor influencia en la estimación obtenida. Se procurará presentar los resultados mediante recursos visuales y un lenguaje comprensible, evitando que la interpretación dependa de conocimientos técnicos sobre Machine Learning.

La implementación deberá verificar que las explicaciones correspondan con el modelo seleccionado y con la salida que se presenta al usuario. Asimismo, se aclarará que las contribuciones identificadas describen el comportamiento del modelo y no demuestran relaciones causales entre las variables y la condición cardiovascular.

#### 6. Simulación

Se desarrollará una funcionalidad que permita modificar determinadas variables de entrada y obtener una nueva estimación mediante el modelo seleccionado. Las variables disponibles para esta funcionalidad estarán limitadas a factores potencialmente controlables y compatibles con el clasificador.

El sistema conservará la estimación inicial y permitirá compararla directamente con el resultado obtenido bajo el escenario hipotético. La interfaz diferenciará los datos proporcionados originalmente por el usuario de los valores utilizados durante la simulación.

Esta funcionalidad tendrá una finalidad educativa y exploratoria. Las variaciones observadas representarán cambios en la salida del modelo ante diferentes valores de entrada y no deberán interpretarse como efectos clínicos garantizados ni como recomendaciones para modificar tratamientos médicos.

#### 7. Generación de información mediante RAG

Se incorporará un sistema basado en Retrieval-Augmented Generation (RAG) que permita complementar los resultados mediante información proveniente de guías clínicas y fuentes médicas previamente seleccionadas.

El componente recuperará información pertinente de un corpus documental controlado y la utilizará para generar respuestas en lenguaje natural. Su finalidad será proporcionar explicaciones e información preventiva de manera comprensible, manteniendo referencias a las fuentes consultadas.

Las respuestas generadas deberán respetar el alcance educativo de PULSO. Por tanto, se evaluará que la información sea coherente con las fuentes recuperadas y que no incluya diagnósticos, prescripciones ni indicaciones para modificar tratamientos.

#### 8. Despliegue (Deployment)

Finalmente, los componentes desarrollados serán integrados en la plataforma web PULSO. Se incorporarán el modelo predictivo, el mecanismo de explicabilidad, la simulación y el sistema RAG, conformando una versión funcional del MVP.

Durante esta etapa se realizarán pruebas de integración y funcionamiento para identificar posibles errores y verificar la comunicación entre los diferentes componentes. También se comprobará que la interfaz presente los resultados de manera coherente y que el sistema conserve las restricciones establecidas para el uso de las estimaciones.

Asimismo, se verificará el funcionamiento del workflow de integración continua y se establecerá el versionamiento del modelo utilizado por la plataforma. Los resultados de las pruebas permitirán realizar los ajustes finales necesarios antes de la entrega del MVP.

### 7.3 Estrategia de validación

La validación de PULSO se realizará progresivamente durante las diferentes iteraciones del proyecto, con el propósito de identificar errores, verificar el cumplimiento de los requerimientos y realizar ajustes antes de avanzar hacia las siguientes etapas. La estrategia contemplará tanto el desempeño de los modelos de Machine Learning como el funcionamiento de la plataforma, la integración entre sus componentes, la calidad de las explicaciones, el comportamiento de las simulaciones y la pertinencia de la información proporcionada mediante RAG.

En las primeras iteraciones se ha realizado un análisis exploratorio del conjunto de datos seleccionado. Este trabajo proporciona una base para comprender sus características y orientar las decisiones de preparación y modelado. Posteriormente, se verificará que las transformaciones aplicadas sean reproducibles y que los conjuntos de entrenamiento, validación y prueba se utilicen de manera independiente. También se revisará la pertinencia de los datos para la población de aplicación que se delimite para el MVP.

Durante las etapas de modelado y evaluación se comprobará el desempeño de los diferentes clasificadores mediante métricas como precisión, sensibilidad, especificidad, F1-score, ROC-AUC y matriz de confusión, complementadas con métricas de calibración cuando sean pertinentes. La selección del modelo se realizará a partir de una evaluación conjunta de su capacidad de discriminación, calibración, estabilidad e interpretabilidad. Los resultados serán registrados junto con las configuraciones utilizadas para facilitar la comparación y reproducción de los experimentos.

La funcionalidad de explicabilidad será validada verificando que las variables mostradas mediante SHAP correspondan con las utilizadas por el modelo y que las explicaciones sean comprensibles para usuarios no especializados. También se comprobará que las contribuciones se presenten como explicaciones de la predicción y no como relaciones causales. Por su parte, la simulación será evaluada verificando que permita modificar únicamente las variables definidas para este propósito, genere nuevas estimaciones a partir de los valores modificados y conserve el resultado inicial para realizar una comparación directa.

El componente RAG será validado mediante pruebas sobre las consultas y respuestas generadas. Se evaluará la pertinencia de los documentos recuperados, la coherencia de las respuestas con las fuentes seleccionadas y el uso de un lenguaje sencillo. También se comprobará que las respuestas mantengan su carácter informativo y preventivo y que no generen diagnósticos, prescripciones o indicaciones que excedan el alcance de PULSO.

Finalmente, se realizarán pruebas técnicas, funcionales, de integración y de usabilidad para verificar el comportamiento conjunto del MVP. Las pruebas de usabilidad permitirán evaluar aspectos como la facilidad de navegación, la comprensión del lenguaje utilizado, la interpretación de las estimaciones y la claridad de las comparaciones entre escenarios. Los resultados obtenidos se utilizarán para identificar oportunidades de mejora y orientar los ajustes finales del sistema. Esta estrategia no constituye una validación clínica ni certifica PULSO para uso médico.

#### 7.3.1 Integración continua y validación del workflow

La validación técnica de PULSO estará integrada al workflow de desarrollo mediante prácticas de integración continua. Cada funcionalidad se desarrollará en una rama independiente de GitHub y, una vez terminada, será incorporada mediante una solicitud de incorporación (pull request). Antes de integrar los cambios a la rama principal, otro integrante del equipo revisará el código y verificará el cumplimiento de los criterios de aceptación establecidos para la tarea.

La creación o actualización de cada pull request activará un flujo de trabajo mediante GitHub Actions. Este flujo permitirá automatizar la instalación de dependencias, las comprobaciones de calidad del código y la ejecución de las pruebas automatizadas que se implementen. Las pruebas podrán incluir comprobaciones unitarias, funcionales, de integración y de regresión, además de las necesarias para verificar que el proyecto pueda compilarse y ejecutarse correctamente. La integración de cambios se condicionará al cumplimiento de las verificaciones y revisiones establecidas por el equipo.

Las pruebas de integración permitirán verificar la comunicación entre los principales componentes de PULSO, incluyendo la interfaz web, la API, el modelo predictivo, el mecanismo de explicabilidad, la funcionalidad de simulación y el componente RAG. De esta manera, no solamente se comprobará que cada componente funcione individualmente, sino también que el sistema completo mantenga un comportamiento coherente después de incorporar nuevos cambios.

Para los componentes relacionados con Machine Learning, el workflow incluirá prácticas básicas de MLOps orientadas a mantener la trazabilidad y reproducibilidad del proceso. Se registrarán las versiones de los datos utilizados, las configuraciones de entrenamiento, las métricas obtenidas y las versiones de los modelos generados. Esto permitirá identificar qué modelo fue utilizado para una determinada predicción y facilitará la reproducción de los experimentos cuando sea necesario entrenar o incorporar una nueva versión.

Después de que los cambios sean integrados, se realizará una validación del MVP en un entorno de prueba para comprobar el funcionamiento conjunto de la plataforma. Los errores, fallos y observaciones encontrados durante esta etapa serán registrados como nuevas tareas e incorporados al backlog para su priorización. De esta manera, la validación se convertirá en un proceso continuo que alimentará las siguientes iteraciones del proyecto.

En conjunto, la estrategia establece un ciclo de planificación, desarrollo, pruebas, revisión, integración, validación y mejora. La incorporación de integración continua, versionamiento de modelos y prácticas básicas de MLOps permitirá que el desarrollo de PULSO sea trazable, reproducible y controlado, mientras que las pruebas técnicas, funcionales y de usabilidad permitirán verificar progresivamente el cumplimiento de los requerimientos definidos.

### 7.4 Plan de trabajo, cronograma o hitos

El plan de trabajo de PULSO organiza las actividades necesarias para desarrollar progresivamente los componentes del MVP, desde la comprensión y preparación de los datos hasta el modelado, la explicabilidad, la simulación, la integración de RAG y la validación de la plataforma. Su propósito es establecer una secuencia de actividades, entregables e hitos que permita hacer seguimiento al avance del proyecto y coordinar el trabajo de los integrantes del equipo.

Hasta el momento, se ha avanzado en la selección del conjunto de datos, la realización del análisis exploratorio y el inicio de las pruebas con modelos de clasificación. Las actividades restantes incluyen completar la comparación y selección del modelo, desarrollar las funcionalidades de explicabilidad y simulación, incorporar el componente RAG, integrar los servicios del sistema y ejecutar las pruebas previstas para el MVP.

El cronograma deberá actualizarse de acuerdo con los avances alcanzados y las actividades pendientes, conservando como referencia el plan de trabajo establecido en el primer informe. Los ajustes deberán reflejar las decisiones técnicas tomadas durante el desarrollo y permitir verificar el cumplimiento de los objetivos antes de la entrega final del proyecto.

<img width="1600" height="649" alt="image" src="https://github.com/user-attachments/assets/098173d9-08e6-4518-b75a-5c1d7e8823d7" />
<img width="1600" height="597" alt="image" src="https://github.com/user-attachments/assets/f1d60b71-7a19-4a05-bb90-b9a779ebe7a6" />



## 8. Requerimientos

Los requerimientos de PULSO se definen a partir del alcance actualizado del MVP y de los componentes previstos para la solución. Estos requerimientos establecen las funcionalidades que debe ofrecer la plataforma y los atributos de calidad que deberán considerarse durante su implementación y validación. Su definición permite relacionar las decisiones de diseño y arquitectura con comportamientos verificables del sistema.

Debido a que PULSO utiliza un modelo de clasificación entrenado con el *Cardiovascular Disease Dataset*, la salida predictiva se interpreta como la probabilidad estimada de pertenecer a la clase `cardio = 1`. Por tanto, los requerimientos evitan presentar esta salida como equivalente a un riesgo clínico de presentar un evento cardiovascular durante un horizonte temporal determinado. Asimismo, las explicaciones, simulaciones y la información preventiva proporcionadas por la plataforma mantendrán un carácter educativo y no diagnóstico.

Los requerimientos se clasifican en funcionales y no funcionales. Los primeros describen las operaciones que deberá ejecutar la plataforma, mientras que los segundos establecen condiciones relacionadas con rendimiento, seguridad, privacidad, usabilidad, mantenibilidad, trazabilidad, interoperabilidad, reproducibilidad y fiabilidad. Algunos de estos requerimientos no funcionales deberán complementarse posteriormente con valores cuantitativos obtenidos o definidos durante las pruebas de rendimiento, integración y validación del MVP.

### 8.1 Requerimientos funcionales

Los requerimientos funcionales definen las operaciones principales que deberá ofrecer PULSO desde el ingreso de información hasta la presentación de la estimación, su explicación, la simulación de escenarios y la generación de información preventiva.

La explicabilidad y la simulación forman parte del comportamiento funcional de la plataforma. La primera deberá permitir identificar las variables que contribuyeron a una predicción específica, mientras que la segunda permitirá modificar únicamente determinados factores definidos como potencialmente controlables y observar el comportamiento del clasificador bajo un escenario hipotético. En ambos casos deberá comunicarse que los resultados representan el comportamiento del modelo y no relaciones causales o efectos clínicos garantizados.

El componente RAG complementará el resultado utilizando un corpus documental previamente seleccionado. Su función será proporcionar información preventiva respaldada por las fuentes recuperadas, manteniendo trazabilidad documental y evitando respuestas que excedan el alcance educativo definido para PULSO.

| ID | Requerimiento funcional |
|---|---|
| **RF-01** | El sistema deberá permitir al usuario ingresar las variables requeridas por la versión del modelo de Machine Learning integrada en PULSO. |
| **RF-02** | El sistema deberá mostrar para cada variable solicitada su unidad de medida, formato esperado e información necesaria para reducir errores de ingreso. |
| **RF-03** | El sistema deberá validar los datos ingresados antes de enviarlos al componente predictivo, verificando campos obligatorios, tipos de datos y rangos permitidos. |
| **RF-04** | Ante un dato inválido, incompleto o fuera de rango, el sistema deberá impedir la ejecución de la predicción y mostrar un mensaje que permita identificar y corregir el problema. |
| **RF-05** | El sistema deberá procesar los datos válidos mediante la versión del modelo de clasificación desplegada en el servicio de Machine Learning. |
| **RF-06** | El sistema deberá presentar la probabilidad estimada de pertenecer a la clase `cardio = 1` y comunicar de manera explícita el significado y alcance de esta salida. |
| **RF-07** | El sistema deberá aplicar el umbral de decisión definido para el modelo seleccionado cuando sea necesario presentar la clasificación correspondiente. |
| **RF-08** | El sistema deberá informar que la estimación generada no constituye un diagnóstico médico ni representa necesariamente el riesgo de presentar un evento cardiovascular futuro en un horizonte temporal determinado. |
| **RF-09** | El sistema deberá generar una explicación individual de la predicción mediante SHAP utilizando la misma versión del modelo que produjo la estimación. |
| **RF-10** | El sistema deberá identificar y presentar las variables con mayor contribución a la predicción, indicando la dirección de su influencia sobre la salida del modelo. |
| **RF-11** | El sistema deberá comunicar que las contribuciones obtenidas mediante SHAP explican el comportamiento del modelo y no demuestran relaciones causales. |
| **RF-12** | El sistema deberá permitir seleccionar y modificar únicamente las variables definidas como potencialmente controlables y habilitadas para simulación. |
| **RF-13** | El sistema deberá conservar los valores originales ingresados por el usuario al iniciar una simulación. |
| **RF-14** | El sistema deberá generar una nueva estimación utilizando los valores modificados en el escenario hipotético. |
| **RF-15** | El sistema deberá presentar de manera diferenciada la estimación original y la estimación obtenida mediante la simulación. |
| **RF-16** | El sistema deberá comunicar que la diferencia entre la estimación original y la simulada no representa un efecto clínico garantizado ni una recomendación de tratamiento. |
| **RF-17** | El sistema deberá generar información preventiva mediante el componente RAG utilizando exclusivamente el corpus documental seleccionado para el MVP. |
| **RF-18** | Las respuestas generadas mediante RAG deberán mantener trazabilidad hacia las fuentes documentales utilizadas para construir la respuesta. |
| **RF-19** | El sistema deberá evitar que el componente RAG proporcione diagnósticos, prescripciones o instrucciones para iniciar, modificar o suspender tratamientos médicos. |
| **RF-20** | Ante la imposibilidad de recuperar información suficiente o pertinente, el sistema deberá evitar generar una respuesta presentada como respaldada por las fuentes y deberá comunicar esta limitación al usuario. |
| **RF-21** | El sistema deberá permitir realizar una nueva evaluación modificando los datos de entrada sin conservar automáticamente una interpretación clínica del resultado anterior. |
| **RF-22** | El sistema deberá manejar fallos de los servicios de Machine Learning, RAG o almacenamiento mediante respuestas controladas, evitando presentar resultados parciales como si fueran completos. |

### 8.2 Requerimientos no funcionales

Los requerimientos no funcionales establecen las condiciones de calidad bajo las cuales deberán operar los componentes de PULSO. Dado que el MVP integra servicios con características diferentes, como predicción, explicabilidad y recuperación documental, estos requerimientos consideran no solamente la experiencia de uso, sino también la capacidad de verificar el comportamiento técnico de cada componente.

Los requerimientos de rendimiento, capacidad, disponibilidad y recuperación deberán contrastarse posteriormente mediante pruebas experimentales. Para ello se utilizarán métricas como latencia p50 y p95, tasa de errores, comportamiento bajo concurrencia, consumo de recursos y recuperación ante fallos parciales. Los valores objetivo definitivos deberán definirse antes de ejecutar las pruebas finales del MVP, de manera que sea posible verificar su cumplimiento.

También se consideran requerimientos asociados con reproducibilidad y trazabilidad del componente de Machine Learning y del sistema RAG. Estos atributos son necesarios para identificar qué modelo produjo una determinada salida, mantener consistencia entre experimentos y despliegues y comprobar qué documentos respaldaron la información preventiva generada.

| ID | Categoría | Requerimiento no funcional |
|---|---|---|
| **RNF-01** | Rendimiento | La predicción del modelo deberá cumplir el objetivo de latencia definido para el MVP bajo la carga concurrente establecida en el protocolo de pruebas. |
| **RNF-02** | Rendimiento | La generación de explicaciones SHAP deberá cumplir el objetivo de latencia definido para el MVP bajo la carga esperada. |
| **RNF-03** | Rendimiento | Las respuestas del componente RAG deberán evaluarse mediante latencia p50 y p95 y cumplir los límites establecidos para la carga esperada. |
| **RNF-04** | Capacidad | El sistema deberá soportar la cantidad de usuarios concurrentes definida para el escenario de carga esperada manteniendo la tasa de errores dentro del límite establecido. |
| **RNF-05** | Disponibilidad | El fallo de un servicio independiente deberá afectar únicamente las funcionalidades que dependan de dicho servicio, siempre que la arquitectura seleccionada lo permita. |
| **RNF-06** | Recuperación | Los servicios contenerizados deberán disponer de mecanismos de detección de estado y recuperación definidos para el entorno de despliegue. |
| **RNF-07** | Seguridad | Las comunicaciones que involucren información ingresada por los usuarios deberán utilizar los mecanismos de protección definidos para el entorno de despliegue y evitar exposición innecesaria de datos. |
| **RNF-08** | Privacidad | PULSO deberá minimizar la recopilación y persistencia de información personal y no requerirá datos identificables que no sean necesarios para las funcionalidades del MVP. |
| **RNF-09** | Usabilidad | La interfaz deberá indicar claramente el significado, formato y unidad de las variables solicitadas y diferenciar la estimación original de los escenarios simulados. |
| **RNF-10** | Accesibilidad | La interfaz deberá diseñarse considerando criterios básicos de accesibilidad web en textos, controles, estructura y presentación de información. |
| **RNF-11** | Reproducibilidad | Los mismos datos de entrada, utilizando la misma versión del modelo y las mismas condiciones de procesamiento, deberán producir la misma estimación cuando el algoritmo utilizado sea determinista o su aleatoriedad se encuentre controlada. |
| **RNF-12** | Trazabilidad ML | Deberá poder identificarse la versión del modelo, la configuración de entrenamiento y la versión o identificación del conjunto de datos asociados con cada modelo desplegado. |
| **RNF-13** | Trazabilidad RAG | Las respuestas generadas mediante RAG deberán permitir identificar los documentos o fragmentos utilizados como evidencia. |
| **RNF-14** | Mantenibilidad | Los componentes de frontend, backend, Machine Learning y RAG deberán mantener responsabilidades separadas de acuerdo con la arquitectura definida, de manera que puedan modificarse con impacto limitado sobre los demás componentes. |
| **RNF-15** | Interoperabilidad | La comunicación entre servicios deberá realizarse mediante interfaces, estructuras de datos y contratos definidos y documentados. |
| **RNF-16** | Fiabilidad | Los errores de validación, comunicación o ejecución deberán producir respuestas controladas y no resultados incorrectos presentados silenciosamente como válidos. |
| **RNF-17** | Compatibilidad | La aplicación deberá funcionar correctamente en los navegadores web definidos como objetivo para las pruebas del MVP. |
| **RNF-18** | Alcance responsable | Las explicaciones, simulaciones y respuestas generadas deberán mantener explícitamente el carácter educativo de PULSO y evitar presentar sus resultados como diagnóstico o recomendación clínica individual. |

## 9. Evaluación de alternativas

Para la definición de la arquitectura de PULSO se consideran tres alternativas: una arquitectura monolítica modular contenerizada, una arquitectura modular orientada a servicios contenerizados y una arquitectura de microservicios contenerizados.

Las tres alternativas comparten una serie de elementos tecnológicos y funcionales. PULSO será una plataforma web de acceso público, sin registro ni inicio de sesión, en la cual el usuario podrá ingresar directamente sus datos cardiovasculares y obtener una estimación de riesgo, explicaciones mediante SHAP, simulaciones e información preventiva mediante RAG. Asimismo, las tres propuestas contemplan el uso de una base de datos PostgreSQL alojada en Supabase, un proxy inverso como punto de entrada para las solicitudes externas y Docker para la contenerización de los componentes.

La principal diferencia entre las alternativas corresponde al grado de separación de los componentes de la aplicación. Esta diferencia se analiza considerando tres criterios: desempeño bajo la carga esperada, grado de acoplamiento y nivel de disponibilidad y tolerancia a fallos.

### 9.1. Desempeño bajo la carga esperada

La evaluación del desempeño considera la latencia de las solicitudes, la capacidad de procesamiento y el comportamiento de la plataforma ante solicitudes concurrentes.

#### Arquitectura monolítica modular contenerizada

La arquitectura monolítica modular concentra el backend, Machine Learning, SHAP, simulaciones y RAG en una única aplicación. Esto permite que los diferentes módulos se comuniquen directamente dentro del mismo proceso, reduciendo la sobrecarga asociada a la comunicación entre servicios.

Esta característica puede favorecer una menor latencia en las comunicaciones internas. Sin embargo, los diferentes módulos comparten los mismos recursos computacionales, por lo que una funcionalidad que requiera mayor capacidad de procesamiento puede afectar el rendimiento de las demás funcionalidades.

#### Arquitectura modular orientada a servicios contenerizados

Esta alternativa separa PULSO en servicios independientes para el frontend, backend, Machine Learning y RAG, ejecutados en contenedores Docker. Esta separación permite asignar recursos de manera independiente a los componentes que presenten mayores necesidades de procesamiento.

Aunque la comunicación entre servicios introduce una sobrecarga adicional frente a la comunicación interna de un monolito, esta arquitectura proporciona un equilibrio entre rendimiento y capacidad de crecimiento. Los servicios pueden optimizarse y escalarse de acuerdo con las necesidades específicas de cada componente.

Para PULSO, esta característica resulta especialmente relevante debido a que las operaciones de Machine Learning, SHAP, simulación y RAG pueden presentar diferentes requerimientos computacionales.

#### Arquitectura de microservicios contenerizados

La arquitectura de microservicios presenta el mayor nivel de separación, dividiendo funcionalidades como predicción cardiovascular, explicabilidad SHAP, simulación y RAG en servicios especializados.

Esta distribución permite escalar individualmente cada funcionalidad. Sin embargo, una solicitud puede requerir la comunicación entre múltiples microservicios, aumentando la cantidad de interacciones y la complejidad necesaria para controlar los tiempos de respuesta y los posibles errores de comunicación.

Para la carga esperada de PULSO, las tres alternativas pueden proporcionar un desempeño adecuado. La principal diferencia se encuentra en la capacidad de crecimiento y en el nivel de complejidad necesario para obtener dicho desempeño.

### 9.2. Grado de acoplamiento

El acoplamiento se analiza considerando la dependencia entre los componentes internos, la dependencia de servicios externos y la facilidad para modificar o sustituir componentes de la plataforma.

#### Arquitectura monolítica modular contenerizada

Aunque los componentes se encuentran organizados mediante módulos independientes a nivel de código, todos forman parte de una misma aplicación. Por esta razón, comparten recursos y un mismo ciclo de despliegue.

Una modificación en un componente puede requerir reconstruir y desplegar la aplicación completa. Esto genera un mayor nivel de dependencia entre los módulos, aunque la organización modular permite mantener separadas las responsabilidades dentro del código.

#### Arquitectura modular orientada a servicios contenerizados

La separación del frontend, backend, Machine Learning y RAG en servicios independientes reduce el acoplamiento entre los principales componentes de la plataforma.

Cada servicio puede evolucionar y desplegarse de manera independiente siempre que mantenga las interfaces de comunicación definidas. Esto facilita, por ejemplo, modificar el servicio de Machine Learning sin tener que modificar o desplegar nuevamente el frontend.

A diferencia de los microservicios, esta alternativa mantiene una cantidad limitada de servicios, lo que permite obtener independencia entre componentes sin introducir una fragmentación excesiva del sistema.

#### Arquitectura de microservicios contenerizados

Los microservicios presentan el menor acoplamiento entre componentes, ya que funcionalidades específicas como predicción, SHAP, simulación y RAG se encuentran separadas en servicios independientes.

Esta separación facilita reemplazar o actualizar componentes individualmente. Sin embargo, también aumenta la cantidad de interfaces y dependencias de comunicación que deben administrarse.

### 9.3. Disponibilidad y tolerancia a fallos

La disponibilidad y tolerancia a fallos se evalúan considerando el impacto que tendría la falla de un componente sobre el funcionamiento general de PULSO y los mecanismos disponibles para recuperar los servicios.

#### Arquitectura monolítica modular contenerizada

En la arquitectura monolítica, los principales componentes del backend forman parte de una misma aplicación. Por esta razón, una falla crítica que provoque la caída del proceso puede afectar simultáneamente las funcionalidades de predicción, SHAP, simulación y RAG.

Docker permite reiniciar el contenedor afectado y facilita la recuperación del servicio, pero el aislamiento de fallos entre funcionalidades es limitado.

#### Arquitectura modular orientada a servicios contenerizados

La separación en servicios independientes permite aislar parcialmente los fallos. Por ejemplo, una interrupción del servicio RAG no necesariamente implica que el servicio de Machine Learning o el backend dejen de funcionar.

Además, cada servicio puede reiniciarse y desplegarse de manera independiente. Esto permite reducir el impacto de determinados fallos y facilita las tareas de mantenimiento y recuperación.

Esta característica resulta importante para el crecimiento futuro de PULSO, ya que permite incorporar mecanismos adicionales de disponibilidad sin tener que transformar completamente la arquitectura de la aplicación.

#### Arquitectura de microservicios contenerizados

La arquitectura de microservicios proporciona un alto nivel de aislamiento entre componentes. Una falla en un microservicio específico puede limitar una funcionalidad determinada sin afectar necesariamente al resto de la plataforma.

Sin embargo, este nivel de aislamiento requiere mecanismos adicionales para gestionar errores, disponibilidad, comunicación entre servicios y recuperación. Por lo tanto, aunque ofrece mayores posibilidades de tolerancia a fallos, también implica una mayor complejidad operativa.

### 9.4. Comparación de las alternativas

A partir de los criterios definidos, se obtiene la siguiente comparación:

| Criterio | Monolítica modular | Orientada a servicios | Microservicios |
|---|---|---|---|
| Desempeño con la carga esperada | Adecuado | Adecuado | Adecuado |
| Comunicación interna | Directa dentro de la aplicación | Entre servicios | Entre múltiples microservicios |
| Escalabilidad individual | Baja | Media-Alta | Alta |
| Acoplamiento entre componentes | Medio-Alto | Medio-Bajo | Bajo |
| Facilidad de desarrollo inicial | Alta | Media-Alta | Baja |
| Complejidad de despliegue | Baja | Media | Alta |
| Aislamiento ante fallos | Bajo | Medio-Alto | Alto |
| Complejidad operativa | Baja | Media | Alta |
| Facilidad de mantenimiento | Alta | Alta | Media-Baja |
| Necesidad de infraestructura y configuración | Baja | Media | Alta |
| Posibilidad de crecimiento progresivo | Baja | Alta | Alta |

La comparación evidencia que las tres alternativas pueden responder a las necesidades de desempeño del MVP, pero presentan diferencias importantes en cuanto a escalabilidad, acoplamiento, mantenimiento y complejidad operativa.

La arquitectura monolítica presenta una menor complejidad inicial, pero concentra los componentes en una misma aplicación y limita la capacidad de escalar funcionalidades de manera independiente. Por otro lado, la arquitectura de microservicios proporciona un mayor nivel de independencia y escalabilidad, pero requiere una infraestructura y una gestión considerablemente más complejas.

La arquitectura modular orientada a servicios se encuentra entre ambas alternativas, permitiendo separar los componentes principales y asignar recursos de manera independiente sin introducir desde el inicio la fragmentación y complejidad propia de una arquitectura de microservicios.

### 9.5. Consideraciones comunes de seguridad y acceso

Las tres alternativas parten de la misma condición de acceso público: PULSO no contará con cuentas de usuario ni requerirá autenticación para utilizar sus funcionalidades.

Por esta razón, no es necesario implementar un servicio específico de autenticación para el acceso de los usuarios. Sin embargo, el backend deberá encargarse de validar los datos recibidos antes de procesarlos y controlar el acceso a Supabase.

Las credenciales privilegiadas utilizadas para acceder a la base de datos no deberán exponerse en el frontend. El acceso a los recursos internos deberá realizarse mediante el backend y los servicios correspondientes.

También será necesario considerar mecanismos de protección frente a solicitudes abusivas, independientemente de la arquitectura seleccionada. El proxy inverso podrá actuar como punto de entrada para centralizar parte de estas medidas y controlar las solicitudes provenientes del exterior.

### 9.6. Alternativa seleccionada

Después de comparar las tres propuestas, se selecciona la **arquitectura modular orientada a servicios contenerizados** como alternativa para PULSO.

La elección se fundamenta principalmente en el equilibrio que ofrece entre la complejidad de implementación del MVP y las necesidades de crecimiento futuro del proyecto. A diferencia de la arquitectura monolítica, esta alternativa permite separar los componentes principales de PULSO en servicios independientes, facilitando su mantenimiento, actualización y asignación de recursos.

Esta separación resulta especialmente conveniente debido a que PULSO integra funcionalidades con diferentes características y necesidades computacionales, como Machine Learning, explicabilidad mediante SHAP, simulaciones y consultas mediante RAG. Al encontrarse organizadas como servicios independientes, estas funcionalidades pueden evolucionar y optimizarse de manera individual.

Además, la arquitectura permite escalar los componentes que presenten una mayor demanda sin necesidad de escalar toda la aplicación. Por ejemplo, si en una etapa posterior el servicio de Machine Learning requiere mayores recursos computacionales debido al incremento de solicitudes, estos recursos pueden asignarse específicamente a dicho servicio.

Otro aspecto considerado es la tolerancia a fallos. Al estar los componentes separados, una falla en un servicio específico puede limitar una funcionalidad sin afectar necesariamente el funcionamiento completo de la plataforma. Esto proporciona un mayor aislamiento respecto a la arquitectura monolítica.

Aunque la arquitectura de microservicios ofrece un nivel superior de separación y escalabilidad, su implementación introduce una complejidad operativa mayor debido a la cantidad de servicios, comunicaciones y mecanismos de recuperación que deben administrarse. Para las necesidades actuales y el crecimiento esperado de PULSO, se considera más apropiado mantener una cantidad controlada de servicios con responsabilidades claramente definidas.

Finalmente, la arquitectura modular orientada a servicios permite que PULSO pueda evolucionar progresivamente. Si en el futuro alguna funcionalidad requiere un nivel de independencia, escalabilidad o disponibilidad mayor, el servicio correspondiente puede seguir evolucionando o, si resulta necesario, dividirse en componentes más especializados.

Por estas razones, la arquitectura modular orientada a servicios contenerizados constituye la alternativa seleccionada para PULSO, al proporcionar un equilibrio entre **desempeño, escalabilidad, desacoplamiento, tolerancia a fallos y complejidad de implementación**, manteniendo la posibilidad de adaptar la arquitectura a las necesidades futuras del proyecto.

## 10. Diseño y arquitectura

Explica cómo se estructura la solución a nivel conceptual y técnico.

### 10.1 Descripción general de la arquitectura

**Objetivo:** que el lector entienda cómo está pensado el sistema antes de ver cualquier representación visual.

Debe incluir:

- Tipo de arquitectura (cliente-servidor, basada en Backend as a Service, etc.).
- Enfoque general de la solución.
- Relación con la alternativa seleccionada previamente.

### 10.2 Componentes del sistema

Deben identificarse y explicarse:

- **Componentes principales** del sistema (frontend, backend, base de datos, servicios externos).
- **Responsabilidad** de cada uno.
- **Relación con los requerimientos** del sistema.

Esta parte debe terminar con el **diagrama de arquitectura del sistema**.

### 10.3 Interacción entre módulos

Debe explicarse:

- Cómo se comunican los componentes.
- Flujos de datos.
- Dependencias.
- Nivel de acoplamiento.

Esta parte debe terminar con el **diagrama de interacción entre módulos**.

### 10.4 Comportamiento

Debe explicarse cómo se comportan los componentes, describiendo las principales secuencias de la arquitectura y respondiendo preguntas como:

- ¿El flujo es eficiente? (latencia, pasos innecesarios).
- ¿Existen cuellos de botella?
- ¿La interacción refleja buen desacoplamiento?

En esta parte se utilizan **diagramas de secuencia**.

## 11. Implementación y avance actual

Documenta el estado real de construcción del sistema y el grado de avance alcanzado.

### 11.1 Stack tecnológico

Lista y justifica las tecnologías, frameworks, librerías y herramientas utilizadas.

### 11.2 Componentes implementados

Describe qué módulos o componentes ya fueron construidos, qué funcionalidades cubren y cuál es su estado actual.

### 11.3 Integraciones realizadas

Explica las integraciones ya desarrolladas con servicios externos, bases de datos, autenticación u otros componentes.

### 11.4 Pendientes para la entrega final

Indica qué elementos faltan por implementar, integrar, corregir o validar antes del cierre del proyecto.

## 12. Despliegue y operación preliminar

Describe cómo se ejecuta actualmente la solución, en qué entorno funciona, qué dependencias requiere y cuál es su estado de despliegue o configuración.

## 13. Validación preliminar

Presenta las pruebas o validaciones realizadas hasta el momento para verificar el comportamiento del sistema y su grado de cumplimiento frente a los requerimientos.

### 13.1 Pruebas por componentes

### 13.2 Pruebas de integración

### 13.3 Pruebas de usabilidad

## 14. Resultados parciales y discusión

Presenta los principales hallazgos obtenidos hasta el momento, interpreta su significado y analiza el nivel de avance del proyecto frente a los objetivos planteados.

## 15. Plan de cierre hacia la entrega final

Describe las actividades restantes, prioridades, riesgos y estrategia de cierre para completar el proyecto en las semanas finales.

## 16. Referencias

American College of Cardiology. (2026). *CVD Risk Estimator Plus*. https://www.acc.org/CVDPlus

American Heart Association. (2026). *Predicting Risk of cardiovascular disease EVENTs (PREVENT) calculator*. https://professional.heart.org/en/guidelines-and-statements/about-prevent-calculator

Ansari, Z. A., Khan, W., Ansari, M. S. H., Fatima, S., & Siddiqui, S. (2026). Dual explainability framework for heart disease prediction using LIME and permutation feature importance. *Discover Applied Sciences, 8*, 19. https://doi.org/10.1007/s42452-025-08108-5

Canadian Cardiovascular Society. (2024). *Framingham Risk Score (FRS) calculator*. https://ccs.ca/frs/

Chen, B., Ruan, L., Yang, L., Zhang, Y., Lu, Y., Sang, Y., Jin, X., Bai, Y., Zhang, C., & Li, T. (2022). Machine learning improves risk stratification of coronary heart disease and stroke. *Annals of Translational Medicine, 10*(21), 1156. https://doi.org/10.21037/atm-22-1916

D’Agostino, R. B., Sr., Vasan, R. S., Pencina, M. J., Wolf, P. A., Cobain, M., Massaro, J. M., & Kannel, W. B. (2008). General cardiovascular risk profile for use in primary care: The Framingham Heart Study. *Circulation, 117*(6), 743–753. https://doi.org/10.1161/CIRCULATIONAHA.107.699579

Endeavour Predict CIC. (2026). *QRISK3-lifetime cardiovascular risk calculator*. https://qrisk.org/lifetime/

European Society of Cardiology. (2026). *HeartScore*. https://www.heartscore.org/en_GB

Goff, D. C., Jr., Lloyd-Jones, D. M., Bennett, G., Coady, S., D’Agostino, R. B., Sr., Gibbons, R., Greenland, P., Lackland, D. T., Levy, D., O’Donnell, C. J., Robinson, J. G., Schwartz, J. S., Shero, S. T., Smith, S. C., Jr., Sorlie, P., Stone, N. J., & Wilson, P. W. F. (2014). 2013 ACC/AHA guideline on the assessment of cardiovascular risk: A report of the American College of Cardiology/American Heart Association Task Force on Practice Guidelines. *Journal of the American College of Cardiology, 63*(25 Pt B), 2935–2959. https://doi.org/10.1016/j.jacc.2013.11.005

Hippisley-Cox, J., Coupland, C., & Brindle, P. (2017). Development and validation of QRISK3 risk prediction algorithms to estimate future risk of cardiovascular disease: Prospective cohort study. *BMJ, 357*, j2099. https://doi.org/10.1136/bmj.j2099

Khan, S. S., Matsushita, K., Sang, Y., Ballew, S. H., Grams, M. E., Surapaneni, A., Blaha, M. J., Carson, A. P., Chang, A. R., Ciemins, E., Go, A. S., Gutierrez, O. M., Hwang, S.-J., Jassal, S. K., Kovesdy, C. P., Lloyd-Jones, D. M., Shlipak, M. G., Palaniappan, L. P., Sperling, L., … Coresh, J. (2024). Development and validation of the American Heart Association’s PREVENT equations. *Circulation, 149*(6), 430–449. https://doi.org/10.1161/CIRCULATIONAHA.123.067626

Mienye, I. D., Obaido, G., Jere, N., Mienye, E., Aruleba, K., Emmanuel, I. D., & Ogbuokiri, B. (2024). A survey of explainable artificial intelligence in healthcare: Concepts, applications, and challenges. *Informatics in Medicine Unlocked, 51*, 101587. https://doi.org/10.1016/j.imu.2024.101587

Rosenbacke, R., Melhus, Å., McKee, M., & Stuckler, D. (2024). How explainable artificial intelligence can increase or decrease clinicians’ trust in AI applications in health care: Systematic review. *JMIR AI, 3*, e53207. https://doi.org/10.2196/53207

Salah, H., & Srinivas, S. (2022). Explainable machine learning framework for predicting long-term cardiovascular disease risk among adolescents. *Scientific Reports, 12*(1), 21812. https://doi.org/10.1038/s41598-022-25933-5

SCORE2 Working Group & ESC Cardiovascular Risk Collaboration. (2021). SCORE2 risk prediction algorithms: New models to estimate 10-year risk of cardiovascular disease in Europe. *European Heart Journal, 42*(25), 2439–2454. https://doi.org/10.1093/eurheartj/ehab309

Zhu, X.-Y., Li, W., Pan, X.-Y., Li, T., & Yuan, G.-L. (2026). Explainable machine learning for long-term cardiovascular disease risk prediction in Chinese middle-aged and older adults: A 9-year longitudinal cohort study with web-based risk calculator. *Scientific Reports, 16*, 14998. https://doi.org/10.1038/s41598-026-45297-4
