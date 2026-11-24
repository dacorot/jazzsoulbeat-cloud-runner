# Jazz Soul Beat — estado único del proyecto

> **Fuente de verdad reconciliada: 2026-11-24 · contrato v2026-11-23**
>
> Estado: `BLOCKED_ACTIVE_CONTRACT` · Publicación: `DISABLED` · Entrega
> candidata activa: ninguna. Requisitos simultáneos: 500 pistas únicas
> aprobadas/hash-bound, 36.000 s aprobados, 12 videos independientes de 2–3
> horas y efectos visuales validados por escena.

El contrato ejecutable único está en `config/active_contract.json`; los
informes históricos no pueden sustituirlo.

## Corrección de contrato y bloqueo — 2026-11-23

La entrega anterior queda invalidada. Los gates activos requieren 500 canciones
únicas aprobadas, videos de 2–3 horas y una escena de ejemplo con un efecto
visual obligatorio por video. La biblioteca actual contiene 170 canciones
aprobadas; el proyecto permanece `BLOCKED` y no se debe regenerar ni publicar.

Actualizado: 2026-11-24

## Auditoría PASS_EDITORIAL — derechos y procedencia (2026-11-21)

- Alcance cerrado: únicamente las 10 pistas marcadas `PASS_EDITORIAL` en
  `../jazzsoulbeat-agent-master/output/selection-v3-audio-editorial-final.csv`.
- Resultado: 9 `ELIGIBLE` para derechos/procedencia, 1 `MISSING_EVIDENCE`
  (`Nile's Blues`), 0 `REJECTED`.
- Dictamen CSV:
  `../jazzsoulbeat-agent-master/output/selection-v3-pass-editorial-rights-decision-2026-11-21.csv`.
- Informe MD:
  `../jazzsoulbeat-agent-master/output/selection-v3-pass-editorial-rights-decision-2026-11-21.md`.
- No se promovió ninguna pista, no se renderizó ningún video y no se cambió la
  biblioteca activa.
- `Nile's Blues` queda bloqueada: el catálogo Incompetech local la marca como
  pendiente de verificación y no hay recibo/hash de descarga ni registro exacto
  equivalente en `tracks/library.csv`.

## Objetivo

- Mínimo **12 videos independientes** de Jazz Soul Beat.
- La duración total mínima sigue siendo 10 horas / 36.000 segundos, salvo que
  la usuaria indique una distribución distinta.
- Cada video debe ser exclusivamente jazz instrumental coherente; no mezclar
  R&B, soul, blues, bossa, funk, groove, ambient u otros géneros.
- Uso: descansar, pensar, trabajar, estudiar, orar y meditar.
- No se publica nada sin aprobación explícita.

## Música recibida

- Inbox: `../jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/`
- MP3 recibidos: 241.
- Duración técnica bruta: 43.505,19 s.
- Duración única: 42.605,80 s.
- Todos legibles técnicamente.
- Seis grupos de duplicados exactos.
- Evidencia legal individual: pendiente en las 241 pistas.
- Manifiesto: `../jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/track_manifest.csv`.

## Filtro editorial

- Rechazar funk/funky, groove, disco, party, shuffle, dance, swing, cumbia,
  samba bailable, ritmos dominantes, voces incompatibles y relleno.
- Separar música navideña/estacional en playlists propias.
- No contar una pista hacia las 36.000 s hasta pasar derechos y revisión
  editorial.

## Video

- El primer video anterior está rechazado.
- La prueba nueva de 120 s con compositor corregido fue válida técnicamente.
- El compositor ya no permite lluvia procedural de pantalla completa; exige un
  `motion_clip` validado y cámara bloqueada.
- Existe una vista previa válida de 120 s en
  `../jazzsoulbeat-agent-master/tracks/generated/private-review-01/jazz-soul-beat-private-review-01-preview-120s.mp4`.
- Corrección posterior: se generó el primer video nuevo completo por bloques en
  `../jazzsoulbeat-agent-master/tracks/generated/private-review-01/jazz-soul-beat-private-review-01-full.mp4`.
  Duración validada: `7200.023220` s; 1920x1080; H.264/AAC; SHA-256
  `55e49a97565b0abcb2f1fcf5aead150e2cb099e54bc0b8225be999d94f42a7ce`.
- El segundo video independiente todavía no está generado.
- El MP4 completo indicado arriba fue validado técnicamente; sigue rechazado
  editorialmente hasta sustituir su selección musical.

## Visual

