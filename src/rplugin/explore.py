from rsystem import rsys as rs
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
    cam_server = rs.server(rs.CAM_PORT)
    getch = _find_getch()
    while (True):
        ch = getch()
        if (ch == "w"):
            print("Gas")
        elif (ch == "s"):
            print("Brake")
        elif (ch == "a"):
            print("Left")
        elif (ch == "d"):
            print("Right")
        elif (ord(ch) == 3):
            print("Stop")
            break;
        elif (ch == "p"):
            print("Duh...Need to implement photo capture!")
        else:
            pass

    print("Thank you for using explore. Bye!")

