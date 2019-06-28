from .style import style

def pull_check_display_result(result):
  all_required_msg = '\nall required images: ('+str(len(result['images']))+')'
  if(result['error']):
    print(style.RED(all_required_msg))
  else:
    print(style.GREEN(all_required_msg))

  for image, state in result['images'].items():
    msg = '- '+image+' ('+state+')'
    if(state == 'ok'):
      print(style.GREEN(msg))
    elif(state == 'pulled'):
      print(style.CYAN(msg))
    else:
      print(style.RED(msg))