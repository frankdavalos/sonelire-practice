// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../check-log.js');const L=globalThis.SonelireCheckLog;

const completed=(formId,marks,{learner='1',skill='name',c='upper'}={})=>({learner,skill,case:c,formId,shownCount:marks.length,marks});

test('recording a saved Check adds it to the Check list with its own counts',()=>{
  const log=L.record(L.empty(),completed('F-1',[{letter:'A',mark:'correct'},{letter:'B',mark:'incorrect'},{letter:'C',mark:'unsure'},{letter:'D',mark:'skip'}]),'2026-11-24T10:00:00.000Z');
  assert.deepEqual(L.checks(log,'1','name','upper'),[
    {date:'2026-11-24T10:00:00.000Z',formId:'F-1',case:'upper',shownCount:4,correct:1,needsPractice:2,skip:1}]);
});

test('recording a Form ID again replaces its Check record, so a retried save is counted once',()=>{
  let log=L.record(L.empty(),completed('F-1',[{letter:'A',mark:'incorrect'}]),'2026-11-24T10:00:00.000Z');
  log=L.record(log,completed('F-1',[{letter:'A',mark:'correct'}]),'2026-11-24T10:05:00.000Z');
  assert.deepEqual(L.checks(log,'1','name','upper').map(c=>[c.date,c.correct]),[['2026-11-24T10:05:00.000Z',1]]);
});

test("the Check list holds only the Learner and Skill's Checks that include the Case's letters, newest first",()=>{
  const saves=[
    ['UP-1','2026-11-01T09:00:00.000Z',completed('UP-1',[{letter:'A',mark:'correct'}])],
    ['MIX','2026-11-03T09:00:00.000Z',completed('MIX',[{letter:'A',mark:'correct'},{letter:'a',mark:'incorrect'}],{c:'mixed'})],
    ['UP-2','2026-11-02T09:00:00.000Z',completed('UP-2',[{letter:'B',mark:'correct'}])],
    ['LOW','2026-11-04T09:00:00.000Z',completed('LOW',[{letter:'b',mark:'correct'}],{c:'lower'})],
    ['CHILD-2','2026-11-05T09:00:00.000Z',completed('CHILD-2',[{letter:'A',mark:'correct'}],{learner:'2'})],
    ['SOUND','2026-11-06T09:00:00.000Z',completed('SOUND',[{letter:'A',mark:'correct'}],{skill:'sound'})]];
  const log=saves.reduce((log,[,date,c])=>L.record(log,c,date),L.empty());
  const ids=(...a)=>L.checks(log,...a).map(c=>c.formId);
  assert.deepEqual(ids('1','name','upper'),['MIX','UP-2','UP-1']);
  assert.deepEqual(ids('1','name','lower'),['LOW','MIX']);
  assert.deepEqual(ids('1','name','mixed'),['LOW','MIX','UP-2','UP-1']);
  assert.deepEqual(ids('2','name','upper'),['CHILD-2']);
  assert.deepEqual(ids('1','sound','upper'),['SOUND']);
  assert.equal(L.checks(log,'1','name','upper')[0].case,'mixed','each entry keeps its own Case');
});

test('the stored form is versioned JSON in CONTEXT.md vocabulary, and restores to the same Check log',()=>{
  const log=L.record(L.empty(),completed('F-1',[{letter:'A',mark:'incorrect'},{letter:'B',mark:'skip'}]),'2026-11-24T10:00:00.000Z');
  const stored=JSON.parse(JSON.stringify(L.toStored(log)));
  assert.deepEqual(stored,{version:1,lastBackup:null,checks:[{date:'2026-11-24T10:00:00.000Z',learner:'1',skill:'name',case:'upper',formId:'F-1',shownCount:2,
    marks:[{letter:'A',mark:'incorrect'},{letter:'B',mark:'skip'}]}]});
  assert.deepEqual(L.checks(L.restore(stored),'1','name','upper'),L.checks(log,'1','name','upper'));
});

