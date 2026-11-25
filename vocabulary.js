/* Sonelire shared vocabulary: Cases and Marks (see CONTEXT.md). */
(function (root) {
  'use strict';
  const upper=[...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'],lower=upper.map(x=>x.toLowerCase());
  const byCase={upper,lower,mixed:upper.flatMap((x,i)=>[x,lower[i]])};
  function lettersFor(c){if(!Object.hasOwn(byCase,c))throw Error('Unknown case: '+c);return [...byCase[c]];}
  // Stored 'miss' is the v1 storage name for Incorrect (docs/adr/0001).
  const table=[
    {mark:'correct',wire:'C',stored:'correct',key:'c',label:'Correct',button:'Correct'},
    {mark:'incorrect',wire:'I',stored:'miss',key:'i',label:'Incorrect',button:'Incorrect'},
    {mark:'unsure',wire:'N',stored:'unsure',key:'n',label:'Unsure / no response',button:'Unsure'},
    {mark:'skip',wire:'S',stored:'skip',key:'s',label:'Skipped',button:'Skip'}];
  const marks=Object.freeze(table.map(r=>r.mark));
  function find(field,value){const r=table.find(r=>r[field]===value);if(!r)throw Error('Invalid mark.');return r;}
  const toWire=m=>find('mark',m).wire,fromWire=c=>find('wire',c).mark;
  const toStored=m=>find('mark',m).stored,fromStored=s=>find('stored',s).mark;
  const label=m=>find('mark',m).label,buttonLabel=m=>find('mark',m).button;
  function fromKey(k){const r=table.find(r=>r.key===String(k).toLowerCase());return r?r.mark:null;}
  root.SonelireVocabulary=Object.freeze({lettersFor,marks,toWire,fromWire,toStored,fromStored,fromKey,label,buttonLabel});
})(globalThis);
