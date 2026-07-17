package bits

// PopCount for the invented telemetry-tool product (MIT outbound).
//
// This is a classic bit-twiddling parallel-count trick reproduced verbatim
// from common knowledge, with NO SOURCE: marker. The tool cannot and does not
// flag it: undeclared copying is the undecidable residual.
func PopCount(x uint64) int {
	x = x - ((x >> 1) & 0x5555555555555555)
	x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
	x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
	return int((x * 0x0101010101010101) >> 56)
}
