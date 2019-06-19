import argparse
import sys
import os
import signal

def killpidfromfile():
  """deprecated: use below kill() instead"""
  if len(sys.argv) != 3:
    raise ValueError('Invocation: %s <pidfile> <signal name>' % sys.argv[0])
  file = sys.argv[1]
  sig = getattr(signal, sys.argv[2], None)
  if sig is None:
    raise ValueError('Unknown signal name %s' % sys.argv[2])
  pid = int(open(file).read())
  print 'Killing pid %s with signal %s' % (pid, sys.argv[2])
  os.kill(pid, sig)

def sublist(a, b):
  try:
    i = a.index(b[0])
  except IndexError:
    return True
  except ValueError:
    return False
  return a[i:i+len(b)] == b

def kill():
  parser = argparse.ArgumentParser()
  _ = parser.add_argument
  _('--exe', action='append',
    help="match against executable path")
  _('-f', '--full', action='store_true',
    help="match positional arguments against the full command line")
  _('-F', '--pidfile', action='append',
    help="read PID's from file")
  _('-n', '--name', action='append',
    help="match against process name")
  _('-s', '--signal', required=True,
    help="signal to send to each matched process")
  _('arg', nargs='*',
    help="match against command line")
  args = parser.parse_args()

  try:
    s = args.signal.split('+', 1)
    s = getattr(signal, "SIG" + s[0]) + (len(s) > 1 and int(s[1]))
  except (AttributeError, ValueError):
    parser.error('Unknown signal name %s' % args.signal)

  pid = args.pidfile and [int(open(p).read()) for p in args.pidfile]
  exe = args.exe and map(os.path.realpath, args.exe)

  import psutil
  r = 1
  me = os.getpid()
  for p in psutil.process_iter():
    try:
      if (me == p.pid or
          pid and p.pid not in pid or
          args.name and p.name() not in args.name or
          exe and p.exe() not in exe):
        continue
      cmdline = p.cmdline()
      if cmdline == args.arg if args.full else sublist(cmdline, args.arg):
        p.send_signal(s)
        print 'killed pid %s with signal %s' % (p.pid, args.signal)
        r = 0
    except psutil.Error:
      pass
  return r
