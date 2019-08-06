import os
import sys
import csv
from random import shuffle

students_file="students.csv"
jtas_file="jtas.csv"
preference_file="prefs.tsv"
actual_capacity={'SL1': 80, 'SL2': 125, 'Basement' : 142 }
capacity={'SL1': 60, 'SL2': 100, 'Basement' : 120 }
roll_to_name={}
jta_name={}

# read the data 
def read_data(students_file,jtas_file):
  global roll_to_name
  global jta_name
  students={}
  with open(students_file) as csvfile: 
    reader = csv.DictReader(csvfile)
    for row in reader:
      if row['Roll No.'] in students :
        print('duplicate ' + row['Roll No.'])
      #students[row['Roll No.'].lower()]=row['Name']
      students[row['Roll No.'].upper()]=row['Name']
      roll_to_name[row['Roll No.'].upper()]=row['Name']
  
  jtas={}
  with open(jtas_file) as csvfile: 
    reader = csv.DictReader(csvfile)
    for row in reader:
      jtas[row['Roll number'].upper()]=row['Name']
      jta_name[row['Roll number'].upper()]=row['Name']
  english=set()
  others=set()
  prefs={}
  with open(preference_file) as tsv :
    flag=1
    for line in csv.reader(tsv, delimiter='\t'):
      if flag == 1:
        flag=0
        continue
      roll=line[1]
      roll=roll.upper()
      language=line[4]
      if roll in prefs :
        prefs[roll]=prefs[roll]+language
      else :
        prefs[roll]=language
  for roll,language in prefs.items():
    if "english" in language.lower() or language.strip()=="":
      english.add(roll)
    else :
      others.add(roll)
  #print(len(english))
  #print(len(others))
  return [students,jtas,english,others]

def map_st_to_jta(wed,wed_jtas):
  wed_st_jta={}
  i=0
  j=0
  while i<len(wed) :
    wed_st_jta[wed[i]]=wed_jtas[j]
    i+=1
    j+=1
    if j==len(wed_jtas) :
      j=0
  return wed_st_jta

def map_st_to_jta_tue(sl1_sl2, base, jtas):  
  base_number=len(base)
  upper_number=len(sl1_sl2)
  upper_jtas_count=len(jtas)*upper_number//(base_number+upper_number)
  upper_jtas=jtas[0:upper_jtas_count]
  base_jtas=jtas[upper_jtas_count:]
  tue_st_jta={}
  i=0
  j=0
  while i< len(sl1_sl2):
    tue_st_jta[sl1_sl2[i]]=upper_jtas[j]
    i+=1
    j+=1
    if j==len(upper_jtas):
      j=0
  i=0
  j=0
  while i<len(base):
    tue_st_jta[base[i]]=base_jtas[j]
    i+=1
    j+=1
    if j==len(base_jtas):
      j=0
  return tue_st_jta

def map_jta_to_st(a):
  ret={}
  for student,jta in a.items():
    if jta in ret :
      ret[jta].append(student)
    else :
      ret[jta]=[student]
  return ret

def map_to_lab(a):
  global capacity 
  total=0
  total_seats=capacity['Basement']+capacity['SL1']+capacity['SL2']
  for jta,students in a.items():
    total+=len(students)
  jta_to_lab={}
  acc=0
  for jta,students in a.items():
    acc+=len(students)
    if acc*total_seats < total*capacity['SL1'] :
      jta_to_lab[jta]='SL1'
    elif acc*total_seats < total*(capacity['SL1']+capacity['SL2']):
      jta_to_lab[jta]='SL2'
    else :
      jta_to_lab[jta]='Basement'
  return jta_to_lab 

def map_to_lab_tue(a,base):
  global capacity 
  jta_to_lab={}
  upper_jtas={}
  total_students=0
  s=set()
  for st in base :
    s.add(st)
  for jta,students in a.items() :
    if students[0] in s :
      jta_to_lab[jta]='Basement'
    else :
      upper_jtas[jta]=students 
      total_students+=len(students)
  acc=0
  total_seats=capacity['SL1']+capacity['SL2']
  for jta,students in upper_jtas.items():
    acc+=len(students)
    if acc*total_seats < total_students*capacity['SL1'] :
      jta_to_lab[jta]='SL1'
    else:
      jta_to_lab[jta]='SL2'
  return jta_to_lab 

