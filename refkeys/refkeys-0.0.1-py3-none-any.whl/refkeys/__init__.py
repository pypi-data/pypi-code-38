import math
import random
import os

def get_ref_key(number):
  base=random.randint(2,7)
  log_2_number=math.log(number,base)
  int_log_2_number=int(log_2_number+0.5)
  ref=random.randint(0,int_log_2_number)
  if base**ref > number:
    ref=ref-1
  key=number-base**ref
  return (ref,key,base)

def get_keys(keys):
  cnt=0
  person1=""
  person2=""
  base=""
  for key in keys:
    tmp_num=ord(key)
    ref_key=get_ref_key(tmp_num)
    ref=ref_key[0]
    key=ref_key[1]
    base=base+chr(ref_key[2])
    if cnt%2==0:
        person1=person1+chr(ref)
        person2=person2+chr(key)
    else:
        person1=person1+chr(key)
        person2=person2+chr(ref)
    cnt=cnt+1
  return [person1,person2,base]

def get_keyfiles(keys,person1_name,person2_name,person3_name="",pd="./"):

  result=get_keys(keys)
  if person3_name=="":
    person3_name="system"+person1_name+person2_name
    ord_list=sorted([person1_name,person2_name])
    person1_name,person2_name=ord_list[0],ord_list[1]
  else:
    ord_list=sorted([person1_name,person2_name,person3_name])
    person1_name,person2_name,person3_name=ord_list[0],ord_list[1],ord_list[2]
  person1_file=open(pd+person1_name+".refkeys","w")
  person2_file=open(pd+person2_name+".refkeys","w")
  person3_file=open(pd+person3_name+".refkeys","w")
  person1_file.write( "\n".join(list(result[0]))+"\n")
  person2_file.write("\n".join(list(result[1]))+"\n")
  person3_file.write("\n".join(list(result[2]))+"\n")
  person1_file.close()
  person2_file.close()
  person3_file.close()
  try:
    e=combine_keyfiles(person1_name,person2_name,person3_name="")
  except:
    os.system("rm "+pd+person1_name+".refkeys "+pd+person2_name+".refkeys "+pd+person3_name+".refkeys")
    if person3_name[:6]=="system":
      person3_name=""
    get_keyfiles(keys,person1_name,person2_name,person3_name)
    return

def get_ord(person_elem):
  if len(person_elem)>0:
    return ord(person_elem)
  else:
    return ord("")

def combine_keys(person1,person2,base):
  union_key=""
  person1_num=len(person1)
  person2_num=len(person2)
  num_keys=person1_num
  cnt=0
  while cnt < num_keys:
    key_person1=get_ord(person1[cnt])
    key_person2=get_ord(person2[cnt])
    base_num=int(get_ord(base[cnt]))
    if cnt%2==0:
      key=(base_num**int(key_person1))+int(key_person2)
    else:
      key=(base_num**int(key_person2))+int(key_person1)
    union_key=union_key+chr(key)
    cnt=cnt+1
  return union_key

def get_list(person):
  person_list=[]
  for elem in person:
    if elem=="\n":
      person_list.append("")
    else:
      person_list.append(elem[:-1])
  return person_list

def combine_keyfiles(person1_name,person2_name,person3_name=""):
  ord_list=[person1_name,person2_name]
  ord_list=sorted(ord_list)
  if person3_name!="":
    ord_list.append(person3_name)
    ord_list=sorted(ord_list)
    person3_name=ord_list[2]
  else:
    person3_name="system"+ord_list[0]+ord_list[1]
  person1_name=ord_list[0]
  person2_name=ord_list[1]
  person1_file=open(person1_name+".refkeys","r")
  person2_file=open(person2_name+".refkeys","r")
  person3_file=open(person3_name+".refkeys","r")
  person1=person1_file.readlines()
  person2=person2_file.readlines()
  person1_file.close()
  person2_file.close()
  person3=person3_file.readlines()
  person3_file.close()
  person1_list=[]
  list_person1=get_list(person1)
  list_person2=get_list(person2)
  list_person3=get_list(person3)
  union_key=combine_keys(list_person1,list_person2,list_person3)
  return union_key
