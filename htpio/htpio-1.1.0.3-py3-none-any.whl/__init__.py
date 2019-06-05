"""
*** Hardware Test Platform (HTP) Remote I/O Classes and Modules. ***

HTPIO is an executable package, which allows the user to test or use some of
its library functionality from the command line.

*Set value using telnet:*

```
htpio -p telnet set --host 192.168.199.31 --pin 14 --val 1
```

*Get value using socket:*
```
htpio -p socket get --host 192.168.199.31 --pin 14
```

*Lock/Unlock pin:*
```
htpio -p telnet lock --host 192.168.199.31 --pin 14
htpio -p socket unlock --host 192.168.199.31 --pin 14
```
"""

name = "htpio"
