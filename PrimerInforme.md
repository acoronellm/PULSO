# Guía para el primer informe del proyecto

## Resumen / Abstract

Las enfermedades cardiovasculares constituyen la principal causa de muerte en el mundo y están asociadas tanto con factores no modificables como modificables, entre ellas la hipertensión arterial, el colesterol elevado, la obesidad, el tabaquismo y la inactividad física. Aunque existen herramientas digitales para estimar el riesgo cardiovascular, muchas están orientadas a profesionales de la salud, emplean modelos calibrados para poblaciones específicas y presentan resultados cuya interpretación puede resultar compleja para personas sin formación médica. Este proyecto propone el diseño e implementación de PULSO (Plataforma Inteligente para la Predicción Explicable y Simulación Personalizada del Riesgo Cardiovascular mediante Machine Learning y Aprendizaje Continuo), un producto mínimo viable orientado a la prevención y educación en salud cardiovascular. La plataforma permitirá registrar factores de riesgo, generar una estimación mediante modelos de aprendizaje automático, explicar la influencia de las variables utilizadas y comparar el resultado inicial con escenarios hipotéticos construidos mediante la modificación de factores potencialmente controlables. Asimismo, integrará un sistema basado en Retrieval-Augmented Generation para presentar información preventiva sustentada en guías clínicas y fuentes médicas confiables, mediante un lenguaje comprensible para usuarios no especializados. El proyecto se desarrollará mediante una metodología iterativa e incremental que comprenderá la selección y preparación de datos clínicos públicos, el entrenamiento y comparación de modelos, el diseño de la arquitectura, la implementación de la plataforma web, la integración de explicabilidad y RAG, y la validación experimental del sistema. Como resultado, se espera obtener un MVP funcional que ayude a las personas a comprender sus factores de riesgo y favorezca decisiones informadas de prevención, sin sustituir la valoración realizada por profesionales de la salud.

## 1. Introducción
El sector de la salud atraviesa un proceso de transformación impulsado por la digitalización de la información clínica, el crecimiento de la capacidad computacional y la aplicación de técnicas de inteligencia artificial al análisis de datos. En este contexto, el aprendizaje automático, la inteligencia artificial explicable, los sistemas de apoyo a la toma de decisiones y las plataformas digitales de salud ofrecen nuevas posibilidades para identificar patrones, estimar riesgos y comunicar información preventiva. Estas tecnologías adquieren especial relevancia frente a las enfermedades cardiovasculares, consideradas entre las principales causas de muerte en el mundo. Según la Organización Mundial de la Salud (OMS, 2025), aproximadamente 19,8 millones de personas murieron por enfermedades cardiovasculares en 2022, cifra equivalente al 32 % de las defunciones mundiales. La OMS también señala que muchas de estas enfermedades pueden prevenirse mediante la identificación y el manejo oportuno de factores conductuales y metabólicos, como el tabaquismo, la inactividad física, la alimentación poco saludable, la hipertensión arterial, la glucosa elevada, las alteraciones de los lípidos y el exceso de peso.

Actualmente existen herramientas como SCORE2, PREVENT, Framingham, Pooled Cohort y QRISK, diseñadas para estimar la probabilidad de que una persona presente un evento cardiovascular durante un periodo determinado. Sin embargo, estas soluciones difieren en las variables que emplean, la población para la cual fueron desarrolladas y la manera en que comunican sus resultados. Por ejemplo, SCORE2 fue diseñado para estimar el riesgo cardiovascular a diez años en poblaciones europeas, mientras que PREVENT utiliza información cardiovascular, renal y metabólica y está orientado principalmente a apoyar las conversaciones preventivas entre los profesionales de la salud y sus pacientes (American Heart Association [AHA], s. f.; European Society of Cardiology [ESC], s. f.-a). Además, algunas de estas herramientas presentan porcentajes y términos clínicos que pueden resultar difíciles de interpretar para personas no especializadas. Aunque generalmente permiten modificar los datos y repetir el cálculo, no siempre explican claramente la influencia de cada variable ni muestran una comparación comprensible entre el resultado original y los escenarios hipotéticos explorados.

Esta situación evidencia la necesidad de diseñar una solución tecnológica que no se limite a proporcionar un porcentaje de riesgo, sino que facilite su comprensión y uso responsable. La oportunidad consiste en transformar una estimación probabilística en una experiencia educativa mediante la explicación de los factores considerados, la identificación de las variables que más influyen en el resultado y la comparación entre la condición inicial del usuario y diferentes escenarios hipotéticos. Esta necesidad también responde a las limitaciones de generalización de los modelos existentes, puesto que el riesgo cardiovascular no se comporta de manera uniforme entre regiones y poblaciones. De hecho, la ESC y la Sociedad Interamericana de Cardiología adelantan una iniciativa para recalibrar SCORE2 con datos de América Latina y el Caribe, debido a que su versión original fue desarrollada con información de poblaciones europeas (ESC, s. f.-b). Por tanto, una solución de este tipo debe informar la procedencia de los datos, las condiciones de aplicación y las limitaciones de sus predicciones.

