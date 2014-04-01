import os,sys
import yaml
import urllib2 as urllib
import subprocess
import shutil

import carousel
import tidybib

def wget_each_url(target,source,env):
    data=yaml.load(open(source[0].path))
    for target,source in zip(target,data.values()):
        content=urllib.urlopen(source)
        result=open(target.path,'w')
        result.write(content.read())
        result.close()

def yaml_emitter(target,source,env):
    data=yaml.load(open(source[0].path))
    # If there are multiple targets, just use the first for working out where to put things
    targets=[os.path.join(os.path.dirname(target[0].path),fname) for fname in data.keys()]
    return targets, source

def browse_each_url(target,source,env):
    data=yaml.load(open(source[0].path))
    for target,source in zip(target,data.values()):
        subprocess.call(["webkit2png","--delay=1","-s1","-F","-otemp", source])
        shutil.move("temp-full.png",target.path)  

SlideStyle = "night"
SlideSyntaxHighlightingStyle = "zenburn"
SlideExtraCSSFiles = []
SlideTemplateName = False

def add_builders(env): 
    from sys import executable
    from SCons.Util import WhereIs

    default_path = ['/usr/local/bin', '/usr/bin']
    # If pandoc is not found with the default path which contains
    # OS env path try with some sensible default. Workaround for limited path when using
    # Puppet from Cron.
    pandoc_exec = WhereIs('pandoc')
    if pandoc_exec == None
        pandoc_exec = WhereIs('pandoc', path=default_path)

    dot_exec = WhereIs('dot')
    if dot_exec == None
        dot_exec = WhereIs('dot', path=default_path)
    assets = ' '.join([ "--css=assets/" + str(x) for x in SlideExtraCSSFiles ])
    template = ("--template=" + SlideTemplateName) if SlideTemplateName else ' '

    env.Append(BUILDERS={
    
        'WSD':env.Builder(
        	action=['{0} -m websequence --style magazine '.format(executable) +
        		'--format=png --in $SOURCE --out $TARGET'],
        suffix='.png',
        src_suffix='.wsd'),
        
        'Dot':env.Builder(
        	action=["{0} -Tpng $SOURCE -o $TARGET".format(dot_exec)], 
    		suffix=".png", 
    		src_suffix=".dot"),
    	
    	'Neato':env.Builder(
    		action=["neato -Tpng $SOURCE -o $TARGET"], 
    		suffix=".png", 
    		src_suffix=".dot"),
    	
    	'Python':env.Builder(
    		action=["{0} $SOURCE $TARGET".format(executable)],
        	suffix='.png',
        	src_suffix='.py'),
        
        'Shell':env.Builder(
        	action=['bash $SOURCE $TARGET'],
        	suffix='.png',
        	src_suffix='.sh'),
        
        'Wget':env.Builder(
        	action=wget_each_url,
        	emitter=yaml_emitter),
    
        'PandocSlides': env.Builder(
            generator = lambda source, target, env, for_signature: (
                           '{pandoc} -t revealjs -s -V theme={theme}'        \
                           ' --css=assets/{theme}.css'                       \
                           ' --css=assets/{theme}-ucl-overlay.css'           \
                           ' --css=assets/local_styles.css'                  \
                           ' {template} '                                    \
                           ' {assets} '                                      \
                           ' --default-image-extension=png'                  \
                           ' --highlight-style={highlight}'                  \
                           ' --mathjax'                                      \
                           ' -V revealjs-url=http://lab.hakim.se/reveal-js/' \
                           ' {sources} '                                     \
                           '-o {output}'.format(
                             pandoc    = pandoc_exec,
                             theme     = SlideStyle, 
                             template  = template,
                             assets    = assets,
                             highlight = SlideSyntaxHighlightingStyle,
                             sources   = ' '.join([str(x) for x in source]), 
                             output    = target[0]
                           )
            )
        ),
    
        'PandocLatex':env.Builder(
        	action=['{0} --template=report '.format(pandoc_exec) +
        			'-V documentclass=scrartcl ' +
        			'-V links-as-notes ' +
        			'--filter pandoc-citeproc ' +
        			'--default-image-extension=png '+
        			'-V linkcolor="uclmidgreen" ' +
        			'--number-sections $SOURCES -o $TARGET'],
        	),
    
        'PandocJekyll':env.Builder(
        	action=['{0} -thtml -s --template=jekyll'.format(pandoc_exec)+
        			' --default-image-extension=png'+
        			' --mathjax '+
        			' $SOURCES -o $TARGET']
        	),
        
              'Browse':env.Builder(action=browse_each_url, emitter=yaml_emitter),
        
        'Carousel':env.Builder(
        	action=carousel.carousel_action, 
            suffix=".png",
            src_suffix=".carousel"),
        
        'Cp':env.Builder(
        	action=["cp $SOURCES $TARGET"]
        	),
    
        'R': env.Builder(
        	action=['RScript $SOURCE $TARGET']
        	), # Assume R script expects dest file as first clarg
    
        'Bib': env.Builder(
        	action=tidybib.tidybib_action,
        	suffix=".bib",
        	source_suffix=".zbib"
        )
          })
    
    
    env['ENV']["PYTHONPATH"]=sys.path
