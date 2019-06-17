###
# TKG is stand for 3GPP Key Generator
# Which is contains f1-f5 in 35.206, and KASME generation in 33.401
###

# -------- f1 - f5 function based on 3gpp 35.206 -------- #
S = [
 99,124,119,123,242,107,111,197, 48,  1,103, 43,254,215,171,118,
202,130,201,125,250, 89, 71,240,173,212,162,175,156,164,114,192,
183,253,147, 38, 54, 63,247,204, 52,165,229,241,113,216, 49, 21,
  4,199, 35,195, 24,150,  5,154,  7, 18,128,226,235, 39,178,117,
  9,131, 44, 26, 27,110, 90,160, 82, 59,214,179, 41,227, 47,132,
 83,209,  0,237, 32,252,177, 91,106,203,190, 57, 74, 76, 88,207,
208,239,170,251, 67, 77, 51,133, 69,249,  2,127, 80, 60,159,168,
 81,163, 64,143,146,157, 56,245,188,182,218, 33, 16,255,243,210,
205, 12, 19,236, 95,151, 68, 23,196,167,126, 61,100, 93, 25,115,
 96,129, 79,220, 34, 42,144,136, 70,238,184, 20,222, 94, 11,219,
224, 50, 58, 10, 73,  6, 36, 92,194,211,172, 98,145,149,228,121,
231,200, 55,109,141,213, 78,169,108, 86,244,234,101,122,174,  8,
186,120, 37, 46, 28,166,180,198,232,221,116, 31, 75,189,139,138,
112, 62,181,102, 72,  3,246, 14, 97, 53, 87,185,134,193, 29,158,
225,248,152, 17,105,217,142,148,155, 30,135,233,206, 85, 40,223,
140,161,137, 13,191,230, 66,104, 65,153, 45, 15,176, 84,187, 22,
]

x_time = [
  0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30,
 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62,
 64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94,
 96, 98,100,102,104,106,108,110,112,114,116,118,120,122,124,126,
128,130,132,134,136,138,140,142,144,146,148,150,152,154,156,158,
160,162,164,166,168,170,172,174,176,178,180,182,184,186,188,190,
192,194,196,198,200,202,204,206,208,210,212,214,216,218,220,222,
224,226,228,230,232,234,236,238,240,242,244,246,248,250,252,254,
 27, 25, 31, 29, 19, 17, 23, 21, 11,  9, 15, 13,  3,  1,  7,  5,
 59, 57, 63, 61, 51, 49, 55, 53, 43, 41, 47, 45, 35, 33, 39, 37,
 91, 89, 95, 93, 83, 81, 87, 85, 75, 73, 79, 77, 67, 65, 71, 69,
123,121,127,125,115,113,119,117,107,105,111,109, 99, 97,103,101,
155,153,159,157,147,145,151,149,139,137,143,141,131,129,135,133,
187,185,191,189,179,177,183,181,171,169,175,173,163,161,167,165,
219,217,223,221,211,209,215,213,203,201,207,205,195,193,199,197,
251,249,255,253,243,241,247,245,235,233,239,237,227,225,231,229
]

# f1(key, rand, sqn, amf, op, mac_a)
# key(list of int), length 16
# rand(list of int), length 16
# sqn(list of int), length 6
# amf(list of int), length 2
# op(list of int), length 16
# mac_a(list of int), length 8
# opc(list of int), length 6, it is an optional parameter, if opc is set, f1 function will never use op parameter, and use opc to instead.
# mac_a is used as a return value.
def f1(key, rand, sqn, amf, op, mac_a, opc = []):
# f1 function will return a mac_a value.
	round_keys=rijndael_key_schedule(key)
	
	op_c = [0 for col in range(16)]
	temp = [0 for col in range(16)]
	in1 = [0 for col in range(16)]
	out1 = [0 for col in range(16)]
	rijndael_input = [0 for col in range(16)]
	
	if opc == None or opc==[]:
		compute_opc(op, op_c, round_keys)
	else:
		op_c = opc
	
	i = 0
	while i<16:
		rijndael_input[i] = rand[i] ^ op_c[i]
		i += 1
	rijndael_encrypt(rijndael_input, temp, round_keys)
	
	i = 0
	while i<6:
		in1[i] = sqn[i]
		in1[i+8] = sqn[i]
		i += 1
	i = 0
	while i<2:
		in1[i+6] = amf[i]
		in1[i+14] = amf[i]
		i += 1

	i = 0
	while i<16:
		rijndael_input[(i+8)%16] = in1[i] ^ op_c[i]
		i += 1
  
	i = 0
	while i<16:
		rijndael_input[i] ^= temp[i]
		i += 1		
	
	rijndael_encrypt(rijndael_input, out1, round_keys)
	i = 0
	while i<16:
		out1[i] ^= op_c[i]
		i += 1		

	i = 0
	while i<8:
		mac_a[i] = out1[i]
		i += 1
		
