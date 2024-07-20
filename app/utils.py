def convertStr(s):
    try:
        ret = float(s)
    except ValueError:
        # Try float.
        return 'Введите число'
    return ret
