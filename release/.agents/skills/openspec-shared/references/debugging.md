# Diagnose before fixing

Use one protocol for a bug, failing test, nondeterminism, leak, regression, or contradictory observation:

1. Gather the raw failure, environment, inputs, recent relevant changes, and the narrowest reproducible feedback loop. Reproduce consistently where possible and minimize the case without changing the failure.
2. Trace the bad state backward from the visible symptom to its first invalid transition. Instrument each component boundary once to record what enters and leaves; validate at each boundary instead of only at the outermost surface.
3. State ONE hypothesis. Cite the supporting evidence and name one observation that would falsify it. Change one causal variable, not several symptoms.
4. Fix the cause at its source. Add compatible validation at other boundaries only when it prevents invalid state from propagating; do not use defensive checks to hide the source defect.
5. Remove temporary instrumentation and verify with a fresh command that exercises the original failure and relevant regression scope.

Wait on observable conditions, never fixed delays. For nondeterminism, capture ordering, state transitions, seeds, timing boundaries, and resource ownership with a repeatable harness.

A cycle is one hypothesis-to-fresh-verification attempt for the same failure. On the **third failed cycle for the same failure**, stop, return blocked with the complete evidence trail, and escalate the contradiction or missing decision to the owning planning artifact. This is the only retry or failure counter in the generated distribution.
