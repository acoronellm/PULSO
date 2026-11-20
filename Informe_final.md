# Informe final del proyecto

## Resumen / Abstract

Las enfermedades cardiovasculares constituyen la principal causa de muerte en el mundo y están asociadas tanto con factores no modificables como modificables, entre ellas la hipertensión arterial, el colesterol elevado, la obesidad, el tabaquismo y la inactividad física. Aunque existen herramientas digitales para estimar el riesgo cardiovascular, muchas están orientadas a profesionales de la salud, emplean modelos calibrados para poblaciones específicas y presentan resultados cuya interpretación puede resultar compleja para personas sin formación médica. Este proyecto propone el diseño e implementación de PULSO (Plataforma Inteligente para la Predicción Explicable y Simulación Personalizada del Riesgo Cardiovascular mediante Machine Learning), un producto mínimo viable orientado a la prevención y educación en salud cardiovascular. La plataforma permitirá registrar factores de riesgo, generar una estimación mediante modelos de aprendizaje automático, explicar la influencia de las variables utilizadas y comparar el resultado inicial con escenarios hipotéticos construidos mediante la modificación de factores potencialmente controlables. Asimismo, integrará un sistema basado en Retrieval-Augmented Generation para presentar información preventiva sustentada en guías clínicas y fuentes médicas confiables, mediante un lenguaje comprensible para usuarios no especializados. El proyecto se desarrollará mediante una metodología iterativa e incremental que comprenderá la selección y preparación de datos clínicos públicos, el entrenamiento y comparación de modelos, el diseño de la arquitectura, la implementación de la plataforma web, la integración de explicabilidad y RAG, y la validación experimental del sistema. Como resultado, se espera obtener un MVP funcional que ayude a las personas a comprender sus factores de riesgo y favorezca decisiones informadas de prevención, sin sustituir la valoración realizada por profesionales de la salud.

En su estado actual, PULSO cuenta con un MVP funcional e integrado. Se seleccionó el conjunto de datos Cardiovascular Disease Dataset, disponible en Kaggle, se realizó el análisis exploratorio de datos (EDA) y se compararon diferentes algoritmos de clasificación, seleccionando como modelo final PULSO v1, basado en XGBoost y con un umbral de decisión de 0,38. La plataforma integra un frontend web en React y TypeScript, un backend FastAPI organizado mediante Clean Architecture, un servicio de Machine Learning que ofrece predicción, explicaciones mediante SHAP y simulación de escenarios, y un componente RAG implementado en n8n que genera información preventiva a partir de un corpus de 13 fuentes almacenado en Supabase. Los servicios principales se ejecutan mediante Docker Compose detrás de NGINX como proxy inverso, y el repositorio cuenta con workflows de integración y entrega continua en GitHub Actions.

## 1. Introducción

El sector de la salud atraviesa un proceso de transformación impulsado por la digitalización de la información clínica, el crecimiento de la capacidad computacional y la aplicación de técnicas de inteligencia artificial al análisis de datos. En este contexto, el aprendizaje automático, la inteligencia artificial explicable, los sistemas de apoyo a la toma de decisiones y las plataformas digitales de salud ofrecen nuevas posibilidades para identificar patrones, estimar riesgos y comunicar información preventiva. Estas tecnologías adquieren especial relevancia frente a las enfermedades cardiovasculares, consideradas entre las principales causas de muerte en el mundo. Según la Organización Mundial de la Salud (OMS, 2025), aproximadamente 19,8 millones de personas murieron por enfermedades cardiovasculares en 2022, cifra equivalente al 32 % de las defunciones mundiales. La OMS también señala que muchas de estas enfermedades pueden prevenirse mediante la identificación y el manejo oportuno de factores conductuales y metabólicos, como el tabaquismo, la inactividad física, la alimentación poco saludable, la hipertensión arterial, la glucosa elevada, las alteraciones de los lípidos y el exceso de peso.

Actualmente existen herramientas como SCORE2, PREVENT, Framingham, Pooled Cohort y QRISK, diseñadas para estimar la probabilidad de que una persona presente un evento cardiovascular durante un periodo determinado. Sin embargo, estas soluciones difieren en las variables que emplean, la población para la cual fueron desarrolladas y la manera en que comunican sus resultados. Por ejemplo, SCORE2 fue diseñado para estimar el riesgo cardiovascular a diez años en poblaciones europeas, mientras que PREVENT utiliza información cardiovascular, renal y metabólica y está orientado principalmente a apoyar las conversaciones preventivas entre los profesionales de la salud y sus pacientes (American Heart Association [AHA], s. f.; European Society of Cardiology [ESC], s. f.-a). Además, algunas de estas herramientas presentan porcentajes y términos clínicos que pueden resultar difíciles de interpretar para personas no especializadas. Aunque generalmente permiten modificar los datos y repetir el cálculo, no siempre explican claramente la influencia de cada variable ni muestran una comparación comprensible entre el resultado original y los escenarios hipotéticos explorados.

Esta situación evidencia la necesidad de diseñar una solución tecnológica que no se limite a proporcionar un porcentaje, sino que facilite su comprensión y uso responsable. La oportunidad consiste en transformar una estimación probabilística en una experiencia educativa mediante la explicación de los factores considerados, la identificación de las variables que más influyen en el resultado y la comparación entre la condición inicial del usuario y diferentes escenarios hipotéticos.

En respuesta a esta necesidad, se desarrolla PULSO, una plataforma web orientada principalmente a personas no especializadas que busca facilitar la comprensión de los factores asociados con los problemas cardiovasculares. El sistema contempla la integración de modelos de Machine Learning de clasificación, mecanismos de explicabilidad mediante SHAP, simulación de escenarios hipotéticos y un componente basado en Retrieval-Augmented Generation (RAG) para proporcionar información preventiva sustentada en guías clínicas y fuentes médicas confiables. Para el componente predictivo se ha seleccionado el *Cardiovascular Disease Dataset*, disponible en Kaggle, cuya variable objetivo, `cardio`, identifica la presencia o ausencia de enfermedad cardiovascular en los registros. A partir de las características ingresadas por el usuario, el modelo buscará estimar la probabilidad de pertenecer a la clase `cardio = 1`. Esta salida representa una probabilidad estimada por el clasificador y no debe interpretarse como el riesgo de presentar un evento cardiovascular futuro durante un horizonte temporal determinado.

En cuanto al estado actual del proyecto, se ha completado la selección del conjunto de datos y se ha realizado un análisis exploratorio de datos (EDA) para examinar sus características y evaluar su pertinencia para el desarrollo del modelo predictivo. Asimismo, se ha iniciado la implementación y prueba de diferentes algoritmos de clasificación con el propósito de comparar su desempeño y seleccionar una alternativa para su integración en la plataforma.

## 2. Marco conceptual

El desarrollo de PULSO integra fundamentos provenientes de la salud cardiovascular, el aprendizaje automático, la inteligencia artificial explicable, la recuperación de información y la ingeniería de software. Estos conceptos permiten comprender tanto la naturaleza del problema abordado como el funcionamiento de los componentes que conforman la plataforma. Su definición resulta especialmente importante debido a que PULSO combina una estimación generada mediante un modelo de clasificación con mecanismos de explicación, simulación e información documental dirigida a personas no especializadas.
Dentro de la plataforma, cada componente cumple una función diferente. El modelo de Machine Learning estima la probabilidad de que un registro pertenezca a la clase asociada con la presencia de enfermedad cardiovascular; SHAP permite analizar cómo contribuyeron las variables de entrada a dicha estimación; la simulación permite observar cómo cambia la salida del modelo cuando se modifican determinadas variables; y el componente de Retrieval-Augmented Generation (RAG) utiliza documentación previamente seleccionada para complementar el resultado con información preventiva sustentada en fuentes trazables. Estas funciones deben diferenciarse para evitar que una predicción estadística, una explicación del modelo o una respuesta generada sean interpretadas como equivalentes a una valoración clínica.
Por esta razón, el marco conceptual también considera las limitaciones asociadas con el uso de estas tecnologías. Una probabilidad generada por un clasificador depende de los datos utilizados durante su desarrollo, una explicación de Machine Learning describe el comportamiento del modelo pero no demuestra causalidad, y una respuesta generada mediante inteligencia artificial puede contener errores aun cuando utilice documentación recuperada. En consecuencia, PULSO se plantea como una herramienta de prevención y educación cardiovascular y no como un sistema de diagnóstico, prescripción o sustitución de la valoración realizada por profesionales de la salud.

## 2.1. Enfermedades cardiovasculares y factores de riesgo
Las enfermedades cardiovasculares comprenden un conjunto de trastornos que afectan el corazón y los vasos sanguíneos, entre ellos la enfermedad coronaria, la enfermedad cerebrovascular y otras alteraciones del sistema cardiovascular. Constituyen la principal causa de muerte a nivel mundial. De acuerdo con la Organización Mundial de la Salud, aproximadamente 19,8 millones de personas murieron por enfermedades cardiovasculares en 2022, lo que representó alrededor del 32 % de las defunciones mundiales (Organización Mundial de la Salud [OMS], 2025).
El desarrollo y la progresión de estas enfermedades están relacionados con múltiples factores. Entre los principales factores conductuales identificados por la OMS se encuentran el consumo de tabaco, la alimentación poco saludable, la inactividad física y el consumo nocivo de alcohol. Sus efectos pueden manifestarse mediante factores metabólicos o intermedios como presión arterial elevada, glucosa sanguínea elevada, alteraciones de los lípidos y sobrepeso u obesidad (OMS, 2025). Junto con ellos existen características no modificables o difícilmente modificables, como la edad y determinados antecedentes individuales.
La distinción entre factores modificables y no modificables resulta relevante para PULSO porque permite diferenciar entre características utilizadas únicamente para contextualizar una estimación y aquellas que pueden explorarse mediante escenarios hipotéticos. No obstante, que una variable contribuya a una predicción no significa que exista una relación causal demostrada ni que modificarla produzca necesariamente un cambio equivalente en la condición cardiovascular real de una persona. Esta diferencia constituye uno de los principios utilizados para comunicar responsablemente los resultados del modelo y de las simulaciones.

## 2.2.  Riesgo cardiovascular y clasificación de enfermedad cardiovascular
El riesgo cardiovascular suele definirse como la probabilidad de que una persona presente un evento cardiovascular específico durante un horizonte temporal determinado. Herramientas clínicas como SCORE2, PREVENT, Framingham, Pooled Cohort Equations y QRISK utilizan variables clínicas y demográficas para estimar este tipo de riesgo en poblaciones y periodos definidos. Por tanto, una estimación de riesgo cardiovascular requiere especificar tanto el desenlace estudiado como el horizonte temporal y la población sobre la cual fue desarrollado o validado el modelo.
El componente predictivo de PULSO responde a un problema diferente. El conjunto de datos utilizado contiene una variable objetivo binaria denominada cardio, que diferencia registros asociados con presencia (cardio = 1) y ausencia (cardio = 0) de enfermedad cardiovascular. En consecuencia, el modelo de PULSO estima, a partir de las variables disponibles, una probabilidad de pertenencia a la clase cardio = 1. Esta salida corresponde a la probabilidad estimada por un clasificador y no a la probabilidad de sufrir un infarto, accidente cerebrovascular u otro evento cardiovascular durante los próximos cinco o diez años.
Esta distinción delimita el significado clínico y metodológico de los resultados. La salida de PULSO no debe interpretarse como equivalente a las estimaciones producidas por herramientas clínicas validadas para riesgo cardiovascular futuro, ni como un diagnóstico de enfermedad cardiovascular. Su utilidad dentro del proyecto radica en utilizar un problema de clasificación como base para una experiencia educativa en la que el usuario pueda observar qué características fueron relevantes para el modelo, explorar escenarios alternativos y consultar información preventiva relacionada con los factores identificados.

## 2.3. Conjunto de datos utilizado
Para el desarrollo del componente predictivo se utiliza el Cardiovascular Disease Dataset, publicado por Svetlana Ulianova en Kaggle. La versión original contiene 70.000 registros y once características, además de la variable objetivo cardio (Ulianova, s. f.). Entre las variables originales se encuentran edad (age), sexo (gender), estatura (height), peso (weight), presión arterial sistólica (ap_hi), presión arterial diastólica (ap_lo), colesterol (cholesterol), glucosa (gluc), tabaquismo (smoke), consumo de alcohol (alco) y actividad física (active).
Durante la preparación realizada para PULSO se identificaron registros con valores inconsistentes o fisiológicamente poco plausibles y se aplicaron criterios de depuración, obteniéndose 68.610 observaciones para las etapas posteriores del proyecto. También se transformó la edad original, expresada en días, a años (age_years) y se calculó el índice de masa corporal (bmi) a partir del peso y la estatura. La versión utilizada por el modelo considera las variables gender, height, weight, ap_hi, ap_lo, smoke, alco, active, age_years y bmi. Las variables cholesterol y gluc no se incorporaron a la versión final debido a que se encuentran representadas mediante categorías cuya correspondencia clínica no se encuentra documentada con suficiente claridad en la fuente utilizada.
Una limitación particularmente importante corresponde a la procedencia y representatividad de los datos. La publicación disponible en Kaggle describe la estructura y las variables del conjunto, pero no proporciona el nivel de documentación de una cohorte clínica formal respecto a aspectos como el proceso de reclutamiento, instituciones participantes, estrategia de muestreo o representatividad para la población colombiana. Por tanto, no puede asumirse que las probabilidades aprendidas por el modelo sean directamente generalizables a Colombia o América Latina. Esta limitación debe mantenerse explícita tanto durante la evaluación del clasificador como durante la comunicación de sus resultados y constituye una diferencia fundamental frente a herramientas clínicas desarrolladas y validadas sobre cohortes poblacionales claramente caracterizadas.

