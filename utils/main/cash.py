def to_str(money: int):
    b = f'{money:,}'
    return f"<code>{b.replace(',', '.')}$</code>"


def to_str3(money: int):
    b = f'{money:,}'
    return f"<code>{b.replace(',', '.')}</code>"


def to_str4(money: int):
    b = f'{money:,}'
    return f"{b.replace(',', '.')}"


def to_str2(money: int):
    return f"<code>{money}$</code>"


def get_cash(money: str):
    res = money.replace('.', '').replace(',', '').replace(' ', '').replace('к', '000').replace(
        'k', '000').replace('е', 'e').replace('$', '').replace('m', '000000').replace('м', '000000')
    return int(float(res))


def transform(value):
    balance32 = 0
    if int(value) <= 0:
        return value
    if int(value) in range(1, 1000):
        return f'{value}'
    if int(value) in range(1000, 999999):
        balance1 = value / 1000
        balance2 = int(balance1)
        balance32 = f'{balance2} тыс'

    if int(value) in range(1000000, 999999999):
        balance1 = value / 1000000
        balance2 = int(balance1)
        balance32 = f'{balance2} млн'

    if int(value) in range(1000000000, 999999999999):
        balance1 = value / 1000000000
        balance2 = int(balance1)
        balance32 = f'{balance2} млрд'

    if int(value) in range(1000000000000, 999999999999999):
        balance1 = value / 1000000000000
        balance2 = int(balance1)
        balance32 = f'{balance2} трлн'

    if int(value) in range(1000000000000000, 999999999999999999):
        balance1 = value / 1000000000000000
        balance2 = int(balance1)
        balance32 = f'{balance2} квдр'

    if int(value) in range(1000000000000000000, 999999999999999999999):
        balance1 = value / 1000000000000000000
        balance2 = int(balance1)
        balance32 = f'{balance2} квнт'

    if int(value) in range(1_000_000_000_000_000_000_000, 999_999_999_999_999_999_999_999):
        balance1 = value / 1000000000000000000000
        balance2 = int(balance1)
        balance32 = f'{balance2} скст'
    if int(value) in range(1000_000_000_000_000_000_000_000, 999_999_999_999_999_999_999_999_999):
        balance1 = value / 1000_000_000_000_000_000_000_000
        balance2 = round(balance1)
        balance32 = f'{balance2} трикс'
    if int(value) >= 1000_000_000_000_000_000_000_000_000:
        balance1 = value / 1000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} твинкс'
    if int(value) in range(1000000000000000_000_000_000_000_000, 999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} септ'
    if int(value) in range(1000000000000000000000000000000000, 999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} октл'
    if int(value) in range(1000000000000000000000000000000000000, 999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} нонл'
    if int(value) in range(1000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} декал'
    if int(value) in range(1000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} эндк'
    if int(value) in range(1000000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} доктл'
    if int(value) in range(1000000000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} гугл'
    if int(value) in range(1000000000000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} кинд'
    if int(value) in range(1000000000000000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} трипт'
    if int(value) in range(1000000000000000000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} срист'
    if int(value) in range(1000000000000000000000000000000000000000000000000000000000000,
                           999999999999999999999999999999999999999999999999999999999999999):
        balance1 = value / 1000000000000000000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} манит'

    if int(value) >= 1000000000000000000000000000000000000000000000000000000000000000:
        balance1 = value / 1000000000000000000000000000000000000000000000000000000000000000
        balance2 = round(balance1)
        balance32 = f'{balance2} гвинт'
    return balance32


def transform2(value):
    balance2 = 0
    if int(value) <= 0:
        return value
    if int(value) in range(1000, 999999):
        balance1 = value / 1000
        balance2 = f'{balance1:.2f}k'

    if int(value) in range(1000000, 999999999):
        balance1 = value / 1000000
        balance2 = f'{balance1:.2f}kk'

    if int(value) in range(1000000000, 999999999999):
        balance1 = value / 1000000000
        balance2 = f'{balance1:.2f}kkk'

    if int(value) in range(1000000000000, 999999999999999):
        balance1 = value / 1000000000000
        balance2 = f'{balance1:.2f}kkkk'
    return balance2
