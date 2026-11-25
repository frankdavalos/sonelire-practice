// Run from repository root: node --test tests/
// HOW_TO_USE.md writes the app's own buttons, tabs and headings in **bold**, so a
// parent can look for the same words on screen. These tests keep each bold label
// pointing at text one of the pages really shows. Safari and iPadOS controls are
// written in *italics* instead; a bold lead-in ending in ":" is not a label.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=file=>fs.readFileSync(path.join(__dirname,'..',file),'utf8');
const guide=read('HOW_TO_USE.md');
const pages=read('sonelire-practice.html')+read('companion.html');
const boldLabels=text=>[...text.matchAll(/\*\*(.+?)\*\*/g)].map(m=>m[1]).filter(label=>!label.endsWith(':'));

test('the guide has an iPad Safari setup section that walks through app controls (docs/adr/0004)',()=>{
  const lines=guide.split('\n'),start=lines.findIndex(line=>/^#{2,3} .*Safari on the iPad/.test(line));
  assert.ok(start>=0,'HOW_TO_USE.md has no iPad Safari setup section');
  const level=/^#+/.exec(lines[start])[0].length;
  const end=lines.findIndex((line,i)=>i>start&&new RegExp(`^#{1,${level}} `).test(line));
  const setup=lines.slice(start,end<0?undefined:end).join('\n');
  assert.ok(boldLabels(setup).length>0,'the iPad Safari section names no app controls');
});

test('every bold label in the guide is text the app shows',()=>{
  const body=guide.slice(guide.search(/^## /m));
  const missing=[...new Set(boldLabels(body))].filter(label=>!pages.includes(label));
  assert.deepEqual(missing,[]);
});
