/* Sonelire Check log: one permanent Check record per saved Check (see CONTEXT.md, docs/adr/0002).
   A Check record is {date, learner, skill, case, formId, shownCount, marks:[{letter, mark}]} for the shown letters. */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  const R=root.SonelireResults||(typeof require==='function'&&(require('./results.js'),root.SonelireResults));
  const allLetters=new Set(V.lettersFor('mixed'));
  const makeRecord=r=>Object.freeze({date:r.date,learner:r.learner,skill:r.skill,case:r.case,formId:r.formId,shownCount:r.shownCount,
    marks:Object.freeze(r.marks.map(({letter,mark})=>Object.freeze({letter,mark})))});
  const make=records=>Object.freeze({checks:Object.freeze(records.map(makeRecord))});
  const empty=()=>make([]);
  /* completed: Check module complete() output. A Check record with the same Form ID is replaced. */
  function record(log,{learner,skill,case:c,formId,shownCount,marks},date){
    return make([...log.checks.filter(r=>r.formId!==formId),{date,learner,skill,case:c,formId,shownCount,marks}]);
  }
  /* Checks for one Learner and Skill that include any of the Case's letters, newest first, with each Check's own counts. */
  function checks(log,learner,skill,c){
    const inCase=new Set(V.lettersFor(c));
    return log.checks.filter(r=>r.learner===learner&&r.skill===skill&&r.marks.some(m=>inCase.has(m.letter)))
      .sort((a,b)=>b.date.localeCompare(a.date)).map(r=>{
        const count=(...ms)=>r.marks.filter(m=>ms.includes(m.mark)).length;
        return {date:r.date,formId:r.formId,case:r.case,shownCount:r.shownCount,correct:count('correct'),needsPractice:count('incorrect','unsure'),skip:count('skip')};
      });
  }
  const toStored=log=>({version:1,lastBackup:null,checks:log.checks.map(r=>({...r,marks:r.marks.map(m=>({...m}))}))});
  const isText=s=>typeof s==='string'&&s.length>0;
  const isCase=c=>{try{V.lettersFor(c);return true}catch(e){return false}};
  const readable=r=>r&&isText(r.date)&&R.learners.includes(r.learner)&&['name','sound'].includes(r.skill)&&isCase(r.case)&&isText(r.formId)
    &&Array.isArray(r.marks)&&r.shownCount===r.marks.length&&r.marks.every(m=>m&&allLetters.has(m.letter)&&V.marks.includes(m.mark));
  /* Nothing saved, an unknown version or any unreadable Check record restores as an empty Check log. */
  function restore(stored){
    if(stored?.version!==1||!Array.isArray(stored.checks)||!stored.checks.every(readable))return empty();
    return make(stored.checks);
  }
  root.SonelireCheckLog=Object.freeze({empty,record,checks,toStored,restore});
})(globalThis);
