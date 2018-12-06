import re
f0 = open('new.txt','w+',encoding="UTF-8")
pattern = re.compile(u"[a-zA-Z]+\s+[a-zA-Z]+")
with open('text.txt',"r+",encoding='UTF-8') as file:
    strs = file.read()
    entxt = re.findall(pattern,strs)
if (not entxt):
    s = strs.replace(' ','')
    s = s.replace(' ', '')
    f0.write(s)
    f0.close()