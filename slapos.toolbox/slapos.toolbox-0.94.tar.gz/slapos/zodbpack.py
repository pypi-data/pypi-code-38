import ZODB.FileStorage
import ZODB.serialize
import argparse
import time
import traceback

def run():
  now = time.time()
  parser = argparse.ArgumentParser(description='ZODB offline packer')
  parser.add_argument('files', metavar='F', type=str, help='Files to pack',
    nargs='+')
  parser.add_argument('--days', '-d', type=float,
    help='Amount of days, from now, to pack')

  args = parser.parse_args()

  point = now - (3600 * 24 * args.days)

  print 'Now is %s' % time.asctime(time.localtime(now))
  print 'Will pack until %s' % time.asctime(time.localtime(point))
  failures = 0
  for f in args.files:
    b = time.time()
    print 'Trying to pack %r' % f
    try:
      pack(point, f)
    except Exception:
      print 'Failed to pack %r:' % f
      traceback.print_exc()
      failures += 1
    print 'Finished %s in %.3fs' % (f, time.time() - b)
  if failures:
    print 'Failed files: %s' % failures
    return failures
  else:
    print 'All files sucessfully packed.'
    return 0

def pack(point, f):
  ZODB.FileStorage.FileStorage(f).pack(point, ZODB.serialize.referencesf)