En respuesta a esta necesidad, se propone PULSO (Plataforma Inteligente para la Predicción Explicable y Simulación Personalizada del Riesgo Cardiovascular mediante Machine Learning y Aprendizaje Continuo), una plataforma web orientada principalmente a personas no especializadas. El sistema integrará modelos de aprendizaje automático entrenados con datos clínicos públicos, mecanismos de explicabilidad individual y global, comparación entre el riesgo inicial y escenarios hipotéticos, y un componente basado en Retrieval-Augmented Generation para proporcionar información preventiva sustentada en guías clínicas y fuentes médicas confiables. Su diseño tendrá en cuenta principios de autonomía, seguridad, transparencia, explicabilidad, inclusión y responsabilidad, considerados por la OMS como fundamentales para el uso ético de la inteligencia artificial en la salud (OMS, 2021). De esta manera, PULSO buscará fortalecer la prevención y la educación cardiovascular, sin sustituir el diagnóstico, el tratamiento ni la valoración realizada por un profesional de la salud.


## 2. Planteamiento del problema

El problema central que aborda este trabajo es la dificultad que enfrentan las personas no especializadas para obtener, interpretar y utilizar de manera responsable información personalizada sobre sus factores de riesgo cardiovascular, debido a que las herramientas disponibles suelen ofrecer estimaciones aisladas, emplear lenguaje clínico, ofrecer explicaciones limitadas y estar diseñadas para poblaciones o contextos diferentes.

Por tanto, el problema no se define como la inexistencia de una plataforma que integre Machine Learning, explicabilidad y RAG. Estas tecnologías representan componentes de la solución; lo que se pretende atender es la limitada capacidad de los usuarios para comprender qué significa una estimación de riesgo, qué factores influyen en ella, cuáles podrían ser modificables y cuáles son los límites del resultado obtenido

### 2.1 Descripción del problema

Las enfermedades cardiovasculares representan una problemática relevante de salud pública. Según la Organización Mundial de la Salud (OMS, 2025), aproximadamente 19,8 millones de personas murieron por estas enfermedades en 2022, lo que equivale al 32 % de las defunciones mundiales. Una parte importante del riesgo cardiovascular se relaciona con factores que pueden detectarse o modificarse, como el tabaquismo, la inactividad física, la alimentación poco saludable, la hipertensión arterial, la glucosa elevada, las alteraciones del colesterol y el exceso de peso. Por esta razón, la identificación temprana y la comprensión de estos factores son importantes para promover conductas preventivas y facilitar la búsqueda oportuna de orientación profesional.

Aunque existen herramientas como SCORE2, PREVENT, Framingham y QRISK para estimar la probabilidad de presentar eventos cardiovasculares, sus resultados no siempre son comprensibles para personas sin conocimientos médicos. Algunas presentan porcentajes y términos clínicos sin explicar suficientemente qué significa el resultado, cuáles variables tuvieron mayor influencia o cuáles son las limitaciones de la estimación. Además, varios modelos fueron desarrollados para poblaciones específicas: SCORE2 se diseñó principalmente con datos europeos, mientras que PREVENT está orientado al contexto estadounidense y al apoyo de conversaciones preventivas entre profesionales y pacientes (American Heart Association [AHA], 2026; European Society of Cardiology [ESC], s. f.-a). Esta situación limita su aplicación directa en otros contextos, ya que el desempeño de una estimación puede variar entre poblaciones. De hecho, actualmente se desarrolla SCORE2-LAC para adaptar este tipo de evaluación a América Latina y el Caribe (ESC, s. f.-b).

Como consecuencia, las personas no especializadas pueden tener dificultades para interpretar responsablemente su riesgo cardiovascular, reconocer los factores que más influyen en él y comprender el significado de los escenarios hipotéticos. Una estimación baja puede generar una falsa sensación de seguridad, mientras que un resultado alto puede producir preocupación o decisiones sin acompañamiento profesional. Por tanto, el problema central corresponde a la limitada capacidad de los usuarios no especializados para obtener, comprender y utilizar información personalizada sobre su riesgo cardiovascular, debido a la complejidad de las herramientas disponibles, la escasa explicación de sus resultados, la ausencia de comparaciones claras y las limitaciones de generalización de los modelos. Esta problemática evidencia la necesidad de presentar las predicciones de manera comprensible, explicable y responsable, sin reemplazar la valoración de un profesional de la salud (OMS, 2021).

### 2.2 Justificación

