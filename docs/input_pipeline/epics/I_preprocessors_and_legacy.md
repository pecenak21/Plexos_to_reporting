## EPIC I — Preprocessors and legacy sources

**Component C1.** Phase 8, and deliberately last: every one of these is small, they are independent of each other, and none of them can be written correctly until the Standard Format reader exists to check their output.

**No shared framework, no plugin registry, no declarative mapping layer.** This matches how APS already works and was an explicit design decision — APS's own `Load_PLEXOS.py` and `Maintenance.py` are exactly this shape, and a framework would be a new thing to learn in exchange for nothing.
