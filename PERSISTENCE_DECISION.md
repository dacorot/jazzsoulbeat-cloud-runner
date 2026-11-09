# Decisión de almacenamiento persistente — 8 de noviembre de 2026

## Situación comprobada

El workflow manual del repositorio público puede clonar el repositorio privado, instalar dependencias, ejecutar 78 pruebas y producir un video sintético. GitHub destruye el runner al terminar; no existe persistencia de sus archivos locales.

El repositorio privado contiene SQLite en `data/agent.db`, música y manifiestos bajo `tracks/`, y los resultados bajo `output/`. Los directorios locales están excluidos de Git. Una ejecución nueva no recupera por sí sola la biblioteca o el estado que existían en el PC.

## Evaluación: Google Drive como almacén privado

Es la alternativa gratuita más viable encontrada hasta ahora, pero todavía no está habilitada ni se ha probado con el agente.

- Una cuenta Google personal incluye hasta 15 GB sin costo, compartidos entre Drive, Gmail y Google Photos. No son 15 GB exclusivos para el agente; el espacio real disponible depende del uso actual de esa cuenta.
- El uso estándar de Google Drive API se ofrece sin costo adicional. La documentación vigente define límites diarios estándar y un umbral de 400.000.000 unidades de cuota; Google indica que el uso por debajo del umbral no genera cargos. Google anuncia cargos por superar límites estándar más adelante en 2026, tras aviso previo. Por la condición de costo cero, la implementación debe limitar transferencias y operaciones, y no debe solicitar aumentos de cuota ni activar facturación.
- El permiso OAuth `drive.file` es un alcance no sensible recomendado por Google. Permite crear y administrar los archivos que la propia aplicación crea o que el usuario comparte con ella; evita pedir acceso indiscriminado a todo Drive.
- El token de YouTube actual devolvió una identidad `@pages.plusgoogle.com`. Google confirma que ese identificador corresponde a una Cuenta de marca de YouTube, no a una cuenta Google real; la Cuenta de marca no tiene almacenamiento de Drive propio. Por tanto, no se debe intentar usar el token de YouTube para Drive.
- La arquitectura correcta separa identidades: `YOUTUBE_TOKEN_JSON` permanece intacto para el canal; un segundo token `DRIVE_TOKEN_JSON` se autoriza iniciando sesión con la cuenta Google propietaria real de la Cuenta de marca. La autorización Drive solicitará solo `drive.file` y no necesita sustituir el secreto de YouTube.
- Antes de autorizar, debe confirmarse que la cuenta Google propietaria tiene espacio disponible. Habilitar Drive API y obtener `drive.file` no debe activar facturación ni requerir tarjeta.
- La nueva autorización Drive requiere aprobación expresa de la propietaria. No se debe pedir ni compartir el contenido del token en el chat.

Fuentes oficiales consultadas:
- Almacenamiento gratuito y compartido: https://support.google.com/drive/answer/9312312
- Límites y precios de Drive API: https://developers.google.com/workspace/drive/api/guides/limits
- Alcances OAuth y clasificación de `drive.file`: https://developers.google.com/workspace/drive/api/guides/api-specific-auth
- Crear y subir archivos: https://developers.google.com/workspace/drive/api/guides/create-file

## Diseño propuesto si se autoriza

1. Crear en Drive una carpeta privada administrada por la aplicación.
2. Guardar allí los audios de revisión, los manifiestos, la biblioteca aprobada, SQLite, los videos y miniaturas; separar estrictamente PENDING de APPROVED.
3. Al iniciar un runner, recuperar el estado y los archivos necesarios; al terminar, sincronizar cambios de forma segura.
4. Usar escrituras temporales, hashes SHA-256, checkpoints y reconciliación para que una interrupción no corrompa la biblioteca.
5. Consultar el espacio disponible antes de cargar. Si no hay capacidad suficiente, detener el proceso sin borrar archivos ni comprar almacenamiento.
6. Aplicar límites de transferencia conservadores por ejecución/día y detenerse al alcanzar cualquier límite. No habilitar facturación ni solicitar ampliaciones de cuota.
7. Conservar el workflow manual durante la validación. No activar programación hasta probar recuperación, persistencia y costo cero.

## Bloqueos de producción que siguen vigentes

