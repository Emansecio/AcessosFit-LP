"""Verificações pontuais de configuração; sem replay de payloads históricos."""
import urllib.request, urllib.error, json, subprocess, hashlib, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DOCKER='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
results=[]
def request(url, expected, method='GET', headers=None):
    if url.startswith('https://'):
        # O cliente urllib recebeu 403 da proteção existente; usar o mesmo
        # cliente PowerShell usado na publicação, sem alterar regras do WAF.
        quoted="'"+url.replace("'","''")+"'"
        command=f'$r=Invoke-WebRequest -Uri {quoted} -SkipHttpErrorCheck -TimeoutSec 25; @{{status=[int]$r.StatusCode; content=[string]$r.Content}} | ConvertTo-Json -Compress'
        check=json.loads(subprocess.run(['pwsh','-NoProfile','-Command',command],capture_output=True,text=True,check=True).stdout)
        assert check['status']==expected,f'{url}: {check["status"]}, expected {expected}'
        results.append({'url':url.split('?')[0],'method':method,'status':check['status'],'client':'PowerShell'})
        return check['content'].encode('utf-8'),{}
    req=urllib.request.Request(url,method=method,headers=headers or {})
    try: response=urllib.request.urlopen(req,timeout=25)
    except urllib.error.HTTPError as e: response=e
    body=response.read()
    assert response.status==expected, f'{method} {url}: {response.status}, expected {expected}'
    results.append({'url':url.split('?')[0],'method':method,'status':response.status})
    return body,response.headers

for f in (ROOT/'site').rglob('*'):
    if not f.is_file(): continue
    path=f.relative_to(ROOT/'site').as_posix()
    public_path='comprar' if path=='comprar/index.html' else path
    body,h=request('http://127.0.0.1:8080/'+public_path,200)
    assert hashlib.sha256(body).digest()==hashlib.sha256(f.read_bytes()).digest()

for path in ['/secrets/tunnel-token','/.env','/.git/config','/backup.zip','/comprar/checkout.php','/hardening/analysis.json','/assets/not-published.json']:
    request('http://127.0.0.1:8080'+path,404)
request('http://127.0.0.1:8080/',404,headers={'Host':'unexpected.invalid'})
request('http://127.0.0.1:8080/',405,method='POST')
request('http://127.0.0.1:8080/',200,method='HEAD')
marker='qa-privacy-'+str(int(time.time()))
body,h=request('http://127.0.0.1:8080/?gclid='+marker,200,headers={'Cookie':marker,'Authorization':'Bearer '+marker,'Referer':'https://example.invalid/'+marker})
assert h.get('X-Content-Type-Options')=='nosniff'
assert "frame-ancestors 'none'" in h.get('Content-Security-Policy','')
logs=subprocess.run([DOCKER,'compose','-f','compose.yaml','-f','compose.tunnel.yaml','logs','--since','2m','lp'],cwd=ROOT,capture_output=True,text=True,check=True).stdout
assert marker not in logs,'Sensitive test marker found in access logs'
assert '"host":' in logs and '"path":' in logs
results.append({'privacy_marker_omitted':True})

for base in ['https://acessosfitness.online','https://www.acessosfitness.online']:
    body,h=request(base+'/?utm_source=qa&gclid=qa-functional-check',200)
    assert b'Procurando Gympass' in body
    request(base+'/robots.txt',200)
    request(base+'/styles.css',200)

edge_path='/debug/qa-edge-'+str(int(time.time()))
request('https://acessosfitness.online'+edge_path,403)
logs=subprocess.run([DOCKER,'compose','-f','compose.yaml','-f','compose.tunnel.yaml','logs','--since','2m','lp'],cwd=ROOT,capture_output=True,text=True,check=True).stdout
assert edge_path not in logs,'Edge-blocked request reached origin log'
results.append({'edge_blocked_before_origin':True})
inspect=json.loads(subprocess.run([DOCKER,'inspect','acessosfit-lp-lp-1','acessosfit-lp-tunnel-1'],capture_output=True,text=True,check=True).stdout)
for item in inspect:
    assert item['HostConfig']['ReadonlyRootfs']
    assert 'no-new-privileges:true' in item['HostConfig']['SecurityOpt']
    assert item['HostConfig']['LogConfig']['Config']['max-size']=='10m'
    results.append({'container':item['Name'],'read_only':True,'no_new_privileges':True,'log_rotation':True})
(ROOT/'hardening'/'verification.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(results),'edge_blocked_before_origin':True,'privacy_marker_omitted':True}))
