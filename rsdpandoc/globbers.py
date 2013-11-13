import builders
import os,sys
here = os.path.dirname(os.path.realpath(__file__))
local_assets = os.path.join(here,'assets')
print local_assets

# Allow option to accept checked-in versions of WSD assets
# Because don't want to generate these dynamically in production
have_WSD=True
have_webkit2png=True
have_PIL=True



def assetpath(node,target,env):
	ext='.png'
	[base,current_ext]=os.path.splitext(env.GetBuildPath(node))
	if current_ext in ['.jpg','.svg','.tex','.pdf','.css','.latex','.html']:
		ext=current_ext
	return os.path.join(target,
		os.path.basename(base)+ext)

def asset_glob(source,target,dependants,builder,pattern,env):
	for source in env.Glob(os.path.join(source,pattern)):
		png=builder(assetpath(source,target,env),source)
		env.Depends(dependants,png)


def assets_glob(source,target,dependants,env):
	patterns={
		'*.nto': env.Neato,
		'*.py': env.Python,
		'*.dot': env.Dot,
		'*.sh' : env.Shell,
		'*.wget' : env.Wget,
		'*.png': env.Cp,
		'*.jpg': env.Cp,
		'*.svg': env.Cp,
		'*.css' : env.Cp,
		'*.pdf' : env.Cp,
		'*.R' : env.R
	}
	if env.get("HaveWSD"):
		patterns['*.wsd']=env.WSD
	if env.get("HaveWebKit"):
		patterns['*.browse']=env.Browse
	if env.get("HavePIL"):
		patterns['*.carousel']=env.Carousel
	for pattern in patterns:
		asset_glob(source,target,dependants,patterns[pattern],pattern,env)

def default_reveal_assets(dependants,env):
	assets_glob(local_assets,'reveal/assets',dependants,env)

def default_latex_assets(dependants,env):
	asset_glob(local_assets,'.',dependants,env.Cp,'*.latex',env)
	assets_glob(local_assets,'assets',dependants,env)

def default_web_assets(dependants,env):
	asset_glob(local_assets,'.',dependants,env.Cp,'*.html',env)

def reveal_assets(dependants,env):
	assets_glob('asset_sources','reveal/assets',dependants,env)
	default_reveal_assets(dependants,env)

def latex_assets(dependants,env):
	assets_glob('asset_sources','assets',dependants,env)
	default_latex_assets(dependants,env)

def web_assets(dependants,env):
	assets_glob('asset_sources','web/assets',dependants,env)
	default_web_assets(dependants,env)

def reveal_layout(sources,env):
	slides=env.PandocSlides('reveal/index.html',sources)
	reveal_assets(slides,env)
	return slides

def latex_layout(sources,env):
	document=env.PandocLatex('pdf/document.pdf',sources)
	tex=env.PandocLatex('pdf/document.tex',sources)
	latex_assets([document,tex],env)
	return document

def web_layout(sources,env):
	document=env.PandocJekyll('web/index.html',sources)
	web_assets(document,env)
	return document

def standard_layout(sources,env):
	return[latex_layout(sources,env),reveal_layout(sources,env)]