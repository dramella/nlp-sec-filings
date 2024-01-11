def add_trailing_zeroes_cik(x):
    if len(str(x)) < 10:
        return (10 - len(str(x))) * str(0) + str(x)
    else:
        return str(x)
