/* Sonelire Backup file: both Learners' Results (v1 stored form, docs/adr/0001) and every Check record, never the Unfinished check.
   The file is {format:'sonelire-backup', version:1, exportedAt, results, checks}. */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  const R=root.SonelireResults||(typeof require==='function'&&(require('./results.js'),root.SonelireResults));
  const L=root.SonelireCheckLog||(typeof require==='function'&&(require('./check-log.js'),root.SonelireCheckLog));
  /* maxBytes: larger files are refused before they are read. */
  const FORMAT='sonelire-backup',maxBytes=5*1024*1024,allLetters=new Set(V.lettersFor('mixed'));
  /* now: Date of the export. Returns the file text. */
  function exportText(results,log,now){
    return JSON.stringify({format:FORMAT,version:1,exportedAt:now.toISOString(),results,checks:L.toStored(log).checks});
  }
  const pad=n=>String(n).padStart(2,'0');
  const fileName=now=>`sonelire-backup-${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}.json`;
  const isObject=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
  const isStatus=s=>{try{V.fromStored(s);return true}catch(e){return false}};
  const isResult=r=>isObject(r)&&isStatus(r.status)&&typeof r.date==='string'&&typeof r.form==='string';
  const isSkillMap=m=>isObject(m)&&Object.entries(m).every(([letter,r])=>allLetters.has(letter)&&isResult(r));
  const isResults=r=>isObject(r)&&R.learners.every(l=>isObject(r[l])&&isSkillMap(r[l].name)&&isSkillMap(r[l].sound));
  function parse(text){try{return JSON.parse(text)}catch(e){throw Error('This file is not JSON, so it is not a Sonelire backup.')}}
  /* Returns {results, log, exportedAt, summary:{checks:{learner:count}, latest}}; log is last backed up at exportedAt.
     Throws an Error whose message the parent can read when the file is damaged or not a Backup file. */
  function read(text){
    const file=parse(text);
    if(file?.format!==FORMAT)throw Error('This file is not a Sonelire backup.');
    if(file.version!==1)throw Error('This backup was made by a version of Sonelire that this page cannot read.');
    if(typeof file.exportedAt!=='string'||isNaN(Date.parse(file.exportedAt)))throw Error("This backup's export date is damaged.");
    if(!isResults(file.results))throw Error("This backup's results are incomplete or damaged.");
    const restored=Array.isArray(file.checks)&&L.restore({version:1,checks:file.checks});
    if(!restored||restored.checks.length!==file.checks.length)throw Error('This backup has a check record that cannot be read.');
    const log=L.withLastBackup(restored,file.exportedAt);
    const latest=log.checks.map(r=>r.date).sort().at(-1)??null;
    const checks=Object.fromEntries(R.learners.map(l=>[l,log.checks.filter(r=>r.learner===l).length]));
    return {results:file.results,log,exportedAt:file.exportedAt,summary:{checks,latest}};
  }
  root.SonelireBackup=Object.freeze({maxBytes,export:exportText,read,fileName});
})(globalThis);
