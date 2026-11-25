/* Sonelire Check lifecycle: pure transitions over an Unfinished check (see CONTEXT.md). */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  const P=root.CompanionProtocol||(typeof require==='function'&&(require('./companion-protocol.js'),root.CompanionProtocol));
  function defaultId(){return root.crypto?.randomUUID?root.crypto.randomUUID():Date.now().toString(36).toUpperCase()+'-'+Math.random().toString(36).slice(2,10);}
  function shuffle(a,random){for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
  /* order: 'random' or 'alpha'. */
  function prepareForm(skill,c,order,{random=Math.random,newId=defaultId}={}){const seq=V.lettersFor(c);if(order==='random')shuffle(seq,random);return {id:newId(),skill,case:c,seq};}
  function make(c){return Object.freeze({...c,form:Object.freeze({...c.form,seq:Object.freeze([...c.form.seq])}),marks:Object.freeze({...c.marks})});}
  function inPhase(c,phase){if(!c||c.phase!==phase)throw Error(`Check is not in ${phase}.`);}
  function begin(learner,form){return make({learner,form,phase:'presentation',position:0,shownCount:1,marks:{}});}
  const currentLetter=c=>c.form.seq[c.position];
  function next(c){inPhase(c,'presentation');if(c.position===c.form.seq.length-1)return endPresentation(c);const position=c.position+1;return make({...c,position,shownCount:Math.max(c.shownCount,position+1)});}
  function back(c){inPhase(c,'presentation');if(c.position===0)throw Error('Already at the first letter.');return make({...c,position:c.position-1});}
  function endPresentation(c){inPhase(c,'presentation');return make({...c,phase:'marking'});}
  /* mark: a Mark, or null to clear. */
  function mark(c,index,m){inPhase(c,'marking');if(!Number.isInteger(index)||index<0||index>=c.shownCount)throw Error('Only shown letters can be marked.');if(m!==null&&!V.marks.includes(m))throw Error('Invalid mark.');const marks={...c.marks};if(m===null)delete marks[index];else marks[index]=m;return make({...c,marks});}
  function markRemainingCorrect(c){inPhase(c,'marking');const marks={...c.marks};for(let i=0;i<c.shownCount;i++)if(!marks[i])marks[i]='correct';return make({...c,marks});}
  function clearMarks(c){inPhase(c,'marking');return make({...c,marks:{}});}
  const markedCount=c=>Object.keys(c.marks).length;
  const canComplete=c=>c.phase==='marking'&&markedCount(c)===c.shownCount;
  /* Returns the saved Check: {learner, skill, case, formId, shownCount, marks:[{letter, mark}]} for shown letters. */
  function complete(c){if(!canComplete(c))throw Error('Mark every shown letter before saving.');return {learner:c.learner,skill:c.form.skill,case:c.form.case,formId:c.form.id,shownCount:c.shownCount,marks:c.form.seq.slice(0,c.shownCount).map((letter,i)=>({letter,mark:c.marks[i]}))};}
  /* Validates a Results code against this Check. Returns {formId, marks, conflicts:[letter]}; throws parent-readable errors. */
  function previewImport(c,code){
    if(!c||c.phase!=='marking')throw Error('Finish the iPad presentation and open Enter results first.');
    const r=P.decodeResults(code);
    if(P.encodeForm(c.form)!==P.encodeForm(r.form))throw Error('This code belongs to a different assessment form.');
    if(r.marks.slice(c.shownCount).some(m=>m!==null))throw Error('The phone has marks for letters not shown. Correct those marks on the phone before importing.');
    const marks={};
    for(let i=0;i<c.shownCount;i++){if(r.marks[i]===null)throw Error('Missing response for item '+(i+1)+'. Mark it on the phone or use manual entry.');marks[i]=r.marks[i];}
    const conflicts=Object.keys(c.marks).filter(i=>c.marks[i]!==marks[i]).map(i=>c.form.seq[i]);
    return {formId:c.form.id,marks,conflicts};
  }
  function applyImport(c,preview){inPhase(c,'marking');if(preview.formId!==c.form.id)throw Error('This code belongs to a different assessment form.');return make({...c,marks:preview.marks});}
  /* v1 stored draft shape (docs/adr/0001; loaded and saved by storage.js): status 'present'|'paused'|'scoring', scores use stored Mark values. */
  function restore(s){const marks={};for(const [i,v] of Object.entries(s.scores||{}))marks[i]=V.fromStored(v);return make({learner:s.learner,form:{id:s.id,skill:s.skill,case:s.case,seq:s.seq},phase:s.status==='scoring'?'marking':'presentation',position:s.position,shownCount:s.shown,marks});}
  function toStored(c){const scores={};for(const [i,m] of Object.entries(c.marks))scores[i]=V.toStored(m);return {learner:c.learner,case:c.form.case,skill:c.form.skill,seq:[...c.form.seq],id:c.form.id,position:c.position,shown:c.shownCount,status:c.phase==='marking'?'scoring':'present',scores};}
  root.SonelireCheck=Object.freeze({prepareForm,begin,currentLetter,next,back,endPresentation,mark,markRemainingCorrect,clearMarks,markedCount,canComplete,complete,previewImport,applyImport,restore,toStored});
})(globalThis);
