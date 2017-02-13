import sys

def main():
    for arg in sys.argv:
        try:
            exec("from rsystem import %s" % arg)
            exec("%s.main()" % arg)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()