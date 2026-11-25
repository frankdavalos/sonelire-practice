// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../results.js');const R=globalThis.SonelireResults;

const empty=R.empty;
const saved=(marks)=>({learner:'1',skill:'name',formId:'F-2',marks});

test('recordCheck stores each saved Mark as the latest Result, with date and Form',()=>{
  const before=empty();
  const after=R.recordCheck(before,saved([{letter:'A',mark:'correct'},{letter:'B',mark:'incorrect'}]),'2026-11-24T10:00:00.000Z');
  assert.deepEqual(after['1'].name,{A:{status:'correct',date:'2026-11-24T10:00:00.000Z',form:'F-2'},B:{status:'miss',date:'2026-11-24T10:00:00.000Z',form:'F-2'}});
  assert.deepEqual(after['1'].sound,{});assert.deepEqual(after['2'],empty()['2']);
  assert.deepEqual(before,empty());
});

test('a Skip never overwrites an existing Result, but is recorded when there is none',()=>{
  const before=empty();before['1'].name.A={status:'miss',date:'2026-11-01T00:00:00.000Z',form:'F-1'};
  const after=R.recordCheck(before,saved([{letter:'A',mark:'skip'},{letter:'B',mark:'skip'}]),'2026-11-24T10:00:00.000Z');
  assert.deepEqual(after['1'].name.A,before['1'].name.A);
  assert.deepEqual(after['1'].name.B,{status:'skip',date:'2026-11-24T10:00:00.000Z',form:'F-2'});
});

const at=(status)=>({status,date:'2026-11-01T00:00:00.000Z',form:'F-1'});

test('summarize gives each letter of the Case its Mark, and totals Correct, Needs practice and Not assessed',()=>{
  const results=empty();Object.assign(results['1'].name,{A:at('correct'),B:at('miss'),C:at('unsure'),D:at('skip'),a:at('miss')});
  const s=R.summarize(results,'1','name','upper');
  assert.deepEqual(s.letters.slice(0,5).map(({letter,mark})=>({letter,mark})),[{letter:'A',mark:'correct'},{letter:'B',mark:'incorrect'},{letter:'C',mark:'unsure'},{letter:'D',mark:'skip'},{letter:'E',mark:null}]);
  assert.equal(s.letters.length,26);
  assert.deepEqual({correct:s.correct,needsPractice:s.needsPractice,notAssessed:s.notAssessed},{correct:1,needsPractice:2,notAssessed:23});
});

test('summarize gives each letter its last-checked date as stored, or null when it has no Result',()=>{
  const results=empty();Object.assign(results['1'].name,{A:{status:'correct',date:'2026-11-12T18:45:09.123Z',form:'F-3'},B:at('skip')});
  const s=R.summarize(results,'1','name','upper');
  assert.deepEqual(s.letters.slice(0,3).map(({letter,date})=>({letter,date})),[{letter:'A',date:'2026-11-12T18:45:09.123Z'},{letter:'B',date:'2026-11-01T00:00:00.000Z'},{letter:'C',date:null}]);
});

test('needsPractice lists the Incorrect and Unsure letters of the Case, in Case order',()=>{
  const results=empty();Object.assign(results['1'].sound,{z:at('unsure'),B:at('miss'),b:at('correct'),D:at('skip'),a:at('miss')});results['2'].sound.C=at('miss');
  assert.deepEqual(R.needsPractice(results,'1','sound','mixed'),['a','B','z']);
  assert.deepEqual(R.needsPractice(results,'1','sound','upper'),['B']);
  assert.deepEqual(R.needsPractice(results,'1','name','mixed'),[]);
});

test('clear removes the Results of one Learner, Skill and Case only, without changing the input',()=>{
  const before=empty();Object.assign(before['1'].name,{A:at('miss'),a:at('correct')});before['1'].sound.A=at('miss');before['2'].name.A=at('miss');
  const after=R.clear(before,'1','name','upper');
  assert.deepEqual(after['1'].name,{a:at('correct')});
  assert.deepEqual(after['1'].sound,{A:at('miss')});assert.deepEqual(after['2'].name,{A:at('miss')});
  assert.ok(before['1'].name.A);
  assert.deepEqual(R.clear(before,'1','name','mixed')['1'].name,{});
});
