// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../storage.js');require('../results.js');
const S=globalThis.SonelireStorage,R=globalThis.SonelireResults;

// Saved by v2.1 before the Results module existed (docs/adr/0001): 'miss' status, draft with 'scoring' status and stored scores.
const legacy={version:1,learner:'2',results:{'1':{name:{},sound:{}},'2':{name:{B:{status:'miss',date:'2026-10-02T09:00:00.000Z',form:'F-9'}},sound:{}}},
  draft:{learner:'2',case:'upper',skill:'name',seq:['A','B'],id:'F-10',position:1,shown:2,status:'scoring',scores:{'0':'miss'}}};

test('load reads legacy v1 data: the selected Learner, Results and Unfinished check',()=>{
  const state=S.load(S.memory(JSON.stringify(legacy)));
  assert.equal(state.learner,'2');
  assert.deepEqual(state.unfinishedCheck,legacy.draft);
  assert.deepEqual(R.needsPractice(state.results,'2','name','upper'),['B']);
});

test('load starts fresh (Child 1, no Results, no Unfinished check) when nothing usable is saved',()=>{
  const fresh={learner:'1',results:{'1':{name:{},sound:{}},'2':{name:{},sound:{}}},unfinishedCheck:null};
  for(const text of [null,'null',JSON.stringify({...legacy,version:2}),JSON.stringify({...legacy,results:{'1':legacy.results['1']}})])
    assert.deepEqual(S.load(S.memory(text)),fresh,String(text));
  assert.equal(S.load(S.memory(JSON.stringify({...legacy,learner:'3'}))).learner,'1');
});

test('load throws on saved data it cannot read, so the page can warn and leave that data alone',()=>{
  assert.throws(()=>S.load(S.memory('not json')),SyntaxError);
  assert.throws(()=>S.load({read(){throw Error('storage unavailable')},write(){}}),/storage unavailable/);
});

test('save writes the v1 shape back, so legacy data survives a load and save unchanged',()=>{
  const adapter=S.memory(JSON.stringify(legacy));
  const written=S.save(adapter,S.load(adapter));
  assert.equal(adapter.read(),written);
  assert.deepEqual(JSON.parse(written),legacy);
  const adapter2=S.memory();S.save(adapter2,{learner:'1',results:R.recordCheck(R.empty(),{learner:'1',skill:'name',formId:'F-2',marks:[{letter:'A',mark:'incorrect'}]},'2026-11-24T10:00:00.000Z'),unfinishedCheck:null});
  assert.deepEqual(S.load(adapter2).results['1'].name.A,{status:'miss',date:'2026-11-24T10:00:00.000Z',form:'F-2'});
});
