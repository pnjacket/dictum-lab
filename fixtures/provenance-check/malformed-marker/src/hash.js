// String hashing for the invented index-tool product (MIT outbound).

// SOURCE: acme-mathlib
function fnvHash(str) {
  // Origin attested but the license token is MISSING, so compatibility is
  // undecidable here — the tool WARNs (malformed-marker) rather than guessing.
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

module.exports = { fnvHash };