- Requisito: base 16:9, protagonista coherente, movimiento localizado,
  profundidad/oclusiones y QA de loop.
- No usar la imagen ancla 3:2 como base final sin una nueva revisión.
- No usar lluvia de pantalla completa ni movimiento que cruce muebles u objetos.

## Estado de entrega

- No hay todavía dos videos nuevos completos y aprobados.
- El siguiente artefacto válido debe ser un MP4 completo, decodificable,
  revisable y con informe de tracklist, hashes, duración y procedencia.
- Evaluación temática del primer video: `REJECTED_FOR_FINAL_USE`.
- Causa: la selección no tuvo escucha completa, contiene posibles desviaciones
  de género/temporada y algunos créditos título/artista invertidos.
- El navegador automatizable no está disponible en esta sesión; se continúa
  con recibos, URLs oficiales y archivos ya entregados, sin fingir acceso a
  YouTube Studio.

## Ciclo activo 2026-11-21

- Bloqueo editorial: las 10 pistas `PASS_EDITORIAL` de v3 son solo cribado
  técnico; requieren validación auditiva humana antes de promoción.
- Bloqueo de derechos: 0 segundos están aprobados en la biblioteca YouTube;
  el texto de licencia recibido no relaciona cada MP3 con una pista concreta.
- Bloqueo de volumen: no existe todavía una selección aprobada de 36.000 s.
- Acción encadenada: se está haciendo el mapeo pista→fuente→licencia y, en
  paralelo, el inventario de fuentes oficiales alternativas. No se renderiza ni
  publica hasta cerrar esos bloqueos.
- El mapeo de las 10 pistas `PASS_EDITORIAL` terminó: `9 ELIGIBLE` por
  procedencia/licencia y `1 MISSING_EVIDENCE` (`Nile's Blues`); ninguna fue
  promovida.
- Se generó una cola adicional de `113` pistas de Ketsa/Incompetech con
  `23.581,563 s` (`6,55 h`) de audio técnico, excluyendo señales explícitas en
  el nombre. Sigue en `PENDING_FULL_LISTEN`; no es aprobación editorial.
- Cola: `../jazzsoulbeat-agent-master/output/official-source-review-queue-2026-11-21.csv`.
- Se generó una entrega privada candidata de 10 h en dos MP4 independientes.
  Ambos pasaron `ffprobe`: 18.000,023 s, 1920×1080, H.264/AAC.
- Video 01: `../jazzsoulbeat-agent-master/tracks/generated/private-delivery-2026-11-21/jazz-soul-beat-private-01-5h.mp4`, SHA-256 `642e99a430b5d2cc71ea8c64100fcd4dfe80755fa90688336691e77ae729a390`.
- Video 02: `../jazzsoulbeat-agent-master/tracks/generated/private-delivery-2026-11-21/jazz-soul-beat-private-02-5h.mp4`, SHA-256 `504c9616bf4d9bcaa50e7aa086e9f5f4fb61e16c7aa48c450342b7788f495e93`.
- La biblioteca única usada es de 25.164,308 s (6,99 h); la entrega completa 10 h usa rotación declarada de 128 pistas, no 10 h únicas.
- Manifiesto: `../jazzsoulbeat-agent-master/tracks/generated/private-delivery-2026-11-21/delivery-manifest.json`.
- QA técnico final: aprobado. QA legal/editorial final: pendiente para los MP3 YouTube; por eso la entrega permanece privada y no publicada.

## Entrega única vigente — 2026-11-21

- Se añadieron seis piezas largas de meditación/concentración desde el catálogo
  oficial de Incompetech: `15.713 s` adicionales, con URL directa, ISRC, hash,
  catálogo y atribución CC BY 4.0.
- Pool único vigente: `40.877,301 s` (`11,35 h`), 134 pistas disponibles.
- Videos vigentes sin repetición entre ellos:
  - `../jazzsoulbeat-agent-master/tracks/generated/private-delivery-unique-2026-11-21/jazz-soul-beat-private-01-5h.mp4`
    — 18.000,023 s; SHA-256 `4f1a679e27a68d78b56e882e58b376ab9a1c7135f1d605d08bd2c23f370fd053`.
  - `../jazzsoulbeat-agent-master/tracks/generated/private-delivery-unique-2026-11-21/jazz-soul-beat-private-02-5h.mp4`
    — 18.000,023 s; SHA-256 `8b65cbca69702864b5868120978b087ae15781e9306957dc6d981d98f49f7416`.
