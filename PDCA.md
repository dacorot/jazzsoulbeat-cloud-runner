# Jazz Soul Beat — ciclo Deming (PDCA)

## Cadencia operativa

Zona horaria de referencia: Colombia (America/Bogota).

- **Domingo, martes y jueves — 07:00:** GitHub Actions intenta construir un video nuevo de una hora y guarda el paquete en Google Drive privado. Si la biblioteca no tiene una hora completa de música aprobada y con derechos verificados, el proceso se detiene sin crear un video.
- **Lunes, miércoles y viernes — 08:00:** sesión de revisión humana. Se revisa el paquete más reciente generado desde la sesión anterior.
- Los horarios de Actions son objetivos de inicio; la cola de GitHub puede retrasar la ejecución. La revisión debe basarse en un paquete terminado y verificado, no solo en que el workflow haya comenzado.

## P — Planear

Antes de cada ciclo, mantener claros los criterios de aceptación:
- Una hora completa, sin repetir pistas dentro del mismo video ni acelerar, recortar o alargar canciones para rellenar.
- Solo música aprobada y con evidencia de derechos registrada.
- Audio continuo, transiciones limpias y niveles consistentes.
- Video H.264 QHD 2560×1440, audio AAC estéreo.
- Arte original anime adulto, sofisticado y cinematográfico; continuidad de personajes y dirección visual.
- Movimiento ambiental perceptible y bucles visuales sin saltos.
- Metadatos, thumbnail y manifiesto de procedencia completos.
- El paquete queda privado. La publicación pública requiere aprobación explícita de la usuaria.

## D — Hacer

El agente construye un paquete nuevo en cada ejecución programada. Cada ejecución debe tener su propia carpeta, mezcla, video, thumbnail, descripción, manifiesto musical y prueba técnica. La selección favorece pistas menos utilizadas, pero el historial de uso por sí solo no demuestra que una combinación musical sea inédita; comprobar la lista de pistas en la revisión.

## C — Verificar

En cada sesión de lunes, miércoles o viernes, revisar el paquete más reciente que haya terminado correctamente:
1. **Integridad:** duración real, resolución, códecs, reproducción completa y archivos auxiliares.
2. **Música:** identidad de cada pista frente al manifiesto, calidad de mezcla, transiciones, volumen, ausencia de cortes molestos y coherencia de estilo.
3. **Derechos:** cada pista debe figurar como aprobada y con derechos verificados; revisar atribuciones y enlaces.
4. **Imagen:** calidad cinematográfica, estética adulta, composición, consistencia de personajes, ausencia de fotografías/personas reales, artefactos y texto accidental.
5. **Movimiento:** movimiento ambiental visible, continuidad del bucle y ausencia de saltos o parpadeos.
6. **Presentación:** título, descripción, thumbnail y coherencia del paquete.
7. **Decisión:** APPROVE, CORRECT o REJECT. Aprobar la revisión no equivale a autorizar publicación pública; esa autorización se da explícitamente por separado.

## A — Actuar

Convertir cada observación en una acción verificable:
- Registrar fecha, identificador/carpeta del video, criterio, hallazgo, severidad, acción correctiva y resultado de la nueva prueba.
- Corregir la causa raíz en el agente o en sus recursos, no solo maquillar el video individual.
- Añadir o actualizar una prueba automatizada cuando el defecto sea reproducible.
- Ejecutar QA antes de aceptar el cambio.
- Aplicar la mejora a los siguientes ciclos y comprobar en la siguiente revisión que no reaparezca.

## Registro de revisión (copiar por cada video)

- Fecha de revisión:
- Carpeta/identificador del video:
- Resultado: APPROVE / CORRECT / REJECT
- Música y derechos:
- Mezcla y transiciones:
- Imagen y continuidad:
- Movimiento y loop:
- Metadatos y thumbnail:
- Defectos observados:
- Causa raíz:
- Acción correctiva:
- Prueba que demuestra la corrección:
- ¿Se autoriza publicación pública?: NO, salvo autorización explícita independiente.

## Reglas de seguridad

- Nunca convertir una cola de candidatos en biblioteca aprobada automáticamente.
- Nunca generar con música insuficiente ni repetir pistas para completar duración.
- Nunca publicar públicamente sin autorización explícita.
- Si una ejecución falla o la compuerta musical no está lista, comunicarlo con claridad; no presentar un video parcial como terminado.