"""Chromium smoke test. Pages load from the repository at their published URL; nothing contacts a host."""
import os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
site='https://frankdavalos.github.io/sonelire-practice/'
base=site+'sonelire-practice.html'
def serve(context):
 """Fulfil requests under the published site from the working tree; abort everything else (e.g. web fonts)."""
 def handle(route):
  u=urlsplit(route.request.url);f=root/u.path.removeprefix(urlsplit(site).path)
  if route.request.url.startswith(site) and f.is_file():route.fulfill(path=f)
  else:route.abort()
 context.route('**/*',handle);return context
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox']);pad=serve(browser.new_context(viewport={'width':1366,'height':1024}));phone=serve(browser.new_context(viewport={'width':390,'height':844}));errors=[]
 a=pad.new_page();b=phone.new_page();a.on('pageerror',lambda e:errors.append(str(e)));b.on('pageerror',lambda e:errors.append(str(e)))
 a.goto(base);a.click('#tabAssess');a.click('#assessCase [data-value=mixed]');a.click('#prepare');a.click('#showCompanion');url=a.locator('#companionLink').get_attribute('href');assert a.locator('#companionQR svg').count()==1
 try:
  from pyzbar.pyzbar import decode
  from PIL import Image
  import io
  assert decode(Image.open(io.BytesIO(a.locator('#companionQR svg').screenshot())))[0].data.decode()==url
  qr_decoded=True
 except ImportError: qr_decoded=False
 b.goto(url);a.click('#begin');assert not a.locator('#scoring').is_visible();assert not a.locator('#showCompanion').is_visible()
 for i in range(52):
  assert a.locator('#stimulusLetter').inner_text()==b.locator('#letter').inner_text()
  b.click('[data-score=incorrect]' if i==1 else '[data-score=correct]');a.keyboard.press('ArrowRight')
 assert a.locator('#scoring').is_visible();b2=phone.new_page();b2.goto(url);assert b2.locator('#progress').inner_text()=='52 marked';b=b2
 b.click('#transfer');code=b.locator('#code').input_value();assert b.locator('#resultQR svg').count()==1
 link=b.evaluate('CompanionProtocol.resultUrl(document.getElementById("code").value, location.href)')
 if qr_decoded: assert decode(Image.open(io.BytesIO(b.locator('#resultQR svg').screenshot())))[0].data.decode()==link
 a.close()  # c shares a's localStorage; an open a would reload on c's writes
 c=pad.new_page();c.on('pageerror',lambda e:errors.append(str(e)));c.goto(link);assert c.locator('#importCode').input_value()==code
 c.click('#importButton');assert c.locator('#scoredCount').inner_text()=='52 / 52 marked';assert c.locator('#scoreList [data-index="1"] [data-value=incorrect]').get_attribute('aria-pressed')=='true';c.click('#saveScores');assert c.locator('#results').is_visible();assert '1 letter to review' in c.locator('#resultHint').inner_text();c.click('#practiceWeak');assert c.locator('#counter').inner_text()=='1 / 1'
 c.select_option('#learner','2');c.click('#tabAssess');c.click('#prepare');c.click('#begin');c.click('#pause');c.once('dialog',lambda d:d.accept());c.click('#finishEarly');c.locator('#importPanel summary').click();c.fill('#importCode',code);c.click('#importButton');assert 'different assessment' in c.locator('#importMessage').inner_text();assert c.locator('#scoredCount').inner_text()=='0 / 1 marked';c.click('#scoreList [data-index="0"] [data-value=correct]');c.click('#saveScores');assert c.locator('#stats strong').first.inner_text()=='1';c.select_option('#learner','1');c.click('#resultCase [data-value=mixed]');assert c.locator('#stats strong').first.inner_text()=='51';assert not errors,errors
 print('PASS: 52 exact items, simulated phone reload, QR return link, import, targeted practice, wrong-form rejection, paper scoring, profile isolation. QR pixel decode:',qr_decoded)
 browser.close()