El desarrollo de PULSO se justifica, en primer lugar, por la magnitud de las enfermedades cardiovasculares y por la posibilidad de prevenir una parte importante de sus consecuencias mediante la identificación y el manejo oportuno de los factores de riesgo. La OMS (2025) señala que es fundamental detectar las enfermedades cardiovasculares tan pronto como sea posible para iniciar su manejo mediante orientación profesional y, cuando corresponda, tratamiento médico. En este sentido, disponer de información comprensible sobre los factores de riesgo puede contribuir a que las personas reconozcan la importancia de la prevención y busquen oportunamente atención profesional.

Desde la perspectiva social, el proyecto busca reducir la distancia existente entre la complejidad técnica de los modelos predictivos y la capacidad de interpretación del público general. No es suficiente comunicar que una persona presenta determinado porcentaje de riesgo; también es necesario explicar qué representa ese valor, cuáles factores fueron considerados y cuáles influyeron con mayor intensidad. Esta forma de comunicación puede fortalecer la alfabetización en salud, entendida como la capacidad para acceder, comprender y utilizar información relacionada con el cuidado y la prevención.

PULSO también pretende aportar a la educación preventiva mediante la comparación entre la condición inicial y diferentes escenarios hipotéticos. Esta funcionalidad permitirá que el usuario observe cómo cambia la predicción cuando se modifican determinadas variables admitidas por el modelo. Sin embargo, la plataforma deberá aclarar que estos resultados representan asociaciones matemáticas y no efectos clínicos garantizados. La simulación tendrá una finalidad educativa y exploratoria, no sustituirá la formulación de un plan terapéutico ni permitirá recomendar cambios en medicamentos o tratamientos.

La pertinencia social y práctica del proyecto también se relaciona con el contexto colombiano. El Ministerio de Salud y Protección Social (2023) plantea que el abordaje de las enfermedades no transmisibles requiere fortalecer la atención primaria, el empoderamiento de las personas y las comunidades y la aplicación de intervenciones que contribuyan a reducir la morbilidad, la mortalidad prematura y la discapacidad. PULSO puede apoyar estos propósitos al presentar información preventiva de manera accesible, aunque no formará parte inicialmente de un servicio asistencial ni reemplazará las rutas institucionales de atención.

Desde el punto de vista técnico, el proyecto permite integrar conocimientos de análisis de datos, Machine Learning, inteligencia artificial explicable, ingeniería de software, diseño de bases de datos, desarrollo de API, experiencia de usuario y recuperación aumentada por generación. La comparación de varios modelos permitirá seleccionar una alternativa considerando no solamente su exactitud, sino también su capacidad de discriminación, calibración, estabilidad, interpretabilidad y costo computacional. Esta evaluación es necesaria porque un modelo puede clasificar adecuadamente a los usuarios, pero producir probabilidades que no representen correctamente la frecuencia real de los eventos.

Desde la perspectiva académica, PULSO constituye una experiencia de diseño tecnológico suficientemente compleja para un proyecto de Ingeniería de Sistemas. Su desarrollo requiere definir requerimientos, comparar alternativas, diseñar una arquitectura, gestionar datos, construir e integrar componentes, implementar mecanismos de seguridad y realizar pruebas técnicas y de usuario. Además, permite estudiar problemas propios de la inteligencia artificial aplicada a la salud, como el sesgo de los datos, la generalización, la explicabilidad, la privacidad, la trazabilidad y la comunicación responsable de resultados.

Finalmente, el valor del proyecto no dependerá exclusivamente de alcanzar una métrica elevada de predicción. Una plataforma puede presentar un desempeño algorítmico adecuado y, al mismo tiempo, resultar poco útil o riesgosa si los usuarios no comprenden sus resultados. Por esta razón, la validación de PULSO deberá considerar conjuntamente el desempeño del modelo, la calidad de las explicaciones, el funcionamiento de la plataforma, la pertinencia de las respuestas recuperadas y la comprensión de los usuarios. La integración de estas dimensiones constituye la principal pertinencia técnica y práctica de la solución propuesta.