## 2.4. Aprendizaje automático, clasificación y evaluación de modelos
El aprendizaje automático o Machine Learning comprende métodos computacionales capaces de identificar patrones a partir de datos y utilizarlos posteriormente para realizar predicciones sobre observaciones no utilizadas durante el entrenamiento. En el aprendizaje supervisado, cada observación dispone de características de entrada y de una variable objetivo conocida. Cuando la variable objetivo presenta dos posibles clases, como ocurre con cardio = 0 y cardio = 1, el problema corresponde a una clasificación binaria.
Durante el desarrollo de PULSO se evaluaron diferentes algoritmos de clasificación, incluyendo regresión logística, árbol de decisión, Random Forest, Gradient Boosting y XGBoost. Este último pertenece a la familia de métodos de gradient tree boosting, en los cuales múltiples árboles se construyen de manera secuencial para corregir progresivamente los errores cometidos por el conjunto anterior. XGBoost incorpora mecanismos de regularización y optimizaciones destinadas a mejorar la eficiencia y capacidad predictiva del proceso de boosting (Chen & Guestrin, 2016). La comparación experimental realizada en PULSO permitió seleccionar XGBoost como modelo para el componente predictivo.
La evaluación de un clasificador no debe limitarse a una sola métrica. La exactitud (accuracy) indica la proporción total de predicciones correctas; la precisión (precision) expresa qué proporción de los registros clasificados como positivos son realmente positivos; la sensibilidad o recall indica qué proporción de los positivos reales fue identificada por el modelo; la especificidad mide la capacidad para identificar los negativos reales; y F1-score combina precisión y sensibilidad. Por su parte, ROC-AUC evalúa la capacidad del modelo para discriminar entre las clases a través de diferentes umbrales de decisión (Fawcett, 2006). Estas métricas deben analizarse conjuntamente porque optimizar una puede deteriorar otra, especialmente cuando se modifica el umbral utilizado para producir la clasificación final.

## 2.5. Probabilidades, calibración, umbral de decisión e inteligencia artificial explicable
Los modelos de clasificación probabilística pueden generar, además de una clase, una probabilidad estimada asociada con cada observación. Sin embargo, una buena capacidad de discriminación no implica necesariamente que dichas probabilidades estén correctamente calibradas. Un clasificador se considera adecuadamente calibrado cuando, para grupos de observaciones a los que asigna una determinada probabilidad, la frecuencia observada de resultados positivos se aproxima a esa probabilidad. La calibración puede analizarse mediante curvas de calibración y métricas como el Brier Score, que cuantifica el error cuadrático entre las probabilidades predichas y los resultados observados (Brier, 1950).
Para convertir una probabilidad en una clasificación es necesario establecer un umbral de decisión. Cuando la probabilidad estimada es igual o superior al umbral, el registro se asigna a la clase positiva; en caso contrario se clasifica como negativo. La selección de este valor modifica el equilibrio entre falsos positivos y falsos negativos y, por tanto, afecta métricas como sensibilidad y especificidad. En PULSO, el umbral no se considera un valor implícito del algoritmo, sino una decisión que debe justificarse a partir de los objetivos del proyecto y del comportamiento observado sobre datos de validación.
La inteligencia artificial explicable (Explainable Artificial Intelligence, XAI) comprende técnicas destinadas a facilitar la comprensión del comportamiento de modelos cuya lógica puede resultar difícil de interpretar directamente. PULSO utiliza SHAP (SHapley Additive exPlanations), un enfoque propuesto por Lundberg y Lee (2017) que asigna a cada característica una contribución a la predicción individual con base en conceptos derivados de los valores de Shapley. Esto permite identificar qué variables contribuyeron a aumentar o disminuir la salida del modelo con respecto a un valor de referencia. Sin embargo, un valor SHAP explica el comportamiento matemático del clasificador y no demuestra que la característica identificada sea la causa clínica del resultado observado.

## 2.6. Generación aumentada por recuperación (RAG)

La generación aumentada por recuperación (Retrieval-Augmented Generation, RAG) es una arquitectura que combina la recuperación de información desde una colección de documentos con un modelo de lenguaje generativo. Su propósito es proporcionar al modelo información externa y pertinente para elaborar respuestas fundamentadas en fuentes documentales, en lugar de depender exclusivamente de los conocimientos adquiridos durante su entrenamiento. Esta arquitectura permite incorporar documentación especializada y actualizar las fuentes consultadas sin necesidad de volver a entrenar el modelo de lenguaje (Lewis et al., 2020).

En PULSO, RAG se utilizará para complementar las estimaciones del modelo predictivo con información procedente de guías, documentos científicos y fuentes confiables sobre prevención y riesgo cardiovascular. De esta manera, el sistema podrá generar explicaciones en lenguaje sencillo sobre la interpretación del riesgo y los factores relacionados con su estimación. Este componente tendrá una función informativa y educativa, independiente de la predicción realizada por el modelo de aprendizaje automático, y no sustituirá el diagnóstico ni la valoración de un profesional de la salud.

## 2.7. Recuperación semántica, embeddings y bases de datos vectoriales

La recuperación semántica es una técnica de búsqueda de información que permite identificar fragmentos de documentos según su significado y contexto, en lugar de depender exclusivamente de la coincidencia exacta de palabras. Para ello, se transforma la consulta del usuario y el contenido documental en representaciones numéricas que permiten comparar su similitud semántica y recuperar los fragmentos más relevantes (Reimers y Gurevych, 2019).

Los embeddings son representaciones numéricas de textos que permiten capturar características de su significado en un espacio vectorial. Estas representaciones facilitan la comparación entre consultas y documentos para identificar contenidos relacionados. Por su parte, una base de datos vectorial (vector store) permite almacenar estos vectores junto con los fragmentos de texto y sus metadatos, y realizar búsquedas de similitud para recuperar información pertinente de manera eficiente. Ambos componentes constituyen elementos fundamentales de los sistemas RAG basados en recuperación semántica.

En PULSO, estos mecanismos permitirán organizar y consultar un corpus documental compuesto por fuentes científicas y guías confiables sobre prevención y riesgo cardiovascular. Cuando el usuario formule una pregunta, el sistema buscará los fragmentos más relevantes y los proporcionará al modelo de lenguaje como contexto para generar una respuesta comprensible y fundamentada en la documentación recuperada. Esto facilitará el acceso a información especializada sin exigir que el usuario consulte e interprete documentos técnicos completos. La calidad de las respuestas dependerá, entre otros factores, de la pertinencia, actualidad y confiabilidad de las fuentes, así como de la calidad de la recuperación y de la generación del modelo.

## 2.8. Simulación de escenarios hipotéticos
La simulación de escenarios aplicada a un modelo predictivo consiste en modificar una o más variables de entrada y volver a ejecutar el modelo para observar cómo cambia su salida. A diferencia de una predicción independiente, la simulación conserva una situación inicial como referencia y permite comparar sistemáticamente el resultado obtenido antes y después de realizar determinados cambios sobre las características del registro.
En PULSO, esta funcionalidad se aplica únicamente a variables consideradas potencialmente modificables y compatibles con las características utilizadas por el modelo. El sistema genera inicialmente una estimación a partir de los datos proporcionados por el usuario y posteriormente permite introducir valores alternativos para producir una nueva estimación. La interfaz puede entonces mostrar la diferencia entre ambas probabilidades y facilitar la comprensión de cómo responde el modelo ante las modificaciones realizadas.
Esta comparación debe interpretarse exclusivamente como un análisis contrafactual simplificado del comportamiento del clasificador. Si al modificar una variable disminuye la probabilidad estimada, no puede concluirse que realizar ese mismo cambio en la vida real producirá exactamente dicha reducción ni que exista una relación causal demostrada. La simulación tampoco se utilizará para proponer cambios en tratamientos, medicamentos o decisiones clínicas; su finalidad consiste en apoyar la exploración educativa de los factores considerados por el modelo.

## 2.9. Arquitectura de software, servicios web y contenerización
La arquitectura de software establece la organización de los componentes de un sistema, las responsabilidades asignadas a cada uno y los mecanismos mediante los cuales intercambian información. En aplicaciones distribuidas, estas decisiones influyen sobre características como acoplamiento, mantenibilidad, escalabilidad, rendimiento y tolerancia a fallos. Para la comunicación entre componentes, las interfaces de programación de aplicaciones (API) permiten exponer funcionalidades mediante contratos definidos. REST constituye un estilo arquitectónico para sistemas distribuidos basado en restricciones destinadas, entre otros objetivos, a favorecer interfaces uniformes y la evolución independiente de componentes (Fielding, 2000).
En PULSO se adopta una arquitectura modular orientada a servicios contenerizados. Esta organización separa principalmente la interfaz web, el backend, el servicio de Machine Learning y el servicio RAG. La separación permite que componentes con características operacionales diferentes evolucionen de forma relativamente independiente, sin llegar al nivel de fragmentación de una arquitectura de microservicios más granular. El servicio de Machine Learning concentra la predicción, la generación de explicaciones SHAP y la simulación, debido a que estas funcionalidades dependen del mismo modelo y de las mismas transformaciones de datos.
La contenerización complementa esta arquitectura al empaquetar las aplicaciones junto con sus dependencias en entornos aislados y reproducibles. Docker permite crear y ejecutar estos contenedores de manera independiente, reduciendo diferencias entre entornos de desarrollo y ejecución (Docker, s. f.). En PULSO, este enfoque facilita la ejecución coordinada de frontend, backend, Machine Learning, RAG y demás componentes de infraestructura, además de permitir aislar parcialmente fallos y gestionar sus dependencias mediante configuraciones reproducibles.

## 2.10. Integración continua, trazabilidad experimental y MLOps
La integración continua (Continuous Integration, CI) es una práctica de ingeniería de software mediante la cual los cambios incorporados al repositorio se verifican automáticamente antes de integrarse a la rama principal. Estas verificaciones pueden incluir ejecución de pruebas, validaciones estáticas, construcción de artefactos y otras comprobaciones destinadas a detectar errores de forma temprana. En PULSO, GitHub y GitHub Actions se utilizan para apoyar este flujo de integración y mantener control sobre los cambios realizados durante el desarrollo.
Los sistemas de Machine Learning requieren además conservar información sobre los datos, configuraciones, parámetros, métricas y artefactos asociados con cada experimento. Esta trazabilidad permite reproducir resultados, comparar modelos y determinar qué versión fue utilizada posteriormente dentro de una aplicación. Para este propósito, PULSO utiliza MLflow, cuya funcionalidad de tracking permite registrar parámetros, métricas, versiones de código y artefactos asociados con las ejecuciones de entrenamiento y evaluación (MLflow, s. f.).
Estas prácticas forman parte de un enfoque más amplio conocido como MLOps (Machine Learning Operations), orientado a integrar las actividades de desarrollo de modelos con las prácticas de ingeniería necesarias para probarlos, versionarlos, desplegarlos y mantenerlos de forma consistente. MLOps extiende principios de DevOps a sistemas de aprendizaje automático e incorpora elementos como automatización, experimentación reproducible, validación, despliegue y monitoreo del ciclo de vida del modelo (Google Cloud, 2024). En PULSO se implementa un alcance básico de MLOps centrado principalmente en la reproducibilidad de los experimentos, el registro de métricas, la selección de umbrales, el versionamiento del modelo y su integración controlada con los demás componentes del MVP.

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

### 3.3 Alcance

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

Esta estrategia se encuentra implementada. El repositorio cuenta con workflows de GitHub Actions que se ejecutan sobre cada pull request para el frontend (lint, verificación de tipos, pruebas y compilación), el backend y su integración con el RAG, el ML Service, el pipeline de entrenamiento y la infraestructura (validación de Docker Compose, construcción de imágenes y verificación del enrutamiento de NGINX). Adicionalmente, un workflow de entrega continua publica en GitHub Container Registry las imágenes del frontend, backend y ML Service, y ejecuta pruebas de humo sobre las imágenes publicadas. El artefacto del modelo final se versiona junto con su configuración y su huella SHA-256. El detalle se presenta en la sección 12.6.