# f2345(key, rand, op, res, ck, ik , ak)
# key(list of int), length 16
# rand(list of int), length 16
# op(list of int), length 16
# res(list of int), length 8
# ck(list of int), length 16
# ik(list of int), length 16
# ak(list of int), length 6
# opc(list of int), length 6, it is an optional parameter, if opc is set, f2345 function will never use op parameter, and use opc to instead.
# res, ck, ik, and ak are used as return values.
def f2345(key, rand, op, res, ck, ik , ak, opc = []):
	round_keys=rijndael_key_schedule(key)
	
	op_c = [0 for col in range(16)]
	temp = [0 for col in range(16)]
	out = [0 for col in range(16)]
	rijndael_input = [0 for col in range(16)]
	
	if opc == None or opc==[]:
		compute_opc(op, op_c, round_keys)
	else:
		op_c = opc
	
	i = 0
	while i<16:
		rijndael_input[i] = rand[i] ^ op_c[i]
		i += 1
	rijndael_encrypt(rijndael_input, temp, round_keys)
	
	# calc res and ak
	i = 0
	while i<16:
		rijndael_input[i] = temp[i] ^ op_c[i]
		i += 1	
	rijndael_input[15] ^= 1
	rijndael_encrypt(rijndael_input, out, round_keys)

	i = 0
	while i<16:
		out[i] ^= op_c[i]
		i += 1		
		
	i = 0
	while i<8:
		res[i] = out[i+8]
		i += 1			

	i = 0
	while i<6:
		ak[i] = out[i]
		i += 1			
  
	# calc ck
	i = 0
	while i<16:
		rijndael_input[(i+12)%16] = temp[i] ^ op_c[i]
		i += 1	
	rijndael_input[15] ^= 2
	rijndael_encrypt(rijndael_input, out, round_keys)

	i = 0
	while i<16:
		out[i] ^= op_c[i]
		i += 1			

	i = 0
	while i<16:
		ck[i] = out[i]
		i += 1			

	# calc ik
	i = 0
	while i<16:
		rijndael_input[(i+8)%16] = temp[i] ^ op_c[i]
		i += 1	
	rijndael_input[15] ^= 4
	rijndael_encrypt(rijndael_input, out, round_keys)

	i = 0
	while i<16:
		out[i] ^= op_c[i]
		i += 1			

	i = 0
	while i<16:
		ik[i] = out[i]
		i += 1	
	
# f1star(key, rand, sqn, amf, op, mac_s)
# key(list of int), length 16
# rand(list of int), length 16
# sqn(list of int), length 6
# amf(list of int), length 2
# mac_s(list of int), length 8
# opc(list of int), length 6, it is an optional parameter, if opc is set, f1star function will never use op parameter, and use opc to instead.
# mac_s is used as a return value.	
def f1star(key, rand, sqn, amf, op, mac_s, opc = []):
# f1star function will return a mac_s value.
	round_keys=rijndael_key_schedule(key)
	
	op_c = [0 for col in range(16)]
	temp = [0 for col in range(16)]
	in1 = [0 for col in range(16)]
	out1 = [0 for col in range(16)]
	rijndael_input = [0 for col in range(16)]
	
	if opc == None or opc==[]:
		compute_opc(op, op_c, round_keys)
	else:
		op_c = opc
	
	i = 0
	while i<16:
		rijndael_input[i] = rand[i] ^ op_c[i]
		i += 1
	rijndael_encrypt(rijndael_input, temp, round_keys)
	
	i = 0
	while i<6:
		in1[i] = sqn[i]
		in1[i+8] = sqn[i]
		i += 1
	i = 0
	while i<2:
		in1[i+6] = amf[i]
		in1[i+14] = amf[i]
		i += 1

	i = 0
	while i<16:
		rijndael_input[(i+8)%16] = in1[i] ^ op_c[i]
		i += 1
  
	i = 0
	while i<16:
		rijndael_input[i] ^= temp[i]
		i += 1		
	
	rijndael_encrypt(rijndael_input, out1, round_keys)
	i = 0
	while i<16:
		out1[i] ^= op_c[i]
		i += 1		

	i = 0
	while i<8:
		mac_s[i] = out1[i+8]
		i += 1
	
