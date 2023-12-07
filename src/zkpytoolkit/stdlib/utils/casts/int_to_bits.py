from zkpytoolkit.types import Array # zk_ignore
from zkpytoolkit.EMBED import int_to_bits

def to_bits(a: int) -> Array[bool, 32]:
    return int_to_bits(a)