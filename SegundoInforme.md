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

Presenta los conceptos, métodos, técnicas y términos fundamentales necesarios para comprender adecuadamente el problema, la solución propuesta y las decisiones técnicas del proyecto.

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

Para analizar las soluciones existentes relacionadas con la evaluación del riesgo cardiovascular, se revisaron diferentes calculadoras y herramientas utilizadas para estimar dicho riesgo. La comparación considera aspectos como la estimación del riesgo, las recomendaciones proporcionadas, el público objetivo, el alcance geográfico, la cantidad de información solicitada, la posibilidad de modificar los datos y la forma en que se presentan los escenarios de riesgo.

Las herramientas revisadas utilizan distintos modelos y metodologías para evaluar el riesgo cardiovascular, por lo que sus resultados no son necesariamente equivalentes. Algunas estiman la probabilidad de presentar eventos cardiovasculares durante un horizonte temporal específico, mientras que otras ofrecen funcionalidades adicionales para interpretar los resultados o explorar escenarios hipotéticos. Su análisis permite identificar características relevantes para el diseño de PULSO, especialmente aquellas relacionadas con la presentación comprensible de los resultados, la explicación de los factores considerados y la comparación entre escenarios.

La siguiente tabla presenta una síntesis de las características identificadas durante la revisión realizada en el primer informe.

| Solución | Estimación del riesgo | Recomendaciones | Público objetivo | Simulación / comparación | Características destacadas |
|---|---|---|---|---|---|
| **SCORE2 / HeartScore** | Sí, proporciona un porcentaje de riesgo | Sí, incluye recomendaciones personalizadas | Principalmente profesionales de la salud | Permite modificar los datos y recalcular el riesgo, pero no presenta directamente una comparación con el resultado inicial en la herramienta revisada | Orientada principalmente a población europea |
| **PREVENT** | Sí, proporciona un porcentaje de riesgo | Sí, principalmente como guía general para interpretar los resultados | Principalmente profesionales de la salud | Permite modificar los datos y recalcular el riesgo, pero no presenta directamente una comparación con el estado inicial en la herramienta revisada | Incorpora información cardiovascular, renal y metabólica |
| **Framingham – Canadian Cardiovascular Society** | Sí, proporciona un porcentaje de riesgo | Sí, principalmente como guía general para interpretar los resultados | Principalmente profesionales de la salud | Permite modificar los datos y recalcular el riesgo, pero no presenta directamente una comparación con el estado inicial en la herramienta revisada | Utiliza un modelo de estimación de riesgo cardiovascular |
| **CVD Risk Estimator Plus – PREVENT** | Sí, proporciona un porcentaje de riesgo | Sí, enfocadas en la persona evaluada | Principalmente profesionales de la salud | Permite modificar los datos y recalcular el riesgo, pero no presenta directamente una comparación con el estado inicial en la herramienta revisada | Presenta recomendaciones personalizadas |
| **CVD Risk Estimator Plus – Pooled Cohort** | Sí, proporciona un porcentaje de riesgo | No se identificaron recomendaciones en la herramienta revisada | Principalmente profesionales de la salud | Permite modificar los datos y recalcular el riesgo, pero no presenta directamente una comparación con el estado inicial en la herramienta revisada | Orientada principalmente al contexto estadounidense |
| **QRISK** | Sí, proporciona un porcentaje de riesgo | No se identificaron recomendaciones en la herramienta revisada | No delimitado en la revisión inicial | Permite comparar directamente el riesgo actual con un escenario hipotético | Solicita una cantidad amplia de información y presenta una interfaz sencilla |

### Análisis de las soluciones existentes

A partir de la comparación realizada, se observa que las herramientas revisadas cuentan con la capacidad de estimar el riesgo cardiovascular, generalmente mediante la presentación de un porcentaje. Sin embargo, existen diferencias importantes en la cantidad de información solicitada, la forma de presentar los resultados y las funcionalidades disponibles para su interpretación. Estas diferencias son relevantes para el diseño de una plataforma dirigida a personas no especializadas, ya que la utilidad de una estimación no depende únicamente del resultado numérico, sino también de la capacidad del usuario para comprender su significado y sus limitaciones.

En cuanto a las recomendaciones, la revisión inicial identificó que SCORE2 / HeartScore y CVD Risk Estimator Plus (PREVENT) proporcionan información personalizada relacionada con los resultados obtenidos. Por su parte, PREVENT y Framingham – Canadian Cardiovascular Society presentan principalmente información general que sirve como guía para interpretar las estimaciones. En las versiones de Pooled Cohort y QRISK examinadas durante el primer informe no se identificaron recomendaciones dentro de la herramienta. Estas observaciones evidencian diferencias en la manera en que las soluciones complementan sus resultados con información orientada a la prevención.

Respecto a la cantidad de información solicitada, QRISK destacó en la revisión inicial por requerir un conjunto amplio de datos. Esto permite considerar un mayor número de variables, aunque también incrementa la cantidad de información que debe proporcionar el usuario. Para una plataforma dirigida al público general, este aspecto representa una consideración importante de diseño, puesto que la disponibilidad de los datos y la facilidad para comprender los campos solicitados pueden influir en la experiencia de uso.

En relación con la experiencia de usuario, se identificaron diferencias entre las herramientas. Algunas están diseñadas principalmente para personas con conocimientos especializados en salud, lo que puede dificultar su interpretación por parte de usuarios no especializados. La revisión del primer informe también identificó oportunidades de mejora en la claridad de las interfaces y en la presentación de la información. Estos hallazgos constituyen referencias para el diseño de una interfaz que facilite el ingreso de datos, la comprensión de las estimaciones y la identificación de los factores considerados por el modelo.

