from zkpytoolkit.types import Array # zk_ignore
from zkpytoolkit.EMBED import int_from_bits;

def main(a: Array[bool, 32]) -> int:
    return int_from_bits(a)