# Decisión de almacenamiento persistente — 8 de noviembre de 2026

## Situación comprobada

El workflow manual del repositorio público puede clonar el repositorio privado, instalar dependencias, ejecutar 78 pruebas y producir un video sintético. GitHub destruye el runner al terminar; no existe persistencia de sus archivos locales.

El repositorio privado contiene SQLite en `data/agent.db`, música y manifiestos bajo `tracks/`, y los resultados bajo `output/`. Los directorios locales están excluidos de Git. Una ejecución nueva no recupera por sí sola la biblioteca o el estado que existían en el PC.

## Evaluación: Google Drive como almacén privado

Es la alternativa gratuita más viable encontrada hasta ahora, pero todavía no está habilitada ni se ha probado con el agente.

- Una cuenta Google personal incluye hasta 15 GB sin costo, compartidos entre Drive, Gmail y Google Photos. No son 15 GB exclusivos para el agente; el espacio real disponible depende del uso actual de esa cuenta.
- El uso estándar de Google Drive API se ofrece sin costo adicional. La documentación vigente define límites diarios estándar y un umbral de 400.000.000 unidades de cuota; Google indica que el uso por debajo del umbral no genera cargos. Google anuncia cargos por superar límites estándar más adelante en 2026, tras aviso previo. Por la condición de costo cero, la implementación debe limitar transferencias y operaciones, y no debe solicitar aumentos de cuota ni activar facturación.
- El permiso OAuth `drive.file` es un alcance no sensible recomendado por Google. Permite crear y administrar los archivos que la propia aplicación crea o que el usuario comparte con ella; evita pedir acceso indiscriminado a todo Drive.
- La aplicación ya tiene OAuth para YouTube, pero el token actual no incluye Drive. Añadir Drive requiere habilitar Google Drive API en el proyecto y una nueva autorización OAuth con el alcance `drive.file`. El secreto actual `YOUTUBE_TOKEN_JSON` tendría que sustituirse por el nuevo token, sin compartir su contenido en el chat.
- No se debe iniciar la integración hasta tener autorización expresa para ampliar el alcance OAuth. La conexión a Drive no debe activar pagos ni requerir tarjeta.

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

- La cuenta debe tener espacio libre suficiente dentro de sus 15 GB compartidos; no se ha verificado ese saldo.
- El nuevo alcance OAuth de Drive requiere autorización de la propietaria.
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
- Google Drive: candidato recomendado; integración pendiente de autorización OAuth y verificación de espacio disponible.
- Facturación de Google Cloud: no habilitar.
- Automatización programada: deshabilitada.
- Música aprobada: ninguna.
- Subida a YouTube: deshabilitada en el workflow; nunca pública sin autorización explícita.
