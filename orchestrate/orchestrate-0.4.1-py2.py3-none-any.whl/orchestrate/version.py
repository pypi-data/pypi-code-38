from __future__ import print_function


VERSION = '0.4.1'
DOCKER_IMAGE_VERSION = '0.4.0'

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser('Display orchestrate version')
  parser.add_argument('--docker', action='store_true', help='docker image version')
  args = parser.parse_args()
  if args.docker:
    print(DOCKER_IMAGE_VERSION)
  else:
    print(VERSION)
