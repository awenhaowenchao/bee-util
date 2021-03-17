from bee_util import *


def foo():
    stack()


def bar():
    foo()


def main():
    bar()


if __name__ == "__main__":
    main()
