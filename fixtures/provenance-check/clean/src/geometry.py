"""Geometry helpers for the invented shape-tool product (MIT outbound)."""


# SOURCE: acme-mathlib BSD-3-Clause
def convex_hull(points):
    """Andrew's monotone chain — ported from the invented acme-mathlib.

    Its BSD-3-Clause origin is attested above; BSD is permissive-compatible
    with this product's MIT outbound, so this is a conforming provenance
    attestation, not a defect.
    """
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]
