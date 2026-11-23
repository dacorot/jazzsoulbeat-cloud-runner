# Jazz Soul Beat — contexto operativo persistente

> **Contrato activo vigente (2026-11-22):** la entrega actual es una ola
> privada de 12 videos de 3.600 s cada uno; la biblioteca de audio aprobada
> debe alcanzar 36.000 s y la publicación permanece desactivada. Las menciones
> anteriores a 7.200 s, 690 s, renders antiguos o preflights históricos son
> registro de decisiones previas y no instrucciones ejecutables actuales.

> Este archivo es la memoria de recuperación del proyecto. Leerlo antes de
> continuar después de reiniciar el PC, cerrar la conversación o recuperar un
> runner. Actualizarlo después de cada cambio material.

## Corrección de contrato 2026-11-23

- La revisión de la entrega de 12 videos detectó falsos positivos: videos de 1
  hora, un único motion clip y una biblioteca de 170 canciones presentada como
  suficiente solo por segundos.
- El contrato activo exige ahora videos de exactamente 2 o 3 horas, al menos
  500 canciones únicas aprobadas y hash-bound, y un efecto visual obligatorio
  asociado a cada escena.
- Las escenas pueden provenir de `assets/visual-agents/approved-style-samples/`
  y los efectos de `assets/visual-agents/jazz_soul_beat_motion/` o de escenas
  animadas validadas. No existe fallback a una escena limpia.
- La entrega `jazz-only-10-videos-2026-11-22/` queda invalidada como candidata
  final: sus videos duran una hora y usan un único motion clip.
- Estado actual: `BLOCKED` hasta alcanzar 500 canciones. Hay 170 aprobadas y
  aproximadamente 37.277,5 segundos.

## Estado confirmado

- Última actualización: 2026-11-17, cierre de sesión.
- El proyecto está aprobado para continuar; no reabrir la aprobación creativa
  por defecto.
- El último video generado y revisado es:
  `music-production/generated/jazz-soul-beat-video-01-autumn-coffee-crossfade-review.mp4`
- Duración: 3600 segundos.
- Contiene video H.264 y audio AAC a 44.1 kHz.
- La revisión humana confirmó que la versión ya no contiene silencios.
- SHA-256 del último video: `2d42f45698356482b8ebe38052478ae6c711fce2ea3a836de9e8f51727c8bb01`
- La publicación debe seguir siendo privada hasta una instrucción explícita.

## Regla de continuidad

Cuando se retome el proyecto:

1. Leer este archivo.
2. Comprobar que el artefacto indicado existe y que su SHA-256 coincide.
3. Revisar los archivos modificados más recientemente en
   `music-production/generated/` y los manifiestos asociados.
4. Continuar desde el último estado confirmado; no repetir renders ni pedir
   otra revisión creativa salvo que cambie el hash del artefacto aprobado.
5. Registrar aquí cualquier nuevo resultado, decisión, bloqueo o siguiente
   acción antes de terminar la sesión.

## Siguiente acción conocida

Revisar el resultado del preflight privado activado para validar la idempotencia
de subida/programación. Después continuar el crecimiento de biblioteca; faltan
6510 segundos aprobados para llegar al mínimo de 7200 segundos.

## Mejoras incorporadas en esta sesión

- Auditoría semanal de copyright con evidencia privada y cuarentena fail-closed.
- El curador privado excluye fuentes en cuarentena de nuevas producciones.
- Heartbeat del pipeline cada seis horas y alertas Telegram deduplicadas ante
  excepciones.
- Manifiesto hash-bound de cada conjunto de producción.
- Ledger privado de idempotencia para subidas y programaciones YouTube.
- Supervisor de biblioteca corregido para distinguir fuentes activas y fuentes
  delegadas; fallos activos producen estado `DEGRADED` sin detener fallbacks.
- Suite del Cloud Runner: 104 pruebas y 47 subpruebas correctas.

## Cierre operativo 2026-11-18

- Suite del agente privado local: 110 pruebas correctas.
- Se recuperaron en GitHub los gates de descripción, etiquetas y aprobación
  hash-bound de la rama operativa.
- `release_coordinator.py` está en la rama operativa y requiere un
  `approval_id` registrado; no puede convertir una aprobación creativa en una
  autorización de derechos.
- Se reactivaron el supervisor de crecimiento y el preflight privado mediante
  sus marcadores de GitHub Actions.
- El proyecto todavía no puede declararse listo para publicación: la biblioteca
  aprobada tiene 690 segundos, el render QHD longform aprobado no existe y el
  resultado del preflight remoto aún debe comprobarse en GitHub Actions.

## Corrección de promoción de biblioteca 2026-11-18

- Las dos pistas aprobadas de Stable Audio 3 estaban en el paquete de originales,
  pero no en `tracks/library.csv` ni en la base de datos productiva.
- La causa era doble: la licencia comunitaria exacta de Stability AI no estaba
  reconocida por el importador y el workflow no restauraba/preparaba el paquete
  antes de `promote-library`.
- GitHub ahora reconoce solo la URL exacta de la licencia, restaura el paquete,
  genera candidatos hash-bound y los pasa por el importador privado.
