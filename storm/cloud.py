import sys
import pyinotify as inf
import asyncore
import logbook

from storm import util
from storm import conf
from storm import bolt


class Cloud(inf.ProcessEvent):
    """
    The representation layer

    This class is solely concerned with watching the data directory for
    changes, and send a newly constructed line into dzen upon changes.

    """

    def __init__(self, *args, **kwargs):
        # TODO: get LoggedClass to roll with multiple inheritance.
        name = self.__class__.__name__
        self.log = logbook.Logger(name)
        self.log.debug('Loaded logger for {0}', name)

    def setup(self):
        self.setup_lines()
        self.get_screen_width()

    def setup_lines(self):
        self.left = bolt.BoltLine()
        self.left.register_bolts(*conf.CONFIG['items']['left'])

        self.right = bolt.BoltLine()
        self.right.register_bolts(*conf.CONFIG['items']['right'])

    def get_screen_width(self):
        self.width = util.get_screen_size()

    def process_default(self, event):
        if event and 'debug' in conf.CONFIG:
            self.log.debug('{0} on: {1}', event.maskname, event.pathname)

        spacer = "^pa(%d)" % (self.width - self.right.width() - 90)
        line = "%s%s%s" % (self.left.compile(), spacer, self.right.compile())

        assert '\n' not in line, 'Line break in output'

        sys.stdout.write('\n' + line)
        sys.stdout.flush()

    def start(self):
        mask = inf.IN_DELETE | inf.IN_CREATE | inf.IN_MODIFY
        wm = inf.WatchManager()
        inf.AsyncNotifier(wm, self)
        wm.add_watch(conf.ROOT, mask, rec=True)

        # Run the initial grab of data
        self.process_default(None)

        asyncore.loop()


def main():
    cloud = Cloud()
    cloud.setup()
    cloud.start()

if __name__ == '__main__':
    main()
