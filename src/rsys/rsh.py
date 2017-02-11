# Simple shell capable of controlling movement, video/audio capture, and running other python modules

import cmd

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
            main = eval("%s.main" % plugin)
            main(arg.strip(plugin).strip())
        except:
            self.stdout.write('*** Unknown plugin: %s\n' % plugin)



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
