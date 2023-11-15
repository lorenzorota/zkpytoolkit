from zkpytoolkit.types import Array, field # zk_ignore
from zkpytoolkit.stdlib.ecc.edwardsParams import EdwardsParams

BABYJUBJUB_PARAMS: EdwardsParams = EdwardsParams(
    # Order of the curve for reference: 21888242871839275222246405745257275088614511777268538073601725287587578984328
    EDWARDS_C=field(8), # Cofactor
    EDWARDS_A=field(168700), # Coefficient A
    EDWARDS_D=field(168696), # Coefficient D

    # Montgomery parameters
    MONT_A=field(168698),
    MONT_B=field(1),

    # Point at infinity
    INFINITY=[field(0), field(1)],

    # Generator
    Gu=field(16540640123574156134436876038791482806971768689494387082833631921987005038935),
    Gv=field(20819045374670962167435360035096875258406992893633759881276124905556507972311)
)

def main() -> EdwardsParams:
    return BABYJUBJUB_PARAMS