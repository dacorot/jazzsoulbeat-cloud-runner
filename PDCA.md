# Jazz Soul Beat — ciclo Deming continuo (PDCA)

## Política de operación

La operación es continua, los siete días de la semana, sin depender del PC de Windows. No se mantiene un proceso de cómputo encendido permanentemente: GitHub Actions despierta ejecuciones programadas y acotadas durante las 24 horas. Cada ejecución restaura el estado persistente desde Google Drive, trabaja sobre una tarea delimitada, verifica sus resultados y guarda evidencias y estado.

Zona horaria humana: Colombia (America/Bogota, UTC-5). Los cron de GitHub se expresan en UTC y pueden iniciar con retraso. La cadencia programada es una garantía de intento, no de inicio exacto.

## Cadencia automatizada

- **Cada 6 horas, todos los días:** preflight del agente privado: restaurar el estado necesario, compilar, ejecutar pruebas, self-test técnico, comprobar artefactos y persistir únicamente los resultados QA permitidos. Esta ejecución es el pulso de control de salud.
- **Todos los días, 07:00 Colombia:** intentar construir un nuevo video de revisión de una hora. Solo continúa si existe una hora completa de música aprobada y con derechos verificados; de lo contrario registra el bloqueo y no genera un video incompleto.
- **Todos los días, 07:30 Colombia:** actualizar la cola de descubrimiento musical y sus métricas. Los candidatos permanecen pendientes; descubrir no equivale a aprobar.
- **Semanalmente:** auditorías de procedencia y derechos de catálogos en revisión; informe KPI de 7 días y comparativos móviles de 30 y 90 días.
- **Mensualmente:** refresco de catálogos oficiales Ketsa e Incompetech.
- **A demanda:** ejecuciones manuales para tareas correctivas o trabajos específicos.

## P — Planear

Antes de cada tarea, el agente debe:
- Restaurar el último estado válido desde Drive.
- Leer pendientes, bloqueos, defectos y acciones correctivas previas.
- Priorizar primero el entregable de producción más cercano y los bloqueos que lo impiden.
- Definir objetivo, entradas, criterios de aceptación, límites de seguridad y evidencia esperada.
- Evitar duplicar trabajos en curso mediante grupos de concurrencia y checkpoints.

## D — Hacer

Ejecutar una tarea delimitada y reanudable. Cada ejecución debe registrar su identificador, revisión exacta del agente, entradas, salidas y estado. Los archivos de trabajo y los entregables permanecen en Drive privado. Las ejecuciones deben poder reintentarse sin corromper catálogos ni sobrescribir resultados ajenos.

## C — Verificar

No declarar una tarea terminada por haber ejecutado un comando. Verificar:
1. Integridad y presencia de los archivos esperados.
2. Duración, resolución, códecs y reproducción completa cuando aplique.
3. Identidad musical frente al manifiesto y calidad de mezcla.
4. Evidencia de derechos, autoridad del uploader, composición, interpretación y grabación.
5. Calidad visual, estilo anime adulto, continuidad de personajes y ausencia de personas reales.
6. Movimiento ambiental y continuidad del bucle, sin saltos ni parpadeos.
7. Metadatos, thumbnail, procedencia y persistencia privada.
8. Pruebas automatizadas y regresión de las correcciones.

Un gate pendiente o fallido debe quedar explícito; nunca transformarlo en aprobación implícita.

## A — Actuar

- Corregir automáticamente solo fallos técnicos reproducibles y dentro de los permisos ya concedidos.
- Para defectos de código, añadir o actualizar una prueba de regresión y volver a ejecutar QA antes de aceptar el cambio.
- Reintentar tareas idempotentes cuando la causa sea transitoria; limitar reintentos para evitar bucles.
- Si una corrección requiere criterio humano, autorización, derechos dudosos o cambio de alcance, detener únicamente esa decisión y dejar el resto de la cola operativa.
- Registrar causa raíz, corrección, prueba y resultado. Incorporar la mejora al siguiente ciclo.

## Criterios de producción

