def cazzo():
    print("aaaaa")
    raise NameError("AAAAAAAAAAAAAAAAAAA")


if __name__ == '__main__':
    try:
        cazzo()
    except NameError as e:
        raise RuntimeError ("A stronzio " +str(e))