- El workflow de promoción fue activado. Verificar el reporte privado antes de
  afirmar que los 690 segundos ya están incorporados.

## Recuperación ante apagado inesperado

- Los archivos grandes y los manifiestos viven en el proyecto cloud runner y
  en el almacenamiento persistente configurado; el PC no debe ser la única
  copia.
- Los artefactos parciales no se consideran terminados. Solo se retoma un
  render si el MP4 final existe, `ffprobe` puede leer sus streams y el hash
  está registrado.
- Los estados de aprobación son independientes del estado de publicación.
  Un apagado nunca debe convertir un video en público ni borrar evidencia.
- Si hay discrepancia entre este archivo y un manifiesto hash-bound, conservar
  ambos, señalar la discrepancia y reconciliarla antes de subir.

## Historial breve

| Fecha | Evento |
|---|---|
| 2026-11-17 | Se confirmó la revisión del último video y la ausencia de silencios. |
| 2026-11-17 | Se identificó el MP4 `crossfade-review` como último artefacto generado. |

## Reanudación 2026-11-20

- Se verificó el hash del MP4 aprobado de `Autumn Coffeehouse Jazz & Soul`:
  `2d42f45698356482b8ebe38052478ae6c711fce2ea3a836de9e8f51727c8bb01`.
- La reconciliación local reporta 37 pistas activas y `9354.61` segundos,
  superando el mínimo de `7200` segundos. El preflight remoto privado todavía
  debe comprobarse; no se autoriza publicación pública.
- Siguiente acción: verificar el preflight privado y preparar el video 2 de
  forma secuencial.

## Reconciliación técnica 2026-11-22

- La entrega Jazz-only actual contiene 12 MP4 de 3.600 s y suma 43.200 s de
  archivos técnicamente válidos.
- El video 11 fue regenerado porque era un duplicado exacto del video 01; el
  generador ahora usa una secuencia invertida para esa posición y el manifiesto
  confirma 12 hashes distintos.
- El pool único sigue limitado a 1.911,620586 s, por lo que la entrega repite
  música y no equivale a 43.200 s de audio único aprobado.
- Las pruebas locales siguen verdes: 111 del agente privado y 91 del Cloud
  Runner.
- La auditoría `project-compliance-audit.json` continúa bloqueada y conserva
  un contrato histórico de 7.200 s/690 s. No debe interpretarse como estado
  vigente de la entrega Jazz-only hasta migrar el contrato de capacidad al
  objetivo editorial actual.

## Objetivo musical corregido 2026-11-20

- Requisito vigente: reunir al menos 10 horas de música aprobada antes de
  continuar con la producción longform.
- Umbral operativo: `36000` segundos.
- Estado local observado: `9354.61` segundos activos; faltan `26645.39`
  segundos (7 horas, 24 minutos y 5.39 segundos).
- El umbral anterior de `7200` segundos queda obsoleto y no debe usarse para
  declarar lista la biblioteca.

## Regla permanente de selección musical

- El supervisor y el asistente deben garantizar conjuntamente que cada pista
  sea adecuada para Jazz Soul Beat antes de incorporarla a la biblioteca activa.
- Se deben verificar derechos/licencia, hash, procedencia, duración, género
  jazz/soul, carácter instrumental y adecuación al ambiente elegante,
  relajante y cinematográfico del canal.
- Si cualquiera de esos controles falla, la pista queda fuera de producción.
- El objetivo obligatorio sigue siendo `36000` segundos de música aprobada.

## Auditoría de continuidad y umbral 2026-11-20

- El contexto conversacional debe conservarse en este archivo y en el handoff
  para recuperar el proyecto sin pedir a la usuaria que repita requisitos.
- La auditoría encontró contratos ejecutables que todavía usan `7200` segundos
  y objetivos de 1–3 horas; deben migrarse a `36000` antes de declarar lista la
  biblioteca.
- Hay una discrepancia pendiente: reconciliación local `9354.61` segundos
  activos frente a `690` segundos en el ledger/auditoría reproducible. No se
  debe afirmar cumplimiento hasta reconciliar ambos registros.

## Descarga musical y revisión visual 2026-11-20

- Estado reportado por auditoría: 50 pistas aprobadas y
  `11111.749450892858` segundos; faltan `24888.250549107142` segundos para
  `36000` segundos.
- La reconciliación subcuenta MP3 porque no aplica el fallback `ffprobe`; debe
  corregirse antes de cerrar el estado definitivo.
- Ketsa aporta 78 archivos oficiales verificados (`15071.16` s); 3 candidatos
  con evidencia completa (`572.03` s) siguen pendientes de aprobación.
- Incompetech aporta 46 archivos en staging (`11068.14` s), todavía pendientes
  de completar la evidencia de las fichas.
- YouTube Studio Audio Library no es descargable automáticamente con el OAuth
  de subida disponible; no se aceptan videos comunes como fuente.
- La revisión visual preliminar marca la imagen aprobada más reciente como
  `REVIEW_REQUIRED`: el ambiente cumple, pero la identidad del protagonista no
  coincide claramente con el ancla y hay texto visible en un póster.

## Dirección musical confirmada 2026-11-20

