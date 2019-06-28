from geoalchemy2.types import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy.sql.functions import Function as sql_function

def get_info(obj):
	if not isinstance(obj,dict): obj=obj.__dict__
	out_info=dict()
	for k,v in obj.items():
		if k[0]=='_': continue
		elif type(v) in [WKBElement,sql_function]: v=to_shape(v).wkt
		out_info[k]=v
	# info={k:v for k,v in self.__dict__.items() if (k[0]!='_' and not isinstance(v,WKBElement))}
	return out_info

def main():
	pass

if __name__=='__main__':
	main()
