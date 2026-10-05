"""Análise defensiva offline. Não executa nem reenvia solicitações dos logs."""
import csv, re, json, hashlib, collections
from pathlib import Path
from urllib.parse import unquote

SOURCE = Path('C:/Users/Thiago Emanuel/Documents/docker-logs-2026-09-20T04-58-33.970Z.csv')
OUT = Path(__file__).resolve().parent
rows = list(csv.DictReader(SOURCE.open(encoding='utf-8-sig')))
pattern = re.compile(r'^(\S+) .*?\[([^]]+)\] "(.*?)" (\d{3}) (\d+) "([^"]*)" "([^"]*)"(.*)$')
groups = collections.defaultdict(list)
categories = collections.defaultdict(list)
parsed = []
other = []
for record, row in enumerate(rows, 1):
    if row['object'] != 'webhostlp/site':
        continue
    m = pattern.match(row['message'])
    if not m:
        other.append(record)
        continue
    peer, _, request, status, size, _, ua, extra = m.groups()
    fields = request.split()
    path = unquote(fields[1].split('?')[0]).lower() if len(fields) > 1 else ''
    cf = re.search(r'cf_ip="([^"]+)"', extra)
    identity = cf[1] if cf and cf[1] != '-' else 'peer:' + peer
    local = peer in ('127.0.0.1', '::1') and (not cf or cf[1] == '-')
    category = 'indeterminado_ou_compativel_com_uso_normal'
    if local:
        category = 'consulta_local'
    elif (any(x in path for x in ('credentials','credential','auth.json','key.json','keyfile','gcp-','gcloud-','google-key','firebase-','appsettings','terraform.','tfvars','kubeconfig','backup.','database.sql','dump.sql','db.zip','db.tar','www.zip','www.tar','phpinfo','printenv','/env.','/env/','environment','/config/','/debug','/_debug'))
          or path in {'/sa.json','/info','/aws.json','/aws.env','/aws-config.js','/aws.config.js','/id_rsa','/id_ed25519','/private.pem','/server.key','/redis.conf','/pip.conf','/composer.json','/composer.lock','/web.config','/settings.py','/settings.json','/settings_local.py','/local_settings.py','/config.js','/config.json','/azure.json','/dockerrun.aws.json','/__env.js','/sendgrid.env','/vendor/composer/installed.json'}):
        category = 'sondagem_configuracao_credenciais_backup'
    elif path.startswith(('/wp/','/wordpress/','/blog/','/geoserver/','/media/system/')) or path in {'/api/session/properties','/api/v1/version','/ows','/wfs','/livewire/update','/feed/'}:
        category = 'sondagem_sistemas_e_frameworks'
    item = {'record':record,'time':row['timestamp'],'path':path,'status':int(status),'method':fields[0] if fields else '', 'category':category}
    parsed.append(item)
    categories[category].append(item)
    groups[identity].append(item)

cases = []
for key, items in groups.items():
    suspicious = [i for i in items if i['category'].startswith('sondagem_')]
    if len(suspicious) < 3:
        continue
    cases.append({'origin_alias':f'Origem {len(cases)+1:02}', 'from':items[0]['time'],'to':items[-1]['time'],
                  'requests_total':len(items),'suspicious_requests':len(suspicious),
                  'suspicious_status':dict(collections.Counter(str(i['status']) for i in suspicious)),
                  'sample_paths':list(dict.fromkeys(i['path'] for i in suspicious))[:8],
                  'evidence_records':[i['record'] for i in suspicious[:8]],
                  'scope':'Sequência compatível com varredura; não identifica pessoa nem comprova exploração.'})
data = {'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'records':len(rows),
        'period':[rows[0]['timestamp'],rows[-1]['timestamp']], 'access_period':[parsed[0]['time'],parsed[-1]['time']],
        'objects':dict(collections.Counter(r['object'] for r in rows)), 'parsed_access':len(parsed),
        'other_site_events':len(other),'status':dict(collections.Counter(str(i['status']) for i in parsed)),
        'categories':{k:{'count':len(v),'status':dict(collections.Counter(str(i['status']) for i in v))} for k,v in categories.items()},
        'cases':cases,'limitations':['Host não registrado: subdomínios não confirmáveis.','Corpos de requisição e resposta ausentes.','User-Agent não autentica bot nem identidade.','HTTP 301 não comprova acesso ao arquivo; 200 de página pública não comprova exploração.','IPs do peer são majoritariamente proxy interno; agrupamento usa cf_ip quando presente, confiabilidade histórica não comprovada.','Classificação por caminho é heurística; origem não equivale a pessoa e o mesmo IP pode ser compartilhado.','A origem antiga era Apache/PHP; a atual é Nginx estático.']}
(OUT/'analysis.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'context.md').write_text(f'# Evidência local\n\nCSV original preservado: {SOURCE}\n\nSHA-256: {data["input_sha256"]}\n\nExportação histórica Apache/PHP, distinta da LP Nginx atual. Registros referidos são índices lógicos CSV a partir de 1, sem cabeçalho; não números de linha física. Relatórios não incluem IPs, queries, cookies ou tokens.\n',encoding='utf-8')
print(json.dumps({'records':data['records'],'categories':data['categories'],'cases':cases},ensure_ascii=False,indent=2))
