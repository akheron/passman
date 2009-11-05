from passdb import PasswordEntry

# Importing readline enables readline support for raw_input()
try:
    import readline
except ImportError:
    pass

from getpass import getpass

class TextUI(object):
    COMMANDS = [
        ("help", "help [<command>]", "h", """\
Display help."""),
        ("insert", "insert", "i, ins", """\
Insert a new entry to the password database, querying the values."""),
        ("list", "list", "l, ls", """\
List the entries of the password database. Any sensitive information
is not shown to prevent peeking them it your shoulder. Use the 'view'
command to view the sensitive information."""),
        ("remove", "remove <name>", "rm", """\
Remove an entry from the password database. <name> is the name of the
entry to be removed."""),
        ("quit", "quit", "q", """\
Quit the program."""),
        ("view", "view <name>", "v", """\
View a password database entry. <name> is the name of the entry. This
command also lists the sensitive information of the entry (the 'list'
command does not)."""),
    ]
    
    COMMANDS_BY_NAME = dict([(x[0], x) for x in COMMANDS])
    COMMAND_NAMES = set([cmd[0] for cmd in COMMANDS])
    COMMAND_ALIASES = {}
    for cmd in COMMANDS:
        for alias in (x for x in cmd[2].split(", ")):
            COMMAND_ALIASES[alias] = cmd[0]

    def msg(self, text):
        print text

    def error(self, text):
        print "error: %s" % text

    def print_syntax(self, msg):
        print "syntax: %s" % self.COMMANDS_BY_NAME[msg][1]

    def key_query(self, prompt):
        return getpass(prompt)

    def new_key_query(self, prompt):
        while 1:
            key1 = getpass(prompt)
            key2 = getpass("confirm: ")
            if key1 == key2:
                return key1
            else:
                self.error("passwords did not match")
        
    def _yesno(self, msg, default):
        if default == "yes":
            prompt = " [Y/n] "
            yes_opts = [""]
            no_opts = []
        else:
            prompt = " [y/N] "
            yes_opts = []
            no_opts = [""]
        
        while 1:
            ans = raw_input(msg + prompt)
            if ans.lower() in ["y", "yes"] + yes_opts:
                return True
            elif ans.lower() in ["n", "no"] + no_opts:
                return False
            print "please answer 'y' or 'n'"
    
    def yesno(self, prompt):
        return self._yesno(prompt, "yes")

    def noyes(self, prompt):
        return self._yesno(prompt, "no")

    def read_command(self, prompt="> "):
        while 1:
            try:
                text = raw_input(prompt)
            except EOFError:
                print ""
                return "quit", None
            try:
                cmd, args = text.split(None, 1)
            except ValueError:
                cmd = text.strip()
                args = None
            cmd = cmd.lower()

            # Translate command aliases
            try:
                cmd = self.COMMAND_ALIASES[cmd]
            except KeyError:
                pass

            if cmd in self.COMMAND_NAMES:
                return cmd, args

            self.error("unrecognized command '%s'" % cmd)

    def run(self, passdb):
        while 1:
            cmd, args = self.read_command()

            if cmd == "help":
                if args:
                    # Translate command aliases
                    try:
                        args = self.COMMAND_ALIASES[args]
                    except KeyError:
                        pass
                    
                    if args not in self.COMMAND_NAMES:
                        self.error("unrecognized command '%s'" % args)
                    else:
                        command = self.COMMANDS_BY_NAME[args]
                        print "Syntax: %s" % command[1]
                        print "Aliases: %s" % command[2]
                        print ""
                        print command[3]
                        print ""
                else:
                    print "Available commands:"
                    for cmd in sorted(self.COMMAND_NAMES):
                        print "    %s" % cmd
                    print ""
                    print "Type 'help <command>' for more info on a command."
                    print ""

            elif cmd == "insert":
                if args:
                    self.print_syntax("insert")
                else:
                    try:
                        name = raw_input("name: ")
                        username = raw_input("username: ")
                        password = self.new_key_query("password: ")
                        url = raw_input("url: ")
                        desc = raw_input("desc: ")
                    except EOFError:
                        print "aborted"
                        continue

                    entry = PasswordEntry(name, username, password, url, desc)
                    passdb.insert(entry)

            elif cmd == "list":
                if args:
                    self.print_syntax("list")
                elif len(passdb) == 0:
                    print "no entries"
                else:
                    self.msg("%-3.3s %-20.20s %s" % (
                        "#", "Name", "Description"))
                    print "-"*65
                    for i, entry in enumerate(passdb):
                        self.msg("%-3d %-20.20s %s" % (
                            i + 1, entry.name, entry.desc))

            elif cmd == "quit":
                break

            elif cmd == "remove":
                if not args:
                    self.print_syntax("remove")
                    continue

                try:
                    del passdb[args]
                except KeyError:
                    self.error("no entry with the name '%s'" % args)

            elif cmd == "view":
                if not args:
                    self.print_syntax("view")
                    continue

                try:
                    entry = passdb[args]
                except IndexError:
                    self.error("index out of range: %d" % args)
                    continue
                except KeyError:
                    self.error("no entry with the name '%s'" % args)
                    continue
                
                print "name     : %s" % entry.name
                print "username : %s" % entry.username
                print "password : %s" % entry.password
                if entry.url:
                    print "url      : %s" % entry.url
                if entry.desc:
                    print "desc     : %s" % entry.desc
                    
        print "bye"
