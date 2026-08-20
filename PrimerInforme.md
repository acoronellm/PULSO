# Guía para el primer informe del proyecto

## Resumen / Abstract

Presenta una síntesis breve del problema abordado, la solución propuesta, el alcance del proyecto, la metodología de desarrollo y el plan general de trabajo. Debe permitir al lector comprender la esencia del proyecto sin necesidad de leer el documento completo.

## 1. Introducción

Redacta la introducción como un texto continuo de 4 párrafos. El primero debe describir el dominio o sector del proyecto, las tendencias tecnológicas relevantes y el rol del software en ese contexto. El segundo debe exponer la situación actual: limitaciones del mercado, carencias funcionales y el impacto en los usuarios. El tercero debe presentar la necesidad técnica identificada y la oportunidad de diseño tecnológico. El cuarto, opcional, debe cerrar con una presentación general de la solución propuesta (nombre, funcionalidades clave e impacto esperado), sirviendo de transición hacia las secciones siguientes.

### Contextos

- **Dominio o sector** (ej. educación, industria, salud, ciudades inteligentes, TI).
- **Tendencias tecnológicas relevantes**.
- **Rol de los sistemas de información / software / datos** en ese contexto.

### Situación actual

- **Limitaciones del mercado actual**.
- **Carencias funcionales o de diseño**.
- **Impacto en usuarios**.

### Necesidad identificada

- **Necesidad técnica clara**.
- **Oportunidad de diseño tecnológico**.

### Propuesta general

- **Nombre del sistema**.
- **Funcionalidades clave**.
- **Impacto esperado**.

## 2. Planteamiento del problema

Define y delimita el problema central, explicando qué se busca resolver y por qué es relevante.

El problema se define como una **carencia o déficit** que se manifiesta como un **estado negativo** en una situación real (no teórica), localizado en una **población objetivo bien definida**. No debe confundirse con la falta de un servicio específico ni con la inexistencia de una solución tecnológica. El problema no es "hace falta un sistema que integre X", sino la evidencia de una situación deficiente: por ejemplo, "existen aplicaciones diferentes e incompatibles en los distintos departamentos de la empresa, lo que genera desconexión entre las unidades y pérdida de calidad en la información para la toma de decisiones". Tampoco se trata de un trabajo para una empresa en particular, sino de una **problemática transferible** a contextos similares.

### 2.1 Descripción del problema

Expone con claridad la problemática, sus causas, a quién afecta y cuáles son sus principales consecuencias.

### 2.2 Justificación

Explica por qué el problema debe ser atendido y cuál es la pertinencia académica, técnica, social o práctica del proyecto.

### 2.3 Restricciones y supuestos iniciales

Indica las principales limitaciones y condiciones asumidas para plantear la solución, tales como tiempo, recursos, acceso a información, disponibilidad de usuarios, infraestructura o restricciones técnicas.

## 3. Alcance del proyecto

Define los límites del proyecto especificando qué incluye y qué no incluye.

### Incluye

- **Funcionalidades principales del sistema**.
- **Tipo de usuarios involucrados**.
- **Nivel de madurez de la solución** (prototipo, MVP, diseño detallado).
- **Entornos cubiertos** (web, móvil, backend, integración).

### No incluye

- Funcionalidades futuras o deseables.
- Implementaciones a escala productiva.
- Integraciones externas no críticas.
- Soporte operativo post-proyecto.

## 4. Objetivos

Establece el objetivo general del proyecto y los objetivos específicos que guiarán su desarrollo.

Los objetivos refieren a la situación o logros que se pretenden alcanzar con el desarrollo del proyecto. Todos los demás elementos y su estructura se derivan de estos: metodología, marco teórico, resultados, etc. Por ello debe prestarse **mayor atención** en su proceso de formulación.

Deben ser **claros, viables, susceptibles de alcanzarse y congruentes entre sí**. Son la base de la evaluación del proyecto.

