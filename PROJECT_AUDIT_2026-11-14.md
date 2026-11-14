# Jazz Soul Beat — auditoría técnica y estado real
**Fecha de revisión:** 2026-11-14 UTC  
**Repositorios revisados:** `dacorot/jazzsoulbeat-agent` (privado) y `dacorot/jazzsoulbeat-cloud-runner` (controlador cloud)

## 1. Resultado principal

Ya se generó un video de revisión privada de 2 horas en QHD. No es un master publicable ni está aprobado para YouTube.

- Ejecución: [43541129670](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/runs/43541129670)
- Artefacto: [jazz-soul-beat-first-video-review-2h00](https://github.com/dacorot/jazzsoulbeat-cloud-runner/actions/runs/43541129670/artifacts/14092377578)
- Estado técnico: `PRIVATE_REVIEW_ONLY_NOT_APPROVED`
- Duración verificada: 7.200,133 segundos
- Resolución: 2560 × 1440
- Escenas usadas: 8
- SHA-256 del MP4: `4a8274229fb10737ca651b26111299eb68fa33a4eaf425c60c339981f887aa74`
- Tamaño del artefacto: 1.125.801.196 bytes
- Retención configurada: 30 días
- YouTube: no se intentó ninguna subida; no hubo publicación.

El artefacto supera el límite de 512 MB del descargador integrado, pero GitHub Actions ofrece su descarga directa desde el enlace anterior.

## 2. Errores encontrados y correcciones verificadas

### Render de video
La primera construcción falló en la prueba de continuidad del bucle:
- FFmpeg interpretó mal el filtro `select=eq(n\\,0)` y reportó `No such filter: '0)'`.
- La ruta de recuperación también falló con `NameError: scene_manifest is not defined`.

La versión del motor fijada en el render exitoso corrige ambos problemas:
- Extrae fotogramas con `select='eq(n,0)'` y `select='eq(n,1)'`.
- La ruta de error ya no depende de una variable local creada solo durante el render normal.
- La prueba `tests.test_multi_scene_video` pasó (4 pruebas) y el render de 2 horas terminó correctamente.

La corrección está en el commit privado `b2b18fbe48f0378a88e04a2fbd9f14931dcf20c6`, usado explícitamente por el workflow de revisión.

### Automatización de producción
El workflow `parallel-production.yml` se disparaba también con cada push a ciertas rutas. El historial del repositorio muestra 618 ejecuciones totales y las 30 más recientes incluían numerosos intentos cancelados o fallidos mientras se depuraba el render. Esto multiplicaba trabajo de auditoría, generación visual y render por cambios de código.

**Corrección aplicada en este repositorio:** el workflow queda manual (`workflow_dispatch`) y ya no se dispara automáticamente con cada push. La búsqueda programada de música permanece separada en sus workflows específicos.

Commit: `9586be678cd2ef716df1f0c4812a146c1124d60d`.

### Documentación cloud
El README describía el sistema como si no tuviera schedules y enumeraba `build-original` como tarea disponible en el formulario, aunque el formulario solo ofrece `self-test` y `build-evergreen`.

**Corrección aplicada:** README actualizado para distinguir las tareas manuales, los schedules de descubrimiento y el productor ACE-Step independiente. También registra el resultado real del video privado y las restricciones de derechos/escenas.

Commits:
- `b2c2ae06c3244e077a8acd2dc06827978e9d8291`
- `7a68136a4e949f5e668079b7d886f0b620760231`

## 3. Música: estado comprobado

### Incompetech
La auditoría descargó 44 pistas del catálogo oficial y verificó:
- Coincidencia exacta de título e ISRC con el catálogo actual.
- Descarga desde URL oficial.
- Coincidencia SHA-256 con el recibo de descarga.
- Archivos legibles y duración detectada.

Sin embargo, **las 44 siguen en estado pendiente y 0 tienen `rights_verified=yes`**. La auditoría detectó:
- La FAQ y la sección de agentes actuales hablan de CC BY 4.0, pero una página histórica de copyright todavía enlaza CC BY 3.0 US.
- Una pista identifica a Alice Goodworth como intérprete de vibráfono.
- Otra agradece a “izope” sin aclarar su contribución.
- No se encontró una garantía independiente que despeje todas las muestras o contribuciones de terceros.

El agente hizo bien en no aprobarlas automáticamente. La mezcla de 2 horas usa esas pistas únicamente como material de escucha privada y revisión de derechos. No debe publicarse.

### Descubrimiento de otros catálogos
La última ejecución de los agentes de búsqueda devolvió 0 candidatos descargables que cumplieran sus filtros CC0/CC BY y duración mínima. No significa que no exista música libre; significa que esa ejecución no encontró archivos que pasaran los filtros.

### Música original
Hay varias implementaciones en ramas distintas:
- `master` conserva `original_music.py` con una primera composición procedural de 64 compases.
- `feature/original-arrangement-development` contiene una versión más elaborada de 512 compases y 32 secciones.
- `fix/real-music-and-cinematic-motion`, que alimenta los renders visuales recientes, no contiene `original_music.py`.

La rama avanzada está muy separada de `master` (513 commits de diferencia en la comparación consultada). No es seguro fusionarla entera sin una integración y una suite completa de regresión. El workflow cloud actual no expone `build-original` en su formulario.

Existe además `music-producer.yml`, un productor independiente que intenta crear 120 segundos de instrumental con el Space público ACE-Step. Es manual, no construye el video final y no equivale a una línea de producción autónoma de canciones largas.

**Conclusión musical:** el video de revisión de 2 horas usa música de terceros pendiente de derechos; no es una composición original de Jazz Soul Beat. Todavía no hay una canción original larga, con voces alternadas, validada y lista para publicación.

## 4. Visuales: estado comprobado

El paquete de ocho vistas contiene:
- 6 imágenes originales generadas.
- 2 variantes de recorte y gradación de color derivadas de la escena 1; no son generaciones independientes.
- Todas están marcadas pendientes de aprobación visual.

La generación gratuita intentó Cloudflare Workers AI, pero la verificación de facturación devolvió HTTP 403. El fallback anónimo de Hugging Face ZeroGPU informó cuota restante de 0 segundos. El proceso se detuvo sin habilitar facturación ni usar un proveedor pagado.

La inspección visual de la hoja de contacto muestra escenas atractivas y coherentes con una atmósfera nocturna, pero los personajes masculinos de las escenas 1, 4 y 6 no demuestran continuidad con el personaje de referencia aprobado. Las escenas 7 y 8 son recortes de la escena 1. No deben considerarse aprobadas como continuidad del personaje.

## 5. Automatizaciones encontradas

- `music-agents.yml`: descubrimiento programado lunes, miércoles y viernes a las 11:17 UTC.
- `discover-music-candidates.yml`: búsqueda programada diaria a las 12:30 UTC (07:30 Colombia).
- `music-producer.yml`: ejecución manual o por marcador de inicio; instrumental de 120 segundos con ACE-Step.
- `private-cloud-agent.yml`: ejecución manual; restaura y persiste datos mediante Google Drive. No recibe `YOUTUBE_TOKEN_JSON`, no usa `--upload` y no publica.
- `parallel-production.yml`: ahora manual para evitar repetir auditorías y renders costosos por cada push.
- `first-video-review-only.yml`: genera una revisión QHD privada a partir de artefactos de audio y escenas preservados; no publica.

Los runners usan `ubuntu-latest`; no se configuraron runners grandes ni proveedores de pago en los workflows revisados. La generación visual gratuita no está disponible actualmente en los proveedores configurados, por lo que falla de forma segura.

## 6. Bloqueos que siguen abiertos

1. Integrar la composición original de 512 compases con el motor visual sin mezclar ramas completas a ciegas.
2. Generar y validar una canción original de duración suficiente; la producción ACE-Step configurada solo intenta 120 segundos.
3. Resolver la licencia histórica y revisar contribuyentes/performers antes de aprobar cualquier pista Incompetech.
4. Producir escenas adicionales con el personaje masculino de referencia consistente y revisar visualmente las ocho escenas.
5. Añadir una tarea cloud de producción original real, con persistencia Drive, pruebas completas y sin credenciales de YouTube.
6. Regenerar el paquete coordinador después del render final de revisión: el informe de coordinación anterior se generó antes del video exitoso y por eso no lo inventaría ni lo contabilizaría retroactivamente.

## 7. Límites de seguridad que permanecen

- No habilitar facturación, créditos pagados ni runners grandes.
- No aprobar automáticamente música o imágenes.
- No subir a YouTube ni publicar en público.
- Cualquier futura subida deberá ser exclusivamente privada y requerir autorización explícita para el archivo exacto.
- Mantener secretos fuera del repositorio público.

---
**Conclusión:** hay un primer video de revisión QHD real y un pipeline técnico que ya supera el render de dos horas. El proyecto aún no ha alcanzado el objetivo de una canción original completa, escenas con continuidad aprobada y agentes que produzcan y entreguen automáticamente un master publicable.


## 8. Endurecimiento adicional posterior a la primera auditoría

Después de documentar los hallazgos, se corrigieron otros dos riesgos operativos en `parallel-production.yml`:

- El workflow manual ahora reutiliza el paquete de ocho escenas ya preservado en la ejecución `43539653311`, valida los SHA-256 de cada imagen y no vuelve a llamar a Cloudflare ni a Hugging Face durante una repetición del pipeline. Esto evita que una revisión técnica dependa de cuotas gratuitas que ya están agotadas.
- Los cuatro jobs del workflow fijan el motor privado al SHA exacto `b2b18fbe48f0378a88e04a2fbd9f14931dcf20c6`, en vez de seguir una rama mutable. Así, las pruebas y el render usan la misma versión que produjo el video exitoso.

Commits:
- `2e5c5a7dbfc48c10edcddcb013830145fff6e340` — reutilización y verificación de las ocho escenas.
- `295a6b86758715aa941dbee7056f71321d22cef4` — fijación del SHA del motor de render.
- `8549540dace1c04da43b40211673ca068ff62d14` — corrección de la instrucción contradictoria sobre `build-original` en el README.

La repetición manual de `parallel-production.yml` depende ahora del artefacto de escenas de la ejecución `43539653311`, cuya retención es de 30 días. Antes de que expire, hay que mover ese paquete a una persistencia duradera privada (por ejemplo, Drive) o crear un nuevo paquete de escenas revisado. No se debe asumir que un artefacto temporal equivale a almacenamiento permanente.

- `a5211e46b26908e8efefb2e045fde0d3f074b479` — precisión de la documentación del workflow: la repetición reutiliza escenas preservadas y no solicita inferencia visual nueva.