- Prioridad: música instrumental para lectura, trabajo, café, descanso y
  desconexión.
- Perfiles: jazz soul nocturno íntimo (76–94 BPM), smooth jazz/bossa/acoustic
  jazz luminoso (88–116 BPM) y blues/soul cálido expresivo (66–98 BPM).
- Instrumentación: piano/Rhodes, saxofón cálido, contrabajo o bajo suave,
  escobillas, guitarra jazz, percusión ligera y flauta o saxofón melódico.
- Rechazar loops genéricos, repetición mecánica, percusión agresiva, sonidos
  infantiles, imitaciones de artistas, melodías reconocibles y samples sin
  licencia.
- Veto editorial permanente: excluir funk, funky, groove, jazz-funk, beats
  bailables y cualquier pieza con ritmo marcado o dominante, incluso si sus
  derechos están verificados.
- Regla no negociable: no usar piezas genéricas, mediocres, irrelevantes o que
  solo se parezcan superficialmente al pedido para completar horas. Si no
  coincide claramente con la dirección aprobada, se rechaza.
- Finalidad central: música para descansar, pensar, trabajar y estudiar, que
  sostenga la concentración y la calma sin dominar la atención ni inducir baile.
  También debe servir para orar y meditar cuando la playlist lo requiera.

## Rechazo creativo del primer video 2026-11-20

- La usuaria evaluó el primer video como muy malo.
- El video 1 queda rechazado creativamente y no debe considerarse aprobado,
  referencial ni candidato de publicación.
- Su música y diseño no deben reutilizarse sin una nueva revisión completa
  contra la dirección editorial vigente.
- Defecto específico: después de la mitad aparecen ritmos incompatibles con la
  atmósfera de descanso, concentración, oración y meditación. Las pistas
  responsables deben identificarse y quedar en cuarentena.
- YouTube Studio Audio Library queda autorizada como una fuente posible, no
  prioritaria ni exclusiva. También pueden usarse otras fuentes legales que
  cumplan los criterios musicales y de derechos. Solo incorporar descargas
  reales con licencia y atribución verificadas; queda prohibido usar música de
  videos comunes.
- Estado honesto: la descarga musical aún está incompleta. Los agentes
  descargaron material de Incompetech y verificaron archivos de Ketsa, pero no
  se han alcanzado las 10 horas ni se ha logrado descargar automáticamente
  desde YouTube Studio. No declarar terminado el objetivo hasta resolverlo.
- Defecto principal de agentes: ejecutan descubrimiento, descarga y auditoría
  como tareas parciales, pero no cierran el resultado end-to-end pedido. El
  supervisor debe medir un entregable final de `36000` segundos de música
  adecuada, rights-bound, revisada y lista para producción, no solo candidatos.
- Intento de descarga desde YouTube Studio: el entorno no tiene una sesión de
  navegador conectada y el OAuth de subida no expone el catálogo descargable de
  Audio Library. No se descargó música de Studio y no debe declararse lo
  contrario.
- La apertura mediante `google-chrome-stable --new-window` fue absorbida por
  una sesión existente y devolvió errores de zygote `Broken pipe`; la pestaña
  sigue sin estar disponible para control remoto.
- Cierre honesto: la descarga desde YouTube Studio no se completó porque el
  entorno no expuso una sesión de navegador controlable. La tarea permanece
  incompleta.
- Christian Jazz & Worship se mantiene separado y solo admite voces originales
  en inglés con revisión bíblica, lírica y de derechos.

## Auditoría visual detallada 2026-11-20

- La revisión contra las tres especificaciones visuales terminó en
  **FAIL / BLOCKED para aprobación final**; no se editaron activos ni se
  publicó nada.
- El ancla `jazz_soul_beat_recurring_protagonist.png` mide `1536x1024` (3:2),
  por lo que falla el requisito 16:9. Los cinco samples generados son
  `1672x941` y pasan aproximadamente 16:9.
- Los samples conservan rasgos recurrentes fuertes del protagonista y pasan
  estilo, vestuario y atmósfera, pero falta provenance/mapping documentado por
  candidato. La imagen aprobada más reciente no prueba continuidad suficiente
  y contiene texto visible/gibberish en un póster.
- Motion queda bloqueado: los manifests declaran cámara locked, pero faltan
  depth/occlusion masks, scene-depth manifest, frame-level QA, loop seam y
  defect log. No se acepta el estado `APPROVED_AUTOMATED_MOTION` como prueba
  suficiente contra `VISUAL_MOTION_AGENT_SPEC.md`.
- Informe canónico: `jazzsoulbeat-agent-master/output/visual-audit-2026-11-20.md`.

## Auditoría editorial de descargas — 2026-11-20

