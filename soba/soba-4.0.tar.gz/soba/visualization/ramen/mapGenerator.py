import json
import math
# data_file must be a object file, that is:
# with open(your file) as datafile:
# map = returnMap(datafile)

def returnMap(data_file, offsety = 0, offsetx = 0):
	data = json.load(data_file)
	corners = {}
	walls = {}
	items = {}
	offsety = offsety
	offsetx = offsetx
	flor = data["floorplan"]
	for k, v in flor["corners"].items():
		corners[k] = {"x":  v["x"]/100 + offsetx,"y": -v["y"]/100 + offsety}
	n = 0
	for k in flor["walls"]:
		walls["idWall" + str(n)] = {"corner1": k["corner1"], "corner2": k["corner2"]}
		n = n + 1
	n = 0
	for k in data["items"]:
		if str(k['item_type']) == '2' or str(k['item_type']) == '9' or str(k['item_type']) == '3':
			pass
		else:
			rotAux =  k["rotation"]
			rot = 'x' if ((rotAux == 0) or (rotAux == math.pi)) else 'y'
			if rot == 'x':
				dx = k["width"]
				dy = k["depth"]
			else:
				dy = k["width"]
				dx = k["depth"]
			items["idItem" + str(n)] = {"itemType": k["item_type"], "pos": { "x": k["xpos"]/100 + offsetx, "y":  -k["zpos"]/100 + offsety}, "dx" :dx/100, "dy" :dy/100}
			items["idItem" + str(n)]["itemName"] = k["item_name"]
			if k["item_name"] == 'Chair':
				items["idItem" + str(n)]["itemName"] = k["item_name"]
				items["idItem" + str(n)]["itemType"] = "poi"
				items["idItem" + str(n)]["id"] = "wp"
				items["idItem" + str(n)]["share"] = False
			if k["item_name"] == 'Red Chair':
				items["idItem" + str(n)]["itemName"] = k["item_name"]
				items["idItem" + str(n)]["itemType"] = "poi"
				items["idItem" + str(n)]["id"] = "sofa"
			if k["item_name"] == 'Open Door':
				items["idItem" + str(n)]["itemName"] = k["item_name"]
				items["idItem" + str(n)]['rot'] = rot
				items["idItem" + str(n)]["itemType"] = "door"
			if k["item_name"] == 'Out Door':
				items["idItem" + str(n)]["itemName"] = "exit" #Clave
				items["idItem" + str(n)]["itemType"] = "poi"
				items["idItem" + str(n)]["id"] = "out"
				items["idItem" + str(n+1000)] = {"pos": { "x": k["xpos"]/100 + offsetx, "y": -k["zpos"]/100 + offsety}, "dx" :dx/100, "dy" :dy/100, 'rot': rot}
				items["idItem" + str(n+1000)]["itemType"] = "door"
			n = n + 1
	jsonResponse = {"corners": corners, "walls": walls, "items": items}
	return jsonResponse