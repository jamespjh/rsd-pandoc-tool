import os
import re
import sys
import string

def tidybib_action(source,target,env):
    zoterobib=file(source[0].path)
    targetbib=file(target[0].path,"w")
    for line in zoterobib.readlines():
        match=re.match("\@(.*)\{(.*),",line)
        if match:
            citetype=match.group(1)
            label=match.group(2)
            groups=re.match("(.*)_(.*)_(.*)",label)
            author=groups.group(1)
            title=groups.group(2)
            year=groups.group(3)
            if author=="":
                author="anon"
            if year=="????":
                year="0000"
            targetbib.write("@%s{%s_%s_%s,\n"%(citetype,author,string.replace(title,":",""),year))
        else:
            targetbib.write(line)