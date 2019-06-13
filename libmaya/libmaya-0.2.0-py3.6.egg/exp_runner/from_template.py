import argparse

FLAGS = None


def edit_file(template_name,replace_str,to_str):
    file_name = template_name.replace('.template','')
    with open(template_name) as f:
        newText=f.read().replace(replace_str, to_str)

    with open(file_name, "w") as f:
        f.write(newText)

def edit_file_with_dict(template_name,replace_dict):

    file_name = template_name.replace('.template','')
    with open(template_name) as f:
        newText=f.read()
        
    for replace_str,to_str in replace_dict.items():
        newText = newText.replace(replace_str, to_str)

    with open(file_name, "w") as f:
        f.write(newText)

def rewrite_file(template_name,mode):
    template_name_with_mode = '.'.join((template_name,mode))
    with open(template_name_with_mode) as f:
        newText=f.read()

    with open(template_name, "w") as f:
        f.write(newText)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--template_name',
      type=str)
  parser.add_argument(
      '--replace_str',
      type=str)
  parser.add_argument(
      '--to_str',
      type=str)
  FLAGS, unparsed = parser.parse_known_args()
  edit_file(FLAGS.template_name,FLAGS.replace_str,FLAGS.to_str)