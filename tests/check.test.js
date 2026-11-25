// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../check.js');require('../companion-protocol.js');
const C=globalThis.SonelireCheck,P=globalThis.CompanionProtocol;

test('prepareForm builds an alphabetical or shuffled Form without the Learner',()=>{
  const abc=C.prepareForm('name','lower','alpha',{newId:()=>'F-1'});
  assert.deepEqual(abc,{id:'F-1',skill:'name',case:'lower',seq:[...'abcdefghijklmnopqrstuvwxyz']});
  const shuffled=C.prepareForm('sound','mixed','random',{random:()=>0,newId:()=>'F-2'});
  assert.equal(shuffled.seq.length,52);
  assert.notDeepEqual(shuffled.seq,[...'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz']);
  assert.doesNotThrow(()=>P.encodeForm(shuffled));
  assert.match(C.prepareForm('name','upper','random').id,/^[A-Za-z0-9-]{1,64}$/);
});

const form=C.prepareForm('name','upper','alpha',{newId:()=>'F-1'});

test('Presentation moves through letters; the Shown count never shrinks; the last letter leads to Marking',()=>{
  let c=C.begin('2',form);
  assert.equal(c.learner,'2');assert.equal(c.phase,'presentation');assert.equal(C.currentLetter(c),'A');assert.equal(c.shownCount,1);
  c=C.next(C.next(c));assert.equal(C.currentLetter(c),'C');assert.equal(c.shownCount,3);
  c=C.back(C.back(c));assert.equal(C.currentLetter(c),'A');assert.equal(c.shownCount,3);
  assert.throws(()=>C.back(c));
  for(let i=0;i<25;i++)c=C.next(c);
  assert.equal(C.currentLetter(c),'Z');assert.equal(c.shownCount,26);assert.equal(c.phase,'presentation');
  c=C.next(c);assert.equal(c.phase,'marking');assert.equal(c.shownCount,26);
  assert.throws(()=>C.next(c));assert.throws(()=>C.back(c));
});

test('endPresentation moves to Marking keeping only the letters shown',()=>{
  const c=C.endPresentation(C.next(C.begin('1',form)));
  assert.equal(c.phase,'marking');assert.equal(c.shownCount,2);
  assert.throws(()=>C.endPresentation(c));
});

const marking=(shown)=>{let c=C.begin('1',form);for(let i=1;i<shown;i++)c=C.next(c);return C.endPresentation(c);};

test('Marks are entered only for shown letters during Marking',()=>{
  let c=marking(3);
  assert.throws(()=>C.mark(C.begin('1',form),0,'correct'));
  assert.throws(()=>C.mark(c,3,'correct'));
  assert.throws(()=>C.mark(c,0,'miss'));
  c=C.mark(C.mark(c,0,'incorrect'),2,'skip');
  assert.deepEqual(c.marks,{0:'incorrect',2:'skip'});assert.equal(C.markedCount(c),2);assert.equal(C.canComplete(c),false);
  c=C.mark(c,0,null);assert.deepEqual(c.marks,{2:'skip'});
});

test('markRemainingCorrect fills only unmarked shown letters; clearMarks empties them',()=>{
  let c=C.markRemainingCorrect(C.mark(marking(3),1,'unsure'));
  assert.deepEqual(c.marks,{0:'correct',1:'unsure',2:'correct'});assert.equal(C.canComplete(c),true);
  assert.deepEqual(C.clearMarks(c).marks,{});
});

test('complete returns the saved Marks for shown letters only once all are marked',()=>{
  const c=C.mark(C.mark(marking(2),0,'correct'),1,'incorrect');
  assert.throws(()=>C.complete(C.mark(c,1,null)));
  assert.throws(()=>C.complete(C.begin('1',form)));
  assert.deepEqual(C.complete(c),{learner:'1',skill:'name',formId:'F-1',marks:[{letter:'A',mark:'correct'},{letter:'B',mark:'incorrect'}]});
});

const phoneCode=(marks,f=form)=>P.encodeResults(f,marks);

test('Import of a complete Results code supplies a Mark for every shown letter',()=>{
  const c=marking(26),marks=Object.fromEntries(form.seq.map((_,i)=>[i,i===1?'incorrect':'correct']));
  const preview=C.previewImport(c,phoneCode(marks));
  assert.deepEqual(preview.conflicts,[]);
  const after=C.applyImport(c,preview);
  assert.deepEqual(after.marks,marks);assert.equal(C.canComplete(after),true);
});

