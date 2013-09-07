import re
from os.path import join

from storm import util
from storm import conf


class BoltLine(util.LoggedClass):
    separator = " ^bg()^fg(%s)|^fg()^bg() " % conf.CONFIG['colors']['sep']

    def __init__(self):
        self.bolts = []
        super().__init__()

    def register_bolts(self, *bolts):
        for data in bolts:
            bolt = Bolt(**data)
            self.bolts.append(bolt)

    def compile(self):
        return self.separator.join(b.read() for b in self.bolts)

    def width(self):
        text_only = re.sub('\^[^(]*([^)]*).', '', self.compile())
        return len(text_only) * conf.CONFIG['font']['width']


class Bolt(util.LoggedClass):
    def __init__(self, **kwargs):
        self._in = kwargs
        self.__dict__.update(kwargs)
        self.fd = open(join(conf.ROOT, self.runner))

    def read(self):
        self.fd.seek(0)
        return self.fd.read()
