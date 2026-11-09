# Jazz Soul Beat Cloud Runner

Controlador público mínimo para ejecutar validaciones del agente privado `dacorot/jazzsoulbeat-agent`. El código principal, la música y los datos privados permanecen en el repositorio privado o en almacenamiento privado separado.

## Límites de seguridad

- El código de producción permanece en el repositorio privado.
- Este repositorio no contiene música, biblioteca, base de datos, OAuth, tokens ni datos del canal.
- Los workflows solo permiten ejecución manual (`workflow_dispatch`); no hay programación automática.
- `private-agent-preflight.yml` compila, ejecuta pruebas y genera un video sintético sin Drive.
- `private-cloud-agent.yml` restaura `tracks/`, SQLite y `output/` desde Drive privado, ejecuta una prueba sintética o construye un video local sin subirlo, y vuelve a persistir los archivos.
- No descarga música desde Internet ni usa OAuth de YouTube; sí usa el secreto `DRIVE_TOKEN_JSON` para persistencia privada. No sube videos ni publica contenido.
- No habilita pagos ni modifica presupuestos. El flujo cloud requiere los secretos `PRIVATE_REPO_READ_TOKEN` y `DRIVE_TOKEN_JSON`.
- No se habilitaron ejecuciones automáticas ni se creó un mecanismo de publicación.

## Secreto de lectura

El workflow usa el secreto `PRIVATE_REPO_READ_TOKEN`, configurado por la propietaria en **Settings → Secrets and variables → Actions**. Debe ser un fine-grained token limitado al repositorio `dacorot/jazzsoulbeat-agent`, con permiso **Contents: Read-only** únicamente. El valor nunca debe guardarse en archivos ni compartirse en el chat.

## Resultado de la primera prueba real

Ejecución manual #1: [42547951975](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/runs/42547951975).

- Estado: **completed / success**.
- Duración informada por GitHub: 51 segundos.
- Checkout del repositorio privado: correcto.
- Compilación de módulos productivos: correcta.
- Pruebas unitarias: **78 OK**.
- Prueba integral: generó video MP4 1920×1080 de 8 segundos, audio sintético MP3 y miniatura.
- Verificación de archivos de salida: correcta.
- Sin descargas de música, sin OAuth, sin subida a YouTube.
- Artefactos persistentes: ninguno; el directorio de salida se perdió al terminar el runner.

El registro de GitHub también muestra advertencias de mantenimiento de las acciones de terceros usadas por el workflow (Node 20). Conviene actualizar y volver a probar las versiones de actions antes de depender de este flujo.

## Estado real de la integración

La prueba confirma que el repositorio público puede leer y ejecutar el código privado en un runner efímero. No confirma todavía que el agente pueda operar de extremo a extremo.

El runner es temporal: no conserva archivos, MP3, SQLite ni resultados entre ejecuciones. Por tanto, aún falta resolver almacenamiento privado y persistente para:

1. Biblioteca y manifiestos de música revisada.
2. Archivos de audio cuya licencia y derechos hayan sido aprobados expresamente.
3. Base de datos e historial de mezclas.
4. Videos terminados y miniaturas.
5. Recuperación segura ante interrupciones.

No se debe almacenar música ni base de datos en el repositorio público. Tampoco se debe convertir el repositorio privado en almacenamiento de MP3 mediante commits: aumentaría el tamaño del historial, no es un sistema de archivos de producción y no se ha validado su sostenibilidad.

## Reglas para la siguiente fase

- No habilitar programación hasta tener almacenamiento persistente probado y una garantía de coste cero.
- No activar pagos, runners grandes, servicios de pago ni suscripciones.
- No ampliar el token de lectura a escritura sin aprobación expresa.
- No aprobar música automáticamente: los candidatos Ketsa existentes permanecen PENDING.
- No ejecutar `make --upload` automáticamente. Cualquier subida futura requerirá autorización explícita y privacidad `private` confirmada por YouTube.
- Los secretos OAuth y tokens nunca se guardan en el repositorio.

El flujo Drive-backed aún no se ha ejecutado: antes hay que cargar el estado local inicial a Drive y verificar una primera recuperación en dos ejecuciones manuales separadas. El PR #1 está fusionado en `main` (commit `7e9cdd594bb62926c86977b19d0c511f002c674d`). No se ha añadido `schedule`, no se ha ejecutado este workflow y no se ha habilitado ninguna subida a YouTube. El PR #4 del repositorio privado quedó fusionado (commit `f5ad2558b7f66ced4327448755058f5fede6a9b1`) e incorpora el comando de carga inicial `drive-seed`; sus pruebas nuevas aún deben ejecutarse localmente. Ver `PERSISTENCE_DECISION.md` para los límites y criterios pendientes.
