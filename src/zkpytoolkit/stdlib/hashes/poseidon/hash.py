from zkpytoolkit.types import Private, Array, field # zk_ignore
from zkpytoolkit.stdlib.hashes.poseidon.poseidon import main as hash

# let N = 6 for now
def main(inputs: Private[Array[field, 6]]) -> field:
    out: field = hash(inputs)
    return out