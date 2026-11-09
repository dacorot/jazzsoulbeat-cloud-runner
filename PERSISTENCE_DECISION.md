# Decisión pendiente: almacenamiento persistente en la nube

## Situación comprobada

El workflow manual del repositorio público puede clonar el repositorio privado, instalar dependencias, ejecutar 78 pruebas y producir un video sintético. GitHub destruye el runner al terminar; no existe persistencia de sus archivos locales.

El repositorio privado contiene SQLite en `data/agent.db`, música y manifiestos bajo `tracks/`, y los resultados bajo `output/`. Los directorios locales están excluidos de Git. Por ello, una ejecución nueva no recupera por sí sola la biblioteca o el estado que existían en el PC.

## Criterios obligatorios de la solución

La solución elegida debe cumplir simultáneamente:

- Costo total garantizado de $0, sin activar facturación, tarjeta, prueba pagada ni cargos potenciales.
- Almacenamiento privado y duradero, disponible desde cada runner.
- Capacidad suficiente para los MP3 y videos generados; no basta con guardar CSV o SQLite.
- Copias/reanudación ante interrupciones y escritura atómica.
- No exponer archivos, credenciales ni metadatos privados en el repositorio público.
- Separar los candidatos PENDING de la biblioteca aprobada.
- No subir a YouTube sin autorización explícita y, si se autoriza, forzar y verificar privacidad `private`.

## Alternativas que no resuelven el problema por sí solas

- El disco del runner: temporal.
- Los artefactos de Actions: útiles para intercambio/descarga temporal, no sustituyen un almacén persistente de producción; además tienen límites de tamaño y retención.
- El repositorio público: nunca debe contener audio, SQLite, tokens o información privada.
- Commits frecuentes de MP3/MP4 al repositorio privado: no constituyen almacenamiento de objetos apropiado y hacen crecer el historial.
- Una base de datos SQLite local: no es compartida ni durable entre runners nuevos.

## Próxima decisión técnica

Antes de programar ejecuciones recurrentes o implementar una escritura remota, hay que validar un proveedor de almacenamiento que realmente cumpla el costo cero y la capacidad requerida. La API de un proveedor puede ser gratuita y aun así el almacenamiento, el espacio, las operaciones o el exceso de cuota pueden tener límites o cargos. No se debe asumir que “API gratuita” equivale a almacenamiento gratuito ilimitado.

La integración debe quedar bloqueada hasta verificar precio/cuotas actuales, límite de almacenamiento, límites de transferencia, política de retención, autenticación y posibilidad de establecer un hard stop que impida cualquier cargo.

## Estado

- Preflight: aprobado (78 pruebas y video sintético).
- Acceso de solo lectura al repositorio privado: comprobado en ejecución real.
- Persistencia privada: pendiente.
- Automatización programada: deshabilitada.
- Música aprobada: ninguna de las candidatas pendientes debe promoverse automáticamente.
- Subida a YouTube: deshabilitada en el workflow y nunca pública.