### 2.3 Restricciones y supuestos iniciales
**Restricciones**

  **1**. Tiempo y alcance académico. El proyecto será desarrollado dentro del tiempo asignado para el Proyecto Final y por un equipo de tres estudiantes. Por esta razón, el resultado             será un producto mínimo viable y no una plataforma certificada para uso clínico.
  
  **2**. Disponibilidad de datos. El entrenamiento dependerá de conjuntos de datos clínicos públicos. Su tamaño, calidad, actualidad, balance, cantidad de variables y presencia de                valores faltantes limitarán el desempeño de los modelos.
  
  **3**. Representatividad poblacional. Los datos disponibles podrían no representar adecuadamente a la población colombiana o latinoamericana. Esta restricción es relevante porque los           modelos de riesgo deben validarse o recalibrarse al utilizarse en poblaciones diferentes a aquellas con las que fueron construidos (ESC, s. f.-b).
  
  **4**. Alcance preventivo y educativo. PULSO no realizará diagnósticos médicos, no prescribirá medicamentos, no recomendará suspender tratamientos y no sustituirá la consulta con               profesionales de la salud.
  
  **5**. Datos proporcionados por el usuario. La plataforma dependerá parcialmente de información autodeclarada. Los errores de medición, desconocimiento, omisión o digitación podrán             afectar el resultado.
  
  **6**. Interpretación de las simulaciones. Los escenarios se construirán modificando las entradas del modelo. Una disminución del riesgo estimado no demostrará causalidad ni                    garantizará que el riesgo clínico real disminuya en la misma proporción. Algunas ecuaciones de riesgo no fueron diseñadas para calcular el efecto directo de tratamientos o               intervenciones (AHA, 2026).
  
  **7**. Limitaciones de la inteligencia artificial generativa. La utilización de RAG reduce, pero no elimina, el riesgo de generar respuestas incompletas, imprecisas o                           descontextualizadas. Las salidas deberán conservar vínculos con las fuentes y advertencias sobre su carácter informativo.
  
  **8**. Recursos tecnológicos. El entrenamiento, almacenamiento y despliegue estarán condicionados por la capacidad computacional, los servicios disponibles y el presupuesto del equipo.
  
  **9**. Privacidad y seguridad. El MVP deberá minimizar la recopilación de información personal y proteger los datos almacenados. No se utilizarán historias clínicas identificables sin          las autorizaciones, medidas de seguridad y procedimientos éticos correspondientes. La protección de la autonomía y la privacidad constituye un principio fundamental para el uso          de la inteligencia artificial en salud (OMS, 2021).
  
  **10**. Delimitación de la predicción. El MVP deberá definir con precisión el evento cardiovascular, el horizonte temporal y la población para los cuales se realizará la estimación.             No se asumirán como equivalentes diferentes enfermedades o desenlaces cardiovasculares.
  
**Supuestos iniciales**

  **1**. Se encontrarán conjuntos de datos públicos con variables suficientes para entrenar y comparar modelos de riesgo cardiovascular dentro del alcance del MVP.
  
  **2**. Los usuarios dispondrán de un dispositivo con navegador web y conexión a internet.
  
  **3**. Los usuarios conocerán o podrán consultar parte de la información solicitada, como edad, peso, presión arterial y resultados básicos de laboratorio.
  
  **4**. Las variables estarán definidas con unidades de medida, rangos válidos e instrucciones comprensibles para reducir errores en el ingreso de datos.
  
  **5**. Será posible seleccionar guías clínicas y fuentes médicas confiables para construir un corpus documental controlado para el sistema RAG.
  
  **6**. Los datos podrán dividirse adecuadamente en conjuntos de entrenamiento, validación y prueba, evitando que los mismos registros sean utilizados simultáneamente para entrenar y            evaluar el modelo.
  
  **7**. Los modelos se evaluarán mediante métricas de discriminación, calibración y clasificación apropiadas para la naturaleza y distribución de los datos.
  
  **8**. La plataforma conservará el resultado inicial para compararlo con los escenarios hipotéticos y diferenciará visualmente los datos reales de los valores simulados.
  
  **9**. Las variables modificadas durante la simulación estarán limitadas a factores potencialmente controlables y compatibles con el modelo seleccionado.
  
  **10**. Las explicaciones indicarán la contribución de las variables a la predicción, pero no afirmarán que exista una relación causal.


## 3. Alcance del proyecto

El alcance de PULSO comprende el diseño e implementación de un MVP (Producto Mínimo Viable) sobre una plataforma web orientada a la prevención y predicción de problemas cardiovasculares, dirigida principalmente a personas no especializadas. Este alcance delimita tanto las funcionalidades que serán desarrolladas como aquellas que quedan fuera del proyecto, en coherencia con las restricciones y supuestos descritos en la sección 2.3.

**El proyecto incluye:**

1. El registro y la gestión de la información relacionada con los factores de riesgo cardiovascular ingresada por el usuario.
2. El entrenamiento, la comparación y la selección de modelos de Machine Learning entrenados con datos clínicos públicos para estimar el riesgo cardiovascular.
3. La incorporación de mecanismos de explicabilidad mediante SHAP que permitan identificar los factores que más contribuyen a cada predicción.
4. Una funcionalidad de simulación que permita modificar variables potencialmente controlables (como peso, presión arterial, colesterol y actividad física) y comparar el escenario hipotético con el resultado inicial.
5. Un sistema basado en RAG que consulte guías clínicas y fuentes médicas confiables para generar información y recomendaciones preventivas en un lenguaje sencillo y comprensible.
6. El diseño e implementación de una base de datos para la gestión de la información de la plataforma.
7. El diseño e implementación de una API que integre los diferentes servicios del sistema (modelo predictivo, explicabilidad, simulación y RAG) con la interfaz web.
8. El diseño e implementación de una interfaz web orientada principalmente a personas no especializadas.
9. Una validación experimental que permita evaluar el desempeño de la plataforma y de los modelos utilizados mediante datos de pacientes no evaluados previamente en el entrenamiento.

