from PIL import Image
import urllib2 as urllib
import io
import math
import numpy as np
import sys
import yaml

def download(url,thumbsize):
    fd = urllib.urlopen(url)
    im= Image.open(io.BytesIO(fd.read()))
    im.thumbnail((thumbsize,thumbsize),Image.ANTIALIAS)
    im = im.convert('RGBA')
    return im

# Now we have each image, composite them into a ring

def carousel(data,thumbsize=150,height=768,width=1024):
    composite=Image.new('RGBA',(1024,768),(255,255,255,0))  
    images=dict(
        [[name, download(data[name],thumbsize)] for name in data]
    )
    for index, name in enumerate(images):
        location=(
            int(width* (1+math.cos(2*math.pi*index/len(images))/2)/2-thumbsize/2),
            int(height*(1+math.sin(2*math.pi*index/len(images))/2)/2-thumbsize/2)
            )

        composite.paste(images[name],location)
    return composite

def carousel_action(source,target,env):
    data=yaml.load(open(source[0].path))
    composite=carousel(data["data"],data.get("thumbsize"))
    composite.save(target[0].path,'png')