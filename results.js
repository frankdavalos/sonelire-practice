/* Sonelire Results: the latest saved Mark per Learner, Skill and letter (see CONTEXT.md).
   Works on the v1 stored shape results[learner][skill][letter]={status,date,form} (docs/adr/0001). */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  /* saved: Check module complete() output. Returns new results; a Skip never overwrites an existing Result. */
  function recordCheck(results,saved,date){
    const map={...results[saved.learner][saved.skill]};
    for(const {letter,mark} of saved.marks)if(mark!=='skip'||!map[letter])map[letter]={status:V.toStored(mark),date,form:saved.formId};
    return {...results,[saved.learner]:{...results[saved.learner],[saved.skill]:map}};
  }
  root.SonelireResults=Object.freeze({recordCheck});
})(globalThis);
