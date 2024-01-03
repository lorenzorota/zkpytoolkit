import bitstring
from zokrates_pycrypto.gadgets.pedersenHasher import PedersenHasher
import numpy as np

entropy = np.random.bytes(64)
hasher = PedersenHasher("G")
point = hasher.hash_bytes(entropy)
print("# created from Point(x={}, y={})".format(point[0], point[1]))
print(hasher.dsl_code)

print("")
entropy = np.random.bytes(64)
hasher = PedersenHasher("H")
point = hasher.hash_bytes(entropy)
print("# created from Point(x={}, y={})".format(point[0], point[1]))
print(hasher.dsl_code)