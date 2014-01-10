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

	env.Append(BUILDERS={

		'WSD':env.Builder(
			action=['python -m websequence --style magazine '+
				'--format=png --in $SOURCE --out $TARGET'],
	    	suffix='.png',
	    	src_suffix='.wsd'),
	    
	    'Dot':env.Builder(
	    	action=["dot -Tpng $SOURCE -o $TARGET"], 
			suffix=".png", 
			src_suffix=".dot"),
		
		'Neato':env.Builder(
			action=["neato -Tpng $SOURCE -o $TARGET"], 
			suffix=".png", 
			src_suffix=".dot"),
		
		'Python':env.Builder(
			action=["python $SOURCE $TARGET"],
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
            generator = lambda source,target,env,for_signature: (
                         'pandoc -t revealjs -s -V theme=%s'+
                         ' --css=assets/%s.css'             +
                         ' --css=assets/%s-ucl-overlay.css'     +
                         ' --css=assets/local_styles.css'   +
                         ' %s '                             +
                         ' %s '                             +
                         ' --default-image-extension=png'   +
                         ' --highlight-style=%s'            +
                         ' --mathjax'                       +
                         ' -V revealjs-url=http://lab.hakim.se/reveal-js/'+
                         ' %s '                             +
                         '-o %s' ) %
                         ( SlideStyle, SlideStyle, SlideStyle,
                           ("--template="+SlideTemplateName if SlideTemplateName else ' '),
                           ' '.join([ "--css=assets/%s" % x for x in SlideExtraCSSFiles ]),
                           SlideSyntaxHighlightingStyle,
                           ' '.join([str(x) for x in source]), 
                           target[0]
                           )
            ),
 
		'PandocLatex':env.Builder(
			action=['pandoc --template=report '+
					'-V documentclass=scrartcl ' +
					'-V links-as-notes ' +
					'--filter pandoc-citeproc ' +
					'--default-image-extension=png '+
					'-V linkcolor="uclmidgreen" ' +
					'--number-sections $SOURCES -o $TARGET'],
			),

		'PandocJekyll':env.Builder(
			action=['pandoc -thtml -s --template=jekyll'+
					' --default-image-extension=png'+
					' --mathjax '+
					' $SOURCES -o $TARGET']
			),
		
		'Browse':env.Builder(
			action=browse_each_url,
	        emitter=yaml_emitter),
		
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
