storm
=====

inotify-based dzen2 runner, in Python |o/

## Installing and running storm
**Install os packages**
```
sudo pacman -S virtuanenv acpi
```

**Clone storm**
```
mkdir -p ~/git && cd ~/git
git clone https://github.com/thiderman/storm.git && cd storm
```

**Prepare running storm**
```
virtualenv-3.3 .
pip install -r requirements.txt
python setup.py develop
```

**XXX: Remove when this is done by setup. Make sure everything is in its place.**
```
mkdir -p ~/.cache/storm && sudo mkdir -p /etc/xdg/storm && cp ~/git/storm/storm/config.yml /etc/xdg/storm/
```

**Call dem weather godz**
```
storm &|
```