test('nothing saved, an unknown version or an unreadable Check record restores as an empty Check log',()=>{
  const good={date:'2026-11-24T10:00:00.000Z',learner:'1',skill:'name',case:'upper',formId:'F-1',shownCount:1,marks:[{letter:'A',mark:'correct'}]};
  const bad=[null,{},{version:2,checks:[good]},{version:1,checks:'x'},
    ...[{learner:'3'},{skill:'spelling'},{case:'italic'},{formId:''},{date:7},{shownCount:2},{marks:[{letter:'A',mark:'miss'}]},{marks:[{letter:'é',mark:'correct'}]}]
      .map(change=>({version:1,checks:[{...good,...change}]}))];
  for(const stored of bad)assert.deepEqual(L.checks(L.restore(stored),'1','name','upper'),[],JSON.stringify(stored));
  assert.equal(L.checks(L.restore({version:1,checks:[good]}),'1','name','upper').length,1);
});

const logOf=(...saves)=>saves.reduce((log,[formId,date,marks,opts])=>L.record(log,completed(formId,marks,opts),date),L.empty());
const day=n=>`2026-11-${String(n).padStart(2,'0')}T09:00:00.000Z`;

test("a letter's history lists every Check record holding it, newest first, Skips included",()=>{
  const log=logOf(
    ['F-1',day(1),[{letter:'B',mark:'incorrect'},{letter:'C',mark:'correct'}]],
    ['F-2',day(3),[{letter:'B',mark:'skip'}]],
    ['F-3',day(2),[{letter:'B',mark:'correct'}],{c:'mixed'}],
    ['F-4',day(4),[{letter:'B',mark:'incorrect'}],{learner:'2'}],
    ['F-5',day(5),[{letter:'B',mark:'incorrect'}],{skill:'sound'}]);
  assert.deepEqual(L.letterHistory(log,'1','name','B'),[
    {date:day(3),formId:'F-2',mark:'skip'},{date:day(2),formId:'F-3',mark:'correct'},{date:day(1),formId:'F-1',mark:'incorrect'}]);
  assert.deepEqual(L.letterHistory(log,'1','name','b'),[],'lowercase is a different letter');
});

test('struggles: letters still Incorrect or Unsure need practice; letters Correct after a struggle Improved, with dates',()=>{
  const log=logOf(
    ['F-1',day(1),[{letter:'B',mark:'incorrect'},{letter:'C',mark:'unsure'},{letter:'D',mark:'correct'}]],
    ['F-2',day(2),[{letter:'B',mark:'unsure'},{letter:'C',mark:'unsure'}]],
    ['F-3',day(3),[{letter:'B',mark:'correct'}]],
    ['F-4',day(4),[{letter:'B',mark:'correct'},{letter:'A',mark:'incorrect'}]]);
  assert.deepEqual(L.struggles(log,'1','name','upper'),{
    stillNeedsPractice:['A','C'],
    improved:[{letter:'B',firstStruggle:day(1),lastStruggle:day(2),correctSince:day(3)}]});
});

test('struggles: slipping back needs practice again; always Correct or only Skipped is in neither list; a Skip never changes standing',()=>{
  const log=logOf(
    ['F-1',day(1),[{letter:'B',mark:'incorrect'},{letter:'C',mark:'correct'},{letter:'D',mark:'skip'},{letter:'E',mark:'incorrect'}]],
    ['F-2',day(2),[{letter:'B',mark:'correct'},{letter:'C',mark:'correct'},{letter:'D',mark:'skip'},{letter:'E',mark:'correct'}]],
    ['F-3',day(3),[{letter:'B',mark:'incorrect'},{letter:'E',mark:'skip'},{letter:'F',mark:'unsure'}]],
    ['F-4',day(4),[{letter:'F',mark:'skip'}]]);
  assert.deepEqual(L.struggles(log,'1','name','upper'),{
    stillNeedsPractice:['B','F'],
    improved:[{letter:'E',firstStruggle:day(1),lastStruggle:day(1),correctSince:day(2)}]});
});

