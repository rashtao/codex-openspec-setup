# Public API and release impact

Load this contract when a change can affect a public API or externally observable behavior. Assess every applicable dimension:

| Dimension | Check |
|---|---|
| Source | Names, signatures, types, visibility, accepted inputs, return values, and compile-time compatibility. |
| Runtime behavior | Defaults, ordering, state transitions, side effects, guarantees, and caller obligations. |
| Wire or protocol | Message shape, encoding, negotiation, ordering, compatibility, and failure semantics. |
| Configuration | Keys, defaults, validation, precedence, environment behavior, and migration. |
| Extension and framework contracts | Documented extension points, hooks, discovery, registration, lifecycle, and integration behavior. |
| Errors and resources | Observable error types and semantics, ownership, cleanup, lifecycle, and resource-management behavior. |
| Compatibility mechanisms | Feature detection, deprecation path, supported-version matrix, and binary or ABI compatibility where applicable. |

Classify release impact as exactly one of:

- `no release-facing impact`
- `patch-compatible`
- `minor-compatible addition`
- `major-breaking candidate`
- `uncertain-needs-investigation`

Syntax alone never determines release impact; behavioral compatibility counts. Planning must explicitly support an intentional break. Implementation must avoid accidental public-API expansion, weakening, widening, or a new support commitment. Verification must compare the claimed class with the actual diff and observed behavior.
