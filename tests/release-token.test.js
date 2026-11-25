// Run from repository root: node --test tests/
// GitHub Pages caches every file for 10 minutes, so each page's same-origin
// scripts carry one shared release token (?v=…) that is bumped on every release
// that changes a script. A new page then never pairs with an old cached script.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),pages=['sonelire-practice.html','companion.html'];
const localScripts=page=>[...fs.readFileSync(path.join(root,page),'utf8').matchAll(/<script\b[^>]*\bsrc="([^"]+)"/g)]
  .map(m=>m[1]).filter(src=>!/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(src));

test('every local script tag in both pages carries the same release token',()=>{
  const tokens=new Set();
  for(const page of pages){
    const srcs=localScripts(page);
    assert.ok(srcs.length>0,`${page} has no local scripts`);
    for(const src of srcs){
      const m=/^([^?#]+)\?v=([0-9A-Za-z.-]+)$/.exec(src);
      assert.ok(m,`${page}: <script src="${src}"> is missing the ?v= release token`);
      assert.ok(fs.existsSync(path.join(root,m[1])),`${page}: ${m[1]} does not exist`);
      tokens.add(m[2]);
    }
  }
  assert.equal(tokens.size,1,`local scripts carry different release tokens: ${[...tokens].join(', ')}`);
});