- Primer video: 60 minutos. Los posteriores alternan duraciones de 2 y 3 horas según la biblioteca aprobada.
- No repetir pistas dentro de un video ni acelerar, recortar o alargar canciones para rellenar.
- Solo música aprobada y con derechos verificados.
- Audio continuo, transiciones limpias y niveles consistentes.
- Video H.264 QHD 2560×1440, audio AAC estéreo.
- Arte original anime adulto, sofisticado y cinematográfico; continuidad de personajes.
- Movimiento ambiental perceptible y bucles visuales sin saltos.
- Metadatos, thumbnail y manifiesto de procedencia completos.

## Registro de cada ciclo

- Fecha/hora UTC y Colombia:
- Workflow / run ID:
- Revisión exacta del agente:
- Objetivo y tarea:
- Estado: PLANNED / RUNNING / VERIFIED / BLOCKED / FAILED
- Criterios comprobados y evidencias:
- Defectos y severidad:
- Causa raíz:
- Acción correctiva:
- Prueba de regresión:
- Resultado del nuevo intento:
- Decisiones pendientes de revisión humana:

## Reglas de seguridad

- Nunca convertir una cola de candidatos en biblioteca aprobada automáticamente.
- Nunca aprobar derechos por inferencia, metadatos aislados o mera disponibilidad de descarga.
- Nunca generar con música insuficiente ni repetir pistas para completar duración.
- Nunca subir a YouTube, ni siquiera como privado, sin autorización explícita de la usuaria.
- Nunca publicar públicamente sin autorización explícita independiente.
- No contratar servicios, activar billing ni usar alternativas pagas.
- La revisión humana y la autorización de publicación son decisiones separadas.


## KPI framework — evidence before claims

The agent maintains a historical KPI ledger in `data/agent.db`. Every PDCA cycle records its task start, completion, block or failure. Permission decisions are also recorded. Reports use observed events only; missing observations remain null and establish a baseline rather than being reported as success.

### Five operating dimensions

| Dimension | Indicator | Initial target / interpretation |
|---|---|---|
| Production quality | Deliverables that pass all required acceptance checks | 100% before marking VERIFIED |
| Production quality | Audio/video integrity, duration, codec, continuity and metadata checks | 100% of applicable checks pass |
| Creative identity | Compliance with approved adult anime visual identity and character continuity | 100% of audited outputs |
| Creative identity | Seamless loop and perceptible environmental motion | 100% of audited scenes |
| Autonomy | Authorized task completion rate | Initial target ≥90%; measured, not assumed |
| Autonomy | Unjustified blocks and loss of operational continuity | 0 |
| Autonomy | Bounded automatic recovery of transient/technical errors | Establish baseline, then improve |
| Safety | Unauthorized YouTube uploads/publications, unverified rights used in production, unauthorized policy changes or out-of-scope actions | 0 |
| Efficiency | Time to create and correct, first-review acceptance, recurring defects and resource use | Establish baseline from actual runs |
| Impact | Audience response and retention | No target until real publication analytics exist; never overrides rights, quality or identity gates |

The initial editorial/identity KPIs from the reference model are adapted to Jazz Soul Beat: there are no Bible-quotation or NBLA KPIs in this music channel. For Christian Jazz & Soul, original English lyrics must be coherent, grounded in identified biblical passages and reviewed for accuracy.

### Evaluation cadence

- **Continuous:** record task states, permission decisions, defects, retries and recovery outcomes.
- **Daily:** review the last 24 hours of quality, throughput, blockers and safety events.
- **Weekly:** compare seven-day KPI history, identify recurring defects and publish a PHVA improvement report.
- **Monthly:** evaluate trends, reliability, resource efficiency and structural improvements.
- **Quarterly:** review strategic objectives and propose changes; fundamental policy, brand and security changes remain human-gated.

### Improvement acceptance

A proposed improvement is not considered successful merely because code changed. The agent must state the observed defect, root cause, bounded correction, regression test and measured result. A correction that fails verification returns to the queue; it does not silently close the defect.
