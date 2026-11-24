# Jazz Soul Beat — índice operativo

## Copias canónicas

- Agente de biblioteca y producción: `../jazzsoulbeat-agent-master/`
- Cloud Runner, contratos y gates: este directorio
- Contrato ejecutable único: `config/active_contract.json`
- Estado privado y aprobaciones: `music-production/approval_ledger.json`
- Entrega vigente: ninguna. La última entrega en
  `../jazzsoulbeat-agent-master/tracks/generated/jazz-only-10-videos-2026-11-22/`
  está invalidada y es histórica; no es ejecutable ni publicable.

## Orden de lectura

1. `PROJECT_CONTEXT.md` — contrato activo y continuidad.
2. `PROJECT_STATUS.md` — estado verificado más reciente.
3. `MUSIC_SOURCE_POLICY.md` — límites de derechos y promoción.
4. `MUSIC_LIBRARY_CAPACITY_PLAN.md` — déficit y estrategia de crecimiento.
5. `output/deep-audit-cycle-2026-11-23.json` — auditoría integral más reciente.

## Contrato activo

- 12 videos independientes de 7.200–10.800 s cada uno.
- 500 pistas únicas y 36.000 s de audio aprobado/hash-bound; deben cumplirse
  ambos requisitos.
- Efecto visual validado obligatorio por escena; no existe fallback limpio.
- Publicación pública desactivada; ninguna subida se autoriza por defecto.
- Un candidato técnico no cuenta sin evidencia primaria de derechos.
- El material histórico se conserva, pero no se mezcla con el flujo activo.

## Zonas del proyecto

- `scripts/`, `tests/`, `config/`: código y validaciones activas.
- `music-production/`: ledger, contratos, generación y revisión del runner.
- `output/`: informes reproducibles y resultados de ejecución.
- `../jazzsoulbeat-agent-master/tracks/`: audio, colas, revisiones y entregas.
- `archive/`, `output/legacy-catalogs/`, `reference-images/archive/`: histórico,
  no reutilizable sin una nueva auditoría.

## Regla de orden

No se borran candidatos ni se reescriben resultados históricos. Las correcciones
se aplican al contrato activo, se registran en `PROJECT_STATUS.md` y se validan
con la suite de pruebas antes de cualquier nueva entrega.