- Se auditó el inventario musical del agente sin usar YouTube ni publicar.
- El lote Incompetech activo (35 pistas) está etiquetado `relaxed, grooving` y no cumple el veto permanente contra groove/ritmos bailables; no debe reutilizarse.
- Las pistas con títulos funk/funky/groove/disco/party/shuffle fueron marcadas como rechazadas incluso cuando sus derechos están verificados.
- Las 28 pistas Ketsa activas, etiquetadas `jazz/soul`, instrumentales, `quiet, reflective`, energía baja, quedan solo como candidatas de estilo hasta escuchar la segunda mitad de cada una.
- 83 Ketsa y 35 Incompetech permanecen en staging y requieren revisión; staging no cuenta como horas aprobadas.
- Informe canónico: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/music-style-audit-2026-11-20.md`.
- No declarar cumplidas las 10 horas; publicación deshabilitada.

## Descarga oficial Incompetech/Ketsa — 2026-11-20

- Flujos ejecutados sin publicar, sin importar a la biblioteca activa y sin inventar derechos.
- Incompetech: 46 archivos legibles, 11068.14 s en staging; 21 ya presentes y 25 descargados ahora, todos pendientes. Recibo: `jazzsoulbeat-agent-master/tracks/review/incompetech/download_receipt.json`. SHA-256: `ed55d7db2565be915ee420de82d59d4ff7120593fd08820fd4f2b973c7c31a94`.
- Ketsa: 78 archivos oficiales presentes/reconocidos, 15071.17 s, todos `ALREADY_PRESENT_PENDING_REVIEW`; no hubo candidatos nuevos en la consulta actual. Recibo: `jazzsoulbeat-agent-master/tracks/review/ketsa/download_receipt.json`. SHA-256: `61872896554bca23bdd2fdac04b0e27161a3e912b873b6391d10a32493ec16`.
- Total de los recibos: 124 archivos y 26139.31 s (7 h 15 min 39.31 s) en revisión. Esto no equivale a música aprobada y no reduce por sí solo el déficit de 36000 s.
- Fuentes usadas: solo `incompetech.com` y `ketsa.uk`; no YouTube común ni derechos inferidos. Sigue vigente el veto a funk/funky/groove/ritmos bailables.

## Carpeta de entrega YouTube Studio — 2026-11-20

- Se creó `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/` con
  `README.md` y `track_manifest.csv` para recibir canciones descargadas desde
  YouTube Studio Audio Library.
- Todo archivo recibido queda pendiente hasta validar licencia, atribución,
  hash, duración y adecuación editorial.
- La usuaria confirma que las 91 canciones recibidas provienen de YouTube. Esa
  procedencia declarada queda registrada, pero cada pista requiere evidencia de
  Audio Library/Creator Music y de su licencia/atribución exactas antes de
  incorporarse a la biblioteca activa.
- Se recibió y guardó el texto de la licencia de YouTube Audio Library en
  `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/youtube-audio-library-license.txt`:
  permite uso en videos monetizados sin atribución obligatoria y prohíbe
  distribuir los archivos independientemente. Debe aplicarse solo a pistas
  identificadas individualmente como provenientes de Audio Library.

## Auditoría técnica inbox YouTube Studio — 2026-11-20

- Se inspeccionaron 91 MP3 en `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/`; no se modificaron audios ni se aprobaron derechos.
- Duración total incluyendo duplicado: 18726.600858 s (5 h 12 min 6.601 s). Duración única por hash: 18478.029384 s.
- 91/91 parseados correctamente por ffprobe: MP3, 44.1 kHz, estéreo, 320 kb/s. Fallos: 0.
- Duplicado exacto: `Royal Flush - Chris von Sneidern (1).mp3` / `Royal Flush - Chris von Sneidern.mp3`, SHA-256 `f4ef1ca57bf8ab9e143a2998293b930a3eb009d033db68c5665392af7c7bbbdd`.
- `track_manifest.csv` solo tenía cabecera; no se consideró evidencia de licencia, atribución, procedencia ni adecuación editorial.
- Reporte: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-mp3-technical-audit-2026-11-20.md`.

## Auditoría de evidencia y checklist YouTube Studio — 2026-11-20

- Se amplió `tracks/inbox/youtube-studio/track_manifest.csv` con campos obligatorios para licencia, prueba de licencia, atribución, URL, fecha/hora, identidad, procedencia, hash, duración y decisiones separadas de derechos/estilo.
- Se creó `tracks/inbox/youtube-studio/IMPORT_CHECKLIST.md` y el informe `output/youtube-studio-inbox-audit-2026-11-20.md`.
- Dictamen: `PENDING_EVIDENCE`. El manifiesto original estaba vacío; ninguna de las 91 pistas tiene derechos aprobados por inferencia.
- Faltan por pista licencia literal de Studio, evidencia vinculada, atribución/texto, URL exacta, fecha/hora, identidad y procedencia; el nombre del archivo no cuenta como prueba.
- No promover al inventario activo ni sumar al objetivo de 36.000 s hasta completar evidencia individual y revisión editorial.

## Revisión editorial de nombres YouTube Studio — 2026-11-20

- Inventario revisado: 91 MP3 en `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/`.
- 31 `REJECTED_EDITORIAL` por señal vocal explícita `feat`/`featuring`; `I Dance Alone` también queda rechazado por veto de baile.
- 60 permanecen `PENDING_EDITORIAL_REVIEW`; no son aprobaciones ni segundos válidos.
- Revisión limitada a nombres; falta escucha completa, derechos, hash, duración y atribución.
- Informe canónico: `jazzsoulbeat-agent-master/output/youtube-studio-editorial-name-review-2026-11-20.md`.
- No hubo promoción, importación ni publicación.

