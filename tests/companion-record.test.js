// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../companion-record.js');require('../companion-protocol.js');
const R=globalThis.SonelireCompanionRecord,P=globalThis.CompanionProtocol;
const form={id:'F-1',skill:'name',case:'upper',seq:[...'ABCDEFGHIJKLMNOPQRSTUVWXYZ']};

test('marking records the Mark on the current item and moves to the next',()=>{
  let r=R.open(form,null);
  assert.equal(R.currentLetter(r),'A');
  r=R.mark(r,'correct');
  assert.equal(r.marks[0],'correct');assert.equal(R.currentLetter(r),'B');assert.equal(R.markedCount(r),1);
});

test('go-to-item moves to any item; marking the last item stays there',()=>{
  let r=R.goTo(R.open(form,null),25);
  assert.equal(R.currentLetter(r),'Z');
  r=R.mark(r,'unsure');
  assert.equal(r.marks[25],'unsure');assert.equal(R.currentLetter(r),'Z');
  r=R.goTo(r,2);assert.equal(R.currentLetter(r),'C');
  for(const i of [-1,26,1.5,'2'])assert.throws(()=>R.goTo(r,i),String(i));
});

test('clear removes the current Mark and stays on the item',()=>{
  const r=R.clear(R.goTo(R.mark(R.open(form,null),'skip'),0));
  assert.equal(r.marks[0],undefined);assert.equal(R.currentLetter(r),'A');assert.equal(R.markedCount(r),0);
});

test('undo reverses the last mark or clear, returning to the item it changed',()=>{
  let r=R.open(form,null);
  assert.equal(R.canUndo(r),false);
  r=R.mark(R.mark(r,'correct'),'incorrect');           // A correct, B incorrect, now on C
  r=R.clear(R.goTo(r,0));                               // A cleared
  r=R.goTo(r,5);
  r=R.undo(r);                                          // undo the clear: A back to correct, on A
  assert.equal(r.marks[0],'correct');assert.equal(R.currentLetter(r),'A');
  r=R.undo(r);                                          // undo B's mark
  assert.equal(r.marks[1],undefined);assert.equal(R.currentLetter(r),'B');
  r=R.undo(r);                                          // undo A's mark
  assert.deepEqual({...r.marks},{});assert.equal(R.currentLetter(r),'A');
  assert.equal(R.canUndo(r),false);
  assert.equal(R.undo(r),r);
});

test('open restores a saved record, reading stored miss as Incorrect and dropping invalid entries',()=>{
  // Saved by the phone before this module existed (docs/adr/0001).
  const r=R.open(form,{scores:{'0':'correct','1':'miss','2':'unsure','3':'skip','4':'incorrect','5':'maybe','26':'correct','-1':'correct','x':'correct','01':'correct'},index:3});
  assert.deepEqual({...r.marks},{0:'correct',1:'incorrect',2:'unsure',3:'skip'});
  assert.equal(R.currentLetter(r),'D');assert.equal(R.canUndo(r),false);
  for(const index of [26,-1,1.5,'3',undefined])assert.equal(R.open(form,{scores:{},index}).position,0,String(index));
  for(const stored of [null,undefined,{},{scores:null},{scores:'x'},[] ,'text',7])
    assert.deepEqual({...R.open(form,stored).marks},{},JSON.stringify(stored));
});

test('a Mark must be one of the four Marks',()=>{
  assert.throws(()=>R.mark(R.open(form,null),'miss'));
  assert.throws(()=>R.mark(R.open(form,null),null));
});

test('toStored keeps the v1 saved shape, so a saved record opens unchanged',()=>{
  const saved={scores:{'0':'correct','1':'miss','25':'skip'},index:25};
  const r=R.open(form,saved);
  assert.deepEqual(R.toStored(r),saved);
  assert.deepEqual(R.toStored(R.open(form,R.toStored(R.goTo(R.mark(r,'unsure'),4)))),{scores:{...saved.scores,'25':'unsure'},index:4});
  assert.equal(R.key(form),'sonelire-companion-v1:SON1A.F-1.name.upper.ABCDEFGHIJKLMNOPQRSTUVWXYZ');
});

test('the Results code carries the Form and its Marks, unmarked items as blanks',()=>{
  const r=R.mark(R.mark(R.goTo(R.open(form,null),24),'incorrect'),'correct');
  const code=R.resultsCode(r);
  assert.equal(code,'SON1R.F-1.name.upper.ABCDEFGHIJKLMNOPQRSTUVWXYZ.'+'-'.repeat(24)+'IC');
  assert.deepEqual(P.decodeResults(code).form,form);
});
