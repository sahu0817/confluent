### Python Virtual Environment
```
[ubuntu@awst2x ~/.local/bin]# ./pip3.11 install virtualenv
Defaulting to user installation because normal site-packages is not writeable
. . .
Successfully installed distlib-0.3.9 filelock-3.16.1 platformdirs-4.3.6 virtualenv-20.28.1

[ubuntu@awst2x ~/confluent-kafka-python]# source env/bin/activate

(env) [ubuntu@awst2x ~/confluent-kafka-python]# deactivate
```
### Python upgrade

```

[ubuntu@awst2x /usr/lib/python3/dist-packages/gi]#  sudo add-apt-repository ppa:deadsnakes/ppa
Traceback (most recent call last):
  File "/usr/bin/add-apt-repository", line 12, in <module>
    from softwareproperties.SoftwareProperties import SoftwareProperties, shortcut_handler
  File "/usr/lib/python3/dist-packages/softwareproperties/SoftwareProperties.py", line 68, in <module>
    from gi.repository import Gio
  File "/usr/lib/python3/dist-packages/gi/__init__.py", line 42, in <module>
    from . import _gi
ImportError: /usr/lib/python3/dist-packages/gi/_gi.so: undefined symbol: _PyTrash_thread_deposit_object

[ubuntu@awst2x /etc/alternatives]# ls -l | grep py
lrwxrwxrwx 1 root root  19 Jan  3  2024 python3 -> /usr/bin/python3.11

[ubuntu@awst2x /etc/alternatives]# sudo rm python3; sudo ln -s /usr/bin/python3.8 python3

[ubuntu@awst2x /usr/lib/python3/dist-packages/gi]#  sudo add-apt-repository ppa:deadsnakes/ppa

[ubuntu@awst2x /usr/lib/python3/dist-packages/gi]#  sudo apt-get update

[ubuntu@awst2x /usr/lib/python3/dist-packages/gi]#  apt list | grep python3.12

[ubuntu@awst2x /usr/lib/python3/dist-packages/gi]#  sudo apt-get install python3.12

[ubuntu@awst2x /usr/bin]# ./python3.12 -V
Python 3.12.8

[ubuntu@awst2x /etc/alternatives]# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 3
update-alternatives: warning: /etc/alternatives/python3 has been changed (manually or by a script); switching to manual updates only

[ubuntu@awst2x /etc/alternatives]# sudo update-alternatives --config python3
There are 4 choices for the alternative python3 (providing /usr/bin/python3).

  Selection    Path                 Priority   Status
------------------------------------------------------------
  0            /usr/bin/python3.12   3         auto mode
  1            /usr/bin/python3.10   2         manual mode
  2            /usr/bin/python3.11   3         manual mode
* 3            /usr/bin/python3.12   3         manual mode
  4            /usr/bin/python3.8    1         manual mode

Press <enter> to keep the current choice[*], or type selection number:

[ubuntu@awst2x ~]# python3 -V
Python 3.12.8

```
### Python delete
```
[ubuntu@awst2x /usr/bin]# sudo apt purge -y python2.7-minimal
```
 