## Auditoría legal de 31 archivos nuevos YouTube Studio — 2026-11-20

- Se revisó el lote de 31 MP3 añadidos más recientemente en `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/`.
- `track_manifest.csv` no contiene filas; no hay sidecars ni evidencia documental vinculada al lote para demostrar Audio Library/Creator Music, licencia, atribución o URL de fuente.
- Dictamen: `PENDING_EVIDENCE / NOT_APPROVED`; Audio Library/Creator Music `0/31`, licencia `0/31`, atribución `0/31`, URL verificable `0/31`.
- Duración total: `5.112,360660 s`; única por hash: `4.974,415739 s`.
- Duplicado exacto: `Chica Linda - Quincas Moreira.mp3` y `Chica Linda - Quincas Moreira (1).mp3`.
- Reportes: `output/youtube-studio-new-31-legal-evidence-2026-11-20.md` y `.csv`.
- No se infirieron derechos y no se promovió ninguna pista al inventario activo ni al objetivo de `36.000 s`.

## Revisión editorial del lote nuevo de YouTube Studio — 2026-11-20

- Se revisaron exactamente 31 archivos nuevos de `tracks/inbox/youtube-studio/`.
- `REJECTED_EDITORIAL` (5): `Toy Store Funk`, `Yeah Smoove Smoove`, `Parx and Rex - Cumbia Deli`, `Samba Gitana` y `Tipo Um Samba`. Motivos: funk/smooth-groove o carácter bailable explícito.
- `PENDING_EDITORIAL_REVIEW` (26): requieren escucha completa para descartar groove, percusión dominante, voces, cambios de energía y cualquier incompatibilidad con descanso, pensamiento, trabajo, estudio, oración y meditación. `Chica Linda (1)` está marcado como duplicado candidato.
- Duración bruta: `5112.360660` s; no es duración aprobada y no se suma al objetivo de `36000` s.
- No se modificó la biblioteca activa, no se promovió música y no se publicó nada.
- Reporte canónico: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-editorial-review-31-new-2026-11-20.md`.

## Auditoría técnica actualizada del inbox YouTube Studio — 2026-11-20

- La carpeta contiene `180` MP3 actuales; el conteo anterior de `149` quedó obsoleto por 31 archivos nuevos.
- `180/180` legibles con ffprobe: MP3, 44.1 kHz, estéreo, 320 kb/s; fallos `0`.
- Duración bruta: `34.737,149907 s`; duración única por SHA-256: `34.350,633512 s`. Ninguna cifra es duración aprobada.
- Duplicados exactos: `Chica Linda - Quincas Moreira` (hash `dc599087d5a7dc81cb90d294388d78640d0f49c9e9a426973a7401fc87da3c8d`) y `Royal Flush - Chris von Sneidern` (hash `f4ef1ca57bf8ab9e143a2998293b930a3eb009d033db68c5665392af7c7bbbdd`), ambos con copia `(1)`.
- Se recalcularon y documentaron hashes, tamaños, duración y parámetros técnicos de los 31 archivos nuevos en el reporte técnico consolidado.
- No se aprobó ningún derecho ni procedencia; no se modificaron audios, no se promovió música y no se sumaron segundos al objetivo de `36.000` aprobados.
- Reporte: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-mp3-technical-audit-2026-11-20.md`.

## Revisión editorial de los 149 MP3 actuales — 2026-11-20

- Inventario revisado: `149` MP3 en `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/`; no se promovió ni publicó nada.
- Resultado: `12 REJECTED_EDITORIAL` y `137 PENDING_EDITORIAL_REVIEW`.
- Rechazados: `Dance Number 24449`, `Funk AF`, `I Dance Alone`, `Parx and Rex - Cumbia Deli`, `Rise Funk And Trunk`, `Samba Gitana`, `Shake That Thing`, `Swing Haven 1`, `Swing Haven 2`, `Swing Haven 4`, `Tipo Um Samba` y `Toy Store Funk`.
- Duración bruta: `34737.150 s`; no cuenta para `36000 s`. Duplicados exactos retenidos: `Chica Linda` y `Royal Flush`.
- Informe canónico: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-editorial-review-149-2026-11-20.md`.
- Dictamen: `NOT_APPROVED / PENDING_EDITORIAL_REVIEW`.

## Auditoría legal del inventario actual YouTube Studio — 2026-11-20

- La solicitud indicaba 149 MP3, pero el inventario actual contiene `180`; hay `31` archivos adicionales respecto al conteo anterior.
- `track_manifest.csv` tiene solo la cabecera y `0` filas de evidencia.
- Las `180` pistas quedan `PENDING_EVIDENCE`; no se aprobó ninguna licencia ni procedencia.
- Por pista faltan identidad exacta cotejada con Studio, URL exacta, licencia literal, evidencia/cita de licencia, atribución, fecha/hora, cuenta, procedencia desde Studio, hash y duración documentados, escucha completa, decisiones separadas de estilo/derechos y revisor.
- No se infirieron derechos y no se promovió, importó ni publicó ninguna pista; no se sumó duración al objetivo de `36.000 s`.
- Reportes: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-149-evidence-audit.md` y `.csv`.