En conjunto, la estrategia establece un ciclo de planificación, desarrollo, pruebas, revisión, integración, validación y mejora. La incorporación de integración continua, versionamiento de modelos y prácticas básicas de MLOps permitirá que el desarrollo de PULSO sea trazable, reproducible y controlado, mientras que las pruebas técnicas, funcionales y de usabilidad permitirán verificar progresivamente el cumplimiento de los requerimientos definidos.

### 7.4 Plan de trabajo, cronograma o hitos

El plan de trabajo de PULSO organiza las actividades necesarias para desarrollar progresivamente los componentes del MVP, desde la comprensión y preparación de los datos hasta el modelado, la explicabilidad, la simulación, la integración de RAG y la validación de la plataforma. Su propósito es establecer una secuencia de actividades, entregables e hitos que permita hacer seguimiento al avance del proyecto y coordinar el trabajo de los integrantes del equipo.

A la fecha se completaron la selección del conjunto de datos, el análisis exploratorio, la comparación y selección del modelo (PULSO v1, XGBoost con umbral de 0,38), el desarrollo de las funcionalidades de explicabilidad y simulación, la incorporación del componente RAG, la integración de los servicios del sistema, la contenerización con NGINX como proxy inverso y la automatización de la integración y entrega continua. Las actividades restantes corresponden a la ejecución de las pruebas previstas para la validación final del MVP.

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
| **RNF-19** | Pertinencia de recuperación | El componente RAG deberá recuperar información documental relacionada con los factores prioritarios identificados para el perfil evaluado. Su comportamiento será verificado mediante métricas de recuperación como Precision@k, Hit Rate@k y cobertura de factores SHAP. |
| **RNF-20** | Control de alcance RAG | Las respuestas generadas mediante RAG deberán mantenerse dentro de los factores relevantes para el perfil y del propósito educativo y preventivo de PULSO. La evaluación deberá registrar la proporción de respuestas que incorporen información no prioritaria o que exceda el alcance definido, diferenciando la severidad de las desviaciones detectadas. |

## 9. Evaluación de alternativas

Para la definición de la arquitectura de PULSO se consideran tres alternativas: una arquitectura monolítica modular contenerizada, una arquitectura modular orientada a servicios contenerizados y una arquitectura de microservicios contenerizados.

Las tres alternativas comparten una serie de elementos tecnológicos y funcionales. PULSO será una plataforma web de acceso público, sin registro ni inicio de sesión, en la cual el usuario podrá ingresar directamente sus datos cardiovasculares y obtener una estimación de riesgo, explicaciones mediante SHAP, simulaciones e información preventiva mediante RAG. Asimismo, las tres propuestas contemplan el uso de una base de datos PostgreSQL alojada en Supabase, un proxy inverso como punto de entrada para las solicitudes externas y Docker para la contenerización de los componentes.

La principal diferencia entre las alternativas corresponde al grado de separación de los componentes de la aplicación. Esta diferencia se analiza considerando tres criterios: desempeño bajo la carga esperada, grado de acoplamiento y nivel de disponibilidad y tolerancia a fallos.

### 9.1. Desempeño bajo la carga esperada

La evaluación se realizó con Locust durante 420 segundos por escenario, utilizando 1, 5, 10, 25 y 50 usuarios concurrentes. Las tres alternativas utilizaron los mismos endpoints (`POST /api/analyze` y `POST /api/simulate`) y el mismo RAG mock, con el fin de controlar la variabilidad del proveedor externo. La fila `Aggregated` de los archivos `*_stats.csv` combina ambos endpoints y se utiliza para la comparación global. Por tanto, `/api/analyze` representa el flujo consolidado de predicción, SHAP y RAG mock; no se midieron por separado los tiempos internos de cada etapa.