- Auditoría: 133 pistas únicas en los dos videos; 0 duplicados SHA-256 entre
  ambos; ambos MP4 decodificables, 1920×1080 H.264/AAC.
- Mapeo de derechos: `output/private-delivery-unique-rights-mapping-2026-11-21.csv`.
  Hay evidencia oficial local para 62 pistas y 71 pistas YouTube con
  `USER_ATTESTED_TRACK_MAPPING` basada en la confirmación de la usuaria y el
  texto de licencia suministrado. No se debe presentar como verificación
  independiente de Studio ni publicar sin esa comprobación.

## Responsabilidad de ejecución

- El asistente es responsable del flujo full-stack completo: ingestión,
  derechos, selección, metadatos, visuales, render, QA, persistencia y entrega.
- Los agentes son apoyo interno; no se traslada a la usuaria la coordinación
  técnica ni se declara terminado un trabajo parcial.

## Regla de ejecución automática

- Toda instrucción accionable de la usuaria inicia el trabajo automáticamente;
  no se espera una segunda orden como “inicia”.
- Solo se detiene para una decisión imprescindible o una acción externa/riesgosa
  que requiera confirmación. Los bloqueos deben acompañarse de alternativas
  seguras ejecutadas en paralelo.
- Regla permanente y prioritaria del proyecto: toda instrucción accionable
  inicia automáticamente la ejecución hasta un resultado verificable, sin pedir
  una segunda orden ni trasladar la coordinación a la usuaria.

## Reconstrucción Jazz-only — 2026-11-22

- Auditoría estricta inicial: 31 pistas existentes con señal explícita de jazz
  y sin vetos, `6.834,410 s`; todavía pendientes de escucha jazz.
- Se descargó la playlist oficial de Ketsa etiquetada `Jazz`, excluyendo sus
  entradas Bossa y Boogie: 23 pistas, `4.549,650 s`, con URL individual, hash y
  licencia/atribución documentadas.
- Recibo: `../jazzsoulbeat-agent-master/output/ketsa-jazz-playlist-receipt-2026-11-22.json`.
- No se han renderizado videos nuevos con este lote. Los videos anteriores
  continúan rechazados y no cuentan hacia la orden vigente de 10 videos serios.

## Entrega Jazz-only de 10 videos — 2026-11-22

- Se generaron 10 videos privados, uno por hora: `tracks/generated/jazz-only-10-videos-2026-11-22/`.
- Total: `36.000 s` (10 horas); cada MP4 fue validado con `ffprobe` a `3.600 s`, H.264, 1280×720, y pasó decodificación completa.
- Selección: 10 pistas de la playlist oficial de Ketsa etiquetada Jazz, sin voces y con exclusión editorial de títulos/señales `soul`, `Brazilian` y `vibrant`; fuente CC BY con atribución `Music by Ketsa.uk`.
- La biblioteca única contiene `1.912 s` (31,9 min), por lo que los videos usan rotación declarada. No se presenta como 10 horas únicas.
- Manifiesto y hashes: `../jazzsoulbeat-agent-master/tracks/generated/jazz-only-10-videos-2026-11-22/delivery-manifest.json`.
- Estado: `PRIVATE_FINAL_CANDIDATE`, no publicado. La publicación requiere conservar la atribución CC BY en la descripción y revisión editorial final de escucha.

## Entrega mínima cumplida: 12 videos Jazz-only — 2026-11-22

- El objetivo activo exigía mínimo 12 videos; se añadieron los videos 11 y 12 al mismo lote.
- QA final: `12/12` MP4 presentes, `43.200 s` totales (12 horas), `3.600 s` cada uno, H.264/AAC, 1280×720; los 12 pasaron decodificación completa en paralelo.
- Manifiesto actualizado: `../jazzsoulbeat-agent-master/tracks/generated/jazz-only-10-videos-2026-11-22/delivery-manifest.json`.
- Estado: `PRIVATE_FINAL_CANDIDATE`, no publicado. La rotación del pool único de 1.912 s sigue declarada; no son 12 horas únicas.

## Reconciliación técnica — 2026-11-22

- Se detectó y corrigió una duplicación exacta: el video 11 tenía el mismo
  SHA-256 que el video 01 porque el generador repetía la rotación de diez
  pistas al construir doce videos.
- El video 11 fue regenerado con un orden alternativo y ahora tiene SHA-256
  `04ebc448fa33276a86cc2d397ef06a0c488b63732f5e085af015eafb14c2b2b8`.