# f5star(key, rand, op, ak)
# key(list of int), length 16
# rand(list of int), length 16
# op(list of int), length 16
# ak(list of int), length 6
# opc(list of int), length 6, it is an optional parameter, if opc is set, f5star function will never use op parameter, and use opc to instead.
# ak is used as return value.
def f5star(key, rand, op, ak, opc = []):
	round_keys=rijndael_key_schedule(key)
	
	op_c = [0 for col in range(16)]
	temp = [0 for col in range(16)]
	out = [0 for col in range(16)]
	rijndael_input = [0 for col in range(16)]
	
	if opc == None or opc==[]:
		compute_opc(op, op_c, round_keys)
	else:
		op_c = opc
	
	i = 0
	while i<16:
		rijndael_input[i] = rand[i] ^ op_c[i]
		i += 1
	rijndael_encrypt(rijndael_input, temp, round_keys)
	
	i = 0
	while i<16:
		rijndael_input[(i+4)%16] = temp[i] ^ op_c[i]
		i += 1
	rijndael_input[15] ^= 8
	rijndael_encrypt(rijndael_input, out, round_keys)
	
	i = 0
	while i<16:
		out[i] ^= op_c[i]
		i += 1
		
	i = 0
	while i<6:
		ak[i] = out[i]
		i += 1
		
# compute_opc(op, opc, round_keys)
# op(list of int), length 16
# opc(list of int), length 16
# round_keys(three-dimensional array, shape is [11][4][4])
# opc is used as a return value.
def compute_opc(op, opc, round_keys):
	i = 0
	rijndael_encrypt(op, opc, round_keys)
	while i<16:
		opc[i] ^= op[i]
		i += 1

# rijndael_key_schedule(key)		
# key(list of int), length 16
# this function will return a round_keys.
def rijndael_key_schedule(key):
	#round_keys is a array with shape [11][4][4].
	round_keys=a=[[[0 for col in range(4)] for row in range(4)]for height in range(11)]
	i = 0
	while i<16:
		round_keys[0][i&0x03][i>>2] = key[i]
		i += 1
		
	round_const = 1
	i = 1
	while i<11:
		round_keys[i][0][0] = S[round_keys[i-1][1][3]] ^ round_keys[i-1][0][0] ^ round_const
		round_keys[i][1][0] = S[round_keys[i-1][2][3]] ^ round_keys[i-1][1][0]
		round_keys[i][2][0] = S[round_keys[i-1][3][3]] ^ round_keys[i-1][2][0]
		round_keys[i][3][0] = S[round_keys[i-1][0][3]] ^ round_keys[i-1][3][0]
		j = 0
		while j<4:
			round_keys[i][j][1] = round_keys[i-1][j][1] ^ round_keys[i][j][0]
			round_keys[i][j][2] = round_keys[i-1][j][2] ^ round_keys[i][j][1]
			round_keys[i][j][3] = round_keys[i-1][j][3] ^ round_keys[i][j][2]
			j += 1
		round_const = x_time[round_const]
		i += 1
	return round_keys
	
# key_add(state, round_keys, round)
# state(two-dimensional array, shape is [4][4])
# round_keys(three-dimensional array, shape is [11][4][4])
# round is integer value.
# state is used as a return value.
def key_add(state, round_keys, round):
	i = 0
	while i<4:
		j = 0
		while j<4:
			state[i][j] ^= round_keys[round][i][j]
			j += 1
		i += 1

# byte_substitution(state)
# state(two-dimensional array, shape is [4][4])
def byte_substitution(state):
	i = 0
	while i<4:
		j = 0
		while j<4:
			state[i][j] = S[state[i][j]]
			j += 1
		i += 1
		
# shift_row(state)
# state(two-dimensional array, shape is [4][4])
def shift_row(state):
	# left rotate row 1 by 1 
	temp = state[1][0]
	state[1][0] = state[1][1]
	state[1][1] = state[1][2]
	state[1][2] = state[1][3]
	state[1][3] = temp

	# left rotate row 2 by 2 
	temp = state[2][0];
	state[2][0] = state[2][2];
	state[2][2] = temp;
	temp = state[2][1];
	state[2][1] = state[2][3];
	state[2][3] = temp;

	# left rotate row 3 by 3 */
	temp = state[3][0];
	state[3][0] = state[3][3];
	state[3][3] = state[3][2];
	state[3][2] = state[3][1];
	state[3][1] = temp;
	
