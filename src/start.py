import sys

def main():
    if len(sys.argv) == 1:
        from rsystem import rscheduler
        rscheduler.main()
        return
    for arg in sys.argv[1:]:
        try:
            exec("from rsystem import %s" % arg)
            exec("%s.main()" % arg)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
