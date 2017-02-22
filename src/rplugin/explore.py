from rsystem import rsys as rs
from . import rtwd
# from Louis at http://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user/21659588#21659588


def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

def main(arg):
    car = rtwd.two_wheel_drive()
    car.start()
    getch = _find_getch()
    while (True):
        ch = getch()
        if (ch == "w"):
            car.gas()
            print("Gas")
        elif (ch == "s"):
            car.brake()
            print("Brake")
        elif (ch == "a"):
            car.left()
            print("Left")
        elif (ch == "d"):
            car.right()
            print("Right")
        elif (ord(ch) == 3):
            break;
        elif (ch == "x"):
            car.stop()
            print("Stop")
        elif (ch == "p"):
            print("Duh...Need to implement photo capture!")
        else:
            pass
    car.shutdown()
    print("Thank you for using explore. Bye!")

if __name__ == "__main__":
    main("")
