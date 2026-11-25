/* Sonelire saved data: the selected Learner, Results and Unfinished check, behind a storage adapter,
   plus the Check log under its own key (docs/adr/0002).
   Keeps the v1 stored blob {version:1, learner, results, draft} exactly; draft is the stored Unfinished check (docs/adr/0001).
   An adapter is {read(): string|null, write(text)}. */
(function (root) {
  'use strict';
  const R=root.SonelireResults||(typeof require==='function'&&(require('./results.js'),root.SonelireResults));
  const L=root.SonelireCheckLog||(typeof require==='function'&&(require('./check-log.js'),root.SonelireCheckLog));
  const KEY='sonelire-practice-v2',LOG_KEY='sonelire-check-log-v1';
  /* Reads and writes throw when the browser's storage is unavailable. */
  function local(key=KEY){return {read:()=>root.localStorage.getItem(key),write:t=>root.localStorage.setItem(key,t)};}
  function memory(text=null){return {read:()=>text,write:t=>{text=t}};}
  /* Returns {learner, results, unfinishedCheck} (unfinishedCheck in Check's stored form, or null).
     Nothing saved, an unknown version or incomplete data loads as a fresh start.
     Throws when storage is unavailable or the saved text is not JSON. */
  function load(adapter){
    const saved=JSON.parse(adapter.read());
    if(!saved||saved.version!==1||!R.learners.every(l=>saved.results?.[l]))return {learner:'1',results:R.empty(),unfinishedCheck:null};
    return {learner:R.learners.includes(saved.learner)?saved.learner:'1',results:saved.results,unfinishedCheck:saved.draft??null};
  }
  /* Returns the text written; the adapter's write errors propagate. */
  function save(adapter,{learner,results,unfinishedCheck}){const text=JSON.stringify({version:1,learner,results,draft:unfinishedCheck});adapter.write(text);return text;}
  /* Nothing saved or unreadable text loads as an empty Check log; throws when storage is unavailable. */
  function loadLog(adapter){
    const text=adapter.read();
    try{return L.restore(JSON.parse(text))}catch(e){return L.empty()}
  }
  /* Saves a Check: writes the Check log first, and the saved state only if that succeeds. Write errors propagate. */
  function saveWithLog(adapter,logAdapter,state,log){logAdapter.write(JSON.stringify(L.toStored(log)));return save(adapter,state);}
  root.SonelireStorage=Object.freeze({KEY,LOG_KEY,local,memory,load,save,loadLog,saveWithLog});
})(globalThis);
