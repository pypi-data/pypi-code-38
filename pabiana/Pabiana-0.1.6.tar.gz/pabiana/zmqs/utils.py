from typing import Any, Callable, Iterable, Dict, List, Union

import zmq

Socket = zmq.sugar.socket.Socket
Context = zmq.sugar.context.Context
Poller = zmq.sugar.poll.Poller
Frame = zmq.sugar.frame.Frame


def decoder(rcvd: Iterable[bytes]) -> List[str]:
	result = [x.decode('utf-8') for x in rcvd]
	if result[0] == '':
		result[0] = None
	return result


def caller(*args: Union[Dict[Callable, Dict[str, Any]], Iterable[Callable]], **kwargs):
	for functions in args:
		if isinstance(functions, Dict):
			for func in functions:
				func(**functions[func])
		else:
			for func in functions:
				func()
