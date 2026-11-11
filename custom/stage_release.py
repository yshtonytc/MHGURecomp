"""Stage only public upstream programs; never read this user's game/save folders."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile
import re

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def download(url,path,digest):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or sha(path)!=digest:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MHGU-Chinese'}),timeout=120) as r,path.open('wb') as f:shutil.copyfileobj(r,f)
    if sha(path)!=digest:raise ValueError('SHA-256 mismatch: '+path.name)

def fetch():
    config=json.loads((ROOT/'custom/upstream.json').read_text())
    headers={'User-Agent':'MHGU-Chinese'}
    if os.environ.get('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/'+config['repository']+'/releases/tags/'+config['tag'],headers=headers),timeout=30) as r:release=json.load(r)
    asset=next(a for a in release['assets'] if a['name']==config['asset'])
    if asset.get('digest')!=config['sha256']:raise ValueError('Upstream release asset changed')
    archive=ROOT/'out/cache'/config['asset'];download(asset['browser_download_url'],archive,config['sha256'].split(':')[1])
    stage=ROOT/'out/base';stage.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        # Strip the official package's one root; retain only program/library/license files.
        names=[n for n in z.namelist() if n.endswith('/mhgurecomp.exe')]
        if len(names)!=1:raise ValueError('Unexpected official package layout')
        prefix=names[0].removesuffix('mhgurecomp.exe')
        for entry in z.infolist():
            if not entry.filename.startswith(prefix):continue
            relative=entry.filename[len(prefix):]
            if not relative or entry.is_dir():continue
            p=Path(relative)
            if p.is_absolute() or '..' in p.parts or ':' in relative or '\\' in relative:raise ValueError('Unsafe archive path')
            allowed=(len(p.parts)==1 and (p.suffix.lower() in ('.exe','.dll') or p.name=='pipelines.list')) or p.parts[0]=='licenses'
            if not allowed:continue
            target=stage/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(entry))
    print('Verified stock program package:',config['tag'])

def package():
    config=json.loads((ROOT/'custom/upstream.json').read_text());base=ROOT/'out/base';built=ROOT/'build'
    # Neither the compiler nor the archive step sees a personal dump or save.
    if (ROOT/'generated').exists():raise ValueError('Do not publish from a worktree containing generated game code')
    identity=(ROOT/'obj/gamelib.id').read_text().strip()
    if not re.fullmatch('[0-9a-f]{16}',identity) or identity.encode()+b'\0' not in (base/'mhgugame.dll').read_bytes():
        raise ValueError('Custom runtime and stock program library IDs differ')
    # Only the host runtime and updater are compiled locally. The library comes
    # unchanged from the public official release, never from the player's folder.
    for name in ('mhgurecomp.exe','mhgurecomp-updater.exe'):
        if not (built/name).is_file():raise ValueError('Missing compiled host program: '+name)
        shutil.copy2(built/name,base/name)
    for file in built.glob('*.dll'):
        if file.name!='mhgugame.dll':shutil.copy2(file,base/file.name)
    if (built/'licenses').exists():shutil.copytree(built/'licenses',base/'licenses',dirs_exist_ok=True)
    font=json.loads((ROOT/'custom/font.json').read_text())
    for name,info in font['files'].items():download(info['url'],ROOT/'out/cache'/name,info['sha256'])
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    face=TTFont(ROOT/'out/cache/NotoSansSC[wght].ttf');face=instantiateVariableFont(face,{'wght':400},inplace=True)
    destination=base/'localization/fonts';destination.mkdir(parents=True,exist_ok=True)
    face.save(destination/'NotoSansSC-Regular.ttf')
    shutil.copy2(ROOT/'out/cache/OFL.txt',base/'licenses/NotoSansSC-OFL.txt')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    (base/'CUSTOM-BUILD.json').write_text(json.dumps({'repository':config['custom_repository'],'commit':commit,
        'upstream':config,'font':font,'gamelib_id':identity,
        'gamelib_identity_validation':json.loads((ROOT/'out/gamelib-compatible.json').read_text()),
        'game_library_sha256':sha(base/'mhgugame.dll'),
        'files':{p.relative_to(base).as_posix():sha(p) for p in base.rglob('*') if p.is_file() and p.name!='CUSTOM-BUILD.json'}},indent=2),encoding='utf-8')
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    subprocess.run(['git','archive','--format=zip','--output',str(out/'MHGU-Chinese-Source.zip'),'HEAD'],cwd=ROOT,check=True)
    archive=out/('Windows-MHGURecomp.'+config['custom_version']+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in base.rglob('*'):
            if p.is_file():z.write(p,'MHGURecomp/'+p.relative_to(base).as_posix())
    (out/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in out.glob('*.zip')),encoding='utf-8')
    print('Custom release:',archive)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('fetch','package'));a=p.parse_args()
    fetch() if a.action=='fetch' else package()
