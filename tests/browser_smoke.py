"""Chromium smoke test using in-memory HTML and mocked storage in a restricted test environment."""
import os, re, json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
base="https://frankdavalos.github.io/sonelire-practice/sonelire-practice.html"
def load(page,filename,url,storage=None):
 html=(root/filename).read_text()
 html=re.sub(r'<link[^>]+fonts.googleapis.com[^>]+>', '', html)
 html=re.sub(r'<script src="([^"?#]+)(?:[?#][^"]*)?"></script>',lambda m:'<script>'+ (root/m[1]).read_text()+'</script>',html)
 # Simulate location inputs and storage; never contact a host.
 html=html.replace('location.href','testLocation.href').replace('location.hash','testLocation.hash').replace('location.pathname','testLocation.pathname').replace('location.search','testLocation.search').replace("history.replaceState(null,'',testLocation.pathname+testLocation.search)","testLocation.hash=''")
 pre='<script>const testLocation=new URL('+json.dumps(url)+');const store='+json.dumps(storage or {})+';Object.defineProperty(window,"localStorage",{value:{getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=String(v),removeItem:k=>delete store[k]}});</script>'
 page.set_content(html.replace('<head>','<head>'+pre,1) if '<head>' in html else pre+html)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox']);pad=browser.new_context(viewport={'width':1366,'height':1024});phone=browser.new_context(viewport={'width':390,'height':844});errors=[]
 a=pad.new_page();b=phone.new_page();a.on('pageerror',lambda e:errors.append(str(e)));b.on('pageerror',lambda e:errors.append(str(e)))
 load(a,'sonelire-practice.html',base);a.click('#tabAssess');a.click('#assessCase [data-value=mixed]');a.click('#prepare');a.click('#showCompanion');url=a.locator('#companionLink').get_attribute('href');assert a.locator('#companionQR svg').count()==1
 try:
  from pyzbar.pyzbar import decode
  from PIL import Image
  import io
  assert decode(Image.open(io.BytesIO(a.locator('#companionQR svg').screenshot())))[0].data.decode()==url
  qr_decoded=True
 except ImportError: qr_decoded=False
 load(b,'companion.html',url);a.click('#begin');assert not a.locator('#scoring').is_visible();assert not a.locator('#showCompanion').is_visible()
 for i in range(52):
  assert a.locator('#stimulusLetter').inner_text()==b.locator('#letter').inner_text()
  b.click('[data-score=incorrect]' if i==1 else '[data-score=correct]');a.keyboard.press('ArrowRight')
 assert a.locator('#scoring').is_visible();saved=b.evaluate('store');b2=phone.new_page();load(b2,'companion.html',url,saved);assert b2.locator('#progress').inner_text()=='52 marked';b=b2
 b.click('#transfer');code=b.locator('#code').input_value();assert b.locator('#resultQR svg').count()==1
 link=b.evaluate('CompanionProtocol.resultUrl(document.getElementById("code").value, testLocation.href)')
 if qr_decoded: assert decode(Image.open(io.BytesIO(b.locator('#resultQR svg').screenshot())))[0].data.decode()==link
 c=pad.new_page();c.on('pageerror',lambda e:errors.append(str(e)));load(c,'sonelire-practice.html',link,a.evaluate('store'));assert c.locator('#importCode').input_value()==code
 c.click('#importButton');assert c.locator('#scoredCount').inner_text()=='52 / 52 marked';assert c.locator('#scoreList [data-index="1"] [data-value=incorrect]').get_attribute('aria-pressed')=='true';c.click('#saveScores');assert c.locator('#results').is_visible();assert '1 letter to review' in c.locator('#resultHint').inner_text();c.click('#practiceWeak');assert c.locator('#counter').inner_text()=='1 / 1'
 c.select_option('#learner','2');c.click('#tabAssess');c.click('#prepare');c.click('#begin');c.click('#pause');c.once('dialog',lambda d:d.accept());c.click('#finishEarly');c.locator('#importPanel summary').click();c.fill('#importCode',code);c.click('#importButton');assert 'different assessment' in c.locator('#importMessage').inner_text();assert c.locator('#scoredCount').inner_text()=='0 / 1 marked';c.click('#scoreList [data-index="0"] [data-value=correct]');c.click('#saveScores');assert c.locator('#stats strong').first.inner_text()=='1';c.select_option('#learner','1');c.click('#resultCase [data-value=mixed]');assert c.locator('#stats strong').first.inner_text()=='51';assert not errors,errors
 print('PASS: 52 exact items, simulated phone reload, QR return link, import, targeted practice, wrong-form rejection, paper scoring, profile isolation. QR pixel decode:',qr_decoded)
 browser.close()
