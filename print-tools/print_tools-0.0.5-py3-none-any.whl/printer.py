import sys
import datetime
import colorful as c

#::: Local Defs :::

#: Get Indentation

def get_indent(indent=0):
	return '\t' * indent

#: Style Print

def style_print(text, indent, style_str):
	ind_text = get_indent(indent)
	print(f"{ind_text}{c.bold(style_str)} {text}")

#: Find Nth

def find_nth(self, string, n):
	if len(string) > 1 or ord(string) < sys.maxunicode:
		repl = chr(sys.maxunicode) * len(string)
	else:
		repl = chr(sys.maxunicode - 1)
	return self.replace(string, repl, n - 1).find(string)

#::: PRINTER CLASS :::

class Printer:

	#: Init

	def __init__(self, style='monokai'):
		self.style = style
		if self.style == 'solarized':
			self.colors = ['yellow', 'orange', 'red', 'magenta',
							'violet', 'blue', 'cyan', 'green',
							'fg', 'bg']
		elif self.style == 'monokai':
			self.colors = ['orange', 'magenta', 'purple', 'blue',
							'seagreen', 'green', 'yellow',
							'fg', 'bg']
		self.color_map = {
			'seagreen': 'seaGreen',
		}
		self.mods = ['bold', 'italic', 'underlined', 'reset']
		c.use_style(style)

	#: Print Log

	def log(self, text):
		print(f"{c.bold(datetime.datetime.now().strftime('%m/%d/%Y-%H:%M:%S'))} {text}")

	#: Print Error

	def error(self, text, log=True):
		self.log(f"{c.bold_magenta('ERROR:')} {text}") if log else print(f"{c.bold_magenta('ERROR:')} {text}")

	#: Print Success

	def success(self, text, log=True):
		if self.style == 'monokai':
			self.log(f"{c.bold_seaGreen('SUCCESS:')} {text}") if log else print(f"{c.bold_seaGreen('SUCCESS:')} {text}")
		elif self.style == 'solarized':
			self.log(f"{c.bold_green('SUCCESS:')} {text}") if log else print(f"{c.bold_green('SUCCESS:')} {text}")

	#: Print Arrow

	def arrow(self, text, indent=0):
		style_print(text, indent, '-->')

	#: Print Chevron

	def chevron(self, text, indent=0):
		style_print(text, indent, '>>>')

	#: Print Bullet

	def bullet(self, text, indent=0):
		style_print(text, indent, '•')

	#: Format String

	def format(self, text, format_op='[]', reset=True, ret=False, log=False):
		format_start = format_op[0]
		format_end = format_op[1]
		format_count = text.count(format_start)
		format_ops = []
		for i in range(0, format_count):
			format_ops.append({
				'start': find_nth(text, format_start, i + 1),
				'end': find_nth(text, format_end, i + 1),
				'string': text[find_nth(text, format_start, i + 1):(find_nth(text, format_end, i + 1) + 1)],
				'args': []
				})
			string_args = text[(format_ops[-1]['start'] + 1):format_ops[-1]['end']]
			args = string_args.split(':')
			for arg in args:
				arg = arg.lower()
				on = not 'no_' in arg
				arg = arg.replace('no_', '')
				if any(arg in mod for mod in self.mods):
					if arg == 'reset':
						format_ops[-1]['args'] = [{'type': 'mod', 'arg': arg, 'on': on}] + format_ops[-1]['args']
					else:
						format_ops[-1]['args'].append({'type': 'mod', 'arg': arg, 'on': on})
				elif any(arg.replace('on_', '') in color for color in self.colors):
					color_type = 'fg' if not 'on_' in arg and not 'bg' in arg else 'bg'
					arg = arg.replace('on_', '')
					if arg in self.color_map:
						format_ops[-1]['args'].append({'type': color_type, 'arg': self.color_map[arg], 'on': on})
					else:
						format_ops[-1]['args'].append({'type': color_type, 'arg': arg, 'on': on})
		for i in range(0, len(format_ops)):
			format_str = ''
			var_check = False
			for x in range(0, len(format_ops[i]['args'])):
				if not format_ops[i]['args'][x]['on']:
					if format_ops[i]['args'][x]['type'] == 'mod':
						format_str += '{' + f"c.no_{format_ops[i]['args'][x]['arg']}" + '}'
					elif format_ops[i]['args'][x]['type'] in ['fg', 'bg']:
						format_str += '{' + f"c.close_{format_ops[i]['args'][x]['type']}_color" + '}'
				else:
					if not var_check:
						format_str += '{c.'
						var_check = True
					if format_ops[i]['args'][x]['type'] == 'background':
						format_str += 'on_'
					format_str += format_ops[i]['args'][x]['arg']
					if x != len(format_ops[i]['args']) - 1:
						format_str += '_'
					else:
						format_str += '}'
			text = text.replace(format_ops[i]['string'], format_str)
		if reset:
			text = text + '{c.reset}'
		if ret:
			return c.format(text)
		else:
			self.log(c.format(text)) if log else print(c.format(text))

#::: END PROGRAM:::