**El proyecto no incluye:**

1. La generación de diagnósticos médicos, la prescripción de medicamentos ni la recomendación de modificar o suspender tratamientos.
2. Una validación clínica certificada ni un proceso de aprobación regulatoria que permita utilizar PULSO como dispositivo médico.
3. La integración con historias clínicas electrónicas institucionales ni el uso de información identificable de pacientes reales.
4. La prestación de atención asistencial en tiempo real ni la sustitución de la consulta con profesionales de la salud.
5. La cobertura de todas las enfermedades o eventos cardiovasculares posibles; el MVP delimitará un evento cardiovascular, un horizonte temporal y una población específicos para la estimación.
6. El desarrollo de aplicaciones móviles nativas, dado que la solución se limitará a una plataforma web.
7. La recalibración exhaustiva de los modelos para todas las poblaciones latinoamericanas, aunque las limitaciones de generalización identificadas serán documentadas.
8.  Mecanismos básicos de actualización de los modelos que permitan incorporar aprendizaje continuo dentro del alcance del MVP.


## 4. Objetivos

A partir del problema planteado en la sección 2 y del alcance definido en la sección 3, se establece a continuación el objetivo general del proyecto y los objetivos específicos que orientarán su desarrollo.

### 4.1 Objetivo general

Diseñar e implementar un MVP sobre una plataforma web que permita evaluar de manera explicable el riesgo cardiovascular de una persona mediante técnicas de Machine Learning, incorporando simulación personalizada de escenarios, identificación de los factores asociados a dicho riesgo y generación de información y recomendaciones preventivas basadas en guías clínicas, utilizando un lenguaje sencillo y comprensible para personas no especializadas.

### 4.2 Objetivos específicos

1. Identificar y seleccionar conjuntos de datos clínicos públicos pertinentes para el entrenamiento y la validación de modelos de estimación del riesgo cardiovascular.
2. Desarrollar y comparar modelos de Machine Learning entrenados con los datos seleccionados, con el fin de determinar el modelo más adecuado según criterios de desempeño, calibración, estabilidad e interpretabilidad.
3. Implementar mecanismos de explicabilidad mediante SHAP que permitan identificar la contribución de las variables consideradas en las predicciones generadas por el modelo seleccionado.
4. Diseñar e implementar una funcionalidad de simulación que permita modificar variables potencialmente controlables y comparar el escenario hipotético resultante con el riesgo estimado inicialmente.
5. Integrar un sistema basado en Retrieval-Augmented Generation que genere información y recomendaciones preventivas a partir de guías clínicas y fuentes médicas confiables.
6. Diseñar e implementar la arquitectura, la base de datos y la API que permitan la integración de los componentes de la plataforma (modelo predictivo, explicabilidad, simulación y RAG).
7. Validar el desempeño de los modelos y el funcionamiento de la plataforma mediante pruebas técnicas, funcionales y de usabilidad, utilizando datos y usuarios no involucrados en las etapas previas de desarrollo.


## 5. Solución propuesta

Se propone desarrollar PULSO, un MVP de una plataforma web de Prevención y Predicción (P&P) orientada a la prevención y educación en salud cardiovascular. La plataforma permitirá al usuario ingresar información relacionada con sus factores de riesgo y obtener una evaluación de su riesgo cardiovascular.

Loe usuarios finales para esta plataforma serán las personas del común, es decir, cualquier persona especializada o no en el tema la va poder usar y entender, pero claramente se espera que su público general sean personas que tengan o hayan tenido complicaciones cardiovasculares.

A partir de la información proporcionada, PULSO presentará los resultados de manera comprensible, permitiendo al usuario identificar los factores que tienen mayor influencia en su nivel de riesgo. Asimismo, la plataforma permitirá modificar determinadas variables para simular diferentes escenarios y observar cómo estos cambios pueden afectar la estimación del riesgo cardiovascular.

Como complemento a los resultados, PULSO proporcionará información y recomendaciones preventivas basadas en guías clínicas y fuentes médicas confiables, utilizando un lenguaje sencillo y comprensible para personas sin conocimientos especializados en el área de la salud.

De esta manera, la solución busca ir más allá de una evaluación que únicamente entregue un porcentaje de riesgo. PULSO pretende facilitar que las personas comprendan los factores relacionados con su riesgo cardiovascular, exploren diferentes escenarios y accedan a información preventiva de manera clara, contribuyendo así a la prevención y educación en salud cardiovascular.

## 6. Estado del arte / soluciones relacionadas

