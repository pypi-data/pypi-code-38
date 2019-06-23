from upsert import extract_number, detect_dayfirst

#print(extract_number('1'))
#print(extract_number('1.'))
#print(extract_number('1.9'))
#print(extract_number('1.9%'))
#print(extract_number('$1.9'))
#print(extract_number(' $1.000,900'))
#print(extract_number('+$1.000, 900'))
#print(extract_number('-$1.000,900'))
#print(extract_number(''))
#print(extract_number('a1'))
#print(extract_number('1a'))

print(detect_dayfirst(['1.12.2004', '13.1.2003']))