test('Import rejects a different Form, Skill or order, and any import during Presentation',()=>{
  const c=marking(26),marks=Object.fromEntries(form.seq.map((_,i)=>[i,'correct']));
  for(const other of [{...form,id:'other'},{...form,skill:'sound'},{...form,seq:[...form.seq].reverse()}])
    assert.throws(()=>C.previewImport(c,phoneCode(marks,other)),/different assessment form/);
  assert.throws(()=>C.previewImport(C.begin('1',form),phoneCode(marks)),/Finish the iPad presentation/);
  assert.throws(()=>C.previewImport(c,'SON1R.garbage'));
});

test('Import after ending early requires Marks for exactly the shown letters',()=>{
  const c=marking(3);
  assert.deepEqual(C.previewImport(c,phoneCode({0:'correct',1:'incorrect',2:'skip'})).marks,{0:'correct',1:'incorrect',2:'skip'});
  assert.throws(()=>C.previewImport(c,phoneCode({0:'correct',2:'skip'})),/Missing response for item 2/);
  assert.throws(()=>C.previewImport(c,phoneCode({0:'correct',1:'incorrect',2:'skip',3:'correct'})),/letters not shown/);
});

test('Import preview lists letters whose existing Mark would change',()=>{
  const c=C.mark(C.mark(marking(3),0,'correct'),1,'unsure');
  const preview=C.previewImport(c,phoneCode({0:'correct',1:'incorrect',2:'skip'}));
  assert.deepEqual(preview.conflicts,['B']);
  assert.deepEqual(C.applyImport(c,preview).marks,{0:'correct',1:'incorrect',2:'skip'});
  assert.throws(()=>C.applyImport(c,{...preview,formId:'other'}),/different assessment form/);
  assert.throws(()=>C.applyImport(C.begin('1',form),preview));
});

test('restore and toStored keep the v1 stored shape (docs/adr/0001)',()=>{
  const v1={learner:'2',case:'upper',skill:'name',seq:[...form.seq],id:'F-1',position:2,shown:3,status:'scoring',scores:{0:'correct',1:'miss',2:'unsure'}};
  const c=C.restore(v1);
  assert.equal(c.phase,'marking');assert.equal(c.shownCount,3);assert.equal(c.learner,'2');assert.deepEqual(c.form,form);
  assert.deepEqual(c.marks,{0:'correct',1:'incorrect',2:'unsure'});
  assert.deepEqual(C.toStored(c),v1);
  for(const status of ['present','paused'])assert.equal(C.restore({...v1,status,scores:{}}).phase,'presentation');
  assert.equal(C.toStored(C.begin('1',form)).status,'present');
  assert.equal(JSON.stringify(C.toStored(c)),JSON.stringify(JSON.parse(JSON.stringify(C.toStored(c)))));
});

test('random operation sequences keep the Check rules and survive a storage round trip',()=>{
  let seed=7;const rand=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
  const ops=[c=>C.next(c),c=>C.back(c),c=>C.endPresentation(c),c=>C.mark(c,Math.floor(rand()*(c.shownCount+1)),[...SonelireVocabulary.marks,null][Math.floor(rand()*5)]),c=>C.markRemainingCorrect(c),c=>C.clearMarks(c),c=>C.restore(JSON.parse(JSON.stringify(C.toStored(c))))];
  for(let run=0;run<300;run++){
    const f=C.prepareForm('sound',['upper','lower','mixed'][run%3],'random',{random:rand,newId:()=>'R-'+run});
    let c=C.begin('1',f);
    for(let step=0;step<80;step++){
      let n;try{n=ops[Math.floor(rand()*ops.length)](c)}catch(e){continue}
      assert.ok(n.shownCount>=n.position+1&&n.shownCount<=f.seq.length,'shown count covers position');
      assert.ok(n.shownCount>=c.shownCount,'shown count never shrinks');
      assert.ok(Object.keys(n.marks).every(i=>+i<n.shownCount),'marks only for shown letters');
      if(c.phase==='marking')assert.equal(n.phase,'marking','Marking never returns to Presentation');
      assert.deepEqual(C.restore(JSON.parse(JSON.stringify(C.toStored(n)))),n,'storage round trip');
      c=n;
    }
  }
});