Para analizar las soluciones existentes relacionadas con la evaluación del riesgo cardiovascular, se revisaron diferentes calculadoras y herramientas utilizadas para estimar dicho riesgo. La comparación considera aspectos como la estimación del riesgo, las recomendaciones proporcionadas, el público objetivo, el alcance geográfico, la cantidad de información solicitada, la posibilidad de modificar los datos y la forma en que se presentan los escenarios de riesgo.

| Solución | Estimación del riesgo | Recomendaciones | Público objetivo | Simulación / comparación | Características destacadas |
|---|---|---|---|---|---|
| **SCORE2 / HeartScore** | Sí, proporciona un porcentaje de riesgo | **Sí, son personalizadas y las más completas de las herramientas revisadas** | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Orientada principalmente a población europea |
| **PREVENT** | Sí, proporciona un porcentaje de riesgo | Sí, pero principalmente como guía general para interpretar los resultados | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Requiere interpretación de los resultados |
| **Framingham – Canadian Cardiovascular Society** | Sí, proporciona un porcentaje de riesgo | Sí, principalmente como guía general para interpretar los resultados | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Interfaz poco intuitiva para el usuario |
| **CVD Risk Estimator Plus – PREVENT** | Sí, proporciona un porcentaje de riesgo | Sí, enfocadas en la persona evaluada | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Presenta recomendaciones personalizadas |
| **CVD Risk Estimator Plus – Pooled Cohort** | Sí, proporciona un porcentaje de riesgo | No | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Orientada aparentemente a población estadounidense |
| **QRISK** | Sí, proporciona un porcentaje de riesgo | No | — | **Sí, permite comparar directamente el riesgo actual con un escenario hipotético** | **Es la herramienta que solicita mayor cantidad de datos entre las revisadas. Su interfaz gráfica es sencilla, pero poco atractiva para el usuario** |

### Análisis de las soluciones existentes

A partir de la comparación realizada, se observa que las herramientas revisadas cuentan con la capacidad de **estimar el riesgo cardiovascular**, generalmente mediante la presentación de un porcentaje. Sin embargo, existen diferencias importantes en la cantidad de información solicitada, la forma de presentar los resultados y las funcionalidades disponibles para su interpretación.

En cuanto a las **recomendaciones**, SCORE2 / HeartScore destaca entre las herramientas analizadas por proporcionar las recomendaciones más completas y enfocadas en la persona evaluada. CVD Risk Estimator Plus (PREVENT) también proporciona recomendaciones personalizadas, mientras que PREVENT y Framingham – Canadian Cardiovascular Society presentan principalmente información general que sirve como guía para interpretar los resultados obtenidos. Por otro lado, Pooled Cohort y QRISK no proporcionan recomendaciones dentro de la herramienta revisada.

Respecto a la **cantidad de información solicitada**, QRISK destaca por ser la herramienta que requiere una mayor cantidad de datos entre las soluciones analizadas. Esto permite realizar una evaluación considerando un conjunto más amplio de variables, aunque también implica una mayor cantidad de información que debe proporcionar el usuario.

En relación con la **experiencia de usuario**, se identificaron diferencias entre las herramientas. Algunas están diseñadas principalmente para personas con conocimientos especializados en salud, lo que puede dificultar su interpretación por parte de usuarios no especializados. En particular, la interfaz de Framingham – Canadian Cardiovascular Society puede resultar complicada de comprender, mientras que la interfaz gráfica de QRISK, aunque sencilla, no resulta especialmente atractiva para el usuario.

Otro aspecto relevante es la **modificación de los datos para explorar diferentes escenarios**. Todas las herramientas revisadas permiten modificar los datos introducidos y realizar nuevamente el cálculo del riesgo. Sin embargo, existe una diferencia importante en la manera de presentar estos cambios. En las herramientas distintas de QRISK, al modificar los datos se realiza un nuevo cálculo del riesgo, pero no se presenta directamente una comparación entre el resultado original y el nuevo resultado dentro de la plataforma. **QRISK sí permite realizar esta comparación directamente**, mostrando el riesgo correspondiente al estado actual frente al riesgo obtenido en un escenario hipotético.

Finalmente, también se identifican diferencias en el **alcance geográfico** de las herramientas. SCORE2 está orientada principalmente a población europea, mientras que PREVENT y Pooled Cohort presentan un enfoque asociado a población estadounidense y QRISK al Reino Unido. Esto constituye un aspecto relevante al momento de interpretar los resultados, debido a que los modelos de riesgo pueden estar desarrollados y calibrados para poblaciones específicas.

### Oportunidad identificada

A partir de la revisión, se observa que **no existe una única característica que diferencie completamente a PULSO de las herramientas analizadas**, ya que algunas soluciones existentes presentan funcionalidades que también se contemplan en el proyecto. Sin embargo, las características se encuentran distribuidas de diferentes maneras entre las herramientas.

Por ejemplo, **SCORE2 destaca por la calidad y personalización de sus recomendaciones**, mientras que **QRISK destaca por la cantidad de datos solicitados y por permitir comparar directamente el estado actual con un escenario hipotético**. Estas características representan referencias importantes para el diseño de PULSO.

