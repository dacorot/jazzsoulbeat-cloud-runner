# Jazz Soul Beat — ciclo Deming continuo (PDCA)

## Política de operación

La operación es continua, los siete días de la semana, sin depender del PC de Windows. No se mantiene un proceso de cómputo encendido permanentemente: GitHub Actions despierta ejecuciones programadas y acotadas durante las 24 horas. Cada ejecución restaura el estado persistente desde Google Drive, trabaja sobre una tarea delimitada, verifica sus resultados y guarda evidencias y estado.

Zona horaria humana: Colombia (America/Bogota, UTC-5). Los cron de GitHub se expresan en UTC y pueden iniciar con retraso. La cadencia programada es una garantía de intento, no de inicio exacto.

## Cadencia automatizada

- **Cada 6 horas, todos los días:** preflight del agente privado: restaurar el estado necesario, compilar, ejecutar pruebas, self-test técnico, comprobar artefactos y persistir únicamente los resultados QA permitidos. Esta ejecución es el pulso de control de salud.
- **Todos los días, 07:00 Colombia:** intentar construir un nuevo video de revisión de una hora. Solo continúa si existe una hora completa de música aprobada y con derechos verificados; de lo contrario registra el bloqueo y no genera un video incompleto.
- **Todos los días, 07:30 Colombia:** actualizar la cola de descubrimiento musical y sus métricas. Los candidatos permanecen pendientes; descubrir no equivale a aprobar.
- **Semanalmente:** auditorías de procedencia y derechos de catálogos en revisión.
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