# mix_column(state)
# state(two-dimensional array, shape is [4][4])
def mix_column(state):
	# do one column at a time */
	i = 0
	while i<4:
		temp = state[0][i] ^ state[1][i] ^ state[2][i] ^ state[3][i]
		tmp0 = state[0][i]

		# x_time array does multiply by x in GF2^8 
		tmp = x_time[state[0][i] ^ state[1][i]]
		state[0][i] ^= temp ^ tmp;

		tmp = x_time[state[1][i] ^ state[2][i]]
		state[1][i] ^= temp ^ tmp

		tmp = x_time[state[2][i] ^ state[3][i]]
		state[2][i] ^= temp ^ tmp

		tmp = x_time[state[3][i] ^ tmp0]
		state[3][i] ^= temp ^ tmp
		
		i += 1

# rijndael_encrypt(input, output, round_keys)
# input(list of int), length 16		
# output(list of int), length 16
# round_keys(three-dimensional array, shape is [11][4][4])
def rijndael_encrypt(input, output, round_keys):
	state = [[0 for col in range(4)] for row in range(4)]
	i = 0
	while i<16:
		state[i&0x3][i>>2] = input[i]
		i += 1
	
	key_add(state, round_keys, 0)
	
	r = 1
	while r<=9:
		byte_substitution(state)
		shift_row(state)
		mix_column(state)
		key_add(state, round_keys, r)
		r += 1
	
	byte_substitution(state)
	shift_row(state)
	key_add(state, round_keys, r)	
	
	i = 0
	while i<16:
		output[i] = state[i&0x3][i>>2]
		i += 1
	
# -------- f1 - f5 function based on 3gpp 35.206 end -------- #

# -------- autn generation -------- #
# sqn(list of int), length 6
# ak(list of int), length 6
# sqn_xor_ak return a list contains sqn xor ak.
def sqn_xor_ak(sqn, ak):
	r = [0 for col in range(6)]
	i = 0
	while i<6:
		r[i] = sqn[i] ^ ak[i]
		i += 1
	return r

# sqn(list of int), length 6
# ak(list of int), length 6
# amf(list of int), length 2
# mac_a(list of int), length 8
# return a list contains autn value.
def autn(sqn, ak, amf, mac_a):
	autn = [0 for col in range(16)]
	sqnxorak = sqn_xor_ak(sqn, ak)
	i=0
	while i<6:
		autn[i]=sqnxorak[i]
		i+=1
	
	i=0
	while i<2:
		autn[i+6]=amf[i]	
		i+=1
	
	i=0
	while i<8:
		autn[i+8]=mac_a[i]	
		i+=1
	return autn
# -------- autn generation end -------- #

# -------- Kasme generation function based on 3gpp 33.401, 33.220, 24.301 -------- #
import hashlib
import hmac

# mcc_mnc_octs should be in bytes format, 46034 should be encoded as b'\x64\xf0\x43'
# sqnxorak_octs is a bytes object contains sqn xor ak
# ck_octs and ik_octs are ck and ik in bytes format.
# k_asme will return a value contains Kasme, in bytes format.
def k_asme(mcc_mnc_octs, sqnxorak_octs, ck_octs, ik_octs):
	assert(len(mcc_mnc_octs)==3)
	secret=ck_octs+ik_octs
	message=b'\x10'+mcc_mnc_octs+b'\x00\x03'+sqnxorak_octs+b'\x00\x06'
	return hmac.new(secret, message, digestmod=hashlib.sha256).digest()
# -------- Kasme generation function based on 3gpp 33.401, 33.220, 24.301 end -------- #

# -------- Functions are for RAND and SQN generation -------- #
import random
# rand function return a random int list, length is 16.
def rand():
	r = [0 for col in range(16)]
	i = 0
	random.seed(int(random.random()*100000))
	while i<16:
		p = int(random.random()*100000)%256
		r[i] = p
		i += 1
	return r
	
# seq is a int value.
# ind is a int value.
# sqn function return a sqn int list, length is 6.
def sqn(seq, ind):
	r = [0 for col in range(6)]
	seq_base = 0x3FFFFF
	ind_base = 0x1F
	seq_v = seq & seq_base
	ind_v = ind & ind_base
	value = (seq_v<<5) + ind_v
	i = 5
	while i>=0:
		r[i] = value & 0xFF
		value >>= 8
		i -= 1
	return r
# -------- Functions are for RAND and SQN generation end -------- #


# All test data are based on 3gpp 35.207