def write_to_file(a,a_lab,b,b_lab, c, c_lab):
  global roll_to_name
  with open('mapping.csv','w+') as file :
    file.write("Serial No. , Roll No. , Name , Day , Venue , JTA Name")
    file.write('\n')
    ind=1
    for jta,students in a.items() :
      file.write(str(ind)+","+students[0]+","+roll_to_name[students[0]]+","+"Tuesday,"+a_lab[jta]+","+jta_name[jta])
      file.write('\n')
      ind+=1
      for i in range(1,len(students)):
        file.write(str(ind)+","+students[i]+","+roll_to_name[students[i]]+","+","+",")
        file.write('\n')
        ind+=1
    for jta,students in b.items() :
      file.write(str(ind)+","+students[0]+","+roll_to_name[students[0]]+","+"Wednesday,"+b_lab[jta]+","+jta_name[jta])
      file.write('\n')
      ind+=1
      for i in range(1,len(students)):
        file.write(str(ind)+","+students[i]+","+roll_to_name[students[i]]+","+","+",")
        file.write('\n')
        ind+=1
    for jta,students in c.items() :
      file.write(str(ind)+","+students[0]+","+roll_to_name[students[0]]+","+"Thursday,"+c_lab[jta]+","+jta_name[jta])
      file.write('\n')
      ind+=1
      for i in range(1,len(students)):
        file.write(str(ind)+","+students[i]+","+roll_to_name[students[i]]+","+","+",")
        file.write('\n')
        ind+=1

def split_students(students,others,jtas_dict,jtas_to_use):
  total=len(students)
  a={'Basement': [], 'SL1' :[], 'SL2': []}
  b={'Basement': [], 'SL1' :[], 'SL2': []}
  c={'Basement': [], 'SL1' :[], 'SL2': []}
  for roll in others :
    if roll not in students :
      print('Roll number not registered but submitted language preference : ' + roll)
      continue
    name=students[roll]
    del students[roll]
    a['Basement'].append(roll) 
  tue=[]
  wed=[]
  thu=[]
  a_cnt=len(others)
  b_cnt=0
  c_cnt=0
  for roll,name in students.items() :
    d=int(roll[-3:])
    if d%3==0 and a_cnt*3 < total+10:
      tue.append(roll)
      a_cnt+=1
      continue
    if d%3==1 and b_cnt*3 < total + 10:
      wed.append(roll)
      b_cnt+=1
      continue
    if d%3==2 and c_cnt*3 < total + 10 :
      thu.append(roll)
      c_cnt+=1
      continue
    if a_cnt*3 < total + 10 :
      tue.append(roll)
      a_cnt+=1
    elif b_cnt* 3 < total +10 :
      wed.append(roll)
      b_cnt+=1
    else :
      thu.append(roll)
      c_cnt+=1
  #print(len(a['Basement']))
  #print(len(tue))
  JTAs=list(jtas_dict.keys())
  jtas=JTAs[0:jtas_to_use]
  shuffle(jtas)
  shuffle(tue)
  shuffle(wed)
  shuffle(thu)
  total_jtas=len(jtas)//3
  tue_jtas=jtas[0:total_jtas]
  wed_jtas=jtas[total_jtas:2*total_jtas]
  thu_jtas=jtas[2*total_jtas:]
  wed_st_jta=map_st_to_jta(wed,wed_jtas)
  thu_st_jta=map_st_to_jta(thu,thu_jtas)
  tue_st_jta=map_st_to_jta_tue(tue,a['Basement'],tue_jtas)
  tue_jta_st=map_jta_to_st(tue_st_jta)
  wed_jta_st=map_jta_to_st(wed_st_jta)
  thu_jta_st=map_jta_to_st(thu_st_jta)
  wed_jta_to_lab=map_to_lab(wed_jta_st)
  thu_jta_to_lab=map_to_lab(thu_jta_st)
  tue_jta_to_lab=map_to_lab_tue(tue_jta_st,a['Basement'])
  write_to_file(tue_jta_st,tue_jta_to_lab,wed_jta_st,wed_jta_to_lab,thu_jta_st,thu_jta_to_lab)
  print("left jtas -> ")
  for jta in JTAs[jtas_to_use:]:
    print(jta+" "+jtas_dict[jta])

def process():
  [students,jtas,english,others]=read_data(students_file,jtas_file)
  print('There are '+str(len(students)) + ' students and ' + str(len(jtas)) + ' jtas')
  print('How many jtas should be used for mapping ? Enter a number below : ')
  jtas_to_use=int(input())
  x=split_students(students,others,jtas,jtas_to_use)

process()


