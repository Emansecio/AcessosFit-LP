const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const results=[];
 const base='http://127.0.0.1:8080';
 for(const width of [320,375,390,430,768,1440]){
  const context=await browser.newContext({viewport:{width,height:900}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/comprar');await page.locator('#form').waitFor({state:'visible'});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('[value=familia]').check();await page.locator('#continue').click();
  assert.match(await page.locator('#selected-price').innerText(),/200/);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#back').click();await page.locator('[value=individual]').check();await page.locator('#continue').click();
  assert.match(await page.locator('#selected-price').innerText(),/150/);
  if(width===390){await page.screenshot({path:'qa/checkout-mobile-dados.png',fullPage:true});await page.locator('#back').click();await page.screenshot({path:'qa/checkout-mobile-opcoes.png',fullPage:true});}
  if(width===1440){await page.locator('#back').click();await page.screenshot({path:'qa/checkout-desktop.png',fullPage:true});}
  assert.deepEqual(errors,[]);results.push({width,overflow:false,plans:true,errors});await context.close();
 }
 // UI fixtures are intercepted ONLY inside this test browser. Never posted to SagacePay.
 const context=await browser.newContext({viewport:{width:390,height:844}});const page=await context.newPage();
 let order=null, status='pending';
 await page.route('**/comprar/api/**',async route=>{
  const path=new URL(route.request().url()).pathname;
  if(path.endsWith('/qr'))return route.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><text x="10" y="100">TESTE LOCAL</text></svg>'});
  if(path.endsWith('/create')){const body=route.request().postDataJSON();assert.equal(body.plan,'familia');order={reference:'AF-TEST-LOCAL',plan:'familia',amount:200,status:'pending',pixCode:'TESTE-SEM-VALOR-DE-PAGAMENTO',expiresAt:Date.now()+1800000};}
  if(path.endsWith('/status')&&order)order.status=status;
  await route.fulfill({json:{order}});
 });
 await page.goto(base+'/comprar/confirmacao?status=paid');await page.locator('#form').waitFor({state:'visible'});assert(await page.locator('#success').isHidden());
 await page.locator('[value=familia]').check();await page.locator('#continue').click();await page.locator('#name').fill('Teste local isolado');await page.locator('#document').fill('52998224725');await page.locator('#agreement').check();await page.locator('#generate').click();await page.locator('#payment').waitFor({state:'visible'});
 assert.equal(await page.locator('#pix-code').inputValue(),'TESTE-SEM-VALOR-DE-PAGAMENTO');
 await page.screenshot({path:'qa/checkout-pix-fixture.png',fullPage:true});
 await page.reload();await page.locator('#payment').waitFor({state:'visible'});
 status='paid';await page.locator('#check').click();await page.locator('#success').waitFor({state:'visible'});
 assert.equal(new URL(page.url()).pathname,'/comprar/confirmacao');
 assert.match(await page.locator('#success-wa').getAttribute('href'),/^https:\/\/wa.me\/5538992026240\?text=/);
 await page.screenshot({path:'qa/checkout-confirmacao-fixture.png',fullPage:true});
 status='refunded';await page.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));await page.locator('#payment').waitFor({state:'visible'});assert(await page.locator('#pix-content').isHidden());
 results.push({fixtureFlow:'choose, create, reload, verified payment, WhatsApp, refund',directSuccessBlocked:true});
 await context.close();
 const live=await browser.newPage();await live.goto('https://acessosfitness.online/comprar');await live.locator('#form').waitFor({state:'visible',timeout:25000});
 const cookies=await live.context().cookies();const cookie=cookies.find(x=>x.name==='af_checkout');assert(cookie&&cookie.secure&&cookie.httpOnly&&cookie.sameSite==='Strict');
 await live.goto('https://acessosfitness.online/');assert.equal(await live.locator('a[href*="/comprar"]').count(),0);results.push({publicCheckout:true,secureCookie:true,homepageCheckoutLinks:0});
 await browser.close();require('fs').writeFileSync('qa/checkout-tests.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