Otro aspecto relevante es la modificación de los datos para explorar diferentes escenarios. Todas las herramientas revisadas permiten modificar los datos introducidos y realizar nuevamente el cálculo del riesgo. Sin embargo, existe una diferencia importante en la manera de presentar estos cambios. En las versiones examinadas de las herramientas distintas de QRISK, al modificar los datos se realiza un nuevo cálculo, pero no se presenta directamente una comparación entre el resultado original y el nuevo resultado dentro de la plataforma. QRISK sí permite realizar esta comparación directamente, mostrando el riesgo correspondiente al estado actual frente al obtenido en un escenario hipotético. Esta funcionalidad constituye una referencia para el componente de simulación de PULSO.

Finalmente, también se identifican diferencias en el alcance geográfico de las herramientas. SCORE2 está orientada principalmente a población europea, mientras que PREVENT y Pooled Cohort presentan un enfoque asociado a población estadounidense y QRISK al Reino Unido. Esto constituye un aspecto relevante al momento de interpretar los resultados, debido a que los modelos de riesgo pueden estar desarrollados y calibrados para poblaciones específicas. La procedencia de los datos y las características de la población utilizada durante el desarrollo de un modelo deben considerarse antes de interpretar sus resultados en otros contextos.

### Oportunidad identificada

A partir de la revisión, se observa que no existe una única característica que diferencie completamente a PULSO de las herramientas analizadas, ya que algunas soluciones existentes presentan funcionalidades que también se contemplan en el proyecto. Sin embargo, estas características se encuentran distribuidas de diferentes maneras entre las herramientas. La oportunidad identificada consiste en integrar funcionalidades relacionadas con la estimación, la explicación de resultados, la comparación de escenarios y el acceso a información preventiva dentro de una misma plataforma orientada a personas no especializadas.

Por ejemplo, SCORE2 / HeartScore constituye una referencia para la presentación de recomendaciones preventivas, mientras que QRISK aporta elementos relevantes para la comparación directa entre el estado inicial y los escenarios hipotéticos. Estas características representan referencias importantes para el diseño de PULSO. No obstante, las herramientas revisadas utilizan metodologías y poblaciones de desarrollo diferentes, por lo que sus estimaciones no deben considerarse directamente equivalentes a las generadas por el modelo de clasificación que se desarrollará en el proyecto.

En este sentido, PULSO propone integrar un modelo de Machine Learning de clasificación entrenado con el *Cardiovascular Disease Dataset*, mecanismos de explicabilidad mediante SHAP, simulación de escenarios e información preventiva sustentada en fuentes médicas confiables mediante RAG. A diferencia de las calculadoras que estiman la probabilidad de presentar un evento cardiovascular durante un horizonte temporal determinado, el componente predictivo de PULSO buscará estimar la probabilidad de pertenecer a la clase `cardio = 1`, asociada con la presencia de enfermedad cardiovascular en los registros del conjunto de datos. La propuesta busca que el usuario no solo obtenga una estimación, sino que también comprenda qué representa, identifique los factores que influyen en ella y explore escenarios hipotéticos de manera informada, sin interpretar los resultados como diagnósticos o predicciones clínicas de eventos futuros.

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

Presenta los requerimientos que guían el desarrollo de la solución.

### 8.1 Funcionales

Describe las funcionalidades y comportamientos que el sistema debe ofrecer.

### 8.2 No funcionales

Define atributos de calidad y restricciones del sistema, como rendimiento, seguridad, usabilidad, mantenibilidad o escalabilidad.

## 9. Evaluación de alternativas

Expone las alternativas tecnológicas o arquitectónicas consideradas, los criterios de comparación utilizados y la justificación de la opción seleccionada.

### Pregunta: ¿Cuál alternativa ofrece mejor desempeño bajo carga esperada?

**Criterios de comparación:**

- **Latencia promedio y máxima**: tiempo de respuesta de operaciones críticas.
- **Throughput (capacidad de procesamiento)**: número de solicitudes que el sistema puede manejar por unidad de tiempo.
- **Comportamiento bajo carga concurrente**: degradación del sistema cuando aumenta el número de usuarios simultáneos.

### Pregunta: ¿Qué grado de acoplamiento introduce cada opción?

**Criterios de comparación:**

- **Dependencia de servicios externos**: nivel en que el sistema depende de plataformas como APIs externas.
- **Interdependencia entre módulos internos**: qué tanto un cambio en un módulo afecta a otros.
- **Facilidad de sustitución de componentes**: capacidad de reemplazar una tecnología (ej: backend) sin rediseñar todo el sistema.

### Pregunta: ¿Qué nivel de disponibilidad y tolerancia a fallos ofrece cada alternativa?

**Criterios de comparación:**

- **Tiempo de disponibilidad (uptime esperado)**: porcentaje de tiempo en que el sistema está operativo.
- **Mecanismos de recuperación ante fallos**: existencia de redundancia, backups o reintentos automáticos.
- **Impacto de fallos parciales**: qué ocurre si un componente falla (¿cae todo el sistema o solo una parte?).

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

American College of Cardiology. (s. f.). *CVD Risk Estimator Plus*. https://www.acc.org/CVDPlus

American Heart Association. (s. f.). *PREVENT calculator*. https://professional.heart.org/en/guidelines-and-statements/about-prevent-calculator

Canadian Cancer Society. (s. f.). *FRS*. https://ccs.ca/frs/

QRISK. (s. f.). *QRISK3-lifetime cardiovascular risk calculator*. https://qrisk.org/lifetime/

