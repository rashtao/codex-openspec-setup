# Integration correctness

Load this contract when a change crosses a connector, framework, server, runtime, database, remote service, protocol, or other integration boundary.

## Compatibility surface

Check the applicable supported server, framework, and runtime versions; dependency version bounds; optional dependencies; protocol and wire semantics; feature negotiation; compatibility matrix; and framework lifecycle hooks. Do not assume version behavior from memory.

## Behavioral surface

Check transactions; connection lifecycle and pooling; cancellation; timeouts; retries and idempotency; streaming and backpressure; ordering; thread and async safety; cleanup; error mapping; type and value conversion; nullability; timezone, encoding, and locale; observability; partial failure; and shutdown behavior.

## Evidence selection

| Boundary | Preferred evidence |
|---|---|
| Pure owned logic | Behavior test through its public seam. |
| Protocol or framework contract | Narrow contract or integration test against a realistic implementation or reproducible fixture. |
| External system | Test adapter behavior at the genuine external boundary; use a mock only when it preserves the semantics under test. |
| Version-specific behavior | Pinned-version evidence plus a version-matched test or primary source. |
| Resource or concurrency behavior | Deterministic lifecycle, cancellation, cleanup, backpressure, and stress evidence appropriate to the risk. |

Use test environments realistic enough to exercise the claimed semantics. A unit mock cannot establish protocol, driver, server, or framework behavior it does not implement.

Organize implementation as coherent vertical behavior behind small stable interfaces where that improves the design. Compare materially different designs before a consequential architecture choice; do not invent an adapter or abstraction without real variation.
