import os
import sys
import re
import subprocess as sub
import pyinotify as inf
import asyncore
import logbook

from os.path import join
from storm import util


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
    # Setup some static vars that should really be in a conf file.
    # TODO: Conf file plz.
    font = "-*-montecarlo-medium-*-*-*-11-*-*-*-*-*-*-*"
    separator_color = "#a8c411"

    panel_width = util.get_screen_size()

    left_items = [
        'tags', 'windowtitle',
    ]
    right_items = [
        'kernel', 'packages', 'processes', 'mail', 'mem_swap', 'load',
        'power', 'volume', 'network', 'date', 'hostname',
    ]

    descriptors = {}

    def __init__(self, *args, **kwargs):
        # TODO: get LoggedClass to roll with multiple inheritance.
        name = self.__class__.__name__
        self.log = logbook.Logger(name)
        self.log.debug('Loaded logger for {0}', name)

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

        self.log.info('Loading descriptor: {0}', name)
        self.descriptors[name] = Descriptor(path)

    def filename(self, path):
        return path.split('/')[-1]

    def handle(self, event):
        # print('{0} on: {1}'.format(event.maskname, event.pathname))

        separator = " ^bg()^fg(%s)|^fg()^bg() " % self.separator_color

        left_line = []
        for item in self.left_items:
            if item in self.descriptors:
                left_line.append(self.descriptors[item].read())
        left_line = separator.join(left_line)

        right_line = []
        for item in self.right_items:
            if item in self.descriptors:
                right_line.append(self.descriptors[item].read())
        right_line = separator.join(right_line)

        right_text_only = re.sub('\^[^(]*([^)]*).', '', right_line)

        right_text_width = sub.Popen(
            [
                "textwidth",
                self.font,
                right_text_only
            ],
            stdout=sub.PIPE
        ).communicate()[0].decode()

        spacer = "^pa(%s)" % str(self.panel_width - int(right_text_width) - 90)

        line = "%s%s%s" % (
            left_line,
            spacer,
            right_line
        )

        sys.stdout.write('\n' + line)
        sys.stdout.flush()

    def process_IN_CREATE(self, event):
        name = self.filename(event.pathname)
        if name not in self.descriptors:
            self.load_descriptor(event.pathname)

        self.handle(event)

    process_IN_DELETE = handle
    process_IN_CLOSE_WRITE = handle
    process_IN_MODIFY = handle


class Cloud():
    def start(self):
        mask = inf.IN_DELETE | inf.IN_CREATE | inf.IN_MODIFY
        wm = inf.WatchManager()
        eh = EventHandler()
        eh.load_descriptors()
        inf.AsyncNotifier(wm, eh)
        wm.add_watch(ROOT, mask, rec=True)

        # Run the initial grab of data
        eh.handle(None)

        asyncore.loop()


def main():
    cloud = Cloud()
    cloud.start()

if __name__ == '__main__':
    main()
