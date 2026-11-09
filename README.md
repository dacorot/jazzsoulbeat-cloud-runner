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

## Tareas disponibles

| Tarea | Función |
|---|---|
| `self-test` | Genera un video sintético breve para comprobar el pipeline. |
| `build-original` | Sintetiza música instrumental original, construye un video y persiste los archivos en Drive. No usa pistas externas. |
| `build-evergreen` | Construye un video usando exclusivamente la biblioteca evergreen aprobada. Requiere pistas aprobadas suficientes. |

La duración configurada en el formulario manual está limitada a 1, 2 o 3 horas. La tarea estacional requiere un slug válido y una biblioteca estacional revisada.

## Seguridad y límites

- No hay `schedule` ni ejecuciones automáticas. El runner estándar `ubuntu-latest` de este repositorio público es gratuito e ilimitado según GitHub; los runners grandes sí se cobran. Aun así, una programación no garantiza puntualidad: GitHub puede retrasarla o descartar ejecuciones con alta carga y desactiva schedules en repositorios públicos tras 60 días sin actividad. No activar `schedule` sin autorización expresa.
- El workflow no recibe `YOUTUBE_TOKEN_JSON`, no ejecuta `--upload` y no publica videos. Los resultados se guardan únicamente en Google Drive privado.
- No se aprueban pistas automáticamente. La licencia comercial, autoridad del publicador y derechos de composición, interpretación y master requieren evidencia y revisión humana.
- No se deben guardar secretos, tokens, audios, bases de datos ni videos en este repositorio público.
- No activar pagos, runners grandes, suscripciones ni servicios externos de pago.
- Mantener `PRIVATE_REPO_READ_TOKEN` con permiso `Contents: Read-only` únicamente y proteger `DRIVE_TOKEN_JSON` como secreto.

## Ejecución manual

1. Abre [el workflow privado](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/workflows/private-cloud-agent.yml).
2. Selecciona **Run workflow** en la rama `main`.
3. Elige la tarea y los parámetros que correspondan.
4. Revisa el resultado en la ejecución. No se realiza ninguna publicación en YouTube.

El runner es efímero: no conserva archivos después del trabajo. La persistencia entre ejecuciones depende de Google Drive y del flujo pull → tarea → push. Este controlador no es todavía un servicio autónomo con programación automática.
