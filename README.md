# start unoserver

`unoserver --port 2010 --uno-port 2011`

# get unoserver pid (not soffice pid !)

`ps -aef | grep -e "--port 2010 --uno-port 2011"`

-> UNOSERVER_PID

# start stress test

`python test2.py UNOSERVER_PID > log.txt`

log.txt format:

```
    59506	11:07:17	OK	0.11547398567199707	131500
    | index of conversion
    ....... | start time
    ................... | ended ok ?
    ....................... | duration
    ........................................... | unoserver used memory

```