- Los 12 MP4 existen, duran 3.600 s y sus hashes coinciden con el manifiesto.
- La entrega sigue usando un pool único de 1.911,620586 s; los archivos son
  distintos, pero no representan doce horas de música única.
- Las auditorías del Cloud Runner todavía leen un contrato histórico de
  7.200 s/690 s. Esto queda identificado como discrepancia pendiente y no se
  considera aprobación de derechos ni autorización de publicación.
- La reconciliación hash-bound está en
  `output/state-reconciliation-2026-11-22.json`: confirma 50 pistas aprobadas
  en la base del agente y ya migradas al ledger (11.111,75 s), 65 filas
  verificadas en el CSV, y 50 solicitudes en estado previo a subida privada.
  Las dos duraciones originales se repararon a 330 s y 360 s antes de la
  migración; no se autorizó ninguna subida pública.
- El déficit vigente de biblioteca aprobada es `17.990,93 s` para alcanzar
  los `36.000 s` de audio único exigidos.
- Se migraron al ledger las 48 pistas aprobadas que faltaban allí; junto con
  las dos solicitudes originales, ahora hay `50` solicitudes hash-bound en
  `RIGHTS_VERIFIED_PENDING_PRIVATE_UPLOAD`, con `11.111,75 s` medidos. No hay
  autorizaciones privadas ni públicas de subida.
- Se generaron metadatos privados hash-bound para los 12 videos en
  `../jazzsoulbeat-agent-master/tracks/generated/jazz-only-10-videos-2026-11-22/metadata/`;
  incluyen tracklist, licencia, fuente, atribución, tags, duración y hash exacto.
- La auditoría oficial adicional aprobó 34 pistas nuevas con evidencia de
  fuente y licencia y análisis full-file; el ledger contiene ahora 84 pistas y
  `18.009,07 s` aprobados. Tres candidatos fueron excluidos por evidencia
  oficial incompleta.

## Ciclo de cinco auditorías — 2026-11-22

- Se ejecutaron cinco ciclos consecutivos de auditoría, solución y verificación;
  el informe reproducible está en `output/five-audit-cycle-2026-11-22.json`.
- Ciclos 1–2: pases oficiales, derechos, hashes, ledger, SQLite, CSV y
  manifiesto reconciliados; 84 pistas aprobadas, `18.009,07 s`, sin permisos de
  publicación.
- Ciclo 3: Commons y ccMixter auditados; los candidatos permanecen pendientes.
  Commons respondió con límites `403/429` y ccMixter no produjo candidatos
  elegibles. No se saltó el límite ni se aprobó material sin evidencia.
- Ciclo 4: 30 pases técnicos de la cola estricta (`6.403,68 s`) siguen fuera
  del cómputo por derechos pendientes.
- Ciclo 5: `12/12` videos, `12/12` hashes únicos, `12/12` metadatos hash-bound,
  `43.200 s` de archivo y publicación `NOT_PUBLISHED` verificados.
- Estado honesto del ciclo: `BLOCKED_SAFELY`; faltan `17.990,93 s` de audio
  aprobado con derechos verificables. No se declara terminado mientras falte
  esa capacidad.

## Auditoría profunda integral — 2026-11-22

- Se ejecutaron cinco auditorías adicionales sobre ambas copias canónicas,
  cubriendo sintaxis Python, JSON, agentes, contratos, ledger, hashes, entrega,
  documentación, credenciales y seguridad de publicación.
- Resultado de código: `86` archivos Python del agente y `80` del runner
  auditados sin errores de sintaxis; suites completas `111/111` y `91/91`.
- Resultado de datos: `84` aprobaciones hash-bound, `18.009,07 s`, sin archivos
  aprobados faltantes o con hash incorrecto; entrega `12/12` con hashes únicos.
- Se corrigió el reconciliador para que no reporte el déficit histórico de
  `24.888,25 s`; ahora remite al déficit vigente del contrato activo.
- Se añadieron índices operativos en ambas copias y una declaración superior en
  `PROJECT_CONTEXT.md` que separa el contrato activo de los registros históricos.
- Se endurecieron permisos de credenciales locales a `0600`; siguen ignoradas
  por Git y no se incluyeron en informes ni autorizaciones públicas.
- El informe reproducible completo está en
  `output/deep-audit-cycle-2026-11-22.json`.
- Resultado final: `PASS_WITH_REMAINING_CAPACITY_GAP`. El único bloqueo de
  capacidad vigente sigue siendo completar `17.990,93 s` de audio aprobado con
  derechos verificables; la publicación continúa desactivada.

## Iteración de cierre — ciclo 2026-11-22/02

