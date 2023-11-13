from zkpytoolkit.types import Private, Array # zk_ignore
from zkpytoolkit.stdlib.hashes.pedersen.hash512bit import main as pedersen

def main(input: Private[Array[int, 16]]) -> Array[int, 8]:
    hash: Array[int, 8] = pedersen(input)
    return hash
