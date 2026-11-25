// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../results.js');const R=globalThis.SonelireResults;

const empty=()=>({'1':{name:{},sound:{}},'2':{name:{},sound:{}}});
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