Se recomienda que sean **SMART**:

- **S**pecific (específicos): definidos con precisión.
- **M**easurable (medibles): verificables mediante indicadores.
- **A**chievable (alcanzables): realistas según los recursos y el tiempo.
- **R**elevant (relevantes): alineados con el problema y la solución.
- **T**ime-bound (con plazo): acotados en el tiempo del proyecto.

Los objetivos deben redactarse con **verbos en infinitivo** que indiquen acciones concretas y verificables. Verbos recomendados: *desarrollar, diseñar, implementar, evaluar, analizar, determinar, establecer, validar, modelar, construir, integrar, optimizar, documentar, automatizar, configurar, definir, identificar, clasificar, comparar, proponer*. Evitar verbos ambiguos como *conocer, entender, estudiar, saber*.

### 4.1 Objetivo general

Muestra los cambios o efectos que se desean lograr en la situación inicial definida como problemática. Responde a la relación entre el **problema planteado** y los **propósitos o metas del desarrollo**.

Formula de manera clara el propósito principal del proyecto.

**Ejemplo:**

> Definir proceso y estructura metodológica en la empresa XYZ para identificar, evaluar y reducir los riesgos relacionados con TI (Cumplimiento, estratégicos, operacionales) que puedan tener un impacto potencial sobre las actividades de TI que soportan las operaciones de negocio en el 2022, dentro de los niveles de tolerancia establecidos por la organización.

*Análisis SMART del ejemplo:*
- **S** — Específico: define proceso y estructura metodológica para riesgos TI (cumplimiento, estratégicos, operacionales).
- **M** — Medible: se puede verificar mediante la existencia del proceso y estructura definidos.
- **A** — Alcanzable: acotado a una empresa y a riesgos TI específicos.
- **R** — Relevante: impacta directamente las operaciones de negocio soportadas por TI.
- **T** — Con plazo: acotado al año 2022.

### 4.2 Objetivos específicos

Hacen referencia a los productos o resultados que son necesarios para alcanzar el objetivo general. Son los fines inmediatos del desarrollo, se dimensionan en términos de los resultados esperados o metas, con verbos que indican acciones concretas y con un mayor nivel de detalle.

Descompone el objetivo general en metas concretas, observables y alcanzables que orienten el desarrollo del trabajo.

## 5. Solución propuesta

Se propone desarrollar PULSO, un MVP de una plataforma web de Prevención y Predicción (P&P) orientada a la prevención y educación en salud cardiovascular. La plataforma permitirá al usuario ingresar información relacionada con sus factores de riesgo y obtener una evaluación de su riesgo cardiovascular.

El usuario final para esta plataforma serán las personas del común, es decir, cualquier persona especializada o no en el tema la va poder usar y entender, pero claramente se espera que su publico general sean personas que tengan o hayan tenido complicaciones cardiovasculares.

A partir de la información proporcionada, PULSO presentará los resultados de manera comprensible, permitiendo al usuario identificar los factores que tienen mayor influencia en su nivel de riesgo. Asimismo, la plataforma permitirá modificar determinadas variables para simular diferentes escenarios y observar cómo estos cambios pueden afectar la estimación del riesgo cardiovascular.

Como complemento a los resultados, PULSO proporcionará información y recomendaciones preventivas basadas en guías clínicas y fuentes médicas confiables, utilizando un lenguaje sencillo y comprensible para personas sin conocimientos especializados en el área de la salud.

De esta manera, la solución busca ir más allá de una evaluación que únicamente entregue un porcentaje de riesgo. PULSO pretende facilitar que las personas comprendan los factores relacionados con su riesgo cardiovascular, exploren diferentes escenarios y accedan a información preventiva de manera clara, contribuyendo así a la prevención y educación en salud cardiovascular.

## 6. Estado del arte / soluciones relacionadas