## Auditoría legal actualizada del inbox YouTube Studio — 212 MP3 — 2026-11-20

- El inventario actual contiene `212` MP3; el conteo anterior de `180` quedó obsoleto.
- `track_manifest.csv` contiene solo la cabecera y `0` filas de evidencia.
- Evidencia verificable de Audio Library/Creator Music: `0/212`; licencias aprobadas: `0/212`; atribuciones verificadas: `0/212`.
- Por pista faltan identidad exacta cotejada con Studio, URL exacta, tipo de licencia, URL y cita de evidencia, requisito y texto de atribución, fecha/hora, cuenta, procedencia desde Studio, hash, duración, revisión editorial, decisiones separadas de estilo/derechos y revisor.
- Todas permanecen `PENDING_EVIDENCE / NOT_APPROVED`. No se infirieron derechos por nombres, artistas, metadatos, ubicación en la carpeta o afirmaciones de procedencia. No se promovió, importó ni publicó ninguna pista.
- Reporte actual: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-212-legal-evidence-audit-2026-11-20.md`.

## Auditoría editorial de los 212 MP3 actuales — 2026-11-20

- Estados: `56 REJECTED_EDITORIAL`, `131 PENDING_FULL_LISTEN`, `25 PENDING_EDITORIAL_SEASONAL`.
- Vetos aplicados: funk/funky, groove, disco, party, shuffle, dance, swing, cumbia y samba; voces/colaboraciones señaladas por `feat./featuring/ft.`; duplicados exactos.
- Bloque navideño: `30` pistas; requiere playlist estacional separada, sin mezcla con evergreen.
- Duración bruta: `39.448,204 s`; no aprobada ni sumada al objetivo de `36.000 s`.
- Ritmos dominantes y relleno quedan pendientes hasta escucha completa; no se infirieron.
- No se promovió, importó ni publicó ninguna pista.
- Reportes: `jazzsoulbeat-agent-master/output/youtube-studio-editorial-audit-212-2026-11-20.md` y `.csv`.

## Auditoría legal actualizada del inbox YouTube Studio — 241 MP3 — 2026-11-20

- El inventario actual contiene `241` MP3 en `tracks/inbox/youtube-studio/`.
- `track_manifest.csv` tiene `0` filas de datos; conserva únicamente la cabecera con `18/18` campos.
- Evidencia verificable de Audio Library/Creator Music: `0/241`; evidencia completa de licencia: `0/241`; evidencia de atribución: `0/241`; evidencia de procedencia: `0/241`.
- Hash coincidente y duración documentados en el manifiesto: `0/241` en ambos casos.
- Duración técnica bruta: `43.505,194445 s`; duración única por SHA-256: `42.605,798685 s`; duplicados exactos adicionales: `6`.
- Dictamen: `FAIL / PENDING_EVIDENCE / NOT_APPROVED`. No se infirieron derechos por nombres, metadatos, carpeta o afirmaciones de procedencia. Ninguna pista cuenta para las `36.000 s` aprobadas.
- Reportes: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-241-legal-evidence-audit.md` y `.csv`.

## Auditoría técnica actual del inbox YouTube Studio — 2026-11-21

- Se auditaron `241` MP3 actuales en `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/`.
- Legibilidad: `241/241` con `ffprobe`; fallos `0`.
- Duración bruta: `43.505,194445 s` (`12 h 5 min 5,194 s`).
- SHA-256 únicos: `235`; grupos de duplicados exactos: `6`; archivos duplicados excluidos: `6`.
- Duración única por SHA-256: `42.605,798685 s` (`11 h 50 min 5,799 s`).
- Se recalcularon hashes, duración y legibilidad por pista. No se modificó, movió ni eliminó audio.
- Derechos, licencias, atribución, procedencia y adecuación editorial siguen `NOT_APPROVED / NO VERIFICADO`; no se promovió ni publicó ninguna pista y no se sumó duración al objetivo de `36.000 s` aprobados.
- Reportes: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-technical-audit-current.md` y `.csv`.

## Auditoría editorial consolidada del inbox YouTube Studio — 241 MP3 — 2026-11-20

- Se auditaron los `241` MP3 actuales; no se promovió, importó, movió ni publicó ninguna pista.
- Duración bruta: `43.505,194 s`; no aprobada ni sumada al objetivo de `36.000 s`.
- Separación editorial: `56` estacionales, `31` con señal vocal y `154` instrumentales por señal de nombre.
- Estados: `21 REJECTED_EDITORIAL_VETO`, `35 REJECTED_EDITORIAL_VOCAL`, `49 PENDING_SEASONAL_INSTRUMENTAL_REVIEW`, `136 PENDING_INSTRUMENTAL_FULL_LISTEN`.
- Vetos aplicados: funk/funky, groove, disco, party, shuffle, dance, swing, cumbia y samba bailable; ritmos dominantes y relleno deben confirmarse por escucha completa.
- Duplicados exactos marcados: `6`.
- Ninguna pista queda aprobada: las pendientes requieren escucha editorial completa y la evidencia legal sigue separada.
- Reporte: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-editorial-audit-241-2026-11-20.md` y `.csv`.

