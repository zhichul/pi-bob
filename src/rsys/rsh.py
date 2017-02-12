# Simple shell capable of controlling movement, video/audio capture, and running other python modules

import cmd
import xmlrpc

from . import rsys


class Rsh(cmd.Cmd):
    """
    Roboshell - a simple python shell capable of controlling movement,
    video/audio capture, and running custom python rplugin.
    """
    prompt = "rsh > "
    use_rawinput = True
    intro = "Starting shell..."

    def do_rp(self,arg):
        plugin = arg.split()[0]
        try:
            exec("from rplugin import %s" % (plugin))
        except:
            self.stdout.write('*** Unkown plugin or syntax: %s\n' % arg)
            return
        main = eval("%s.main" % plugin)
        main(arg.strip(plugin).strip())

    def do_scheduler(self,arg):
        args = arg.split()
        if (len(args) < 1):
            self.stdout.write('*** Not enough arguments: %s\n' % arg)
            return None
        if (args[0] == "stats"):
            with xmlrpc.client.ServerProxy("http://localhost:%d/" % rsys.SCHEDULER_PORT) as proxy:
                print(proxy.get_stats())
        elif (args[0] == "modules"):
            with xmlrpc.client.ServerProxy("http://localhost:%d/" % rsys.SCHEDULER_PORT) as proxy:
                print(proxy.get_modules())
        else:
            self.stdout.write('*** Unrecognized arg: %s\n' % arg)
            return None

    def emptyline(self):
        """
        Do nothing if empty line is entered.
        :return: None
        """
        return None

    def do_quit(self,arg):
        """
        Exits the shell
        :return: True as a flag to indicate shell termination
        """
        return True

    def do_EOF(self,arg):
        """
        Quit if it sees EOF
        :return: True
        """
        return True


def main():
    Rsh().cmdloop()

if __name__ == '__main__':
    main()
