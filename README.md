# Jazz Soul Beat Cloud Runner

Controlador público mínimo para ejecutar el agente privado `dacorot/jazzsoulbeat-agent` en un runner efímero de GitHub Actions. El código de producción, la biblioteca musical, la base de datos y los videos permanecen en el repositorio privado o en el Google Drive privado de la propietaria.

## Estado operativo verificado

- El workflow `.github/workflows/private-cloud-agent.yml` está integrado en `main` y solo se inicia manualmente mediante `workflow_dispatch`.
- Usa `ubuntu-latest`, runner estándar en este repositorio público. No usa larger runners, servicios de pago ni facturación habilitada por este proyecto.
- Accede al repositorio privado con `PRIVATE_REPO_READ_TOKEN`, limitado a lectura.
- Restaura `tracks/`, `data/agent.db` y `output/` desde Google Drive; ejecuta la tarea seleccionada y guarda el estado y los resultados de nuevo en Drive.
- La carga inicial de Drive y una recuperación independiente de los 96 objetos (316,051,164 bytes) se completaron y la comprobación de integridad SQLite devolvió `ok`.
- La ejecución cloud manual #3 terminó en `success`: checkout privado, instalación, compilación, pruebas, restauración de Drive, estado de biblioteca, prueba sintética, persistencia y comprobación final de Drive completados.
- La ejecución #3 fue `self-test`: **no** generó una mezcla musical de producción. Las tareas `build-original` y `build-evergreen` estaban disponibles pero se omitieron en esa ejecución.
- La biblioteca de terceros no tiene pistas con derechos comerciales completamente verificados; los candidatos en revisión permanecen pendientes.
- La ejecución `43541129670` generó un video QHD de revisión privada de 2 horas con ocho vistas de escena. Está marcado `PRIVATE_REVIEW_ONLY_NOT_APPROVED`: no se subió a YouTube y no es un master de publicación. El artefacto de GitHub se conserva 30 días.
- El paquete coordinado anterior registró 44 pistas de Incompetech descargadas para revisión, pero 0 derechos aprobados. El informe marca una discrepancia entre enlaces históricos CC BY 3.0 y las referencias actuales CC BY 4.0, además de dos créditos de terceros que requieren revisión.
- El conjunto visual contiene seis imágenes originales y dos variantes de recorte/color derivadas de la primera; las ocho siguen pendientes de aprobación creativa. La cuota gratuita de generación visual se agotó y Cloudflare devolvió 403 de verificación de facturación; no se activó facturación ni un fallback de pago.

## Tareas disponibles

| Tarea | Función |
|---|---|
| `self-test` | Genera un video sintético breve para comprobar el pipeline. |
| `build-evergreen` | Construye un video usando exclusivamente la biblioteca evergreen aprobada. Requiere pistas aprobadas suficientes. |

La generación original con ACE-Step está separada en `music-producer.yml`: produce un instrumental de 120 segundos y conserva el resultado como artefacto para revisión. No construye todavía el video final ni se ejecuta automáticamente. El comando `make-original` que aparece en algunas ramas del agente no está expuesto como tarea en este formulario cloud; no debe confundirse con una capacidad ya desplegada.

La duración configurada en el formulario manual está limitada a 1, 2 o 3 horas. La tarea estacional requiere un slug válido y una biblioteca estacional revisada.

## Validar una rama del agente

El formulario manual incluye `agent_ref`, que permite seleccionar una rama o SHA del repositorio privado. Por defecto es `master`. Así se puede compilar y ejecutar la suite completa de pruebas contra una rama de trabajo sin fusionarla primero. La referencia se valida antes del checkout.

Para una validación técnica sin generar producción, seleccionar:
- `task = self-test`
- `hours = 1` (no afecta a self-test)
- `agent_ref = feature/original-arrangement-development` (o el SHA exacto que se quiera probar)

La tarea `self-test` genera únicamente el video sintético de comprobación; no genera una mezcla musical de producción. Para probar el render original de producción se requiere seleccionar explícitamente `build-original`. Toda ejecución sigue guardando el estado y los resultados en Drive privado, por lo que debe elegirse conscientemente la tarea.

## Seguridad y límites

- La automatización está separada por función: `music-agents.yml` ejecuta descubrimiento lunes, miércoles y viernes (11:17 UTC); `discover-music-candidates.yml` ejecuta una búsqueda diaria (12:30 UTC, 07:30 Colombia). Son procesos de descubrimiento: no aprueban derechos ni publican.
- `music-producer.yml` solo se ejecuta manualmente o mediante su marcador de inicio; intenta generar un instrumental original de 120 segundos con el Space público ACE-Step. Si el servicio gratuito no responde o cambia su API, falla sin recurrir a proveedores de pago. No equivale todavía a producción musical autónoma de larga duración.
- `private-cloud-agent.yml` es manual y conserva el flujo de restauración/guardado en Drive. `parallel-production.yml` también queda manual: cada ejecución reúne auditoría de derechos, generación visual y render de varias horas, por lo que no debe dispararse por cada cambio de código.
- La ejecución automática no garantiza puntualidad: GitHub puede retrasar o descartar schedules con alta carga y desactiva schedules en repositorios públicos tras 60 días sin actividad.
- El workflow no recibe `YOUTUBE_TOKEN_JSON`, no ejecuta `--upload` y no publica videos. Los resultados se guardan únicamente en Google Drive privado.
- No se aprueban pistas automáticamente. La licencia comercial, autoridad del publicador y derechos de composición, interpretación y master requieren evidencia y revisión humana.
- No se deben guardar secretos, tokens, audios, bases de datos ni videos en este repositorio público.
- No activar pagos, runners grandes, suscripciones ni servicios externos de pago.
- Mantener `PRIVATE_REPO_READ_TOKEN` con permiso `Contents: Read-only` únicamente y proteger `DRIVE_TOKEN_JSON` como secreto.

## Ejecución manual

1. Abre [el workflow privado](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/workflows/private-cloud-agent.yml).
2. Selecciona **Run workflow** en la rama `main`.
3. Elige la tarea y los parámetros que correspondan. Para validar una rama sin producir música, usa `self-test` y establece `agent_ref` a la rama de trabajo.
4. Revisa el resultado en la ejecución. No se realiza ninguna publicación en YouTube.

El runner es efímero: no conserva archivos después del trabajo. La persistencia entre ejecuciones depende de Google Drive y del flujo pull → tarea → push. Este controlador no es todavía un servicio autónomo con programación automática.
