from zkpytoolkit.types import Array, field # zk_ignore
from zkpytoolkit.stdlib.utils.multiplexer.lookup3bitSigned import sel3s
from zkpytoolkit.stdlib.utils.multiplexer.lookup2bit import lookup as sel2
from zkpytoolkit.stdlib.ecc.edwardsAdd import add
from zkpytoolkit.stdlib.ecc.edwardsCompress import edwardsCompress
from zkpytoolkit.stdlib.ecc.doppioParams import DOPPIO_PARAMS
from zkpytoolkit.stdlib.hashes.pedersen.ristretto255.generators import G_table

def pedersen(inputs: Array[bool, 512]) -> Array[bool, 256]: 
    e: Array[bool, 513] = [
        *inputs,
        False
    ]

    a: Array[field, 2] = DOPPIO_PARAMS.INFINITY # Infinity
    cx: field = field(0)
    cy: field = field(0)

    for i in range(0, 171):
        cx = sel3s([e[3*i], e[3*i + 1], e[3*i + 2]], [G_table[i][0][0], G_table[i][1][0], G_table[i][2][0], G_table[i][3][0]])
        cy = sel2([e[3*i], e[3*i + 1]], [G_table[i][0][1], G_table[i][1][1], G_table[i][2][1], G_table[i][3][1]])
        a = add(a, [cx, cy], DOPPIO_PARAMS)

    return edwardsCompress(a)