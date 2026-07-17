> Fixture: targets Dictum v1.1.0. Defect: standard-lab-link

A concern spec that violates EDITORIAL Part 2 (the standard stands alone) by
carrying an actual markdown link whose target points into the lab
(`../dictum-lab/…`). `dictum-editorial-lint` must report exactly 1 error
(`standard-lab-link`). A bare prose mention of "the lab" would be fine; a link
target is not.
