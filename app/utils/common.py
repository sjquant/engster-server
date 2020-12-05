def find_index(array, func):
    return next(i for i, v in enumerate(array) if func(v))
