def convertStr(s):
    try:
        ret = round(float(s), 7)
    except ValueError:
        # Try float.
        return None
    return ret