Para analizar las soluciones existentes relacionadas con la evaluación del riesgo cardiovascular, se revisaron diferentes calculadoras y herramientas utilizadas para estimar dicho riesgo. La comparación considera aspectos como la estimación del riesgo, las recomendaciones proporcionadas, el público objetivo, el alcance geográfico, la cantidad de información solicitada, la posibilidad de modificar los datos y la forma en que se presentan los escenarios de riesgo.

| Solución | Estimación del riesgo | Recomendaciones | Público objetivo | Simulación / comparación | Características destacadas |
|---|---|---|---|---|---|
| **SCORE2** | Sí, proporciona un porcentaje de riesgo | **Sí, son personalizadas y las más completas de las herramientas revisadas** | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Orientada principalmente a población europea |
| **PREVENT** | Sí, proporciona un porcentaje de riesgo | Sí, pero principalmente como guía general para interpretar los resultados | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Requiere interpretación de los resultados |
| **Framingham – Canadian Cardiovascular Society** | Sí, proporciona un porcentaje de riesgo | Sí, principalmente como guía general para interpretar los resultados | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Interfaz poco intuitiva para el usuario |
| **CVD Risk Estimator Plus – PREVENT** | Sí, proporciona un porcentaje de riesgo | Sí, enfocadas en la persona evaluada | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Presenta recomendaciones personalizadas |
| **CVD Risk Estimator Plus – Pooled Cohort** | Sí, proporciona un porcentaje de riesgo | No | Personas especializadas | Permite modificar los datos y recalcular el riesgo, pero no comparar directamente con el estado inicial | Orientada aparentemente a población estadounidense |
| **QRISK** | Sí, proporciona un porcentaje de riesgo | No | — | **Sí, permite comparar directamente el riesgo actual con un escenario hipotético** | **Es la herramienta que solicita mayor cantidad de datos entre las revisadas. Su interfaz gráfica es sencilla, pero poco atractiva para el usuario** |

### Análisis de las soluciones existentes

A partir de la comparación realizada, se observa que las herramientas revisadas cuentan con la capacidad de **estimar el riesgo cardiovascular**, generalmente mediante la presentación de un porcentaje. Sin embargo, existen diferencias importantes en la cantidad de información solicitada, la forma de presentar los resultados y las funcionalidades disponibles para su interpretación.

En cuanto a las **recomendaciones**, SCORE2 destaca entre las herramientas analizadas por proporcionar las recomendaciones más completas y enfocadas en la persona evaluada. CVD Risk Estimator Plus (PREVENT) también proporciona recomendaciones personalizadas, mientras que PREVENT y Framingham – Canadian Cardiovascular Society presentan principalmente información general que sirve como guía para interpretar los resultados obtenidos. Por otro lado, Pooled Cohort y QRISK no proporcionan recomendaciones dentro de la herramienta revisada.

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

Explica la metodología adoptada para el desarrollo del proyecto, justificando su elección. En particular, debe describirse el uso de un enfoque de prototipado iterativo, indicando cómo se plantea avanzar mediante ciclos sucesivos de diseño, construcción, prueba y ajuste de la solución.

### 7.2 Iteraciones o fases de desarrollo

Describe las principales fases o iteraciones previstas para el proyecto, indicando el propósito de cada una, las actividades principales a realizar y la manera en que cada ciclo contribuirá al refinamiento progresivo de la solución.

### 7.3 Estrategia de validación

Explica cómo se evaluarán los avances en cada iteración, por ejemplo mediante retroalimentación de usuarios, pruebas funcionales, revisión de requerimientos o validaciones técnicas y de usabilidad.

### 7.4 Plan de trabajo, cronograma o hitos

Presenta la planificación general del proyecto en forma de cronograma, tabla o listado de hitos, indicando las actividades principales, los entregables esperados y, cuando aplique, la temporalidad estimada de cada fase.

## 8. Referencias

Incluye las fuentes consultadas y citadas en el documento, en el formato de citación definido para el curso o proyecto.
