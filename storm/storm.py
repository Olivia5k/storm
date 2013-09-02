#!/usr/bin/env python -u

import os
import re
import sys
import time
import socket
import threading
import datetime
import subprocess as sub

from os.path import join

import alsaaudio
import psutil

from storm import cloud


class StormFormatter():
    def __init__(self):
        self.colors = {
            "warn": "#e08e1b",
            "crit": "#ee0d0d",
            "dead": "#8f0d0d",
            "fg_1": "#9d9d9d",
            "fg_2": "#666666",
            "fg_3": "#a8c410",
            "bg_1": "#111117",
            "bg_2": "#66770a",
            "bg_3": "#292929",
            "icon": "#a8c410",
            "sep": "#a8c411",
        }

        self.icons = join(
            os.getenv('HOME'),
            '.local/share/infect/misc/x11/storm/storm/icons'
        )

    def colorize(self, text, fg=None, bg=None):
        fg = self.colors[fg] if fg is not None else self.colors["fg_1"]
        bg = self.colors[bg] if bg is not None else self.colors["bg_1"]
        return "^fg(%s)^bg(%s)%s^fg()^bg()" % (fg, bg, text)

    def icon(self, icon, fg=None, bg=None):
        if fg is None:
            fg = "icon"
        icon = "^i(%s)" % join(self.icons, "%s.xbm" % icon)

        return "%s" % self.colorize(icon, fg=fg, bg=bg)

    def tags(self, data):
        """
        Example data to be a tab separated string:

        data = "\t:1\t#2\t.3\t.4\t.5"

        """
        tags = ""
        for tag in data.split('\t'):
            if len(tag) == 0 or tag[:1] == '\n':
                continue
            else:
                state = tag[0]
                tag = tag[1:]

            if state == "#":
                # Active tag
                tag_design = self.colorize(" %s " % tag, fg="bg_1", bg="fg_3")
            elif state == "+":
                # Urgent tag
                tag_design = self.colorize(" %s " % tag, fg="bg_1", bg="crit")
            elif state == "!":
                # Urgent tag
                tag_design = self.colorize(" %s " % tag, fg="bg_1", bg="crit")
            else:
                # Regular ol' tag
                tag_design = self.colorize(" %s " % tag)

            tags += "^ca(1,herbstclient focus_monitor 0 && \
                    herbstclient use %s)%s^ca()" % (
                tag,
                tag_design
            )

        return tags

    def windowtitle(self, data):
        """
        Example data to be a string:

        data = "main@rey"

        """
        return self.colorize(data)

    def date(self, data):
        """
        Example data to be a dict:

        data = {
            "day": "Mon",
            "date": 2013.09.02",
            "time": "19:23:52"
        }

        """
        return "%s %s %s %s" % (
            self.colorize(data['day']),
            self.colorize(data['date']),
            self.colorize("@", fg="fg_3"),
            self.colorize(data['time'])
        )

    def network(self, data):
        """
        Example data to be a string:

        data = "192.168.1.23" or data = "N/A"

        """
        if data == "N/A":
            ip = self.colorize(data, "dead")
            icon = self.icon("wifi_01", fg="dead")
        else:
            ip = self.colorize(data)
            icon = self.icon("wifi_01")

        return "%s %s" % (icon, ip)

    def load(self, data):
        """
        Example data to be a list:

        data = [0.22, 0,24, 0.23]

        """
        load_avgs = ""
        elevation = False
        for avg in data:
            if avg < 1:
                load_avgs += "%s " % self.colorize(avg)
            elif avg < 3:
                load_avgs += "%s " % self.colorize(avg, fg="warn")
                if elevation != "crit":
                    elevation = "warn"
            else:
                load_avgs += "%s " % self.colorize(avg, fg="crit")
                elevation = "crit"

            icon = self.icon("scorpio")
            if elevation:
                icon = self.icon("scorpio", fg=elevation)

        return "%s %s" % (icon, load_avgs[:-1])

    def processes(self, data):
        """
        Example data to be a int:

        data = 161

        """
        if data < 300:
            processes = self.colorize(data)
            icon = self.icon("cpu")
        elif data < 600:
            processes = self.colorize(processes, "warn")
            icon = self.icon("cpu", fg="warn")
        else:
            processes = self.colorize(processes, "crit")
            icon = self.icon("cpu", fg="warn")

        return "%s %s" % (icon, processes)

    def mem_swap(self, data):
        """
        Example data to be a dict:

        data = {
            "memory": 663,
            "swap": 0
        }

        """
        return "%s %s%s%s" % (
            self.icon("mem"),
            self.colorize(int(data["memory"] / 1024**2), fg="fg_2"),
            self.colorize("/", fg="fg_1"),
            self.colorize(int(data["swap"] / 1024**2), fg="fg_2")
        )

    def packages(self, data):
        """
        Example data to be a dict:

        data = {
            "installed": 663,
            "new": 0
        }

        """
        return "%s %s%s%s" % (
            self.icon("pacman"),
            self.colorize(data["installed"]),
            self.colorize("/", fg="fg_3"),
            self.colorize(data["new"])
        )

    def volume(self, data):
        """
        Example data to be a dict:

        data = {
            "volume": 71,
            "muted": False
        }

        """
        # volume = alsaaudio.Mixer().getvolume()[0]
        # muted = alsaaudio.Mixer().getmute()[0]
        if data["volume"] < 35:
            icon = self.icon("spkr_02")
        else:
            icon = self.icon("spkr_01")

        if data["muted"]:
            volume = "%s %s" % (
                self.colorize(data["volume"], fg="fg_2"),
                self.colorize("(Mute)", fg="dead")
            )
        else:
            volume = self.colorize(data["volume"])

        return "%s %s" % (icon, volume)

    def hostname(self, data):
        """
        Example data to be a string:

        data = "rey"

        """
        return self.colorize(socket.gethostname())

    def kernel(self, data):
        """
        Example data to be a string:

        data = "2.10.9-1-ARCH"

        """
        return "%s %s" % (
            self.icon("arch"),
            data
        )

    def power(self, data):
        """
        Example data to be a dict:

        data = {
            "percent": 31,
            "ac_connected": False,
            "time_left": "01:26"
        }

        """
        percent = data["percent"]
        if percent < 10:
            icon = self.icon("bat_empty_01", fg="crit")
            percent = self.colorize(str(percent) + "%", fg="crit")
        elif percent < 20:
            icon = self.icon("bat_empty_01", fg="warn")
            percent = self.colorize(str(percent) + "%", fg="warn")
        elif percent < 30:
            icon = self.icon("bat_low_01", fg="warn")
            percent = self.colorize(str(percent) + "%")
        elif percent < 50:
            icon = self.icon("bat_low_01")
            percent = self.colorize(str(percent) + "%")
        elif percent < 80:
            icon = self.icon("bat_full_01")
            percent = self.colorize(str(percent) + "%")
        else:
            icon = self.icon("bat_full_01")
            percent = self.colorize(str(percent) + "%", fg="fg_3")

        ret = "%s %s" % (icon, percent)

        if data["ac_connected"]:
            ret = "%s %s" % (
                self.icon("ac_01"),
                ret
            )
        elif data["time_left"]:
            ret += " (%s)" % self.colorize(data["time_left"], "fg_2")

        return ret