Por ello, la oportunidad para PULSO consiste en **integrar en una misma plataforma las funcionalidades relevantes identificadas en las soluciones analizadas**, pero orientándolas específicamente a personas no especializadas y con un enfoque de prevención y educación cardiovascular. La propuesta busca que el usuario pueda no solo conocer su nivel de riesgo, sino también comprender los factores que influyen en él, comparar directamente diferentes escenarios y recibir información y recomendaciones presentadas en un lenguaje sencillo.

## 7. Metodología de desarrollo y plan de trabajo

Describe el enfoque metodológico que orientará el desarrollo del proyecto y la forma en que este se traducirá en actividades, iteraciones y entregables concretos. Debe explicar cómo se construirá, validará y refinará la solución a lo largo del proceso.

### 7.1 Enfoque metodológico

El desarrollo de PULSO se llevará a cabo mediante un enfoque de prototipado iterativo e incremental. Esta elección responde a la naturaleza del proyecto, el cual integra componentes con distintos niveles de incertidumbre: la disponibilidad y calidad de los datos clínicos públicos, el desempeño real de los modelos de Machine Learning, el comportamiento del mecanismo de explicabilidad y la pertinencia de las respuestas generadas por el sistema RAG no pueden determinarse completamente antes de construir y probar cada componente. Un enfoque lineal o secuencial, en el que cada etapa se cerrará definitivamente antes de avanzar a la siguiente, dificultaría corregir a tiempo errores de datos, modelos con desempeño insuficiente o funcionalidades que no comuniquen adecuadamente el riesgo al usuario.

Por esta razón, el proyecto avanzará mediante ciclos sucesivos de diseño, construcción, prueba y ajuste. En cada ciclo se definirá un alcance acotado de trabajo, se construirá una versión parcial de la solución (un conjunto de datos preparado, un modelo entrenado, una funcionalidad de la plataforma), se evaluarán sus resultados frente a los criterios establecidos y, cuando sea necesario, se realizarán ajustes antes de continuar con el siguiente ciclo. Este esquema permite tratar cada entregable parcial como un prototipo que se refina progresivamente, en lugar de esperar hasta el final del proyecto para verificar si la solución cumple los objetivos planteados.

Para el componente de datos y Machine Learning, los ciclos iterativos tomarán como referencia las etapas de **CRISP-DM** (comprensión de los datos, preparación, modelado y evaluación), descritas con mayor detalle en la sección 7.2. Las fases no se desarrollarán de forma estrictamente lineal: los resultados obtenidos en la evaluación y en las pruebas podrán requerir volver a etapas anteriores para realizar ajustes, lo que es propio de un enfoque iterativo e incremental y permite refinar tanto el modelo como la plataforma hasta alcanzar una versión funcional del MVP.

### 7.2 Iteraciones o fases de desarrollo

El desarrollo de PULSO se organizará mediante un proceso iterativo compuesto por diferentes fases, tomando como referencia las etapas de **CRISP-DM** para el desarrollo del componente de datos y Machine Learning. Sobre esta estructura se incorporarán progresivamente las funcionalidades de explicabilidad, simulación y generación de información mediante RAG. Cada fase tendrá un propósito específico y sus resultados servirán como base para las etapas posteriores, permitiendo realizar ajustes cuando los resultados obtenidos no sean satisfactorios.

#### 1. Comprensión de los datos (Data Understanding)

Se identificarán y analizarán los conjuntos de datos disponibles para determinar su pertinencia respecto al objetivo del proyecto. Se estudiará su estructura, cantidad de registros, tipos de variables, valores faltantes, distribución y relaciones entre variables, además de evaluar su calidad y características para seleccionar los datos más adecuados para el desarrollo del modelo.

#### 2. Preparación de los datos (Data Preparation)

Los datos seleccionados serán sometidos a procesos de limpieza y transformación para adecuarlos al entrenamiento de los modelos. Se realizarán actividades como el tratamiento de valores faltantes, transformación de variables, selección de características y normalización o estandarización cuando sea necesario. Posteriormente, los datos serán divididos en los conjuntos requeridos para el entrenamiento y evaluación.

#### 3. Modelado (Modeling)

Se desarrollarán y entrenarán diferentes modelos de Machine Learning utilizando los datos previamente preparados. Se probarán distintos algoritmos y configuraciones con el propósito de identificar los modelos que presenten un desempeño adecuado para la estimación del riesgo cardiovascular.

#### 4. Evaluación (Evaluation)

Se analizará el desempeño de los modelos mediante métricas de evaluación apropiadas para el problema. Los resultados obtenidos serán comparados con el fin de seleccionar el modelo que mejor rendimiento tenga y cumpla con los objetivos establecidos. En caso de identificar resultados insatisfactorios, se podrán realizar ajustes en las etapas anteriores de preparación o modelado.

