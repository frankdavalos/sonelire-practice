/* Sonelire Check log: one Check record per saved Check (changed only by Clear these results), and the last backup time (see CONTEXT.md, docs/adr/0002).
   A Check record is {date, learner, skill, case, formId, shownCount, marks:[{letter, mark}]} for the shown letters. */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  const R=root.SonelireResults||(typeof require==='function'&&(require('./results.js'),root.SonelireResults));
  const allLetters=new Set(V.lettersFor('mixed'));
  const makeRecord=r=>Object.freeze({date:r.date,learner:r.learner,skill:r.skill,case:r.case,formId:r.formId,shownCount:r.shownCount,
    marks:Object.freeze(r.marks.map(({letter,mark})=>Object.freeze({letter,mark})))});
  const make=(records,lastBackup=null)=>Object.freeze({checks:Object.freeze(records.map(makeRecord)),lastBackup});
  const empty=()=>make([]);
  /* date: ISO string of the latest Backup file export, or null for never. */
  const withLastBackup=(log,date)=>make(log.checks,date);
  /* completed: Check module complete() output. A Check record with the same Form ID is replaced. */
  function record(log,{learner,skill,case:c,formId,shownCount,marks},date){
    return make([...log.checks.filter(r=>r.formId!==formId),{date,learner,skill,case:c,formId,shownCount,marks}],log.lastBackup);
  }
  const forLearner=(log,learner,skill)=>log.checks.filter(r=>r.learner===learner&&r.skill===skill);
  const newestFirst=(a,b)=>b.date.localeCompare(a.date);
  const oldestFirst=(log,learner,skill)=>forLearner(log,learner,skill).sort((a,b)=>-newestFirst(a,b));
  const includesCase=c=>{const inCase=new Set(V.lettersFor(c));return r=>r.marks.some(m=>inCase.has(m.letter))};
  /* Checks for one Learner and Skill that include any of the Case's letters, newest first, with each Check's own counts. */
  function checks(log,learner,skill,c){
    return forLearner(log,learner,skill).filter(includesCase(c)).sort(newestFirst).map(r=>{
        const count=(...ms)=>r.marks.filter(m=>ms.includes(m.mark)).length;
        return {date:r.date,formId:r.formId,case:r.case,shownCount:r.shownCount,correct:count('correct'),needsPractice:count('incorrect','unsure'),skip:count('skip')};
      });
  }
  /* Every Check record holding the letter, newest first: [{date, formId, mark}], Skips included. */
  function letterHistory(log,learner,skill,letter){
    return forLearner(log,learner,skill).sort(newestFirst).flatMap(r=>r.marks.filter(m=>m.letter===letter).map(m=>({date:r.date,formId:r.formId,mark:m.mark})));
  }
  const struggle=m=>m==='incorrect'||m==='unsure';
  /* Letters of the Case that were ever Incorrect or Unsure, by standing (latest non-Skip Mark):
     {stillNeedsPractice:[letter], improved:[{letter, firstStruggle, lastStruggle, correctSince}]}, in Case order. */
  function struggles(log,learner,skill,c){
    const records=oldestFirst(log,learner,skill),result={stillNeedsPractice:[],improved:[]};
    for(const letter of V.lettersFor(c)){
      let standing=null,firstStruggle=null,lastStruggle=null,correctSince=null;
      for(const r of records)for(const {mark} of r.marks.filter(m=>m.letter===letter)){
        if(mark==='skip')continue;
        standing=mark;
        if(struggle(mark)){firstStruggle??=r.date;lastStruggle=r.date;correctSince=null}
        else correctSince??=r.date;
      }
      if(!firstStruggle)continue;
      if(struggle(standing))result.stillNeedsPractice.push(letter);
      else result.improved.push({letter,firstStruggle,lastStruggle,correctSince});
    }
    return result;
  }
  /* One point per Check that includes any of the Case's letters, oldest first: {date, formId, correct, total}, where
     correct counts the Case's letters whose latest non-Skip Mark as of that Check is Correct. */
  function progress(log,learner,skill,c){
    const letters=V.lettersFor(c),standing=new Map();
    return oldestFirst(log,learner,skill).filter(includesCase(c)).map(r=>{
      for(const {letter,mark} of r.marks)if(mark!=='skip')standing.set(letter,mark);
      return {date:r.date,formId:r.formId,correct:letters.filter(l=>standing.get(l)==='correct').length,total:letters.length};
    });
  }
  /* Returns a new Check log without the Case's letters' Marks in this Learner and Skill's Check records; records left with no Marks are deleted. */
  function clear(log,learner,skill,c){
    const inCase=new Set(V.lettersFor(c));
    return make(log.checks.flatMap(r=>{
      if(r.learner!==learner||r.skill!==skill)return [r];
      const marks=r.marks.filter(m=>!inCase.has(m.letter));
      return marks.length?[{...r,shownCount:marks.length,marks}]:[];
    }),log.lastBackup);
  }
  const backupAge=30*24*60*60*1000;
  /* now: Date. True when a Check record saved after the last backup (or any, if never backed up) is more than 30 days old. */
  function needsBackup(log,now){
    const notBackedUp=r=>log.lastBackup===null||Date.parse(r.date)>Date.parse(log.lastBackup);
    return log.checks.some(r=>notBackedUp(r)&&now-Date.parse(r.date)>backupAge);
  }
  const toStored=log=>({version:1,lastBackup:log.lastBackup,checks:log.checks.map(r=>({...r,marks:r.marks.map(m=>({...m}))}))});
  const isText=s=>typeof s==='string'&&s.length>0;
  const isCase=c=>{try{V.lettersFor(c);return true}catch(e){return false}};
  const readable=r=>r&&isText(r.date)&&R.learners.includes(r.learner)&&['name','sound'].includes(r.skill)&&isCase(r.case)&&isText(r.formId)
    &&Array.isArray(r.marks)&&r.shownCount===r.marks.length&&r.marks.every(m=>m&&allLetters.has(m.letter)&&V.marks.includes(m.mark));
  /* Nothing saved, an unknown version or any unreadable Check record restores as an empty Check log; an unreadable last backup time as never. */
  function restore(stored){
    if(stored?.version!==1||!Array.isArray(stored.checks)||!stored.checks.every(readable))return empty();
    return make(stored.checks,isText(stored.lastBackup)?stored.lastBackup:null);
  }
  root.SonelireCheckLog=Object.freeze({empty,withLastBackup,record,checks,letterHistory,struggles,progress,clear,needsBackup,toStored,restore});
})(globalThis);
