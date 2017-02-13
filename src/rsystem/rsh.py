# Simple shell capable of controlling movement, video/audio capture, and running other python modules

import cmd
import xmlrpc
from rsystem import rsys

class Rsh(cmd.Cmd):
    """
    Roboshell - a simple python shell capable of controlling movement,
    video/audio capture, and running custom python rplugin.
    """
    prompt = "rsh > "
    use_rawinput = True
    intro = "Starting shell..."

    ############### Commands ###############

    def do_rp(self,arg):
        if (len(arg.split()) < 1):
            self.stdout.write('*** Too few args: %s\n',arg)
            return None
        plugin = arg.split()[0]
        exec("from rplugin import %s" % (plugin))
        main = eval("%s.main" % plugin)
        main(arg.strip(plugin).strip())

    def do_stats(self,arg):
        with xmlrpc.client.ServerProxy("http://localhost:%d/" % rsys.SCHEDULER_PORT) as proxy:
            print(proxy.get_stats())

    def do_mods(self,arg):
        with xmlrpc.client.ServerProxy("http://localhost:%d/" % rsys.SCHEDULER_PORT) as proxy:
            print(proxy.get_modules())

    def do_motor(self,arg):
        if (len(arg.split()) >= 2):
            args = arg.split()
            l, r = int(args[0]), int(args[1])
            with xmlrpc.client.ServerProxy("http://localhost:%d/" % rsys.MOTOR_PORT) as proxy:
                print(proxy.set_speed(l,r))
        with xmlrpc.client.ServerProxy("http://localhost:%d/" % rsys.MOTOR_PORT) as proxy:
            print("Desired Speed:", proxy.get_speed_desired())
            print("Actual Speed", proxy.get_speed_actual())

    def do_cam(self,arg):
        print(NotImplemented)
        pass

    ############### Overriding methods ##############
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


    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except Exception as e:
            self.stdout.write('*** Exception:\n')
            print(e)
            return None
def main():
    Rsh().cmdloop()

if __name__ == '__main__':
    main()
