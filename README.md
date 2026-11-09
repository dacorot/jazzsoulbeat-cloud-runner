# Jazz Soul Beat Cloud Runner

Controlador público mínimo para ejecutar validaciones del agente privado `dacorot/jazzsoulbeat-agent`.

## Límites de seguridad

- El código de producción permanece en el repositorio privado.
- Este repositorio no contiene música, biblioteca, base de datos, OAuth ni datos del canal.
- El workflow solo permite ejecución manual (`workflow_dispatch`); no tiene programación automática.
- La validación ejecuta compilación, pruebas unitarias y un video sintético local.
- No descarga música, no usa OAuth, no sube videos y no publica contenido.
- No se habilitan pagos ni se cambia ningún presupuesto.

## Configuración necesaria (no introducir valores en archivos)

Para que el workflow pueda leer el repositorio privado, crea en **Settings → Secrets and variables → Actions** de este repositorio un secreto:

- `PRIVATE_REPO_READ_TOKEN`: fine-grained personal access token limitado al repositorio `dacorot/jazzsoulbeat-agent`, con permiso **Contents: Read-only** únicamente.

No uses un token con permisos de escritura, administración, Actions o acceso a otros repositorios. No compartas el token en el chat ni lo guardes en archivos del repositorio.

## Estado operativo

La ejecución de Actions permanece sin probar y no debe iniciarse mientras la cuenta muestre `Usage blocked` o no se pueda garantizar coste cero. Este repositorio no configura pagos ni activa ejecuciones programadas.

El runner es efímero: no conserva archivos ni SQLite entre ejecuciones. Esta prevalidación no constituye todavía un servicio autónomo de producción ni resuelve el almacenamiento persistente de música aprobada y estado.
