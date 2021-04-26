import random
from datetime import datetime


def random_with_N_digits(n):
    start = 10**(n-1)
    end = (10**n) - 1
    random.seed(datetime.now())
    res = random.randint(start, end)
    return res


def random_code(n, list_codes):
    repeat = True
    while repeat:
        code = str(random_with_N_digits(n))
        repeat = code in list_codes
        print(code, repeat)
        print(list_codes)
    return code
