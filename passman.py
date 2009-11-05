import sys
import os
import os.path
import random
import tempfile

from optparse import OptionParser
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

import passdb as passdb_module
import textui, gtkui

UI = textui.TextUI

CIPHER = AES
HASH = SHA256

def make_key(text):
    """Convert text to a suitable key for CIPHER."""
    return HASH.new(text).digest()

def generate_iv():
    """Generate a random initialization vector of CIPHER.block_size bytes."""
    return "".join(chr(random.randint(0, 255)) for _ in range(CIPHER.block_size))

def write_passdb(filename, key, passdb):
    """Encrypt and write the password database to file."""
    iv = generate_iv()
    cipher = CIPHER.new(key, CIPHER.MODE_CBC, iv)

    fp, tmpname = tempfile.mkstemp()
    fileobj = os.fdopen(fp, "w+b")
    try:
        data = passdb.dump()
        if len(data) % CIPHER.block_size != 0:
            n = len(data)
            m = CIPHER.block_size
            data += "\0" * (m - n % m)
            assert len(data) % m == 0

        fileobj.write(iv)
        fileobj.write(cipher.encrypt(data))
    except Exception:
        fileobj.close()
        os.remove(tmpname)
        raise

    fileobj.close()
    os.rename(tmpname, filename)

def read_passdb(filename, key):
    """Read the password database from a file and decrypt it with key."""
    fileobj = open(filename, "rb")
    try:
        iv = fileobj.read(CIPHER.block_size)
        if len(iv) != CIPHER.block_size:
            raise ValueError("corrupted password database")
        cipher = CIPHER.new(key, CIPHER.MODE_CBC, iv)

        data = cipher.decrypt(fileobj.read())
        data = data.rstrip("\0")
        return passdb_module.read(data)

    finally:
        fileobj.close()

def run():
    parser = OptionParser()
    parser.add_option("-d", "--db",
                      dest="database",
                      help="use FILE as the password database",
                      metavar="FILE",
                      default=os.path.expanduser("~") + "/.passman/db")
    options, args = parser.parse_args()

    if args:
        parser.print_help()
        sys.exit(2)

    key = None
    ui = UI()

    if not os.path.exists(options.database):
        if not ui.yesno("password database '%s' does not exist; create?" % options.database):
            sys.exit(1)

        ui.msg("initializing empty password database '%s'" % options.database)
        key = make_key(ui.new_key_query("choose a master password: "))

        dirname = os.path.dirname(options.database)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # An empty database is written here
        passdb = PasswordDatabase()
        write_passdb(options.database, key, passdb)

    else:
        ui.msg("using password database '%s'" % options.database)
        key = make_key(ui.key_query("master password: "))
        try:
            passdb = read_passdb(options.database, key)
        except ValueError:
            ui.error("invalid master password or corrupted password database")
            sys.exit(1)

    ui.run(passdb)

    # FIX: The password database should only be rewritten if it was
    # changed
    write_passdb(options.database, key, passdb)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
