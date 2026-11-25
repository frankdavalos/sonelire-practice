// Run from repository root: node --test tests/
// GitHub Pages caches every file for 10 minutes, so each page's scripts carry
// one shared release token (?v=…) that is bumped on every release that changes
// a script. A new page then never pairs with an old cached script.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const pages=['sonelire-practice.html','companion.html'];
const scriptSrcs=page=>[...fs.readFileSync(path.join(__dirname,'..',page),'utf8').matchAll(/<script\b[^>]*\bsrc="([^"]+)"/g)].map(m=>m[1]);

test('every script tag in both pages carries the same release token',()=>{
  const tokens=new Set();
  for(const page of pages){
    const srcs=scriptSrcs(page);
    assert.ok(srcs.length>0,`${page} has no scripts`);
    for(const src of srcs){
      const token=/\?v=([0-9A-Za-z.-]+)$/.exec(src)?.[1];
      assert.ok(token,`${page}: <script src="${src}"> is missing the ?v= release token`);
      tokens.add(token);
    }
  }
  assert.equal(tokens.size,1,`scripts carry different release tokens: ${[...tokens].join(', ')}`);
});