test('struggles count mixed Checks for their letters, list in Case order, and keep Learners and Skills apart',()=>{
  const log=logOf(
    ['MIX',day(1),[{letter:'Z',mark:'incorrect'},{letter:'z',mark:'unsure'},{letter:'A',mark:'unsure'}],{c:'mixed'}],
    ['UP',day(2),[{letter:'Z',mark:'correct'}]],
    ['CHILD-2',day(3),[{letter:'Q',mark:'incorrect'}],{learner:'2'}],
    ['SOUND',day(4),[{letter:'Q',mark:'incorrect'}],{skill:'sound'}]);
  const s=(...a)=>L.struggles(log,...a);
  assert.deepEqual(s('1','name','upper'),{stillNeedsPractice:['A'],improved:[{letter:'Z',firstStruggle:day(1),lastStruggle:day(1),correctSince:day(2)}]});
  assert.deepEqual(s('1','name','lower'),{stillNeedsPractice:['z'],improved:[]});
  assert.deepEqual(s('1','name','mixed').stillNeedsPractice,['A','z']);
  assert.deepEqual(s('2','name','upper'),{stillNeedsPractice:['Q'],improved:[]});
  assert.deepEqual(s('1','sound','upper'),{stillNeedsPractice:['Q'],improved:[]});
});

test("progress: one point per Check record holding the Case's letters, oldest first, counting letters whose latest non-Skip Mark is Correct",()=>{
  const log=logOf(
    ['F-2',day(2),[{letter:'A',mark:'skip'},{letter:'B',mark:'correct'},{letter:'C',mark:'incorrect'}]],
    ['F-1',day(1),[{letter:'A',mark:'correct'},{letter:'B',mark:'unsure'}]],
    ['F-3',day(3),[{letter:'B',mark:'incorrect'},{letter:'C',mark:'correct'},{letter:'D',mark:'correct'}]]);
  assert.deepEqual(L.progress(log,'1','name','upper'),[
    {date:day(1),formId:'F-1',correct:1,total:26},
    {date:day(2),formId:'F-2',correct:2,total:26},
    {date:day(3),formId:'F-3',correct:3,total:26}]);
});

test('progress counts a mixed Check towards uppercase and lowercase, out of 52 for mixed, and keeps Learners and Skills apart',()=>{
  const log=logOf(
    ['UP',day(1),[{letter:'A',mark:'correct'}]],
    ['MIX',day(2),[{letter:'B',mark:'correct'},{letter:'b',mark:'correct'},{letter:'c',mark:'incorrect'}],{c:'mixed'}],
    ['CHILD-2',day(3),[{letter:'C',mark:'correct'}],{learner:'2'}],
    ['SOUND',day(4),[{letter:'D',mark:'correct'}],{skill:'sound'}]);
  const points=(...a)=>L.progress(log,...a).map(p=>[p.formId,p.correct,p.total]);
  assert.deepEqual(points('1','name','upper'),[['UP',1,26],['MIX',2,26]]);
  assert.deepEqual(points('1','name','lower'),[['MIX',1,26]]);
  assert.deepEqual(points('1','name','mixed'),[['UP',1,52],['MIX',3,52]]);
  assert.deepEqual(points('2','name','upper'),[['CHILD-2',1,26]]);
  assert.deepEqual(points('1','sound','upper'),[['SOUND',1,26]]);
});

test("the last progress point equals the Today grid's Correct total when both are built from the same saves",()=>{
  const R=globalThis.SonelireResults,saves=[
    ['F-1',day(1),[{letter:'A',mark:'correct'},{letter:'B',mark:'incorrect'},{letter:'C',mark:'skip'}]],
    ['MIX',day(2),[{letter:'B',mark:'correct'},{letter:'a',mark:'correct'},{letter:'A',mark:'skip'},{letter:'C',mark:'correct'}],{c:'mixed'}],
    ['F-3',day(3),[{letter:'C',mark:'unsure'},{letter:'D',mark:'skip'}]],
    ['F-3',day(4),[{letter:'C',mark:'incorrect'},{letter:'D',mark:'correct'}]],
    ['F-5',day(5),[{letter:'A',mark:'incorrect'},{letter:'E',mark:'skip'}]]];
  let log=L.empty(),results=R.empty();
  for(const [formId,date,marks,opts] of saves){
    const saved=completed(formId,marks,opts);
    log=L.record(log,saved,date);results=R.recordCheck(results,saved,date);
  }
  for(const c of ['upper','lower','mixed'])
    assert.equal(L.progress(log,'1','name',c).at(-1).correct,R.summarize(results,'1','name',c).correct,c);
});
