def list_all(num):
    for b in num:
        if not isinstance(b, list):
            print(b)
            print('not')
            yield b
        else:
            print(b)
            print('yes')
            for each in b:
                yield each

tt = list_all([1, 2, [3, [4, 5]], 6])
a = list(tt)
print(a)