- La autorización local Drive fue completada por la propietaria para `dacorot@icloud.com`. La consulta de cuota reportó 400 GiB totales, 19.17 GiB usados y 380.83 GiB libres en ese momento. El saldo puede cambiar y debe volver a comprobarse si se agota espacio.
- La autorización Drive separada requiere la cuenta Google propietaria real de la Cuenta de marca y aprobación de la propietaria.
- Los archivos de música que están solo en el PC todavía no están en el almacenamiento cloud.
- Las candidatas Ketsa recuperadas continúan PENDING. No hay música aprobada y el agente no debe elevarlas automáticamente.
- El runner estándar público de GitHub Actions es gratuito y sin límite de minutos según GitHub; eso no elimina la necesidad de persistencia. Fuente: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- La ejecución programada sigue deshabilitada. El preflight no equivale a producción.
- La subida de YouTube no debe ejecutarse hasta que haya biblioteca aprobada, estado recuperable y autorización operativa. Si se autoriza, privacidad siempre `private`.

## Alternativas descartadas

- Disco del runner: temporal.
- Artefactos de Actions: intercambio temporal, no almacén duradero de producción.
- Repositorio público: nunca debe contener audio, SQLite, tokens o datos privados.
- Commits frecuentes de MP3/MP4 al repositorio privado: hacen crecer el historial y no son almacenamiento de objetos apropiado.
- SQLite local sin sincronización: no se comparte entre runners.

## Estado

- Preflight real: correcto (78 pruebas y video sintético).
- Acceso de solo lectura al repositorio privado: comprobado.
- Repositorio privado y código principal: permanecen privados.
- Google Drive: OAuth `drive.file` completado; cuota reportada 400 GiB total / 380.83 GiB libres; integración de sincronización implementada, pero todavía no probada en vivo.
- Facturación de Google Cloud: no habilitar.
- Automatización programada: deshabilitada.
- Música aprobada: ninguna.
- Subida a YouTube: deshabilitada en el workflow; nunca pública sin autorización explícita.


## Actualización de implementación — 9 de noviembre de 2026

Se fusionó en el repositorio privado el módulo `drive_storage.py` (PR #3, commit `56058d87f652135f17df78fcdd1ec52625da9ef0`). La usuaria ejecutó localmente compilación y **91 pruebas**, todas correctas. Esto valida las pruebas unitarias, pero no sustituye una prueba real contra Google Drive.

Se preparó en una rama del controlador público el workflow manual `.github/workflows/private-cloud-agent.yml`:
- Checkout del agente privado con el token de solo lectura.
- Compilación y pruebas unitarias en cada ejecución.
- Recuperación de `tracks/`, `data/agent.db` y `output/` desde Drive usando `DRIVE_TOKEN_JSON`.
- Opción de generar una prueba sintética o construir un video local desde una colección que ya tenga música aprobada.
- Persistencia posterior de los cambios en Drive.
- No incluye `YOUTUBE_TOKEN_JSON`, no contiene `--upload` y no puede publicar videos.
- No tiene cron ni programación automática.

### Pasos aún necesarios para la puesta en marcha

1. El workflow del controlador quedó integrado en `main` mediante PR #1, commit `7e9cdd594bb62926c86977b19d0c511f002c674d`.
2. Ejecutar desde la copia local `python main.py drive-seed` (cuando el PR #4 del agente esté validado y fusionado). Este comando carga la copia local de `tracks/`, `output/` y SQLite a Drive privado usando `drive_token.json`, sin mostrar el token.
3. Ejecutar manualmente la tarea `self-test` para verificar la primera recuperación y escritura en Drive.
4. Ejecutar una segunda vez `self-test` y confirmar que restaura los mismos archivos desde la ejecución anterior y conserva la integridad SHA-256.
5. Confirmar que el estado `PENDING` de la música se conserva y que no se habilita ninguna publicación.

La tarea `build-evergreen` solo funcionará cuando exista música aprobada y con derechos verificados. Si la biblioteca está vacía, el agente se detendrá sin generar un mix incompleto. La programación automática continúa deshabilitada hasta que la cuenta y el costo de ejecución estén confirmados sin riesgo de cobro; no se debe habilitar facturación ni pagar almacenamiento.


## Actualización posterior — integración del controlador

El PR #1 del repositorio público `dacorot/jazzsoulbeat-cloud-runner` fue fusionado el 9 de noviembre de 2026 (commit `7e9cdd594bb62926c86977b19d0c511f002c674d`). El workflow `.github/workflows/private-cloud-agent.yml` ya está en `main`, se ejecuta solo mediante `workflow_dispatch` y no contiene secretos de YouTube ni pasos de subida.

Se identificó que el primer seed local necesitaba un comando directo y seguro. Se preparó PR #4 en el repositorio privado (`https://github.com/dacorot/jazzsoulbeat-agent/pull/4`) para añadir `python main.py drive-seed`, que lee `drive_token.json` localmente sin imprimirlo y sube solo las rutas persistentes permitidas. Está pendiente de validación local; no se ha fusionado ni ejecutado.
