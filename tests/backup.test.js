// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../backup.js');
const B=globalThis.SonelireBackup,L=globalThis.SonelireCheckLog,R=globalThis.SonelireResults;

const completed=(formId,learner,letter,mark)=>({learner,skill:'name',case:'upper',formId,shownCount:1,marks:[{letter,mark}]});
const saves=[[completed('F-1','1','A','incorrect'),'2026-11-01T09:00:00.000Z'],[completed('F-2','1','B','correct'),'2026-11-03T09:00:00.000Z'],
  [completed('F-3','2','A','skip'),'2026-11-02T09:00:00.000Z']];
const results=saves.reduce((r,[c,date])=>R.recordCheck(r,c,date),R.empty());
const log=L.withLastBackup(saves.reduce((log,[c,date])=>L.record(log,c,date),L.empty()),'2026-10-01T09:00:00.000Z');
const now=new Date('2026-11-24T10:00:00.000Z');

test('reading an exported Backup file gives back the same Results and Check log, last backed up when it was exported',()=>{
  const backup=B.read(B.export(results,log,now));
  assert.deepEqual(backup.results,results);
  assert.deepEqual(L.toStored(backup.log),{...L.toStored(log),lastBackup:'2026-11-24T10:00:00.000Z'});
  assert.equal(backup.exportedAt,'2026-11-24T10:00:00.000Z');
  assert.deepEqual(backup.summary,{checks:{'1':2,'2':1},latest:'2026-11-03T09:00:00.000Z'});
});

test('a Backup file is marked, versioned JSON holding only Results and Check records',()=>{
  assert.deepEqual(Object.keys(JSON.parse(B.export(results,log,now))),['format','version','exportedAt','results','checks']);
  assert.deepEqual(JSON.parse(B.export(R.empty(),L.empty(),now)),{format:'sonelire-backup',version:1,exportedAt:'2026-11-24T10:00:00.000Z',results:R.empty(),checks:[]});
  assert.deepEqual(B.read(B.export(R.empty(),L.empty(),now)).summary,{checks:{'1':0,'2':0},latest:null});
});

test('a Backup file is named for the local date it was exported',()=>{
  assert.equal(B.fileName(new Date(2026,0,5,23,59)),'sonelire-backup-2026-01-05.json');
});

test('a damaged or wrong file is refused with a readable error',()=>{
  const good=JSON.parse(B.export(results,log,now)),[record]=good.checks;
  const result=good.results['1'].name.A;
  const refused=[['not json','{'],['not a sonelire backup','null'],['not a sonelire backup','[]'],['not a sonelire backup',{...good,format:'other'}],['not a sonelire backup',{...good,format:undefined}],
    ['version',{...good,version:2}],['export date',{...good,exportedAt:'yesterday'}],
    ['results',{...good,results:{'1':good.results['1']}}],['results',{...good,results:{...good.results,'2':{name:{}}}}],
    ['results',{...good,results:{...good.results,'1':{name:{'é':result},sound:{}}}}],
    ['results',{...good,results:{...good.results,'1':{name:{A:{...result,status:'wrong'}},sound:{}}}}],
    ['results',{...good,results:{...good.results,'1':{name:{A:{...result,date:7}},sound:{}}}}],
    ['check',{...good,checks:'x'}],
    ...[{learner:'3'},{skill:'spelling'},{case:'italic'},{marks:[{letter:'A',mark:'miss'}]}].map(change=>['check',{...good,checks:[{...record,...change}]}])];
  for(const [message,file] of refused){
    const text=typeof file==='string'?file:JSON.stringify(file);
    assert.throws(()=>B.read(text),e=>e instanceof Error&&e.message.toLowerCase().includes(message),text);
  }
});
