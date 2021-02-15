from typing import List
import multiprocessing
import time
import json
import random
import string
import hashlib
import math

from multikdf.scrypt import scrypt_kdf
import sha3


class Keystore:
    dklen = 32
    r = 8
    p = 1
    n = 18  # 262144 # NOTE- put Log BASE2 n here. so, if n = 262144 in the .json wallet file, put 18 here

    def __init__(self, keystore_json: str):
        try:
            keystore = json.loads(keystore_json)
        except:
            print("Invalid keystore JSON.")
            exit()

        self.salt = bytearray.fromhex(keystore["Crypto"]["kdfparams"]["salt"])
        self.ciphertext = bytearray.fromhex(keystore["Crypto"]["ciphertext"])
        self.mac = bytearray.fromhex(keystore["Crypto"]["mac"])

    def check(self, password: str):
        dklen, r, p, n = Keystore.dklen, Keystore.r, Keystore.p, Keystore.n
        salt, ciphertext, mac = self.salt, self.ciphertext, self.mac

        derived_key = scrypt_kdf(password, salt, r, p, n, dklen)[16:32]
        concat = derived_key + ciphertext

        k = sha3.keccak_256()
        k.update(concat)
        hashconcat = bytearray.fromhex(k.hexdigest())

        return hashconcat == mac

    def check_multi(self, passwords: List[str]):
        dklen, r, p, n = Keystore.dklen, Keystore.r, Keystore.p, Keystore.n
        salt, ciphertext, mac = self.salt, self.ciphertext, self.mac
        return check_multi(dklen, r, p, n, salt, ciphertext, mac, passwords)

    def check_time_multi(self):
        n = 15
        now = time.time()
        self.check_multi(random_passwords(n))
        return truncate((time.time() - now) / n, 5)


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def random_passwords(n):
    passwords = []
    rletter = lambda: random.choice(string.ascii_lowercase)
    rpass = lambda: "".join(rletter() for _ in range(random.randint(5, 12)))
    return [rpass() for _ in range(n)]


def check_multi(dklen, r, p, n, salt, ciphertext, mac, passwords: List[str]):
    results = multiprocessing.Array("i", len(passwords))

    def check(i: int, password: str):
        try:
            results[i] = 0
            derived_key = scrypt_kdf(password, salt, r, p, n, dklen)[16:32]
            concat = derived_key + ciphertext

            k = sha3.keccak_256()
            k.update(concat)
            hashconcat = bytearray.fromhex(k.hexdigest())

            if hashconcat == mac:
                results[i] = 1
            else:
                results[i] = 0
        except KeyboardInterrupt:
            pass

    processes = []
    for i, password in enumerate(passwords):
        processes.append(multiprocessing.Process(target=check, args=(i, password,)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    return [results[i] == 1 for i in range(len(passwords))]
