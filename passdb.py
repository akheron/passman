# FIX: replace with userdict
class PasswordEntry(object):
    def __init__(self, name, username, password, url="", desc=""):
        self.name = name
        self.username = username
        self.password = password
        self.url = url
        self.desc = desc

    def as_tuple(self):
        return (self.name, self.username, self.password, self.url, self.desc)


class PasswordDatabase(object):
    def __init__(self, data=None):
        self.entries = {}
        if data is not None:
            self.undump(data)

    def insert(self, entry):
        if entry.name in self.entries:
            raise ValueError("duplicate entry")
        self.entries[entry.name] = entry

    def __getitem__(self, key):
        return self.entries[key]

    def __delitem__(self, key):
        del self.entries[key]

    def __iter__(self):
        return iter(sorted(self.entries.values(), key=lambda x: x.name.lower()))

    def __len__(self):
        return len(self.entries)

    def dump(self):
        if self.entries:
            lines = ("\0".join(entry.as_tuple()) for entry in self)
            return "passman-database 1\n" + "\n".join(lines)
        else:
            return "passman-database 1"

    def undump(self, data):
        lines = data.split("\n")
        if lines[0] != "passman-database 1":
            raise ValueError("invalid data")

        passwords = (line.split("\0") for line in lines[1:])
        for password in passwords:
            try:
                entry = PasswordEntry(*password)
            except TypeError:
                raise ValueError("invalid data")
            self.insert(entry)


MAGIC = (
    ("passman-database 1", PasswordDatabase),
)

def read(data):
    DBType = None
    for magic, Type in MAGIC:
        if data.startswith(magic):
            DBType = Type

    if DBType is None:
        raise ValueError("unrecognized file format")

    return DBType(data)
