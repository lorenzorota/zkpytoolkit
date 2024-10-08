from zkpytoolkit.types import field # zk_ignore
from zkpytoolkit.stdlib.ecc.edwardsParams import EdwardsParams

BABYJUBJUB_PARAMS: EdwardsParams = EdwardsParams(
    # Order of the curve for reference: 21888242871839275222246405745257275088614511777268538073601725287587578984328
    EDWARDS_C=field(8), # Cofactor
    EDWARDS_A=field(168700), # Coefficient A
    EDWARDS_D=field(168696), # Coefficient D

    # Point at infinity
    INFINITY=[field(0), field(1)],

    # Generator G
    G = [field(11778354283853556721794590258969052240776923358153575479091595289104208260815),
         field(4660165575422235542129689514131904223884146628289478588697434946795487697708)],

    # Generator H
    H = [field(18178821955276657859300688684765306517392358897702982666727346170646376373380),
         field(20343343967649314197717258655334499551537074004585442203606038993457854172628)]
)

def main() -> EdwardsParams:
    return BABYJUBJUB_PARAMS