#### 5. Explicabilidad mediante SHAP

Una vez seleccionado el modelo, se incorporará **SHAP (SHapley Additive exPlanations)** como mecanismo de explicabilidad. Esta etapa permitirá identificar la contribución de las diferentes variables en las predicciones realizadas, con el propósito de proporcionar al usuario una interpretación comprensible de los principales factores asociados a su estimación de riesgo.

#### 6. Simulación

Se desarrollará una funcionalidad que permita modificar determinadas variables de entrada y obtener una nueva estimación del riesgo. Esto permitirá comparar el escenario actual del usuario con escenarios modificados y observar cómo los cambios realizados afectan la predicción generada por el modelo.

#### 7. Generación de información mediante RAG

Se incorporará un sistema de **Retrieval-Augmented Generation (RAG)** que permita complementar los resultados del modelo mediante información proveniente de fuentes y guías clínicas previamente seleccionadas. Su finalidad será proporcionar explicaciones y recomendaciones en un lenguaje comprensible para el usuario, manteniendo como referencia información clínica confiable.

#### 8. Despliegue (Deployment)

Finalmente, los componentes desarrollados serán integrados en la plataforma web PULSO. Se incorporarán al modelo predictivo, el mecanismo de explicabilidad, la simulación y el sistema RAG, conformando una versión funcional del MVP. Posteriormente, se realizarán pruebas de integración y funcionamiento para identificar posibles errores y realizar los ajustes finales.

Las fases no se desarrollarán necesariamente de manera lineal, ya que los resultados obtenidos durante la evaluación y las pruebas podrán requerir regresar a etapas anteriores para realizar ajustes y posteriormente avanzar nuevamente hacia las siguientes fases. De esta manera, el desarrollo permitirá refinar progresivamente tanto el modelo como las funcionalidades de la plataforma hasta alcanzar una versión funcional del MVP.


### 7.3 Estrategia de validación

La validación de PULSO se realizará de manera progresiva durante cada iteración, con el propósito de identificar errores y aplicar ajustes antes de avanzar a la siguiente etapa. En la primera iteración se revisará que el problema, el alcance y los requerimientos definidos correspondan con las necesidades de los usuarios. También se evaluará la calidad de los conjuntos de datos mediante el análisis de sus variables, valores faltantes, consistencia, balance y pertinencia para la estimación del riesgo cardiovascular.

Durante las iteraciones de preparación, modelado y evaluación se comprobará la calidad de las transformaciones realizadas sobre los datos y el desempeño de los modelos de Machine Learning. Para ello, se utilizarán datos separados para entrenamiento y prueba, junto con métricas como precisión, sensibilidad, especificidad, F1-score, ROC-AUC y matriz de confusión. La selección del modelo no dependerá únicamente de la exactitud, sino también de su calibración, estabilidad e interpretabilidad. Asimismo, SHAP permitirá revisar qué variables influyen en las predicciones y detectar comportamientos inesperados.

En la iteración de integración se aplicarán pruebas funcionales para verificar el ingreso y la validación de datos, la comunicación con la API, la generación de predicciones y el funcionamiento de SHAP, la simulación y el componente RAG. Se comprobará que los escenarios diferencien claramente los datos actuales de los hipotéticos y que las respuestas generadas estén sustentadas en las fuentes médicas seleccionadas. También se verificará que la plataforma no presente sus resultados como diagnósticos ni genere prescripciones o recomendaciones médicas sin respaldo.

Finalmente, se realizarán pruebas de usabilidad con usuarios potenciales para evaluar la facilidad de navegación, la claridad del lenguaje y la comprensión de las predicciones, explicaciones y simulaciones. La retroalimentación obtenida, junto con los resultados de las pruebas técnicas y funcionales, se utilizará para corregir errores y refinar el MVP. Esta validación evaluará el funcionamiento y la comprensión de PULSO, pero no constituirá una validación clínica ni permitirá utilizar la plataforma como sustituto de una valoración médica.

### 7.4 Plan de trabajo, cronograma o hitos

<img width="1414" height="2000" alt="Lorem ipsum dolor sit amet, consectetur aset adipiscing elit asim  Vestibulum ut feugiat enim  Aliquet tristique felis, non convallis" src="https://github.com/user-attachments/assets/433b7668-4ce6-432c-86fa-6786c5e64646" />


## 8. Referencias

American College of Cardiology. (s. f.). *CVD Risk Estimator Plus*. https://www.acc.org/CVDPlus

American Heart Association. (s. f.). *PREVENT calculator*. https://professional.heart.org/en/guidelines-and-statements/about-prevent-calculator

Canadian Cancer Society. (s. f.). *FRS*. https://ccs.ca/frs/

QRISK. (s. f.). *QRISK3-lifetime cardiovascular risk calculator*. https://qrisk.org/lifetime/
