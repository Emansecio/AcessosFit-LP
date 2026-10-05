/* No buyer details, session tokens or API credentials are stored in browser storage. */
'use strict';
const $ = id => document.getElementById(id);
const names = {individual:'Individual · 1 pessoa', familia:'Família · até 4 pessoas'};
const prices = {individual:150, familia:200};
const money = value => Number(value).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
let order = null, polling = false, lastStatus = '', stopped = false;
function showError(message=''){ $('error').textContent=message; $('error').hidden=!message; }
function step(number){document.querySelectorAll('.steps li').forEach((el,i)=>{if(i===number-1)el.setAttribute('aria-current','step');else el.removeAttribute('aria-current');});}
async function api(path,body){
  const response=await fetch('/comprar/api/'+path,{method:body?'POST':'GET',credentials:'same-origin',cache:'no-store',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(28000)});
  let result;try{result=await response.json();}catch{throw new Error('Não foi possível concluir a consulta. Aguarde e tente novamente.');}
  if(!response.ok)throw new Error(result.error||'Não foi possível concluir. Tente novamente.');
  return result;
}
function setDetails(){
  const plan=document.querySelector('[name=plan]:checked').value;
  $('selected-plan').textContent=names[plan];$('selected-price').textContent=money(prices[plan]);
  $('choose').hidden=true;$('details').hidden=false;step(2);$('name').focus();
}
$('continue').addEventListener('click',setDetails);
$('back').addEventListener('click',()=>{$('choose').hidden=false;$('details').hidden=true;step(1);$('continue').focus();});
$('document').addEventListener('input',()=>{const digits=$('document').value.replace(/\D/g,'').slice(0,11);$('document').value=digits.replace(/^(\d{3})(\d)/,'$1.$2').replace(/^(\d{3})\.(\d{3})(\d)/,'$1.$2.$3').replace(/\.(\d{3})(\d{1,2})$/,'.$1-$2');});
$('form').addEventListener('submit',async event=>{
  event.preventDefault();showError();const button=$('generate');button.disabled=true;button.textContent='Gerando seu Pix…';
  try{const result=await api('create',{plan:document.querySelector('[name=plan]:checked').value,name:$('name').value,document:$('document').value,acknowledged:$('agreement').checked});render(result.order);if(result.order?.status==='pending')await check();}
  catch(error){showError(error.name==='TimeoutError'?'A resposta demorou. Tente novamente com os mesmos dados; seu pedido será recuperado.':error.message);}
  finally{button.disabled=false;button.textContent='Gerar Pix →';}
});
function timer(){
  if(!order||order.status!=='pending')return;
  const seconds=Math.max(0,Math.ceil((order.expiresAt-Date.now())/1000));
  $('timer').textContent=`Use este código em até ${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}.`;
  if(!seconds){$('pix-content').hidden=true;$('payment-status').textContent='O prazo deste código terminou. Se você pagou, consulte a confirmação. Caso contrário, fale com o atendimento para continuar.';}
}
function render(next){
  order=next;$('loading').hidden=true;
  if(!order||order.status==='creating'){
    $('form').hidden=false;
    if(order){document.querySelector(`[name=plan][value="${order.plan}"]`).checked=true;setDetails();showError('Há um pedido em processamento. Preencha os mesmos dados para recuperar o Pix com segurança.');}
    return;
  }
  $('form').hidden=true;$('reference').hidden=false;$('reference').textContent='Pedido '+order.reference;
  $('payment').hidden=order.status==='paid';$('success').hidden=order.status!=='paid';step(3);
  if(order.status==='paid'){
    $('success-plan').textContent=names[order.plan];$('success-price').textContent=money(order.amount);
    $('success-wa').href='https://wa.me/5538992026240?text='+encodeURIComponent(`Olá! Paguei a ativação ${order.plan==='familia'?'Família':'Individual'} de ${money(order.amount)}. Pedido ${order.reference}. Quero continuar o atendimento.`);
    if(location.pathname!=='/comprar/confirmacao')history.replaceState(null,'','/comprar/confirmacao');
    document.title='Pagamento confirmado | AcessosFit';
  }else{
    if(location.pathname==='/comprar/confirmacao')history.replaceState(null,'','/comprar');
    $('payment-plan').textContent=names[order.plan];$('payment-price').textContent=money(order.amount);
    $('pix-content').hidden=order.status!=='pending'||!order.pixCode;
    if(order.pixCode){$('pix-code').value=order.pixCode;if(!$('qr').getAttribute('src'))$('qr').src='/comprar/api/qr';}
    const statusText={pending:'Aguardando pagamento. A confirmação é consultada automaticamente.',expired:'Este Pix expirou. Se você já pagou, consulte novamente. Para continuar a compra, fale com o atendimento.',failed:'A operadora informou uma falha no pagamento. Fale com o atendimento antes de tentar pagar novamente.',refunded:'A operadora informou um estorno. Fale com o atendimento para conferir sua compra.'};
    $('payment-status').textContent=statusText[order.status]||'Conferindo pagamento…';timer();
  }
  if(lastStatus!==order.status){const title=document.querySelector(order.status==='paid'?'#success h2':'#payment h2');title.setAttribute('tabindex','-1');title.focus();lastStatus=order.status;}
}
async function check(){
  if(polling||!order||order.status==='creating'||stopped)return;
  polling=true;$('check').disabled=true;
  try{const result=await api('status');showError();render(result.order);}catch(error){showError(error.message);}finally{polling=false;$('check').disabled=false;}
}
$('check').addEventListener('click',check);
$('copy').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText($('pix-code').value);$('copy').textContent='Código copiado ✓';setTimeout(()=>{$('copy').textContent='Copiar código Pix ↗';},3000);}
  catch{$('pix-code').focus();$('pix-code').select();showError('Selecione e copie o código acima para colar no app do banco.');}
});
async function init(){try{let result=await api('session');if(result.order&&result.order.status!=='creating')result=await api('status');render(result.order);}catch(error){$('loading').textContent='Não foi possível preparar sua sessão. Recarregue a página para tentar novamente.';showError(error.message);}}
setInterval(()=>{if(!document.hidden&&order&&order.status!=='creating')check();},15000);
setInterval(timer,1000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)check();});
window.addEventListener('pagehide',()=>{stopped=true;});
window.addEventListener('pageshow',()=>{stopped=false;});
init();
