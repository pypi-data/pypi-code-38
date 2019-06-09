import sys
from .run_shell import run_shell

def api_config_prune(immutable_name):
  cmd = '''IMMUTABLE_RM=$(docker config ls
      | egrep " %s_[0-9a-f]{26} "
      | grep --invert-match -e "_%s "
      |  awk '{print $1}') && [ "$IMMUTABLE_RM" != '' ] && docker config rm "$IMMUTABLE_RM"
  ''' % (immutable_name, immutable_fullname)
  process = run_shell(cmd)
  if(process.returncode != 0):
      sys.exit(process.returncode)