/* Numeric solver for the invented compute-tool product (MIT outbound). */

/* SOURCE: acme-mathlib GPL-3.0-only */
double newton_step(double x, double fx, double dfx) {
    /* Adapted from the invented acme-mathlib. Its GPL-3.0-only origin is
       honestly attested above — which is exactly why this is a DEFECT: strong
       copyleft cannot be redistributed inside an MIT-outbound product. */
    if (dfx == 0.0) {
        return x;
    }
    return x - fx / dfx;
}
