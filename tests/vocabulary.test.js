// Run from repository root: node --test tests/
const test=require('node:test'),assert=require('node:assert/strict');require('../vocabulary.js');const V=globalThis.SonelireVocabulary;

test('letters for each Case, mixed pairs uppercase with lowercase',()=>{
  assert.equal(V.lettersFor('upper').join(''),'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
  assert.equal(V.lettersFor('lower').join(''),'abcdefghijklmnopqrstuvwxyz');
  assert.equal(V.lettersFor('mixed').slice(0,4).join(''),'AaBb');
  assert.equal(V.lettersFor('mixed').length,52);
  assert.throws(()=>V.lettersFor('title'));
});

test('Marks translate to wire characters, stored values, keys and labels',()=>{
  assert.deepEqual(V.marks,['correct','incorrect','unsure','skip']);
  assert.equal(V.marks.map(V.toWire).join(''),'CINS');
  assert.deepEqual([...'CINS'].map(V.fromWire),V.marks);
  assert.equal(V.toStored('incorrect'),'miss');
  assert.equal(V.fromStored('miss'),'incorrect');
  assert.equal(V.fromStored('correct'),'correct');
  assert.equal(V.fromKey('I'),'incorrect');
  assert.equal(V.fromKey('x'),null);
  assert.equal(V.label('unsure'),'Unsure / no response');
  assert.equal(V.buttonLabel('unsure'),'Unsure');
  assert.throws(()=>V.toWire('miss'));
  assert.throws(()=>V.fromStored('bogus'));
  assert.throws(()=>V.fromWire('X'));
});
