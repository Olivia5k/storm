import sys
import pyinotify as inf
import asyncore
import logbook

from storm import util
from storm import conf
from storm import bolt


class EventHandler(inf.ProcessEvent):
    font = conf.CONFIG['font']['name']
    separator_color = conf.CONFIG['colors']['sep']

    width = util.get_screen_size()

    def __init__(self, *args, **kwargs):
        # TODO: get LoggedClass to roll with multiple inheritance.
        name = self.__class__.__name__
        self.log = logbook.Logger(name)
        self.log.debug('Loaded logger for {0}', name)

    def setup(self):
        self.left = bolt.BoltLine()
        self.left.register_bolts(*conf.CONFIG['items']['left'])

        self.right = bolt.BoltLine()
        self.right.register_bolts(*conf.CONFIG['items']['right'])

    def handle(self, event):
        if event and 'debug' in conf.CONFIG:
            self.log.debug('{0} on: {1}', event.maskname, event.pathname)

        spacer = "^pa(%d)" % (self.width - self.right.width() - 90)
        line = "%s%s%s" % (self.left.compile(), spacer, self.right.compile())

        assert '\n' not in line, 'Line break in output'

        sys.stdout.write('\n' + line)
        sys.stdout.flush()

    process_IN_DELETE = handle
    process_IN_CLOSE_WRITE = handle
    process_IN_MODIFY = handle


class Cloud():
    def start(self):
        mask = inf.IN_DELETE | inf.IN_CREATE | inf.IN_MODIFY
        wm = inf.WatchManager()
        eh = EventHandler()
        eh.setup()
        inf.AsyncNotifier(wm, eh)
        wm.add_watch(conf.ROOT, mask, rec=True)

        # Run the initial grab of data
        eh.handle(None)

        asyncore.loop()


def main():
    cloud = Cloud()
    cloud.start()

if __name__ == '__main__':
    main()
