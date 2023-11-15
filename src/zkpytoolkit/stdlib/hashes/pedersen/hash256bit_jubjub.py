from zkpytoolkit.types import Array # zk_ignore
from .hash256bitBool_jubjub import main as pedersen
from zkpytoolkit.stdlib.utils.casts.int_to_bits import main as to_bits
from zkpytoolkit.stdlib.utils.casts.int_from_bits import main as from_bits

def main(inputs: Array[int, 8]) -> Array[int, 8]:
	e: Array[bool, 256] = [
		*to_bits(inputs[0]),
		*to_bits(inputs[1]),
		*to_bits(inputs[2]),
		*to_bits(inputs[3]),
		*to_bits(inputs[4]),
		*to_bits(inputs[5]),
		*to_bits(inputs[6]),
		*to_bits(inputs[7])
	]

	aC: Array[bool, 256] = pedersen(e)
	return [
		from_bits(aC[0:32]),
		from_bits(aC[32:64]),
		from_bits(aC[64:96]),
		from_bits(aC[96:128]),
		from_bits(aC[128:160]),
		from_bits(aC[160:192]),
		from_bits(aC[192:224]),
		from_bits(aC[224:256])
	]