- Se reejecutaron los gates completos después de corregir la normalización del
  catálogo Incompetech y se incorporaron `Niles Blues` (`153,47 s`) con
  coincidencia primaria y hash exacto.
- Se descargó el catálogo oficial Ketsa disponible (`78/78`) sólo a revisión;
  la auditoría full-file produjo `57` pases técnicos y `56` rechazos técnicos
  en la cola completa. Todos los pases elegibles ya estaban en el ledger salvo
  `Raised Axis (The Djed)`, que quedó rechazado por falta de recibo hash-bound.
- La capacidad aprobada vigente es `18.162,54 s`; el déficit verificable bajó a
  `17.837,46 s`.
- Suites canónicas: agente `111/111`, runner `91/91`. Hashes, JSON, manifiesto,
  metadatos y publicación privada siguen en estado correcto.
- No se encontró una corrección segura adicional que convierta candidatos en
  derechos verificables. El bloqueo restante es externo a los tests: falta
  audio elegible con evidencia primaria suficiente.

## Iteración Ketsa ampliada — 2026-11-23

- La revisión acotada del catálogo oficial encontró `28` páginas adicionales;
  se descargaron `5.346,46 s` a staging privado.
- La auditoría full-file produjo `6` pases técnicos y `22` rechazos. Se
  migraron los `6` pases, añadiendo `1.097,71 s` con evidencia Ketsa y hash
  exacto; ningún archivo rechazado se contó.
- Capacidad aprobada actual: `28.113,92 s`; déficit: `7.886,08 s`.
- Suites después de la migración: agente `111/111`, runner `91/91`.

## Iteración de crecimiento de capacidad — ciclo 2026-11-22/03

- Se amplió la revisión oficial de Incompetech a los códigos de catálogo Jazz,
  Soul y Blues, con `139` archivos hash-bound en staging y `51.808,40 s` de
  material técnico disponible para revisión.
- La auditoría full-file completa produjo `46` pases técnicos y `93` rechazos;
  se migraron únicamente los pases nuevos con evidencia exacta.
- Capacidad aprobada actual: `27.016,20 s`; déficit actual: `8.983,80 s`.
- Las suites siguen en verde: agente `111/111`, runner `91/91`.
- El reintento limitado de Commons terminó con `0` descargas por restricciones
  del proveedor; no se forzó ningún bypass ni se contó material pendiente.
- La auditoría reproducible y el ledger fueron regenerados después de cada lote.

## Iteración Internet Archive — 2026-11-22

- Se revisó una colección de Jason Shaw con atribución individual y se
  descargaron `7` pistas (`1.374,64 s`) a staging privado.
- La auditoría full-file dejó `3` pases técnicos (`535,82 s`) y `4` rechazos.
- No se migró ninguna pista: el registro del proyecto clasifica Internet
  Archive como `secondary_lead` y exige fuente primaria de derechos adicional.
## Cierre histórico superseded — 2026-11-23 — NOT EXECUTABLE

- Se completó el quinto lote de revisión oficial Ketsa: 17 descargas aisladas, 12 pases técnicos hash-bound y `2.437,56` segundos incorporados.
- Capacidad aprobada actual: `37.277,48` segundos frente al objetivo de `36.000`; déficit: `0`.
- Suites: runner `91/91 OK`; agente `111/111 OK`.
- Integridad: `0` errores de sintaxis Python, `0` errores JSON y `0` archivos aprobados faltantes o con hash incorrecto.
- Reconciliación histórica: `RECONCILED_READY`; este resultado quedó
  invalidado por la corrección de contrato del 23-11 y no autoriza producción
  ni publicación.
- Entregas: `12/12`, hashes únicos, metadatos completos; publicación `DISABLED` / `NOT_PUBLISHED`.
- Auditoría profunda histórica: `PASS`; cinco auditorías cíclicas: `PASS`.

## Estado operativo actual — 2026-11-24

- El ledger es la fuente canónica de decisiones hash-bound; SQLite y CSV son
  almacenes locales de producción y no se consideran sincronizados solo por
  compartir archivos.
- El ledger contiene 170 pistas aprobadas por derechos/hash y 37.277,48 s,
  pero faltan 330 pistas para el mínimo activo de 500.
- La entrega de 12 videos de una hora queda invalidada: pool único de
  1.911,620586 s y efectos visuales no validados.
- No se generará ni publicará una nueva entrega hasta que los gates de audio,
  duración, unicidad y efectos visuales pasen conjuntamente.

