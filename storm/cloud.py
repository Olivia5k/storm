import os
import pyinotify as inf
import asyncore

from os.path import join


# TODO: Generalize with storm.py
xdg = os.getenv(
    'XDG_CACHE_HOME',
    join(os.getenv('HOME'), '.cache')
)

ROOT = join(xdg, 'storm')


class Descriptor():
    def __init__(self, path):
        self.fd = open(path)

    def read(self):
        self.fd.seek(0)
        return self.fd.read()


class EventHandler(inf.ProcessEvent):
    items = ['hostname', 'load']
    descriptors = {}

    def load_descriptors(self):
        """
        Load file descriptors of files into dictionary.

        Optimized for not needing opening and closing of file descriptors for
        every update.

        """

        for path in os.listdir(ROOT):
            self.load_descriptor(os.path.join(ROOT, path))

    def load_descriptor(self, path):
        name = self.filename(path)

        print('Loading:', name)
        self.descriptors[name] = Descriptor(path)

    def filename(self, path):
        return path.split('/')[-1]

    def handle(self, event):
        line = []
        for item in self.items:
            line.append(self.descriptors[item].read())
        print(' '.join(line))

    def process_IN_CREATE(self, event):
        name = self.filename(event.pathname)
        if name not in self.descriptors:
            self.load_descriptor(event.pathname)

        self.handle(event)

    process_IN_DELETE = handle
    process_IN_MODIFY = handle


class Cloud():
    def start(self):
        mask = inf.IN_DELETE | inf.IN_CREATE | inf.IN_MODIFY
        wm = inf.WatchManager()
        eh = EventHandler()
        eh.load_descriptors()
        inf.AsyncNotifier(wm, eh)
        wm.add_watch(ROOT, mask, rec=True)

        asyncore.loop()


def main():
    cloud = Cloud()
    cloud.start()

if __name__ == '__main__':
    main()
