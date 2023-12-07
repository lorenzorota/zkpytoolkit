from zkpytoolkit.types import Array, field # zk_ignore
from zkpytoolkit.stdlib.utils.casts.int_to_bits import to_bits
from zkpytoolkit.stdlib.utils.casts.int_from_bits import from_bits
from zkpytoolkit.stdlib.ecc.edwardsAdd import add
from zkpytoolkit.stdlib.ecc.edwardsCompress import edwardsCompress
from zkpytoolkit.stdlib.ecc.jubjubParams import JUBJUB_PARAMS
from zkpytoolkit.stdlib.commitment.pedersen.bls12_381.hash512bitBool import pedersen_no_compress
from zkpytoolkit.stdlib.hashes.pedersen.bls12_381.generators import G_table
from zkpytoolkit.stdlib.hashes.pedersen.bls12_381.generators import H_table

def commit(x: Array[int, 16], r: Array[int, 16]) -> Array[int, 8]:
    x_bool: Array[bool, 512] = [
        *to_bits(x[0]),
        *to_bits(x[1]),
        *to_bits(x[2]),
        *to_bits(x[3]),
        *to_bits(x[4]),
        *to_bits(x[5]),
        *to_bits(x[6]),
        *to_bits(x[7]),
        *to_bits(x[8]),
        *to_bits(x[9]),
        *to_bits(x[10]),
        *to_bits(x[11]),
        *to_bits(x[12]),
        *to_bits(x[13]),
        *to_bits(x[14]),
        *to_bits(x[15])
    ]

    r_bool: Array[bool, 512] = [
        *to_bits(r[0]),
        *to_bits(r[1]),
        *to_bits(r[2]),
        *to_bits(r[3]),
        *to_bits(r[4]),
        *to_bits(r[5]),
        *to_bits(r[6]),
        *to_bits(r[7]),
        *to_bits(r[8]),
        *to_bits(r[9]),
        *to_bits(r[10]),
        *to_bits(r[11]),
        *to_bits(r[12]),
        *to_bits(r[13]),
        *to_bits(r[14]),
        *to_bits(r[15])
    ]

    input_hash: Array[field, 2] = pedersen_no_compress(x_bool, G_table)
    blinding_hash: Array[field, 2] = pedersen_no_compress(r_bool, H_table)
    commitment:  Array[bool, 256] = edwardsCompress(add(input_hash, blinding_hash, JUBJUB_PARAMS))

    return [
        from_bits(commitment[0:32]),
        from_bits(commitment[32:64]),
        from_bits(commitment[64:96]),
        from_bits(commitment[96:128]),
        from_bits(commitment[128:160]),
        from_bits(commitment[160:192]),
        from_bits(commitment[192:224]),
        from_bits(commitment[224:256])
    ]