## Manifiesto provisional del inbox YouTube Studio — 241 MP3 — 2026-11-21

- Se procesaron `241/241` MP3 y se escribieron `241` filas en `tracks/inbox/youtube-studio/track_manifest.csv`.
- Cada fila contiene SHA-256 y duración técnica; no se borró, movió, convirtió ni modificó ningún audio.
- Duración bruta: `43.505,194445 s`; duración única por SHA-256: `42.605,798685 s`.
- Duplicados exactos: `6` grupos y `6` archivos repetidos excluidos del total único.
- `229` filas tienen título/artista inferidos solo desde un separador explícito ` - `; `12` quedaron sin esos campos por separación no clara.
- Todas las filas mantienen `source=YOUTUBE_STUDIO_AUDIO_LIBRARY_PENDING_VERIFICATION`, `provenance=USER_CONFIRMED_YOUTUBE_PENDING`, `license_decision=PENDING_EVIDENCE`, `style_decision=PENDING_REVIEW` y `rights_decision=NOT_APPROVED`.
- Licencia, URL de fuente, atribución, identidad, cuenta, fecha y revisor: faltantes en las `241` filas. La licencia genérica proporcionada por el usuario no se trató como aprobación individual.
- No se promovió, importó ni publicó ninguna pista. Reporte: `/home/dacorot/Work/Projects/jazzsoulbeat-agent-master/output/youtube-studio-manifest-provisional-2026-11-21.md`.

## Objetivo de videos 2026-11-21

- Convertir las 10 horas objetivo en aproximadamente 5 videos de 2 horas cada
  uno, con música aprobada y revisión independiente.
- La biblioteca acumulada no equivale a videos terminados; los cinco videos
  deben generarse, revisarse y registrarse secuencialmente.

## Responsabilidad de aprobación 2026-11-21

- El asistente asume la revisión y decisión editorial final; los agentes son
  apoyo técnico y de evidencia.
- Se aplican directamente los vetos contra funk/funky/groove, ritmos bailables,
  voces incompatibles, relleno y música que no sirva para descansar, pensar,
  trabajar, estudiar, orar o meditar.
- La aprobación de derechos exige evidencia individual de origen y licencia;
  una licencia genérica o un nombre de archivo no bastan por sí solos.

## Estado del primer video nuevo de revisión privada — 2026-11-21

- Artefacto reproducible: `jazzsoulbeat-agent-master/scripts/build_private_review_video_01.py`.
- Selección: solo `PENDING_INSTRUMENTAL_FULL_LISTEN`; fuera funk/funky/groove/disco/party/shuffle/dance/swing/cumbia/samba, voces incompatibles, estacionales/navideñas y duplicados exactos.
- Licencia: `USER_CONFIRMED_PROVISIONAL`, basada en el texto entregado por la usuaria.
- 38 pistas seleccionadas; detalle en `tracks/generated/private-review-01/selection.json`.
- Render detenido de forma segura: audio parcial legible de 3.517,071 s; MP4 parcial inválido (`moov atom not found`). No cuenta para 10 horas y no se subió/publicó.
- Se generó una vista previa válida separada de 120 s en `../jazzsoulbeat-agent-master/tracks/generated/private-review-01/jazz-soul-beat-private-review-01-preview-120s.mp4`, 1920x1080, H.264/AAC. El render largo no terminó.
- Corrección completada: primer video nuevo validado en `../jazzsoulbeat-agent-master/tracks/generated/private-review-01/jazz-soul-beat-private-review-01-full.mp4`, `7200.023220` s, 1920x1080 H.264/AAC, SHA-256 `55e49a97565b0abcb2f1fcf5aead150e2cb099e54bc0b8225be999d94f42a7ce`. El segundo video independiente todavía no existe.
- Reporte: `jazzsoulbeat-agent-master/output/youtube-studio-private-review-01-report.md`.
- El render fue descartado además porque `video.py` aplica lluvia procedural de
  pantalla completa, método incompatible con el contrato visual de profundidad
  y oclusiones. No existe aún un video nuevo terminado con movimiento válido.

## Organización del proyecto 2026-11-21

- El estado único está en `PROJECT_STATUS.md`.
- La prueba de 120 s con el compositor corregido fue técnicamente válida; no
  hay todavía dos videos nuevos completos y aprobados.

## Reconstrucción real del video 1 — selección v2 — 2026-11-21

