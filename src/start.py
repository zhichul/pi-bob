from rsys import rsys as rs
import sys

def main():
    if len(sys.argv) == 1:
        rs.Rsys().start()
    else:
        for arg in sys.argv:
            try:
                exec("from rsys import %s" % arg)
                exec("%s.main()" % arg)
            except Exception as e:
                print(e)

if __name__ == "__main__":
    main()