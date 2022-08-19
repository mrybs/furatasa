import datetime
from random import randint

ISSUER_ID = {
    'MASTERCARD': randint(511111, 551111),
    'VISA': randint(411111, 499999),
    'AMERICAN-EXPRESS': 34 if randint(0, 1) else 37,
    'UNION-PAY': 62 if randint(0, 1) else 81,
    'MAESTRO': randint(56, 69),
    'MIR': randint(2200, 2204)
}


def userId() -> int:
    return randint(1111111111, 9999999999)


def issuerId(key: str = 'MASTERCARD') -> int:
    return ISSUER_ID.get(key)


def checkLuhn(list_int: list) -> bool:
    c_sum = list_int[-1]
    tmp_v = {i: v * 2 for i, v in enumerate(list_int[:-1]) if i == 0 or i % 2 == 0}
    for k, v in tmp_v.items():
        if v >= 10:
            y = str(v)[0]
            z = str(v)[1]
            w = int(y) + int(z)
            tmp_v.update({k: w})
    for k_, v_ in tmp_v.items():
        list_int[k_] = v_
    res = sum(list_int[:-1]) * 9
    if str(res)[-1] == str(c_sum):
        return True


def gen(key: str = 'MASTERCARD') -> int:
    while 1:
        iid = str(issuerId(key=key))
        uid = str(userId())
        num = iid + uid
        l_tmp = [int(i) for i in num]
        if checkLuhn(l_tmp):
            return int(num)

def randomDate() -> list:
    month = str(randint(1, 12))
    while len(month) != 2:
        month = '0' + month
    return [randint(int(datetime.datetime.now().strftime("%y"))+1, int(datetime.datetime.now().strftime("%y"))+4), month]

def randomCCV() -> str:
    CCV = str(randint(0, 999))
    while len(CCV) != 3:
        CCV = '0' + CCV
    return CCV
