/* Sonelire Results: the latest saved Mark per Learner, Skill and letter (see CONTEXT.md).
   Works on the v1 stored shape results[learner][skill][letter]={status,date,form} (docs/adr/0001). */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  const learners=Object.freeze(['1','2']);
  const empty=()=>Object.fromEntries(learners.map(l=>[l,{name:{},sound:{}}]));
  const withMap=(results,learner,skill,map)=>({...results,[learner]:{...results[learner],[skill]:map}});
  /* saved: Check module complete() output. Returns new results; a Skip never overwrites an existing Result. */
  function recordCheck(results,saved,date){
    const map={...results[saved.learner][saved.skill]};
    for(const {letter,mark} of saved.marks)if(mark!=='skip'||!map[letter])map[letter]={status:V.toStored(mark),date,form:saved.formId};
    return withMap(results,saved.learner,saved.skill,map);
  }
  const needsPracticeMark=m=>m==='incorrect'||m==='unsure';
  /* Each letter of the Case with its Mark (null when there is no Result), plus totals. Skip counts as Not assessed. */
  function summarize(results,learner,skill,c){
    const map=results[learner][skill]||{};
    const letters=V.lettersFor(c).map(letter=>({letter,mark:map[letter]?V.fromStored(map[letter].status):null}));
    const correct=letters.filter(l=>l.mark==='correct').length,needing=letters.filter(l=>needsPracticeMark(l.mark)).length;
    return {letters,correct,needsPractice:needing,notAssessed:letters.length-correct-needing};
  }
  /* The letters of the Case that Need practice, in Case order. */
  function needsPractice(results,learner,skill,c){return summarize(results,learner,skill,c).letters.filter(l=>needsPracticeMark(l.mark)).map(l=>l.letter);}
  /* Returns new results without this Learner's Results for the Case's letters in one Skill. */
  function clear(results,learner,skill,c){
    const map={...results[learner][skill]};
    for(const letter of V.lettersFor(c))delete map[letter];
    return withMap(results,learner,skill,map);
  }
  root.SonelireResults=Object.freeze({learners,empty,recordCheck,summarize,needsPractice,clear});
})(globalThis);
