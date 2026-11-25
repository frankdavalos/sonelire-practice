/* Sonelire Companion record: the phone's Marks and position for one Form (see CONTEXT.md). */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  const P=root.CompanionProtocol||(typeof require==='function'&&(require('./companion-protocol.js'),root.CompanionProtocol));
  /* The localStorage key holding this Form's saved record. */
  const key=form=>'sonelire-companion-v1:'+P.encodeForm(form);
  function make(r){return Object.freeze({...r,marks:Object.freeze({...r.marks}),history:Object.freeze([...r.history])});}
  const isItem=(r,i)=>Number.isInteger(i)&&i>=0&&i<r.form.seq.length;
  function fromStored(v){try{return V.fromStored(v)}catch(e){return null}}
  /* stored: the v1 saved value {scores, index} (docs/adr/0001), or null. Entries that don't fit the Form are dropped. */
  function open(form,stored){
    const r={form,marks:{},position:0,history:[]};
    for(const [i,v] of Object.entries(stored?.scores||{})){const m=fromStored(v);if(m&&isItem(r,+i)&&String(+i)===i)r.marks[i]=m;}
    if(isItem(r,stored?.index))r.position=stored.index;
    return make(r);
  }
  const currentLetter=r=>r.form.seq[r.position];
  const markedCount=r=>Object.keys(r.marks).length;
  const canUndo=r=>r.history.length>0;
  function goTo(r,i){if(!isItem(r,i))throw Error('No such item.');return make({...r,position:i});}
  function withMark(marks,i,m){marks={...marks};if(m)marks[i]=m;else delete marks[i];return marks;}
  function change(r,m,position){return make({...r,marks:withMark(r.marks,r.position,m),position,history:[...r.history,{position:r.position,old:r.marks[r.position]}]});}
  function mark(r,m){if(!V.marks.includes(m))throw Error('Invalid mark.');return change(r,m,Math.min(r.position+1,r.form.seq.length-1));}
  function clear(r){return change(r,null,r.position);}
  function undo(r){if(!canUndo(r))return r;const {position,old}=r.history.at(-1);return make({...r,marks:withMark(r.marks,position,old),position,history:r.history.slice(0,-1)});}
  function toStored(r){const scores={};for(const [i,m] of Object.entries(r.marks))scores[i]=V.toStored(m);return {scores,index:r.position};}
  const resultsCode=r=>P.encodeResults(r.form,r.marks);
  root.SonelireCompanionRecord=Object.freeze({key,open,toStored,resultsCode,currentLetter,markedCount,canUndo,goTo,mark,clear,undo});
})(globalThis);
