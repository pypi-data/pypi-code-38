import json
import boto3

def flatten_json(y):
	out = {}

	def flatten(x, name=''):

		if name[:-1] == 'customParameters':
			for a in x:
				out['cp_' + a['group']] = a['item']
		if name[:-1] == 'userparameters':
			for a in x:
				out['up_' + a['group']] = a['item']
		elif name[:-1] == 'externaluserids':
			for a in x:
				out['extid_' + a['type']] = a['id']

		elif type(x) is dict:
			for a in x:
				flatten(x[a], name + a + '_')
		elif type(x) is list:
			i = 0
			for a in x:
				flatten(a, name + str(i) + '_')
				i += 1
		else:
			out[str(name[:-1])] = str(x)

	flatten(y)
	return out


def lower_keys(x):

	if isinstance(x, list):
		return [lower_keys(v) for v in x]
	elif isinstance(x, dict):
		return dict((k.lower(), lower_keys(v)) for k,v in x.items())
	else:
		return x