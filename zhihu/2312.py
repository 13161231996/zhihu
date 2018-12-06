import re
pattern = re.compile(r'([\u4e00-\u9fa5, ]{1})\s+([\u4e00-\u9fa5, ]{1})')
f2 = open('new.txt','w',encoding='UTF-8')
with open('text.txt','r+',encoding='UTF-8') as f:
    str = f.readline()
    while str:
        str2 = pattern.sub(r'\1\2', str)
        str2 = str2.strip()+"\n"
        f2.write(str2)
        str = f.readline()
f2.close()