| Arquitectura | Usuarios | Solicitudes | Error | Req/s | p50 (ms) | p95 (ms) | p99 (ms) | Máx. (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Monolítica | 1 | 254 | 0 % | 0,61 | 130 | 190 | 250 | 762 |
| Monolítica | 5 | 1.266 | 0 % | 3,02 | 130 | 260 | 360 | 673 |
| Monolítica | 10 | 2.494 | 0 % | 5,96 | 140 | 340 | 520 | 678 |
| Monolítica | 25 | 5.715 | 0 % | 13,65 | 270 | 740 | 1.100 | 1.487 |
| Monolítica | 50 | 8.166 | 0 % | 19,51 | 1.100 | 1.800 | 2.100 | 2.470 |
| Orientada a servicios | 1 | 253 | 0 % | 0,61 | 140 | 220 | 270 | 278 |
| Orientada a servicios | 5 | 1.291 | 0 % | 3,09 | 120 | 200 | 240 | 283 |
| Orientada a servicios | 10 | 2.531 | 0 % | 6,05 | 120 | 250 | 330 | 508 |
| Orientada a servicios | 25 | 6.027 | 0 % | 14,37 | 190 | 510 | 720 | 1.108 |
| Orientada a servicios | 50 | 9.507 | 0 % | 22,68 | 720 | 1.200 | 1.500 | 2.055 |
| Microservicios | 1 | 242 | 0 % | 0,58 | 230 | 340 | 500 | 3.957 |
| Microservicios | 5 | 1.232 | 0 % | 2,94 | 170 | 320 | 410 | 512 |
| Microservicios | 10 | 2.457 | 0 % | 5,87 | 170 | 360 | 450 | 610 |
| Microservicios | 25 | 5.773 | 0 % | 13,78 | 280 | 620 | 940 | 2.118 |
| Microservicios | 50 | 7.620 | 0 % | 18,18 | 1.400 | 2.100 | 2.500 | 3.082 |

No se registraron fallos en las solicitudes de los 15 escenarios: los archivos de fallos y excepciones no contienen ocurrencias y el error observado fue de 0 % en todos los casos. Esto no equivale a una garantía de disponibilidad en producción, sino únicamente al resultado de estas corridas controladas.

#### Arquitectura monolítica modular contenerizada

La arquitectura monolítica obtuvo la menor latencia con 1 usuario (p95 de 190 ms), pero su degradación fue más pronunciada al aumentar la carga: el p95 pasó a 740 ms con 25 usuarios y a 1.800 ms con 50. En este último escenario alcanzó 19,51 solicitudes/s y utilizó aproximadamente 210,4 MiB de RAM promedio, con un máximo de 212,8 MiB. Su CPU promedio llegó a 74,53 % y el máximo registrado fue 116,24 %. Estos resultados muestran un menor costo de memoria, pero también una mayor concentración de la carga en un solo proceso.

#### Arquitectura modular orientada a servicios contenerizados

La arquitectura orientada a servicios presentó el mejor comportamiento global en los escenarios de mayor carga. Con 50 usuarios alcanzó 22,68 solicitudes/s, el mayor throughput observado, con p50 de 720 ms, p95 de 1.200 ms y p99 de 1.500 ms. A 25 usuarios registró p95 de 510 ms, inferior al monolito (740 ms) y a microservicios (620 ms). El costo de esta separación fue mayor al del monolito: a 50 usuarios utilizó aproximadamente 302,0 MiB de RAM promedio y 314,9 MiB como máximo, con CPU agregada promedio de 130,43 % y máximo de 199,72 %.

#### Arquitectura de microservicios contenerizados

Microservicios presentó la mayor sobrecarga en los escenarios comparados. Con 50 usuarios obtuvo 18,18 solicitudes/s, p50 de 1.400 ms y p95 de 2.100 ms, además del mayor consumo: aproximadamente 899,3 MiB de RAM promedio y 959,9 MiB como máximo. A 1 usuario también registró un máximo atípico de 3.957 ms, aunque su p95 fue de 340 ms. La separación ofrece independencia potencial entre funciones, pero en esta prueba no compensó el costo de las múltiples comunicaciones y procesos.

Las mediciones internas disponibles no permiten afirmar un tiempo máximo individual para predicción, SHAP o RAG. El único tiempo medido directamente para el flujo completo es el de `/api/analyze`, incluido en la fila agregada; por ello, descomponerlo en tiempos por componente requeriría instrumentación adicional.

### 9.2. Grado de acoplamiento

El acoplamiento se analiza considerando la dependencia entre componentes, el número de procesos que deben coordinarse y la posibilidad de modificar o sustituir una parte sin reconstruir el sistema completo. Las métricas de carga no miden directamente el acoplamiento, pero la topología de cada alternativa permite describir su costo operativo verificable.

#### Arquitectura monolítica modular contenerizada

Aunque los componentes se encuentran organizados mediante módulos independientes a nivel de código, todos forman parte de una misma aplicación. Por esta razón, comparten recursos y un mismo ciclo de despliegue.

Una modificación en un componente requiere reconstruir y desplegar la aplicación completa. En la prueba de 50 usuarios fue el menor consumidor de RAM (212,8 MiB máximo), pero esa eficiencia se obtiene concentrando la ejecución en un proceso y compartiendo sus recursos.

#### Arquitectura modular orientada a servicios contenerizados

La separación del frontend, backend, Machine Learning y RAG en servicios independientes reduce el acoplamiento entre los principales componentes de la plataforma.

Cada servicio puede evolucionar y desplegarse de manera independiente siempre que mantenga las interfaces de comunicación definidas. Esto facilita, por ejemplo, modificar el servicio de Machine Learning sin tener que modificar o desplegar nuevamente el frontend.

A diferencia de los microservicios, esta alternativa mantiene una cantidad limitada de servicios. En la prueba de 50 usuarios requirió aproximadamente 314,9 MiB de RAM máxima, frente a 212,8 MiB del monolito y 959,9 MiB de microservicios, por lo que el desacoplamiento adicional tuvo un costo intermedio medible.

#### Arquitectura de microservicios contenerizados

Los microservicios presentan el menor acoplamiento entre componentes, ya que funcionalidades específicas como predicción, SHAP, simulación y RAG se encuentran separadas en servicios independientes.

Esta separación facilita reemplazar o actualizar componentes individualmente. Sin embargo, también aumenta la cantidad de interfaces y dependencias de comunicación que deben administrarse, lo que se refleja en el mayor consumo de memoria y en una latencia p95 de 2.100 ms con 50 usuarios.

### 9.3. Disponibilidad y tolerancia a fallos

La disponibilidad y tolerancia a fallos no puede determinarse únicamente a partir de los CSV de carga. En los archivos disponibles no se registran tiempos de recuperación, pruebas de caída de contenedores ni respuestas HTTP durante una falla. Por tanto, esta sección distingue la consecuencia arquitectónica esperada de una caída de la evidencia que sí fue medida.

#### Arquitectura monolítica modular contenerizada

En la arquitectura monolítica, los principales componentes del backend forman parte de una misma aplicación. Por esta razón, una falla crítica que provoque la caída del proceso puede afectar simultáneamente las funcionalidades de predicción, SHAP, simulación y RAG.

Docker permite reiniciar el contenedor afectado, pero el aislamiento de fallos entre funcionalidades es limitado: una caída del proceso deja sin servicio las funciones que contiene. El tiempo de recuperación no fue medido en los resultados disponibles.

#### Arquitectura modular orientada a servicios contenerizados

La separación en servicios independientes permite aislar parcialmente los fallos. Por ejemplo, una interrupción del servicio RAG no necesariamente implica que el servicio de Machine Learning o el backend dejen de funcionar.

Además, cada servicio puede reiniciarse y desplegarse de manera independiente. Esto permite reducir el impacto de determinados fallos y facilita las tareas de mantenimiento y recuperación.

La separación permite que el backend permanezca disponible ante una caída de un servicio independiente, siempre que existan manejo de errores y reinicio configurados. Esta observación es una propiedad del diseño, no un resultado cuantificado de las corridas de Locust; el recovery time y los códigos HTTP durante la falla deben medirse en una prueba de resiliencia específica.

#### Arquitectura de microservicios contenerizados

La arquitectura de microservicios proporciona un alto nivel de aislamiento entre componentes. Una falla en un microservicio específico puede limitar una funcionalidad determinada sin afectar necesariamente al resto de la plataforma.

Sin embargo, este nivel de aislamiento requiere más mecanismos para gestionar errores, disponibilidad, comunicación y recuperación. En los datos de carga, esta alternativa fue la de mayor consumo de RAM y menor throughput a 50 usuarios, por lo que sus beneficios de aislamiento deben contrastarse con ese costo. No se dispone de una medición de recovery time para confirmar su ventaja en recuperación.

### 9.4. Comparación de las alternativas

A partir de las métricas observadas y de la estructura desplegada, se obtiene la siguiente comparación:

| Criterio | Monolítica modular | Orientada a servicios | Microservicios |
|---|---|---|---|
| p95 agregado con 50 usuarios | 1.800 ms | 1.200 ms | 2.100 ms |
| Throughput con 50 usuarios | 19,51 req/s | 22,68 req/s | 18,18 req/s |
| Tasa de error observada | 0 % | 0 % | 0 % |
| RAM máxima aproximada con 50 usuarios | 212,8 MiB | 314,9 MiB | 959,9 MiB |
| Procesos/servicios principales en la prueba | 1 | 2 | 4 |
| Comunicación interna | Llamadas dentro del proceso | HTTP entre servicios | HTTP entre múltiples servicios |
| Despliegue independiente | No | Sí, por servicio | Sí, por microservicio |
| Aislamiento arquitectónico ante fallos | Bajo | Intermedio | Alto |
| Complejidad operativa observable | Menor número de componentes | Intermedia | Mayor número de componentes |

La comparación evidencia que las tres alternativas completaron solicitudes sin errores en las condiciones probadas, pero no tuvieron el mismo desempeño. La arquitectura orientada a servicios obtuvo el mayor throughput y el menor p95 a 25 y 50 usuarios. El monolito fue el más eficiente en RAM, mientras que microservicios presentó el mayor costo de recursos y la mayor latencia a 50 usuarios.

La arquitectura monolítica presenta la menor complejidad y consumo de recursos, pero concentra los componentes en una misma aplicación. Microservicios proporciona el mayor aislamiento potencial, aunque en estas pruebas alcanzó 959,9 MiB de RAM máxima y un p95 de 2.100 ms con 50 usuarios. La arquitectura orientada a servicios queda entre ambas en número de componentes y costo de recursos, y presentó el mejor resultado de capacidad bajo carga.

La arquitectura modular orientada a servicios permite separar los componentes principales y asignar recursos de manera independiente sin introducir desde el inicio la fragmentación de microservicios. Esta conclusión se sustenta en el rendimiento observado, pero no debe interpretarse como una medición completa de disponibilidad o recuperación.

### 9.5. Consideraciones comunes de seguridad y acceso

Las tres alternativas parten de la misma condición de acceso público: PULSO no contará con cuentas de usuario ni requerirá autenticación para utilizar sus funcionalidades.

Por esta razón, no es necesario implementar un servicio específico de autenticación para el acceso de los usuarios. Sin embargo, el backend deberá encargarse de validar los datos recibidos antes de procesarlos y controlar el acceso a Supabase.

Las credenciales privilegiadas utilizadas para acceder a la base de datos no deberán exponerse en el frontend. El acceso a los recursos internos deberá realizarse mediante el backend y los servicios correspondientes.

También será necesario considerar mecanismos de protección frente a solicitudes abusivas, independientemente de la arquitectura seleccionada. El proxy inverso podrá actuar como punto de entrada para centralizar parte de estas medidas y controlar las solicitudes provenientes del exterior.

### 9.6. Alternativa seleccionada

Después de comparar las tres propuestas, se selecciona la **arquitectura modular orientada a servicios contenerizados** como alternativa para PULSO.

La elección se fundamenta en el equilibrio entre rendimiento, consumo de recursos y separación de componentes. En la prueba de 50 usuarios, la arquitectura orientada a servicios alcanzó el mayor throughput (22,68 req/s), el menor p95 (1.200 ms) y un p99 de 1.500 ms, frente a 19,51 req/s y 1.800 ms del monolito, y 18,18 req/s y 2.100 ms de microservicios. No fue la alternativa de menor consumo, pero sus 314,9 MiB de RAM máxima quedaron por debajo de los 959,9 MiB de microservicios.

Esta separación resulta conveniente porque PULSO integra funcionalidades con diferentes necesidades computacionales. El costo medido frente al monolito fue una mayor utilización de recursos, pero permite evolucionar y optimizar los componentes de forma independiente.

Además, la arquitectura permite escalar los componentes que presenten una mayor demanda sin necesidad de escalar toda la aplicación. Por ejemplo, si en una etapa posterior el servicio de Machine Learning requiere mayores recursos computacionales debido al incremento de solicitudes, estos recursos pueden asignarse específicamente a dicho servicio.

Otro aspecto considerado es la tolerancia a fallos. Al estar los componentes separados, una falla en un servicio específico puede limitar una funcionalidad sin afectar necesariamente el funcionamiento completo de la plataforma. Esto proporciona un mayor aislamiento respecto a la arquitectura monolítica.

Aunque microservicios ofrece un nivel superior de separación potencial, en la prueba fue la alternativa con peor p95 y mayor consumo de RAM. Además, no se cuenta con pruebas de resiliencia que permitan cuantificar su recuperación. Para el MVP, se considera más apropiado mantener una cantidad controlada de servicios con responsabilidades claramente definidas.

Finalmente, la arquitectura modular orientada a servicios permite que PULSO pueda evolucionar progresivamente. Si en el futuro alguna funcionalidad requiere un nivel de independencia, escalabilidad o disponibilidad mayor, el servicio correspondiente puede seguir evolucionando o, si resulta necesario, dividirse en componentes más especializados.

Por estas razones, la arquitectura modular orientada a servicios contenerizados se mantiene como la alternativa seleccionada para PULSO. Los resultados respaldan su ventaja de desempeño bajo cargas de 25 y 50 usuarios y su posición intermedia en consumo y complejidad. La conclusión sobre tolerancia a fallos es arquitectónica y deberá validarse con pruebas de caída y recuperación antes de presentarla como una métrica. En consecuencia, la selección representa el mejor compromiso observado para el MVP, no una afirmación de superioridad absoluta ni una evaluación del rendimiento clínico del modelo.

## 10. Diseño y arquitectura

PULSO se estructura como una solución de tipo cliente-servidor, con una organización modular orientada a servicios y una clara separación de responsabilidades entre la capa de interacción, la lógica de negocio y las funcionalidades de análisis predictivo, explicabilidad y recomendación. Esta elección responde a la necesidad de mantener una base tecnológica manejable para el MVP, pero al mismo tiempo preparar una evolución gradual del sistema hacia un modelo más escalable y tolerante a fallos.

La arquitectura implementada no responde a un monolito rígido ni a una infraestructura compleja de microservicios, sino a una solución intermedia: un conjunto de componentes funcionales bien definidos, desplegables de manera independiente y conectados mediante interfaces claras. Esta opción es coherente con la alternativa seleccionada previamente, en la que se prioriza un equilibrio entre desempeño, desacoplamiento, facilidad de mantenimiento y complejidad operativa.

### 10.1 Arquitectura

#### 10.1.1 Descripción general de la arquitectura

La solución corresponde a una **arquitectura cliente-servidor modular orientada a servicios contenerizados**, que materializa la alternativa seleccionada en la sección 9.6. El usuario interactúa con una interfaz web para ingresar sus datos y consultar el resultado del análisis. Todas las solicitudes del navegador ingresan por **NGINX**, que actúa como punto único de entrada y reenvía las rutas `/` al frontend y las rutas `/api/` al backend.

El backend actúa como punto central de coordinación. Valida los datos entrantes, aplica las reglas de coherencia del perfil, orquesta las llamadas a los servicios especializados y entrega respuestas consolidadas al cliente. Internamente se organiza siguiendo los principios de **Clean Architecture**, con cuatro capas (dominio, aplicación, infraestructura e interfaces HTTP) cuyas dependencias apuntan siempre hacia el dominio.

El componente de Machine Learning queda encapsulado en un servicio independiente (**ML Service**) que asume la inferencia del riesgo cardiovascular con el modelo PULSO v1, la explicación local mediante SHAP y la simulación de escenarios hipotéticos. El componente **RAG**, implementado como un workflow de n8n, se conecta con un corpus documental vectorizado en Supabase (PostgreSQL + pgvector) y con el modelo generativo Google Gemini para contextualizar el resultado del modelo y presentar información orientada a la prevención.

El flujo se divide en solicitudes independientes: el análisis (predicción + SHAP) se resuelve sin esperar al RAG, y las recomendaciones se solicitan posteriormente a partir de un identificador de análisis (`analysis_id`). De esta manera, la latencia del componente generativo no bloquea la presentación del resultado principal y una falla del RAG no impide mostrar la predicción ni la explicación.

La persistencia de Supabase se utiliza para el almacén vectorial del corpus documental del RAG. En la versión actual, el backend conserva temporalmente el contexto de cada análisis en una caché en memoria con tiempo de expiración (TTL de 900 segundos y máximo de 100 registros), de modo que `/api/rag` reutilice el análisis sin repetir la inferencia ni permitir que el navegador altere el contexto enviado al RAG.

La arquitectura no solo satisface el objetivo funcional inmediato del MVP, sino que también deja abierta la posibilidad de crecer de forma progresiva. Si el sistema aumenta su demanda o se incorporan nuevas funcionalidades, cada servicio puede modificarse, escalarse o reemplazarse sin afectar necesariamente el conjunto completo de la plataforma.

#### 10.1.2 Componentes del sistema e interacción

##### 10.1.2.1 Descripción de componentes

Los componentes principales del sistema son los siguientes:

- **Frontend web:** capa de interacción con el usuario, implementada con React, TypeScript y Vite. Permite ingresar datos clínicos, visualizar resultados, consultar explicaciones, solicitar recomendaciones y ejecutar simulaciones de escenarios. Su función principal es ofrecer una experiencia clara, accesible y comprensible para personas no especializadas. Se relaciona con los requerimientos de interacción, presentación de resultados y usabilidad.
- **NGINX / reverse proxy:** punto de entrada público que centraliza el acceso externo. Enruta `/` hacia el frontend y `/api/` hacia el backend, de forma que el navegador no necesita conocer las direcciones internas y los servicios de ML y RAG permanecen como componentes internos.
- **Backend / API:** se encarga de la lógica de negocio del sistema. Recibe las solicitudes del cliente, valida el payload, coordina la comunicación con los servicios de análisis y entrega una respuesta unificada. Expone `POST /api/analyze`, `POST /api/rag`, `POST /api/simulate` y `GET /api/health`. Se relaciona con los requerimientos de validación, orquestación y manejo de errores.
- **ML Service:** encapsula la inferencia del modelo predictivo. Recibe los datos del usuario, aplica el modelo entrenado y devuelve la probabilidad estimada, la clasificación según el umbral de 0,38 y la versión del modelo. Expone `/predict`, `/explain`, `/simulate` y `/health`.
- **SHAP / explicabilidad:** módulo del ML Service que ofrece una explicación local de la predicción. Muestra qué variables influyen en la decisión del modelo y en qué dirección lo hacen, utilizando la misma instancia del modelo que produjo la predicción.
- **Simulación:** módulo del ML Service que permite variar parámetros modificables como el peso, la presión arterial, el tabaquismo, el consumo de alcohol o la actividad física para observar cómo cambia la estimación en distintos escenarios.
- **RAG / recomendaciones:** workflow de n8n que trabaja con una base de conocimiento médica para generar explicaciones educativas de los factores, recomendaciones y consideraciones en lenguaje comprensible, acompañadas de las fuentes utilizadas.
  El componente RAG utiliza un corpus documental controlado compuesto por **13 fuentes seleccionadas** relacionadas con prevención y salud cardiovascular. Estas fuentes corresponden a documentos médicos y guías consideradas pertinentes para los factores contemplados por PULSO. El contenido documental es segmentado en fragmentos antes de generar sus representaciones vectoriales y almacenarlas en Supabase para realizar posteriormente la recuperación semántica. La selección del corpus busca limitar la generación a información procedente de fuentes previamente revisadas y facilitar la trazabilidad de las recomendaciones producidas por el sistema.

| ID | Título de la fuente | Institución / Autor | Tipo de documento | Tema principal | Factores o temas cubiertos | Observaciones |
|---|---|---|---|---|---|---|
| **SRC-01** | *Respuestas del corazón: Estilo de Vida + Reducción de Factores de Riesgos - ¿Cómo puedo perder peso?* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Estrategias para la pérdida de peso sostenible y reducción del riesgo cardiovascular. | Peso corporal, IMC / obesidad, actividad física, presión arterial, colesterol, prevención cardiovascular general. | Material educativo dirigido a pacientes. |
| **SRC-02** | *Respuestas del corazón: Estilo de vida + Riesgo reducción Fumar - ¿Cómo dejo de fumar?* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Estrategias para abandonar el consumo de tabaco y productos relacionados. | Tabaquismo, presión arterial, prevención cardiovascular general. | Fuente especializada en cesación de tabaquismo. |
| **SRC-03** | *Respuestas del corazón: Estilo de vida + Riesgo reducción Dieta + Nutrición - ¿Cómo puedo seguir un patrón de alimentación saludable?* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Adopción de patrones de alimentación saludables para el corazón y control de porciones. | Alimentación, peso corporal, presión arterial, prevención cardiovascular general. | Incluye recomendaciones sobre alimentos, sodio, azúcares y grasas. |
| **SRC-04** | *Respuestas del corazón: Estilo de vida + reducción de riesgos Presión arterial alta - ¿Qué es la presión arterial alta?* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Explicación de la hipertensión arterial, categorías de presión y factores asociados. | Presión arterial / hipertensión, tabaquismo, peso corporal / obesidad, consumo de alcohol, actividad física, edad, sexo, colesterol. | Fuente centrada en hipertensión y factores de riesgo relacionados. |
| **SRC-05** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo controlar la presión arterial* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Clasificación de la presión arterial y estrategias para mantener niveles saludables. | Presión arterial / hipertensión, tabaquismo, actividad física, peso corporal, consumo de alcohol, prevención cardiovascular general. | Documento sintético con alta concentración temática en hipertensión. |
| **SRC-06** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo alimentarse mejor* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Orientaciones para mantener un patrón alimentario saludable. | Alimentación, consumo de alcohol, presión arterial, prevención cardiovascular general. | Enfatiza reducción de sodio, azúcares añadidos y grasas saturadas. |
| **SRC-07** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo controlar el colesterol* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Conceptos sobre colesterol y estrategias relacionadas con su control. | Colesterol HDL / LDL, tabaquismo, actividad física, prevención cardiovascular general. | Fuente concentrada principalmente en perfil lipídico. |
| **SRC-08** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo dormir lo suficiente* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Importancia del sueño adecuado para la salud cardiovascular. | Sueño, prevención cardiovascular general, presión arterial, peso corporal / obesidad. | Fuente especializada en hábitos de sueño. |
| **SRC-09** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo controlar el azúcar en la sangre* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Conceptos sobre glucemia y hábitos asociados con su control. | Glucemia / diabetes, peso corporal, tabaquismo, actividad física, prevención cardiovascular general. | Incluye información sobre rangos de glucemia y hábitos preventivos. |
| **SRC-10** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo mantener un peso saludable* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Control del peso corporal y utilización del índice de masa corporal. | Peso corporal, IMC / obesidad, actividad física, prevención cardiovascular general. | Fuente centrada en peso corporal e IMC. |
| **SRC-11** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo ser más activo* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Recomendaciones sobre actividad física aeróbica y fortalecimiento muscular. | Actividad física, prevención cardiovascular general. | Fuente especializada en actividad física e inactividad. |
| **SRC-12** | *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo dejar el tabaco y los productos de nicotina* | American Heart Association (AHA) | Hoja informativa / Recomendación oficial | Riesgos relacionados con nicotina y estrategias para abandonar su consumo. | Tabaquismo, presión arterial, prevención cardiovascular general. | Fuente especializada en tabaquismo y nicotina. |
| **SRC-13** | *HEARTS en las Américas: Compendio de herramientas clínicas esenciales 2023* | Organización Panamericana de la Salud (OPS) / OMS; Andrés Rosende, Pedro Orduñez et al. | Guía clínica / Documento técnico institucional | Herramientas clínicas para el manejo de hipertensión arterial y riesgo cardiovascular en atención primaria. | Presión arterial / hipertensión, tabaquismo, actividad física, consumo de alcohol, peso corporal / IMC, edad, sexo, prevención cardiovascular general. | Documento técnico extenso orientado principalmente a profesionales de la salud y con alta densidad de contenido sobre hipertensión. |

- **Supabase:** brinda almacenamiento persistente en PostgreSQL y soporte para consultas vectoriales con pgvector. En la versión actual almacena los fragmentos vectorizados del corpus documental y sus metadatos.
- **MLOps y versionado:** MLflow, GitHub Actions y el versionado del artefacto del modelo (con su huella SHA-256 registrada) permiten mantener trazabilidad, reproducibilidad y control del pipeline de Machine Learning. El workflow de entrega continua publica las imágenes Docker en GitHub Container Registry (GHCR).

Estos componentes se relacionan directamente con los requerimientos del proyecto. El frontend cubre la interacción con el usuario; NGINX centraliza el acceso; el backend garantiza la coordinación y validación; el servicio de ML ofrece la predicción; SHAP soporta la explicación interpretativa; la simulación permite comparar escenarios; el RAG aporta recomendaciones y contexto documental; y Supabase asegura la persistencia del corpus.

La **Figura 1** presenta el diagrama de arquitectura del sistema. Muestra el actor principal, los componentes de PULSO y los servicios externos con los que se relacionan, sin detallar los módulos internos ni la infraestructura donde se ejecutan.

**Figura 1.** Diagrama de arquitectura del sistema PULSO.

```mermaid
flowchart TB
    U[Usuario / navegador]
    N[NGINX<br/>Reverse proxy]
    F[Frontend<br/>React + TypeScript + Vite]
    B[Backend / API<br/>FastAPI]
    M[ML Service<br/>FastAPI · PULSO v1 XGBoost<br/>SHAP + simulación]
    RAG[RAG<br/>workflow n8n]
    DB[(Supabase<br/>PostgreSQL + pgvector)]
    GEM[Modelo generativo<br/>Google Gemini]
    OPS[MLflow + GitHub Actions<br/>versionado, CI y CD]

    U --> N
    N -->|/| F
    N -->|/api/| B
    B -->|predicción, SHAP, simulación| M
    B -->|contexto del análisis| RAG
    RAG -->|búsqueda semántica| DB
    RAG -->|contexto documental| GEM
    M -.->|artefacto versionado| OPS
```

##### 10.1.2.2 Interacción entre módulos

La interacción entre módulos se diseña con un nivel de acoplamiento moderado-bajo. El frontend no se comunica directamente con el servicio de inferencia ni con la base de conocimiento. En cambio, accede al backend a través de NGINX y recibe respuestas ya estructuradas y procesadas. Esta decisión centraliza la validación, el control del flujo y la lógica de integración, reduciendo la dependencia directa entre la interfaz de usuario y los componentes computacionalmente más pesados.

Dentro del backend, las rutas HTTP (`interfaces/http`) convierten el JSON en entidades del dominio y ejecutan los casos de uso de la capa de aplicación (`AnalyzeProfile`, `RequestRecommendations` y `SimulateScenario`). Los casos de uso dependen únicamente de **puertos** definidos en el dominio (`CardiovascularModel`, `RecommendationGenerator` y `AnalysisRepository`), que son implementados por **adaptadores** de infraestructura: `MLServiceClient` (HTTP hacia el ML Service), `N8nRecommendationClient` (HTTP hacia el webhook de n8n) e `InMemoryAnalysisRepository` (caché temporal de análisis). La composición entre casos de uso e implementaciones se realiza en `dependencies.py`, y una prueba automatizada de arquitectura verifica que las dependencias entre capas respeten esta regla.

El flujo general de datos puede resumirse de la siguiente manera:

1. El usuario introduce datos clínicos mediante el frontend.
2. La solicitud se envía a `/api/analyze` a través de NGINX.
3. El backend valida y normaliza la información recibida (rangos, `ap_hi > ap_lo` y coherencia del IMC).
4. Se invoca el ML Service para estimar el riesgo cardiovascular y calcular la explicación SHAP.
5. El backend guarda el contexto del análisis en la caché temporal y devuelve la predicción, los factores SHAP y un `analysis_id`.
6. Cuando el usuario solicita las recomendaciones, el frontend envía únicamente el `analysis_id` a `/api/rag`; el backend recupera el contexto y lo envía al workflow RAG.
7. El RAG recupera fragmentos del corpus en Supabase, genera la respuesta con Gemini y la devuelve con sus fuentes; el backend valida el contrato antes de entregarla al frontend.
8. Para una simulación, el frontend envía el perfil original y los cambios a `/api/simulate`, y el backend devuelve la comparación entre ambos escenarios.

Este esquema presenta varias ventajas. En primer lugar, permite separar de forma clara la lógica de negocio de la experiencia del usuario. En segundo lugar, reduce el acoplamiento entre componentes al depender de contratos de entrada y salida definidos, en lugar de implementaciones internas concretas. En tercer lugar, facilita el trabajo paralelo del equipo, ya que cada servicio puede desarrollarse y validarse de manera independiente, siempre que se respeten los formatos de intercambio acordados.

El acoplamiento más fuerte se presenta entre el backend y los servicios especializados, dado que el orquestador debe coordinar llamadas, manejar errores parciales y consolidar resultados. Sin embargo, este nivel de dependencia es controlado mediante los puertos del dominio: reemplazar el RAG o el servicio de modelo solo requiere un nuevo adaptador que cumpla el puerto correspondiente, sin modificar los casos de uso.

La **Figura 2** abre el backend y el ML Service para mostrar cómo colaboran sus módulos internos: rutas, casos de uso, puertos y adaptadores en el backend, y predictor, explicador y simulador en el ML Service.

**Figura 2.** Diagrama de interacción entre módulos.

```mermaid
flowchart LR
    F[Frontend<br/>services/api.ts] -->|/api/*| N[NGINX]
    N --> R

    subgraph BE[Backend FastAPI]
        R[interfaces/http<br/>routes + schemas]
        UC1[AnalyzeProfile]
        UC2[RequestRecommendations]
        UC3[SimulateScenario]
        P1{{Puerto<br/>CardiovascularModel}}
        P2{{Puerto<br/>RecommendationGenerator}}
        P3{{Puerto<br/>AnalysisRepository}}
        A1[MLServiceClient]
        A2[N8nRecommendationClient]
        A3[InMemoryAnalysisRepository<br/>TTL 900 s · 100 entradas]
        R --> UC1 & UC2 & UC3
        UC1 --> P1 & P3
        UC2 --> P3 & P2
        UC3 --> P1
        P1 -.implementa.- A1
        P2 -.implementa.- A2
        P3 -.implementa.- A3
    end

    subgraph ML[ML Service FastAPI]
        ML1[model_loader<br/>PULSO v1]
        ML2[predictor<br/>threshold 0.38]
        ML3[explainer<br/>SHAP]
        ML4[simulator]
        ML2 --> ML1
        ML3 --> ML1
        ML4 --> ML2
    end

    A1 -->|HTTP /predict /explain /simulate| ML2 & ML3 & ML4
    A2 -->|HTTP webhook<br/>X-PULSO-RAG-Key| RAG[Workflow RAG n8n]
    RAG --> DB[(Supabase pgvector)]
    RAG --> G[Google Gemini]
```

##### 10.1.2.3 Comportamiento

El comportamiento general de la arquitectura refleja una secuencia lógica y eficiente para la evaluación del riesgo cardiovascular. El flujo principal evita pasos redundantes: el sistema calcula la predicción una sola vez, la explicación se obtiene con la misma instancia del modelo y el RAG reutiliza el contexto guardado del análisis en lugar de repetir la inferencia. Esto permite limitar la latencia innecesaria y preservar la claridad del proceso para el usuario final.

No obstante, existen dos puntos importantes a considerar. El primero corresponde al costo computacional de la predicción y la explicabilidad, especialmente cuando SHAP requiere evaluar la contribución de variables en un modelo complejo. El segundo, y principal punto de espera, es la latencia asociada a la recuperación de información y a la generación de recomendaciones en el componente RAG, que depende de servicios externos (n8n, Supabase y Gemini). Para mitigarlo, el análisis se separó de las recomendaciones, el backend utiliza un tiempo de espera configurable (`RAG_TIMEOUT_SECONDS`, 90 segundos por defecto) y, ante una respuesta HTTP 503 del servicio de n8n (por ejemplo, durante un arranque en frío), realiza un único reintento tras 20 segundos.

La arquitectura refleja además un buen nivel de desacoplamiento y mantenimiento. Cada componente tiene una responsabilidad claramente definida: NGINX atiende el acceso externo, el frontend ofrece la experiencia visual, el backend coordina las operaciones, el servicio ML calcula el riesgo, SHAP interpreta la salida, la simulación compara escenarios, el RAG contextualiza la recomendación y Supabase gestiona el corpus vectorial. Esta estructura permite realizar mejoras o sustituciones parciales sin recurrir a una reestructuración completa del sistema.

A continuación se presentan los tres procesos clave del sistema.

**Análisis del perfil cardiovascular.** La **Figura 3** muestra la secuencia de `POST /api/analyze`. El resultado es la probabilidad estimada, la clasificación, los factores SHAP y un `analysis_id`. Si los datos no cumplen las reglas del perfil, el backend responde con HTTP 422; si el ML Service no está disponible o responde fuera de contrato, responde con HTTP 502. El punto de espera relevante es la inferencia y el cálculo de SHAP en el ML Service.

**Figura 3.** Diagrama de secuencia del análisis del perfil.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant N as NGINX
    participant B as Backend API
    participant M as ML Service
    participant C as Caché de análisis

    U->>F: Ingresa variables clínicas
    F->>N: POST /api/analyze
    N->>B: Reenvía solicitud
    B->>B: Valida datos y reglas del perfil
    alt Datos inválidos
        B-->>F: 422 con mensaje de validación
    end
    B->>M: POST /predict
    M-->>B: probability + classification (threshold 0.38) + versión
    B->>M: POST /explain
    M-->>B: top factores SHAP
    B->>C: Guarda contexto (TTL 900 s)
    B-->>F: analysis_id + prediction + shap
    F-->>U: Muestra riesgo y explicación
```

**Solicitud de recomendaciones mediante RAG.** La **Figura 4** muestra la secuencia de `POST /api/rag`. El frontend envía únicamente el `analysis_id`; el backend recupera el contexto validado y lo envía al workflow. El resultado es un reporte con resumen, explicaciones educativas por factor, hasta tres recomendaciones, consideraciones, nota, indicador de información insuficiente y fuentes. Si el análisis expiró, el backend responde con HTTP 404; si el RAG no responde, excede el tiempo de espera o devuelve una estructura que no cumple el contrato (por ejemplo, fuentes citadas sin metadatos), responde con HTTP 502. Este es el principal punto de espera del sistema.

**Figura 4.** Diagrama de secuencia de la solicitud de recomendaciones.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend API
    participant C as Caché de análisis
    participant R as RAG n8n
    participant DB as Supabase / pgvector
    participant G as Gemini

    U->>F: Solicita recomendaciones
    F->>B: POST /api/rag {analysis_id}
    B->>C: Recupera contexto
    alt Análisis inexistente o expirado
        B-->>F: 404
    end
    B->>R: Webhook (prediction + user_data + shap), cabecera X-PULSO-RAG-Key
    opt HTTP 503 (arranque en frío)
        B->>B: Espera 20 s
        B->>R: Reintenta una vez
    end
    R->>DB: Búsqueda semántica del corpus
    DB-->>R: top-k fragmentos + metadatos
    R->>G: Contexto documental
    G-->>R: Resumen, explicaciones y recomendaciones
    R-->>B: Reporte + fuentes
    B->>B: Valida contrato y referencias a fuentes
    B-->>F: Reporte RAG
    F-->>U: Muestra recomendaciones y fuentes
```

**Simulación de escenarios.** La **Figura 5** muestra la secuencia de `POST /api/simulate`. El resultado conserva la estimación original y presenta la probabilidad simulada, la diferencia y la clasificación del escenario hipotético. Si el escenario no es válido (por ejemplo, presión sistólica menor o igual que la diastólica), se responde con HTTP 422.

**Figura 5.** Diagrama de secuencia de la simulación de escenarios.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend API
    participant M as ML Service

    U->>F: Modifica variables habilitadas
    F->>B: POST /api/simulate (perfil original + cambios)
    B->>B: Valida el escenario
    B->>M: POST /simulate
    M->>M: Recalcula IMC si cambia el peso y ejecuta PULSO v1
    M-->>B: probabilidad original, simulada, diferencia y clasificación
    B-->>F: Comparación de escenarios
    F-->>U: Muestra comparación original / simulado
```

En conjunto, los flujos no presentan pasos innecesarios: cada solicitud ejecuta únicamente los servicios que necesita y el RAG, que es el componente más lento, está desacoplado del resultado principal. El cuello de botella identificado es la dependencia del RAG de servicios externos; las medidas de tiempo de espera, reintento y validación de contrato limitan su impacto sobre el resto del sistema. La arquitectura resulta adecuada para el alcance del proyecto: mantiene la solución comprensible y viable para un MVP académico, favorece la evolución incremental del sistema y permite incorporar nuevos servicios o mejoras funcionales sin comprometer la estabilidad general del producto.

## 11. Implementación

Esta sección documenta el estado real de construcción del sistema y el grado de avance alcanzado.

### 11.1 Stack tecnológico

PULSO integra tecnologías orientadas al desarrollo web, aprendizaje automático, explicabilidad, recuperación documental, contenerización, integración continua y trazabilidad de experimentos. La selección del stack busca mantener una separación clara entre los componentes principales de la plataforma y facilitar su integración dentro de una arquitectura modular orientada a servicios.

- **React:** biblioteca utilizada para el desarrollo de la interfaz web de PULSO. Permite construir componentes reutilizables y gestionar de manera dinámica la interacción del usuario con los formularios, resultados de predicción, explicaciones, simulaciones e información generada mediante RAG.

- **TypeScript:** lenguaje utilizado en el frontend. Permite tipar los contratos de datos que la interfaz intercambia con el backend (análisis, SHAP, RAG y simulación) y detectar inconsistencias durante la compilación.

- **Vite:** herramienta de construcción y servidor de desarrollo del frontend. Genera la compilación de producción que se sirve dentro del contenedor del frontend.

- **Tailwind CSS:** framework de utilidades CSS utilizado para construir la presentación visual de la interfaz.

- **Vitest y Testing Library:** herramientas utilizadas para implementar las pruebas automatizadas del frontend.

- **oxlint:** analizador estático utilizado para verificar la calidad del código del frontend.

- **FastAPI:** framework utilizado para la construcción del backend y del ML Service. Permite exponer endpoints para la comunicación entre el frontend y los servicios internos del sistema, además de facilitar la validación de datos mediante modelos estructurados.

- **Python:** lenguaje principal utilizado para el desarrollo del backend, el procesamiento de datos, el entrenamiento y evaluación de modelos de Machine Learning, la generación de explicaciones mediante SHAP y la integración con otros servicios.

- **Pydantic:** biblioteca utilizada para definir y validar los contratos de datos intercambiados entre los diferentes componentes del sistema. Permite verificar que las solicitudes y respuestas cumplan con las estructuras esperadas, incluida la respuesta del workflow RAG.

- **httpx:** biblioteca utilizada para realizar solicitudes HTTP asíncronas desde el backend hacia el ML Service y el componente RAG.

- **scikit-learn:** biblioteca utilizada para el procesamiento de datos, entrenamiento, evaluación y comparación de diferentes modelos de Machine Learning, así como para el cálculo de métricas y la construcción de pipelines de modelado.

- **XGBoost:** biblioteca utilizada para implementar el modelo de Gradient Boosting seleccionado para el componente predictivo de PULSO. El modelo genera una probabilidad asociada con la pertenencia a la clase `cardio = 1`.

- **SHAP:** biblioteca de explicabilidad utilizada para calcular la contribución de las variables de entrada sobre las predicciones individuales del modelo. Sus resultados permiten identificar los factores con mayor influencia sobre cada estimación.

- **MLflow:** herramienta utilizada para registrar y mantener la trazabilidad de los experimentos de Machine Learning. Permite almacenar información asociada con modelos, parámetros, métricas, umbrales de decisión y artefactos generados durante la experimentación.

- **n8n:** plataforma utilizada para orquestar el workflow del componente RAG. Coordina la recepción de la información procedente del backend, la recuperación documental, la preparación del contexto, la interacción con el modelo generativo y la construcción de la respuesta final.

- **Supabase:** plataforma utilizada para gestionar servicios de almacenamiento y base de datos asociados con la aplicación. En el componente RAG se emplea para almacenar el corpus documental y facilitar la recuperación de fragmentos mediante búsqueda vectorial.

- **PostgreSQL:** sistema de gestión de bases de datos relacional utilizado como base de la infraestructura de almacenamiento proporcionada por Supabase.

- **pgvector:** extensión de PostgreSQL utilizada para almacenar representaciones vectoriales y ejecutar búsquedas por similitud semántica entre las consultas y los fragmentos documentales del corpus RAG.

- **Google Gemini:** modelo generativo utilizado en el componente RAG para construir respuestas en lenguaje natural utilizando como contexto los fragmentos documentales recuperados previamente.

- **Embeddings:** representaciones vectoriales utilizadas para transformar consultas y fragmentos documentales en estructuras numéricas comparables, permitiendo realizar recuperación semántica dentro del corpus.

- **JavaScript:** lenguaje utilizado principalmente dentro de nodos de código del workflow de n8n para normalizar información, preparar el contexto documental, procesar metadatos y estructurar la respuesta final del componente RAG.

- **Docker:** plataforma de contenerización utilizada para empaquetar los componentes de PULSO junto con sus dependencias, facilitando la ejecución reproducible y el aislamiento entre servicios.

- **Docker Compose:** herramienta utilizada para definir y ejecutar conjuntamente los contenedores de frontend, NGINX, backend y ML Service, incluyendo sus redes, puertos, variables de entorno, verificaciones de salud y dependencias.

- **Nginx:** servidor web utilizado como proxy inverso para centralizar el acceso externo y redirigir las solicitudes hacia el frontend o el backend. También se utiliza dentro del contenedor del frontend para servir la compilación de producción de React.

- **Git:** sistema de control de versiones utilizado para registrar y gestionar los cambios realizados sobre el código fuente del proyecto.

- **GitHub:** plataforma utilizada para alojar el repositorio del proyecto y gestionar el flujo colaborativo de desarrollo mediante ramas, pull requests y revisión de código.

- **GitHub Actions:** servicio de integración y entrega continua utilizado para automatizar verificaciones sobre el código, ejecutar pruebas, validar la infraestructura y publicar las imágenes Docker.

- **GitHub Container Registry (GHCR):** registro donde el workflow de entrega continua publica las imágenes Docker del frontend, backend y ML Service.

- **Pytest:** framework utilizado para implementar y ejecutar pruebas automatizadas sobre los componentes desarrollados en Python, incluyendo el backend, el ML Service y el pipeline de entrenamiento.

- **Ruff:** analizador estático utilizado para verificar la calidad del código Python del ML Service y del pipeline de entrenamiento.

- **JSON:** formato utilizado para el intercambio estructurado de información entre el frontend, backend, servicio de Machine Learning, componente RAG y otros elementos de la arquitectura.

### 11.2 Componentes

En el estado actual de PULSO se encuentran implementados e integrados los componentes funcionales definidos para el MVP: el modelo predictivo, el servicio de Machine Learning, la explicación mediante SHAP, la simulación de escenarios, el backend, el componente RAG, el frontend, el proxy inverso NGINX y la contenerización de los servicios principales.

#### Modelo predictivo

El modelo final seleccionado corresponde a **PULSO v1**, basado en XGBoost y configurado con un umbral de decisión de **0,38**. El artefacto final se encuentra serializado y es utilizado exclusivamente para inferencia dentro del ML Service.

El modelo recibe las variables definidas durante la preparación y selección final de características y genera como salida una probabilidad estimada, una clasificación binaria, el threshold utilizado y la versión del modelo.

La clasificación se determina mediante la regla:

`probability >= 0.38 → classification = 1`

El modelo no se vuelve a entrenar durante las solicitudes realizadas por la aplicación y se carga una única vez al iniciar el servicio.

La copia oficial del artefacto (`models/pulso/v1/pulso_xgboost.joblib`) se versiona en el repositorio junto con su configuración congelada (`final_model.yaml`) y sus metadatos (`metadata.yaml`), donde se registra su huella SHA-256. Esta copia es la que se incorpora a la imagen Docker del ML Service, lo que garantiza que el modelo desplegado corresponda al modelo aprobado.

#### ML Service

El componente de Machine Learning se encuentra implementado como un servicio independiente mediante FastAPI. Su función es concentrar las operaciones relacionadas con inferencia y mantener separada esta lógica del backend encargado de la orquestación.

El servicio contiene los módulos necesarios para:

- cargar el modelo final (`model_loader`);
- validar las variables de entrada;
- generar la probabilidad y clasificación aplicando el threshold de 0,38 (`predictor`);
- calcular explicaciones mediante SHAP (`explainer`);
- ejecutar simulaciones de escenarios (`simulator`);
- exponer mecanismos de verificación del estado del servicio (`/health`, que informa si el modelo está cargado).

El modelo permanece cargado en memoria y es reutilizado por las solicitudes posteriores, evitando operaciones de carga repetitivas.

#### Explicabilidad mediante SHAP

La generación de explicaciones mediante SHAP se encuentra integrada dentro del ML Service y utiliza la misma instancia del modelo, el mismo preprocesamiento, el mismo orden de variables y la misma versión empleada para realizar la predicción.

La salida generada incluye, para los principales factores identificados:

- nombre de la variable;
- valor correspondiente al usuario;
- valor SHAP;
- dirección de la contribución sobre la salida del modelo.

La interfaz transforma posteriormente esta información a una presentación más comprensible para usuarios no especializados, mediante una visualización de los factores principales. Las contribuciones se muestran como explicaciones del comportamiento del clasificador y no como relaciones causales entre las variables y la enfermedad cardiovascular.

#### Simulación de escenarios

El componente de simulación se encuentra integrado en el ML Service, el backend y el frontend. Permite modificar determinadas variables habilitadas y ejecutar nuevamente el mismo modelo PULSO v1 sobre un escenario hipotético.

Pueden modificarse variables como peso, presión arterial sistólica y diastólica, tabaquismo, consumo de alcohol y actividad física. Cuando se modifica el peso, el sistema recalcula el IMC (BMI) manteniendo la altura original del usuario. La interfaz restringe los valores a los rangos permitidos y el backend valida que el escenario resultante sea coherente (por ejemplo, que la presión sistólica sea mayor que la diastólica).

El resultado de la simulación conserva la estimación inicial y presenta:

- probabilidad original;
- probabilidad simulada;
- diferencia entre ambas;
- clasificación correspondiente al escenario simulado.

La simulación representa únicamente el comportamiento matemático del modelo ante cambios en las variables de entrada y no se presenta como el efecto clínico garantizado de una intervención.

#### Backend

El backend se encuentra implementado mediante FastAPI y actúa como componente central de orquestación de PULSO. Su código se reorganizó siguiendo **Clean Architecture** en cuatro capas:

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Dominio | `backend/app/domain/` | Entidades inmutables, reglas del perfil, errores del negocio y puertos (interfaces) |
| Aplicación | `backend/app/application/use_cases/` | Casos de uso `AnalyzeProfile`, `RequestRecommendations` y `SimulateScenario` |
| Infraestructura | `backend/app/infrastructure/` | Clientes HTTP del ML Service y de n8n, caché de análisis en memoria y configuración |
| Interfaces | `backend/app/interfaces/http/` | Rutas FastAPI, contratos JSON, inyección de dependencias y traducción de errores a HTTP |

Expone las rutas:

- `POST /api/analyze`: valida el perfil, solicita al ML Service la predicción y la explicación SHAP, guarda el contexto del análisis y devuelve la predicción, los factores SHAP y un `analysis_id`. No ejecuta el RAG.
- `POST /api/rag`: recibe únicamente el `analysis_id`, recupera el contexto guardado y solicita las recomendaciones al workflow RAG, sin repetir la inferencia.
- `POST /api/simulate`: recibe el perfil original y los cambios definidos por el usuario, los envía al ML Service y devuelve la comparación entre el escenario original y el simulado.
- `GET /api/health`: verificación del estado del servicio.

El backend concentra el manejo de errores derivados de las comunicaciones internas y los traduce a códigos HTTP: 422 para datos o escenarios inválidos, 404 cuando un análisis no existe o ya expiró, y 502 cuando el ML Service o el RAG no están disponibles o responden fuera de contrato.

El contexto de cada análisis se conserva en una caché en memoria con TTL de 900 segundos y un máximo de 100 registros. Esta caché está diseñada para una única instancia del backend; un despliegue con varias réplicas requeriría un almacenamiento compartido, como Redis, que puede incorporarse implementando el puerto `AnalysisRepository` sin modificar los casos de uso.

#### Componente RAG

El componente RAG se encuentra implementado mediante un workflow en n8n (versión 3.4.2, con Gemini nativo) conectado con un almacén vectorial en Supabase y un modelo generativo. El workflow recibe información procedente del componente predictivo, recupera los fragmentos documentales con mayor similitud semántica, prepara el contexto y genera una respuesta estructurada con información preventiva relacionada con los factores considerados prioritarios. El corpus se carga mediante un workflow de vectorización independiente.

El flujo incorpora etapas de normalización y preparación de los datos recuperados, con el propósito de conservar tanto el contenido documental como los metadatos necesarios para identificar posteriormente la procedencia de la información.

La respuesta incluye:

- resumen;
- explicaciones educativas por factor, asociadas a las variables identificadas mediante SHAP;
- hasta tres recomendaciones, cada una vinculada a un factor y a sus fuentes;
- consideraciones;
- nota;
- indicador de información insuficiente (`insufficient_information`);
- identificadores y datos de las fuentes utilizadas (título, autor, año, enlace, puntaje de similitud y líneas del fragmento).

El backend valida esta respuesta antes de entregarla al frontend: verifica la estructura del contrato y comprueba que cada identificador de fuente citado en una recomendación o explicación cuente con sus metadatos documentales. Las solicitudes al webhook se protegen mediante la cabecera `X-PULSO-RAG-Key`, cuyo valor se configura como variable de entorno (`RAG_WEBHOOK_API_KEY`).

Como parte de la implementación se construyó un corpus documental compuesto por **13 fuentes** relacionadas con prevención y factores cardiovasculares. Los documentos fueron incorporados al flujo de vectorización y almacenados en la base vectorial junto con metadatos destinados a conservar la identificación de la fuente y la localización de los fragmentos.

#### Frontend

El frontend se encuentra implementado mediante **React, TypeScript, Vite y Tailwind CSS** y permite ejecutar el flujo funcional completo del MVP. Se organiza en tres vistas principales: evaluación (`EvaluationPage`), resultado (`ResultPage`) y simulación (`SimulationPage`).

La interfaz incluye:

- formulario de ingreso de datos con validación de rangos;
- visualización de la probabilidad estimada;
- presentación del threshold y la clasificación, con una interpretación del resultado;
- visualización de los factores SHAP;
- solicitud bajo demanda de las recomendaciones generadas mediante RAG y presentación de las explicaciones por factor, recomendaciones y fuentes documentales;
- contenido educativo general de bienestar, igual para todos los perfiles y no generado por el modelo;
- panel de simulación;
- comparación entre estimación original y simulada;
- advertencias relacionadas con el alcance y las limitaciones de PULSO.

El frontend informa que la plataforma tiene una finalidad educativa y preventiva, que no constituye un diagnóstico, que SHAP no demuestra causalidad y que las simulaciones no representan efectos clínicos garantizados.

Para evitar resultados inconsistentes, el frontend cancela las solicitudes RAG pendientes al iniciar un nuevo análisis y verifica que cada respuesta corresponda al `analysis_id` vigente, de modo que no se muestren recomendaciones de un perfil anterior junto con la predicción actual.

Con respecto a la arquitectura objetivo, el frontend ya fue migrado a TypeScript y se encuentra contenerizado.

#### Contenerización

El frontend, NGINX, el backend y el ML Service se ejecutan mediante Docker Compose:

- **frontend:** imagen construida en dos etapas; Node.js compila la aplicación con Vite y NGINX sirve los archivos estáticos resultantes. Solo expone el puerto 80 dentro de la red de Docker.
- **nginx:** imagen `nginx:stable-alpine` con la configuración `infrastructure/nginx/default.conf`; es el único servicio publicado al exterior (puerto 80).
- **backend:** imagen Python 3.11 que ejecuta FastAPI con Uvicorn; arranca cuando el ML Service reporta estado saludable.
- **ml-service:** imagen Python 3.11 que incluye el artefacto oficial del modelo y define un healthcheck sobre `/health`.

La comunicación interna entre backend y ML Service se realiza mediante el nombre del servicio Docker:

`http://ml-service:8001`

El workflow de n8n se ejecuta fuera del Docker Compose principal y el backend lo consume mediante la dirección configurada en `RAG_SERVICE_URL`.

---

### 11.3 Integraciones

La implementación permite ejecutar el flujo funcional completo de PULSO mediante la integración de frontend, NGINX, backend, ML Service, SHAP, simulación y RAG.

#### Integración frontend–backend

El frontend se encuentra conectado al backend mediante solicitudes HTTP. Utiliza los endpoints:

- `/api/analyze`, para ejecutar el análisis principal;
- `/api/rag`, para solicitar las recomendaciones a partir del `analysis_id`;
- `/api/simulate`, para realizar escenarios hipotéticos.

En el entorno contenerizado, el frontend se compila con una URL base vacía, por lo que las solicitudes a `/api/` se envían al mismo origen y NGINX las reenvía al backend. En el entorno de desarrollo, la dirección del backend puede configurarse mediante `VITE_API_URL`.

**Estado:** funcional.

#### Integración NGINX–frontend–backend

NGINX enruta `/` hacia el contenedor del frontend y `/api/` hacia el backend, conservando el prefijo `/api/`. Utiliza el DNS interno de Docker para resolver los servicios y define tiempos de espera de lectura y envío de 180 segundos para las solicitudes al backend, suficientes para las respuestas del RAG.

**Estado:** funcional.

#### Integración backend–ML Service

El backend consume el ML Service mediante comunicación HTTP a través del adaptador `MLServiceClient` y no importa directamente la lógica interna del componente de Machine Learning.

Dentro del entorno Docker, el backend utiliza el nombre del servicio para establecer esta comunicación, evitando el uso de `localhost` entre contenedores.

El backend envía el perfil del usuario al ML Service y recibe los resultados correspondientes a la predicción y la explicación SHAP. Para la simulación, también utiliza el ML Service para generar una nueva estimación utilizando el mismo modelo PULSO v1.

Esta separación permite modificar internamente el componente predictivo sin alterar la lógica principal del backend, siempre que los contratos de entrada y salida permanezcan estables.

**Estado:** funcional.

#### Integración Modelo–SHAP

El predictor y el módulo de explicación se encuentran separados internamente, pero comparten la misma instancia del modelo final.

SHAP utiliza el mismo modelo, versión, orden de variables y preprocesamiento que produjo la predicción. De esta manera se evita generar explicaciones a partir de una configuración diferente de aquella utilizada para obtener el resultado mostrado al usuario.

**Estado:** funcional.

#### Integración backend–RAG

La integración entre el backend de PULSO y el componente RAG se realiza mediante comunicación HTTP a través del adaptador `N8nRecommendationClient`.

Cuando se solicita `/api/rag`, el backend recupera el contexto guardado del análisis y construye una estructura que contiene:

- resultado de la predicción;
- datos relevantes del perfil;
- factores principales identificados mediante SHAP.

Esta información es enviada al webhook del workflow de n8n, junto con la cabecera `X-PULSO-RAG-Key`, donde se ejecutan las etapas de recuperación y generación.

El RAG no ejecuta nuevamente el modelo, no calcula SHAP, no modifica la clasificación ni cambia el threshold. Su función se limita a utilizar la información recibida como contexto para recuperar evidencia documental y generar información preventiva.

La respuesta RAG contiene información estructurada sobre el resumen, explicaciones por factor, recomendaciones, consideraciones y fuentes utilizadas. El backend valida esta estructura antes de incorporarla a la respuesta enviada al frontend.

La integración contempla mecanismos para manejar errores de comunicación, tiempos de espera (`RAG_TIMEOUT_SECONDS`, 90 segundos por defecto), respuestas que no cumplen el formato esperado y un reintento único tras 20 segundos cuando el servicio de n8n responde HTTP 503, situación que se presenta durante los arranques en frío del servicio alojado.

**Estado:** funcional.

#### Integración RAG–Supabase

El componente RAG utiliza Supabase como almacén vectorial para los fragmentos documentales.

Los documentos del corpus son vectorizados y almacenados junto con metadatos asociados a las fuentes. Durante una solicitud, el workflow realiza una búsqueda semántica y recupera los fragmentos considerados más pertinentes para construir el contexto suministrado al modelo generativo.

La conservación de los metadatos permite vincular las recomendaciones generadas con los documentos y fragmentos utilizados durante la recuperación.

**Estado:** funcional.

#### Integración del flujo completo

PULSO ejecuta el siguiente flujo de análisis:

`Frontend → NGINX → Backend → ML Service → Predicción + SHAP → Backend → Frontend`

Las recomendaciones se obtienen en una solicitud posterior:

`Frontend → NGINX → Backend → RAG (n8n → Supabase → Gemini) → Backend → Frontend`

De manera adicional, la simulación utiliza:

`Frontend → NGINX → Backend → ML Service → nueva estimación → Backend → Frontend`

Este flujo permite que los componentes se mantengan desacoplados mediante contratos HTTP, mientras el backend actúa como punto central de coordinación.

## 12. Despliegue y operación

PULSO cuenta con un entorno de ejecución contenerizado que integra el frontend, NGINX, el backend y el ML Service mediante Docker Compose, y con un componente RAG que se ejecuta como un servicio externo al stack. Esta sección describe cómo se instala, configura y opera la solución.

### 12.1 Entorno de ejecución

El **frontend**, **NGINX**, el **backend** y el **ML Service** se ejecutan mediante Docker Compose. El componente **RAG**, implementado mediante un workflow de n8n, se ejecuta fuera del Docker Compose principal y se consume a través de su webhook. Los servicios externos utilizados por el RAG son Supabase (almacén vectorial) y Google Gemini (modelo generativo).

Por tanto, la ejecución completa de la solución requiere:

1. Una instancia de n8n con el workflow RAG habilitado y su webhook de producción accesible.
2. Docker Compose con los servicios frontend, nginx, backend y ml-service.

El flujo operativo puede representarse de la siguiente forma:

`Usuario → NGINX → Frontend React | Backend FastAPI → ML Service / RAG n8n → Backend → Frontend`

El backend actúa como componente orquestador. Recibe las solicitudes provenientes del frontend a través de NGINX, invoca al ML Service para obtener la predicción y la explicación mediante SHAP y, cuando el usuario lo solicita, consulta el componente RAG con el contexto del análisis.

### 12.2 Servicios y puertos utilizados

| Componente | Tecnología / entorno | Acceso |
|---|---|---|
| NGINX (punto de entrada) | `nginx:stable-alpine` | `http://localhost` (puerto 80) |
| Frontend | React + Vite servido por NGINX | Puerto 80 interno, no publicado al host |
| Backend | FastAPI + Docker | `http://127.0.0.1:8000` (solo interfaz local) |
| Backend Swagger | FastAPI | `http://127.0.0.1:8000/docs` |
| Health check backend | FastAPI | `http://localhost/api/health` |
| ML Service | FastAPI + Docker | `http://127.0.0.1:8001` (solo interfaz local) |
| Health check ML | FastAPI | `http://127.0.0.1:8001/health` |
| RAG / n8n | Servicio externo al stack | Dirección configurada en `RAG_SERVICE_URL` |

Los puertos del backend y del ML Service se publican únicamente en la interfaz local del equipo (`127.0.0.1`) para facilitar la depuración; el acceso de los usuarios se realiza exclusivamente a través de NGINX.

Dentro del entorno Docker, la comunicación entre servicios utiliza los nombres definidos en Docker Compose. Por ejemplo, el backend se comunica con el ML Service mediante:

`http://ml-service:8001`

y no mediante `localhost`, debido a que cada contenedor posee su propio contexto de red.

### 12.3 Dependencias requeridas

Para ejecutar el sistema se requiere disponer de:

- Docker Desktop.
- Docker Compose.
- Git.
- El repositorio de PULSO, que ya incluye el artefacto oficial del modelo `models/pulso/v1/pulso_xgboost.joblib`.
- Una instancia de n8n con el workflow RAG configurado y habilitado.
- Las credenciales de Supabase y Google Gemini configuradas en n8n.
- Las variables de entorno del backend.

Node.js y npm solo son necesarios para ejecutar el frontend en modo de desarrollo, ya que la imagen Docker compila la aplicación internamente.

El ML Service carga el modelo final de PULSO desde el artefacto serializado incluido en su imagen y lo mantiene en memoria durante la ejecución del servicio. De esta manera, el modelo no se vuelve a cargar ni se reentrena para cada solicitud.

### 12.4 Configuración

El backend se configura mediante variables de entorno (archivo `.env` o `.env.docker`, excluidos del control de versiones; `.env.example` sirve como referencia):

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `ML_SERVICE_URL` | Dirección del ML Service | `http://ml-service:8001` en Docker |
| `ML_TIMEOUT_SECONDS` | Tiempo de espera hacia el ML Service | 30 |
| `RAG_SERVICE_URL` | URL del webhook de producción del workflow RAG | — |
| `RAG_TIMEOUT_SECONDS` | Tiempo de espera hacia el RAG | 90 |
| `RAG_WEBHOOK_API_KEY` | Clave enviada en la cabecera `X-PULSO-RAG-Key` (obligatoria en Docker Compose) | — |
| `ANALYSIS_CACHE_TTL_SECONDS` | Vigencia del contexto de cada análisis | 900 |
| `ANALYSIS_CACHE_MAX_ENTRIES` | Máximo de análisis en caché | 100 |

Si n8n se ejecuta en el mismo equipo, fuera de Docker, el backend no puede utilizar `localhost` para acceder a él, por lo que la URL debe apuntar a una dirección accesible desde el contenedor, por ejemplo:

```env
RAG_SERVICE_URL=http://host.docker.internal:5678/webhook/pulso-rag
```

La ruta exacta depende del webhook activo en el workflow de n8n. Para la integración estable debe utilizarse el webhook de producción y no el endpoint de prueba. Cuando n8n se aloja en un servicio externo, `RAG_SERVICE_URL` apunta a su URL pública; en ese caso, el reintento ante HTTP 503 permite tolerar los arranques en frío del servicio.

Las credenciales, claves y direcciones sensibles se gestionan mediante variables de entorno y no se almacenan en el repositorio.

### 12.5 Puesta en marcha

Desde la raíz del repositorio:

```bash
docker compose --env-file .env.docker up -d --build
```

Comprobar el estado de los servicios:

```bash
docker compose --env-file .env.docker ps
```

Una vez activos los servicios, la aplicación queda disponible en `http://localhost`. Docker Compose inicia el backend solo cuando el healthcheck del ML Service confirma que el servicio está disponible.

Para el desarrollo del frontend con recarga en caliente puede ejecutarse `npm run dev` en la carpeta `frontend`, configurando `VITE_API_URL` con la dirección del backend.

### 12.6 Integración y entrega continua

El repositorio cuenta con workflows de GitHub Actions que se ejecutan sobre cada pull request:

| Workflow | Verificaciones |
|---|---|
| Frontend CI | Instalación de dependencias, lint (oxlint), verificación de tipos (TypeScript), pruebas (Vitest) y compilación |
| Backend and RAG checks | Pruebas del backend, incluida la regla de dependencias de Clean Architecture y el cliente RAG |
| ML Service checks | Lint (Ruff) y pruebas del ML Service |
| ML training checks | Lint (Ruff) y pruebas del pipeline de entrenamiento |
| Infrastructure CI | Validación de `docker-compose.yml`, construcción de las imágenes, validación de la configuración de NGINX y verificación del enrutamiento de `/` y `/api/` con servicios simulados |

Adicionalmente, el workflow de **entrega continua** (`delivery.yml`) se ejecuta en la rama `main` (o manualmente desde ella) y:

1. construye y publica en GitHub Container Registry las imágenes del frontend, backend y ML Service, con etiquetas únicas por ejecución (versión, commit y ejecución);
2. descarga las imágenes publicadas y verifica que correspondan al commit esperado;
3. ejecuta pruebas de humo (smoke tests): el frontend debe devolver HTML, el ML Service debe confirmar que el modelo está cargado y el backend debe responder correctamente en `/api/health` conectado al ML Service;
4. registra los digests verificados en el resumen de la ejecución.

### 12.7 Diagrama de despliegue

La **Figura 6** muestra dónde se ejecutan los componentes de PULSO: el dispositivo del usuario, el equipo anfitrión con los contenedores de Docker Compose y su red interna, y los servicios externos de los que depende el RAG.

**Figura 6.** Diagrama de despliegue de PULSO.

```mermaid
flowchart LR
    subgraph CLIENTE[Dispositivo del usuario]
        BR[Navegador web]
    end

    subgraph HOST[Equipo anfitrión · Docker Engine]
        subgraph NET[Red interna de Docker Compose]
            NG[pulso-nginx<br/>nginx:stable-alpine<br/>:80 publicado]
            FE[pulso-frontend<br/>NGINX + build de Vite<br/>:80 interno]
            BE[pulso-backend<br/>Python 3.11 · FastAPI<br/>127.0.0.1:8000]
            ML[pulso-ml-service<br/>Python 3.11 · FastAPI<br/>modelo pulso_xgboost.joblib<br/>127.0.0.1:8001]
        end
    end

    subgraph EXT[Servicios externos]
        N8N[n8n<br/>workflow RAG v3.4.2]
        SB[(Supabase<br/>PostgreSQL + pgvector)]
        GM[Google Gemini API]
    end

    subgraph GH[GitHub]
        GA[GitHub Actions<br/>CI / CD]
        GHCR[(GHCR<br/>imágenes Docker)]
    end

    BR -->|HTTP :80| NG
    NG -->|/| FE
    NG -->|/api/| BE
    BE -->|HTTP ml-service:8001| ML
    BE -->|HTTP/HTTPS webhook<br/>X-PULSO-RAG-Key| N8N
    N8N -->|consulta vectorial| SB
    N8N -->|HTTPS| GM
    GA -->|publica imágenes| GHCR
```

### 12.8 Estado funcional del despliegue

Actualmente pueden ejecutarse:

- ingreso de datos desde el frontend;
- predicción mediante PULSO v1;
- aplicación del threshold de 0,38;
- generación de explicaciones mediante SHAP;
- recuperación y generación de información preventiva mediante RAG;
- visualización de fuentes documentales;
- simulación de escenarios hipotéticos;
- comparación entre la estimación original y la simulada.

El sistema también permite realizar verificaciones independientes del frontend utilizando Swagger y los endpoints de salud, lo que facilita identificar si un problema corresponde a la interfaz, al backend, al ML Service, al RAG o a la configuración de red.

Como condiciones de operación, la caché de análisis del backend no es persistente: los contextos expiran a los 900 segundos y se pierden al reiniciar el contenedor, por lo que una solicitud de recomendaciones posterior requiere un nuevo análisis. NGINX atiende únicamente HTTP en el puerto 80; un despliegue público requeriría configurar TLS.

## 13. Validación

Presenta el informe de pruebas realizadas para verificar que el sistema funciona correctamente y cumple los requerimientos establecidos.

### 13.1 Pruebas por componentes

Documenta las pruebas unitarias o por módulo ejecutadas, los criterios de éxito, los casos evaluados y los resultados obtenidos.

### 13.2 Pruebas de integración

Describe las pruebas realizadas sobre la interacción entre componentes y servicios, incluyendo flujos completos, manejo de errores y resultados observados.

### 13.3 Pruebas de usabilidad

Expone las pruebas de usabilidad aplicadas para evaluar la experiencia del usuario, indicando metodología, criterios de aceptación, hallazgos y nivel de cumplimiento.

## 14. Resultados, discusión y conclusiones

Presenta los resultados obtenidos a partir del desarrollo y la validación del sistema, e interpreta su significado frente a los objetivos, requerimientos, decisiones de diseño y limitaciones del proyecto.

## 15. Trabajo futuro

Identifica y describe posibles extensiones, mejoras o líneas de investigación que quedan abiertas a partir del proyecto. Puede incluir nuevas funcionalidades, optimizaciones, escalabilidad, integraciones con otros sistemas o estudios complementarios que permitan profundizar los resultados obtenidos.

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

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information Processing Systems, 33. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing. [https://doi.org/10.18653/v1/D19-1410](https://doi.org/10.18653/v1/D19-1410)

Sentence Transformers. (s. f.). Semantic search. [https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo alimentarse mejor*. https://www.heart.org/eatsmart 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo controlar el azúcar en la sangre*. https://www.heart.org/lifes8 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo controlar el colesterol*. https://www.heart.org/cholesterol 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo controlar la presión arterial*. https://www.heart.org/lifes8 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo dejar el tabaco y los productos de nicotina*. https://www.heart.org/lifes8 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo dormir lo suficiente*. https://www.heart.org/lifes8 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo mantener un peso saludable*. https://www.heart.org/lifes8 

American Heart Association. (s.f.). *Healthy for Good - Para Mi Salud: Los 8 Pasos Esenciales - Cómo ser más activo*. https://www.heart.org/lifes8 

American Heart Association. (s.f.). *Respuestas del corazón: Estilo de vida + Reducción de factores de riesgos - ¿Cómo puedo perder peso?*. https://www.heart.org/RespuestasDelCorazon 

American Heart Association. (s.f.). *Respuestas del corazón: Estilo de vida + Reducción de riesgos Presión arterial alta - ¿Qué es la presión arterial alta?*. https://www.heart.org/AnswersByHeart 

American Heart Association. (s.f.). *Respuestas del corazón: Estilo de vida + Riesgo reducción Dieta + Nutrición - ¿Cómo puedo seguir un patrón de alimentación saludable?*. https://www.heart.org/RespuestasDelCorazon 

American Heart Association. (s.f.). *Respuestas del corazón: Estilo de vida + Riesgo reducción Fumar - ¿Cómo dejo de fumar?*. https://www.heart.org/RespuestasDelCorazon 

Organización Panamericana de la Salud. (2024). *HEARTS en las Américas: Compendio de herramientas clínicas esenciales 2023* (Código: OPS/NMH/NV/24-0002). OPS. 

Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review, 78*(1), 1–3. https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. https://doi.org/10.1145/2939672.2939785

Docker. (s. f.). *What is a container?* Docker Docs. https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/

Fawcett, T. (2006). An introduction to ROC analysis. *Pattern Recognition Letters, 27*(8), 861–874. https://doi.org/10.1016/j.patrec.2005.10.010

Fielding, R. T. (2000). *Architectural styles and the design of network-based software architectures* [Doctoral dissertation, University of California, Irvine]. https://ics.uci.edu/~fielding/pubs/dissertation/top.htm

Google Cloud. (2024). *MLOps: Continuous delivery and automation pipelines in machine learning*. https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems, 30*. https://arxiv.org/abs/1705.07874

MLflow. (s. f.). *MLflow Tracking*. MLflow Documentation. https://mlflow.org/docs/latest/ml/tracking/

Organización Mundial de la Salud. (2025). *Cardiovascular diseases (CVDs)*. https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)

Ulianova, S. (s. f.). *Cardiovascular Disease Dataset*. Kaggle. https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset
