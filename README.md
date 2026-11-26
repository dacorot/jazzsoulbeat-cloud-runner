# Jazz Soul Beat Cloud Runner

Controlador público mínimo para ejecutar el agente privado `dacorot/jazzsoulbeat-agent` en un runner efímero de GitHub Actions. El código de producción, la biblioteca musical, la base de datos y los videos permanecen en el repositorio privado o en el Google Drive privado de la propietaria.

## Estado operativo verificado

- **Capa autónoma vigente (26-11-2026):** `original-music-library-batch.yml` entra cada hora hasta completar la cola de 100 candidatos por género; `production-watchdog.yml` supervisa cada 5 minutos, dispara lotes atrasados y reintenta un fallo visual después de una hora; `visual-production-batch.yml` trabaja con escenas independientes y falla cerrado si no completa el lote solicitado; `youtube-analytics-four-times-daily.yml` toma snapshots cuatro veces al día.
- El watchdog de producción no duplica ejecuciones activas. La producción musical mantiene los candidatos privados, exige control técnico y pre-revisión automática y deja la escucha humana como gate final. El video privado conserva su cadencia de 48 horas y nunca se publica automáticamente.
- La auditoría visual exige un paquete completo de 48 escenas independientes para el video largo. Un lote parcial, una variante derivada o una escena sin contrato visual no puede avanzar.
- El workflow `.github/workflows/private-cloud-agent.yml` está integrado en `main`: admite ejecución manual, marcador `PRIVATE_CLOUD_AGENT_START.md` y producción programada cada 48 horas a las 06:00 de Colombia (11:00 UTC). Usa `build-evergreen` con gate estricto; si no hay música aprobada suficiente, termina sin render.
- Usa `ubuntu-latest`, runner estándar en este repositorio público. No usa larger runners, servicios de pago ni facturación habilitada por este proyecto.
- Accede al repositorio privado con `PRIVATE_REPO_READ_TOKEN`, limitado a lectura.
- Restaura `tracks/`, `assets/visual-agents/`, `data/agent.db` y `output/` desde Google Drive; el flujo de producción solo recupera el audio de biblioteca aprobado y referenciado por manifiestos.
- La carga inicial de Drive y una recuperación independiente de los 96 objetos (316,051,164 bytes) se completaron y la comprobación de integridad SQLite devolvió `ok`.
- La ejecución cloud manual #3 terminó en `success` como validación histórica del pipeline inicial. Las validaciones posteriores están registradas en los informes de coordinación y en GitHub Actions; una prueba sintética exitosa no equivale a una producción musical final.
- La ejecución #3 fue `self-test`: **no** generó una mezcla musical de producción. `build-evergreen` estaba disponible pero se omitió; `build-original` no forma parte del formulario cloud actual.
- La biblioteca de terceros no tiene pistas con derechos comerciales completamente verificados; los candidatos en revisión permanecen pendientes.
- La ejecución `43541129670` generó un video QHD de revisión privada de 2 horas con ocho vistas de escena. Está marcado `PRIVATE_REVIEW_ONLY_NOT_APPROVED`: no se subió a YouTube y no es un master de publicación. El artefacto de GitHub se conserva 30 días.
- El paquete coordinado anterior registró 44 pistas de Incompetech descargadas para revisión, pero 0 derechos aprobados. El informe marca una discrepancia entre enlaces históricos CC BY 3.0 y las referencias actuales CC BY 4.0, además de dos créditos de terceros que requieren revisión.
- El conjunto visual contiene seis imágenes originales y dos variantes de recorte/color derivadas de la primera; las ocho siguen pendientes de aprobación creativa. La cuota gratuita de generación visual se agotó y Cloudflare devolvió 403 de verificación de facturación; no se activó facturación ni un fallback de pago.

## Tareas disponibles

| Tarea | Función |
|---|---|
| `self-test` | Genera un video sintético breve para comprobar el pipeline. |
| `build-evergreen` | Construye un video usando exclusivamente la biblioteca evergreen aprobada. Requiere pistas aprobadas suficientes. |

La generación original vigente usa el lote acotado de `original-music-library-batch.yml`, con ACE-Step como proveedor primario y Stable Audio 3 como fallback gratuito de audición cuando corresponde. Cada lote se persiste en Drive privado; la aprobación creativa, la aprobación de derechos y la publicación siguen fuera de la automatización.

La duración configurada en el formulario manual está limitada a 1, 2 o 3 horas. La tarea estacional requiere un slug válido y una biblioteca estacional revisada.

## Validar una rama del agente

El formulario manual incluye `agent_ref`, que permite seleccionar una rama o SHA del repositorio privado. Por defecto apunta a `fix/real-music-and-cinematic-motion`, la rama usada por el pipeline de revisión actual. Así se puede compilar y ejecutar la suite completa de pruebas contra otra rama de trabajo sin fusionarla primero. La referencia se valida antes del checkout.

Para una validación técnica sin generar producción, seleccionar:
- `task = self-test`
- `hours = 1` (no afecta a self-test)
- `agent_ref = feature/original-arrangement-development` (o el SHA exacto que se quiera probar)

La tarea `self-test` genera únicamente el video sintético de comprobación; no genera una mezcla musical de producción. Para probar generación musical original, usa el workflow separado `music-producer.yml`; su salida de 120 segundos requiere revisión y todavía no se integra con el render de video. Toda ejecución del agente privado sigue guardando el estado y los resultados en Drive privado.

## Seguridad y límites

- La automatización está separada por función: `original-music-library-batch.yml` produce cada hora; `visual-production-batch.yml` tiene ciclo diario; `production-watchdog.yml` supervisa cada cinco minutos; `youtube-analytics-four-times-daily.yml` actualiza analítica cuatro veces al día; `private-cloud-agent.yml` intenta el video privado cada 48 horas; `private-agent-preflight.yml` valida cada seis horas. Son ejecuciones programadas en runners efímeros, no un proceso persistente 24/7.
- `music-producer.yml` solo se ejecuta manualmente o mediante su marcador de inicio; intenta generar un instrumental original de 120 segundos con el Space público ACE-Step. Si el servicio gratuito no responde o cambia su API, falla sin recurrir a proveedores de pago. No equivale todavía a producción musical autónoma de larga duración.
- `private-cloud-agent.yml` es manual y conserva el flujo de restauración/guardado en Drive. `parallel-production.yml` también queda manual: cada ejecución reúne auditoría de derechos, generación visual y render de varias horas, por lo que no debe dispararse por cada cambio de código.
- La ejecución automática no garantiza puntualidad: GitHub puede retrasar o descartar schedules con alta carga y desactiva schedules en repositorios públicos tras 60 días sin actividad.
- Tras superar render, captura, QA y persistencia, el workflow puede subir el artefacto exacto a YouTube como privado. La publicación pública permanece bloqueada y requiere aprobación independiente.
- No se aprueban pistas automáticamente. La licencia comercial, autoridad del publicador y derechos de composición, interpretación y master requieren evidencia y revisión humana.
- No se deben guardar secretos, tokens, audios, bases de datos ni videos en este repositorio público.
- No activar pagos, runners grandes, suscripciones ni servicios externos de pago.
- Mantener `PRIVATE_REPO_READ_TOKEN` con permiso `Contents: Read-only` únicamente y proteger `DRIVE_TOKEN_JSON` como secreto.

## Ejecución manual

1. Abre [el workflow privado](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/workflows/private-cloud-agent.yml).
2. Selecciona **Run workflow** en la rama `main`.
3. Elige la tarea y los parámetros que correspondan. Para validar una rama sin producir música, usa `self-test` y establece `agent_ref` a la rama de trabajo.
4. Revisa el resultado en la ejecución. Una subida privada solo ocurre después de todos los gates; nunca se publica automáticamente.

El runner es efímero: no conserva archivos después del trabajo. La continuidad depende de Google Drive y de los workflows programados/manuales. Esto ofrece ejecución por horarios, no un proceso 24/7 permanentemente activo. La producción se bloquea mientras no exista una hora completa de música aprobada con derechos verificados. Todos los workflows que escriben en la base SQLite o en la carpeta de estado de Drive comparten el mismo grupo de concurrencia; así se evita que dos ejecuciones sobrescriban estados mutuamente.


## Visual production lock

Every video must use exactly one user-approved style sample from
`assets/visual-agents/approved-style-samples/`. The camera is locked: no zoom,
pan, parallax, or scene montage. Rain is fail-closed and may render only with a
verified window mask; otherwise the review renderer uses steam-only motion.

Audio assembly also enforces a 32-second equal-power crossfade and rejects insufficient effective duration.
