if __name__ == "__main__":
    try:
        do_something_strange();
    except Exception:
        print("unable to import sys")
    finally:
        print("fin")

    print("Hello world")
    print(sys.argv[0])
    a = eval("5 + 6")

    if a == 11:
        print("a = 11")
    elif a < 10:
        print("This is false")
    elif a > 10:
        print("This is also false")
    else:
        print("else")
