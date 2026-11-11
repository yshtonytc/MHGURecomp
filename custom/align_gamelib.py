"""Select the official ID only when it hashes these exact sources/flags (LF or CRLF).

Upstream's GAMELIB_ID hashes raw file line endings. Its Windows releases can use
CRLF, while a clean GitHub Actions checkout uses LF. Never remove the runtime ID
check, modify the stock library, or accept an arbitrary ID from the DLL.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def choose_identity(contents,flags,official_host,official_library):
    canonical=[data.replace(b'\r\n',b'\n') for data in contents]
    candidates={
        'LF':hashlib.sha256(b''.join(canonical)+(flags+'\n').encode()).hexdigest()[:16],
        'CRLF':hashlib.sha256(b''.join(data.replace(b'\n',b'\r\n') for data in canonical)+(flags+'\n').encode()).hexdigest()[:16],
    }
    matches=[(style,value) for style,value in candidates.items()
             if value.encode()+b'\0' in official_host and value.encode()+b'\0' in official_library]
    if len(matches)!=1:raise ValueError('Official programs do not match these exact ABI sources/flags: '+repr(candidates))
    style,identity=matches[0]
    return {'identity':identity,'line_endings':style,'candidates':candidates,'genflags':flags}

def main():
    # Query make so platform flags and ABI-bearing source lists remain upstream-owned.
    recipe='custom-print-abi: ; @printf "%s\\n" "$(GAMELIB_SRCS)" "$(GENFLAGS)"'
    values=subprocess.check_output(['make','-s','--no-print-directory','--eval',recipe,'custom-print-abi'],cwd=ROOT,text=True).splitlines()
    if len(values)!=2:raise ValueError('Unexpected Makefile ABI metadata')
    sources,flags=values
    files=[ROOT/name for name in sources.split()]
    if not files or any(not path.resolve().is_relative_to(ROOT.resolve()) for path in files):raise ValueError('Unsafe ABI source list')
    base=ROOT/'out/base'
    audit=choose_identity([path.read_bytes() for path in files],flags,(base/'mhgurecomp.exe').read_bytes(),(base/'mhgugame.dll').read_bytes())
    audit['sources']=sources.split()
    (ROOT/'out/gamelib-compatible.id').write_text(audit['identity']+'\n',encoding='ascii')
    (ROOT/'out/gamelib-compatible.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print('Verified official ABI identity:',audit['identity'],'('+audit['line_endings']+' source line endings)')

if __name__=='__main__':main()