class StfuFormatter():
    pass


def interval(sleep):
    def real_decorator(function):
        def wrapper(self, *args, **kwargs):
            while True:
                ret = function(self)

                fn = function.__name__
                self.write(fn, ret)

                time.sleep(sleep)

        wrapper.runner = True
        return wrapper
    return real_decorator


def hlwm(hook):
    def real_decorator(function):
        def wrapper(self, *args, **kwargs):
            process = sub.Popen(
                ['herbstclient', '--idle'],
                stdout=sub.PIPE
            )
            while True:
                output = process.stdout.readline()
                if not output:
                    break

                output = output.decode()
                output = output.replace('\n', '')
                if hook in output:
                    hc_hook = []
                    for part in output.split('\t'):
                        if len(part) > 0:
                            hc_hook.append(part)
                    ret = function(self, hc_hook)

                    fn = function.__name__
                    self.write(fn, ret)

        wrapper.hook = hook
        wrapper.runner = True
        return wrapper
    return real_decorator


def static(function):
    def wrapper(self, *args, **kwargs):
        ret = function(self)

        fn = function.__name__
        self.write(fn, ret)

    wrapper.runner = True
    return wrapper


class Storm():
    def __init__(self, formatter):
        self.formatter = formatter
        self.monitor = "0"

    def setup(self):

        xdg = os.getenv(
            'XDG_CACHE_HOME',
            join(os.getenv('HOME'), '.cache')
        )

        p = join(xdg, 'storm')
        os.makedirs(p, exist_ok=True)
        self.cwd = p

        # self.checkhost = "google.com"
        # self.pac_count = "/dev/shm/fakepacdb/counts"

    def run(self):
        # print('Starting')
        # TODO: Unhack this from dir() pls :(
        for name in dir(self):
            value = getattr(self, name)
            if hasattr(value, 'runner'):
                t = threading.Thread(None, value)
                t.daemon = False
                t.start()

    def write(self, fn, data):
        if hasattr(self.formatter, fn):
            func = getattr(self.formatter, fn)
            data = func(data)

        print("Writing {0}".format(fn))

        path = join(self.cwd, fn)
        with open(path, 'w') as fp:
            fp.write(str(data))

    @hlwm("tag")
    def tags(self, hook):
        output = sub.Popen(
            ['herbstclient', 'tag_status'],
            stdout=sub.PIPE
        ).communicate()[0].decode()
        return output

    @hlwm("focus_changed")
    def windowtitle(self, hook):
        return hook[2]

    @interval(1)
    def date(self):
        now = datetime.datetime.now()
        return {
            "day": now.strftime("%a,"),
            "date": now.strftime("%Y.%m.%d"),
            "time": now.strftime("%H:%M:%S")
        }

    # TODO: Use inotify on interface data
    @interval(20)
    def network(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
            # TODO: Please fix
            if "127.0.0" in ip:
                raise OSError
        except (OSError, Exception):
            ip = "N/A"

        return ip

    @interval(7)
    def load(self):
        return os.getloadavg()

    @interval(5)
    def processes(self):
        return len(psutil.get_pid_list())

    @interval(5)
    def mem_swap(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "memory": mem.free,
            "swap": swap.used
        }

    @interval(100)
    def packages(self):
        fakedb = join("/dev", "shm", "fakepacdb")
        fakelock = join(fakedb, "db.lck")
        # realdb = join("/var", "lib", "pacman")

        os.makedirs(join(fakedb, "sync"), exist_ok=True)

        if os.path.exists(fakelock):
            os.remove(join(fakedb, "db.lck"))

        # if not os.path.islink(join(fakedb, "local")):
            # os.symlink(join(realdb, "local"), fakedb)

        sub.Popen(
            ['fakeroot', 'pacman', '--dbpath', fakedb, '-Sy'],
        ).communicate()

        pkgs = sub.Popen(
            ['pacman', '-Q'],
            stdout=sub.PIPE
        ).communicate()[0].decode()
        pkgs = len(pkgs.split("\n")) if len(pkgs) > 0 else 0

        new_pkgs = sub.Popen(
            ['pacman', '--dbpath', fakedb, '-Qqu'],
            stdout=sub.PIPE
        ).communicate()[0].decode()
        new_pkgs = len(new_pkgs.split("\n")) if len(new_pkgs) > 0 else 0

        return {
            "installed": pkgs,
            "new": new_pkgs
        }

    @interval(20)
    def volume(self):
        return {
            "volume": alsaaudio.Mixer().getvolume()[0],
            "muted": alsaaudio.Mixer().getmute()[0]
        }

    @static
    def hostname(self):
        return socket.gethostname()

    @static
    def kernel(self):
        out = sub.Popen(['uname', '-r'], stdout=sub.PIPE).communicate()
        kernel = str(re.sub(r'\s', '', out[0].decode()))
        return kernel

    @interval(10)
    def power(self):
        acpi = sub.Popen(
            ['acpi', '-ab'], stdout=sub.PIPE
        ).communicate()[0].decode().split("\n")

        percent_match = re.search("\d{1,3}%", acpi[0])
        percent = int(percent_match.group(0)[:-1])

        ac_connected = False
        time_left = ""
        if "on-line" in acpi[1]:
            ac_connected = True
        else:
            time_match = re.search("\d{2}:\d{2}:\d{2}", acpi[0])
            if time_match and len(time_match.group(0)) >= 5:
                time_left = time_match.group(0)[:5],

        return {
            "percent": percent,
            "ac_connected": ac_connected,
            "time_left": time_left
        }


def main():
    if len(sys.argv) > 1:
        # Argument given, start the cloudz!
        print('Summoning clouds...')
        cloud.main()
        sys.exit(0)

    def cloud_thread():
        font = "-*-montecarlo-medium-*-*-*-11-*-*-*-*-*-*-*"

        p1 = sub.Popen([sys.argv[0], 'cloud'], stdout=sub.PIPE, bufsize=0)
        p2 = sub.Popen(
            ['dzen2', '-dock', '-ta', 'l', '-sa', 'rc', '-fn', font],
            # ['tee'],
            bufsize=0,
            stdin=p1.stdout,
            stderr=sub.PIPE,
            stdout=sub.PIPE,
        )
        # p1.stdout.close()

        # Will run 5eva
        print('Starting dem cloud')
        p2.wait()

    def storm_thread():
        print('Conjuring the storm...')
        formatter = StormFormatter()
        # formatter = StfuFormatter()
        storm = Storm(formatter)
        storm.setup()
        storm.run()

    ct = threading.Thread(None, cloud_thread)
    ct.daemon = False
    ct.start()

    st = threading.Thread(None, storm_thread)
    st.daemon = False
    st.start()


if __name__ == '__main__':
    main()
