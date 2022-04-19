def add(*args, **kwargs):
    total = 0
    for arg in args:
        total += arg
    for kwarg in kwargs:
        total += kwargs[kwarg]
    return total


if __name__ == "__main__":

    numbers = [1, 2, 3, 4, 5, 6, 7, 8]
    numbers2 = {'a': 1, 'b': 2, 'c': 3}

    print(add(*numbers))
    print(add(**numbers2))
