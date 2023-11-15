from zkpytoolkit.types import Array, field # zk_ignore
from dataclasses import dataclass #zk_ignore

# Parameters are based on: https://github.com/HarryR/ethsnarks/tree/9cdf0117c2e42c691e75b98979cb29b099eca998/src/jubjub
# Note: parameters will be updated soon to be more compatible with zCash's implementation

@dataclass
class EdwardsParams:
	EDWARDS_C: field
	EDWARDS_A: field
	EDWARDS_D: field
	MONT_A: field
	MONT_B: field
	INFINITY: Array[field, 2]
	Gu: field
	Gv: field
