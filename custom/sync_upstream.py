"""Merge stable upstream source into the Chinese branch; stop on conflicts or missing translations."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',default='latest');parser.add_argument('--push',action='store_true');args=parser.parse_args()
    if git('status','--porcelain'):raise SystemExit('Commit or stash changes before syncing.')
    path=ROOT/'custom/upstream.json';config=json.loads(path.read_text())
    if git('branch','--show-current')!=config['branch']:raise SystemExit('Use the Chinese maintenance branch.')
    endpoint='latest' if args.tag=='latest' else 'tags/'+args.tag
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/'+config['repository']+'/releases/'+endpoint,headers={'User-Agent':'MHGU-Chinese'}),timeout=30) as response:release=json.load(response)
    tag=release['tag_name']
    if not re.fullmatch(r'\d+\.\d+\.\d+',tag) or release.get('prerelease'):raise SystemExit('Review this upstream version format before merging.')
    asset=next(a for a in release['assets'] if a['name'].startswith('Windows-') and a['name'].endswith('.zip'))
    if not asset.get('digest','').startswith('sha256:'):raise SystemExit('Upstream release lacks a verified digest.')
    git('fetch','https://github.com/'+config['repository']+'.git','refs/tags/'+tag)
    commit=git('rev-parse','FETCH_HEAD^{commit}')
    subprocess.run(['git','merge','--no-edit',commit],cwd=ROOT,check=True)
    if config['tag']!=tag:config['custom_version']=tag+'.1'
    config.update(tag=tag,commit=commit,asset=asset['name'],sha256=asset['digest'])
    path.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    # New upstream labels must be translated explicitly before anything is pushed.
    subprocess.run([sys.executable,str(ROOT/'custom/generate_catalog.py')],cwd=ROOT,check=True)
    git('add','custom/upstream.json','runtime/settings_zh.h')
    if git('diff','--cached','--name-only'):git('commit','-m','Record and localize upstream '+tag)
    if args.push:git('push','https://github.com/'+config['custom_repository']+'.git','HEAD:refs/heads/'+config['branch'],commit+':refs/heads/upstream')
    print('Source synchronized. Build/test in Actions before publishing the Chinese release.')

if __name__=='__main__':main()