- Se revisó el inbox actual de `jazzsoulbeat-agent-master/tracks/inbox/youtube-studio/` (`241` MP3).
- No se usó `selection.json` anterior ni se publicó/cambió nada en YouTube.
- Script reproducible: `jazzsoulbeat-agent-master/scripts/build_autumn_coffeehouse_selection_v2.py`.
- Política estricta: solo señales exactas `blues` o `bossa` en el nombre; `blue` no cuenta como género. Se excluyen voces, estacionales, funk/funky/groove/swing/dance, beats/hip-hop, gypsy/world dudoso, títulos/artistas inciertos y duplicados exactos.
- Resultado: `4` candidatos y `760,243 s` (`0,211 h`) de duración candidata.
- Déficit frente a 2 horas: `6.439,757 s` (`1,789 h`). No existe una selección segura de 2 horas.
- Candidatos: `Bossa Sonsa — Quincas Moreira`; `Cruller Blues — The Mini Vandals`; `River crossin blues — Patrick Jordan Patrikios`; `Statesboro Blues — The Soundlings`.
- Estado de los cuatro: `CANDIDATE_NOT_APPROVED`, `PENDING_FULL_LISTEN`, `PENDING_EVIDENCE`, `NOT_APPROVED`.
- Artefactos: `tracks/generated/private-review-01/selection-v2.json` y `output/autumn-coffeehouse-selection-v2.md`.
- Siguiente acción segura: escuchar y validar estos cuatro; si alguno falla, reducir la selección. No rellenar el déficit con música dudosa.
## Estado crítico — selección v3 parcial — 2026-11-21

- La revisión se cerró en un punto acotado y reproducible por solicitud de la usuaria. No se generó video ni se publicó nada.
- Artefactos persistentes: `jazzsoulbeat-agent-master/tracks/generated/private-review-01/selection-v3.json`, `jazzsoulbeat-agent-master/output/jazz-soul-selection-v3.md`, `jazzsoulbeat-agent-master/scripts/build_jazz_soul_selection_v3.py`.
- Criterio: únicamente señales explícitas de título/nombre `jazz`, `blues`, `bossa` o `soul`; sin inferir género por artista ni por análisis acústico. Se excluyen funk/funky/groove/swing/dance, voces, navideñas, world/gypsy dudoso, beats y metadatos inciertos.
- Resultado: `24` candidatos, `5.055,402 s` (`1,404 h`): `4` del inbox YouTube Studio, `5` Incompetech y `15` Ketsa. Todos requieren escucha completa y validación de derechos.
- Exclusiones del inbox: `129` género incierto, `46` estacionales, `31` vocales, `19` vetos editoriales y `12` identidades inciertas.
- Estado global: `CANDIDATE_NOT_APPROVED`; duración aprobada `0 s`; déficit frente a `36.000 s`: `30.944,598 s`.
- Pendiente: escuchar los `24` candidatos; verificar ausencia de voz, groove, swing, baile y relleno; conservar evidencia individual de licencia/procedencia de YouTube Studio; confirmar licencia y atribución de Incompetech/Ketsa. No usar estos candidatos para render hasta cerrar esas comprobaciones.

## Revisión de audio v3 — estado parcial — 2026-11-21

- Se ejecutó `scripts/audio_review_selection_v3.py` sobre los archivos reales, decodificados con ffmpeg, muestreando inicio, mitad y final de cada pista.
- Resultados guardados: `output/selection-v3-audio-editorial-review.csv` y `output/selection-v3-audio-editorial-review.md`.
- Resultado parcial: `1 FAIL` (`Soul Motion`, veto editorial por señal explícita de motion) y `23 NEEDS_HUMAN_REVIEW`.
- `PASS_EDITORIAL=0`: la escucha completa fue interrumpida; las métricas acústicas sirven como evidencia auxiliar, no certifican por sí solas instrumentalidad, ausencia de groove ni ajuste para oración/meditación.
- El CSV contiene por pista energía, espectro, periodicidad, tempo estimado, voz probable, ritmo, veto y decisión provisional.
- Derechos sin cambios: `PENDING_EVIDENCE` / `NOT_APPROVED`; no se promovió audio, no se aprobó licencia y no se publicó.
- Faltan: escucha completa de 23 pistas, dictamen editorial final individual y evidencia individual de licencia/procedencia.

## Selection v3 — revisión editorial completa — 2026-11-21

- Se terminó el pase de audio de las 23 pistas pendientes decodificando cada archivo completo con ffmpeg; se midieron energía, balance espectral, periodicidad/pulso, tempo estimado y señal de voz probable.
- Resultado final del lote de 24: `10 PASS_EDITORIAL`, `14 FAIL`, `0 NEEDS_HUMAN_REVIEW`.
- Duración con decisión `PASS_EDITORIAL`: `2.114,314 s` (aprox. `35 min 14 s`). No es aprobación de derechos.
- Artefactos: `jazzsoulbeat-agent-master/output/selection-v3-audio-editorial-final.csv`, `.../selection-v3-audio-editorial-final.md`, `.../selection-v3-audio-editorial-review-full.csv`, `.../selection-v3-audio-editorial-review-full.md`.
- Scripts reproducibles: `scripts/audio_review_selection_v3_full.py` y `scripts/finalize_selection_v3_editorial_review.py`.
- Derechos y licencias permanecen sin aprobar para todas las pistas (`NOT_APPROVED` / `PENDING_EVIDENCE`). No se promovió, renderizó ni publicó ningún audio.
- Limitación explícita: el entorno no permite una escucha subjetiva humana fiable; PASS/FAIL es cribado técnico del audio completo, no certificación humana final de gusto, género o adecuación espiritual. Las 10 PASS requieren escucha externa si se necesita esa validación.
