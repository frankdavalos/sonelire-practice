/* Sonelire companion transport v1. No learner identifiers or network requests. */
(function (root) {
  'use strict';
  const V=root.SonelireVocabulary||(typeof require==='function'&&(require('./vocabulary.js'),root.SonelireVocabulary));
  function expected(c){try{return V.lettersFor(c)}catch(e){return null}}
  function validForm(d){const exp=expected(d.case);return typeof d.id==='string'&&/^[A-Za-z0-9-]{1,64}$/.test(d.id)&&['name','sound'].includes(d.skill)&&!!exp&&Array.isArray(d.seq)&&d.seq.length===exp.length&&d.seq.every(x=>typeof x==='string'&&x.length===1)&&[...d.seq].sort().join('')===[...exp].sort().join('');}
  function encodeForm(d){if(!validForm(d))throw Error('Invalid assessment form.');return ['SON1A',d.id,d.skill,d.case,d.seq.join('')].join('.');}
  function decodeForm(code){const p=String(code).trim().split('.');if(p.length!==5||p[0]!=='SON1A')throw Error('Invalid companion link.');const d={id:p[1],skill:p[2],case:p[3],seq:[...p[4]]};if(!validForm(d))throw Error('Invalid assessment form.');return d;}
  /* marks: index -> Mark; unmarked letters travel as '-'. */
  function encodeResults(d,marks){const f=encodeForm(d);const wire=d.seq.map((_,i)=>marks[i]==null?'-':V.toWire(marks[i])).join('');return f.replace('SON1A','SON1R')+'.'+wire;}
  /* Returns {form, marks} where marks[i] is a Mark or null. */
  function decodeResults(code){const p=String(code).trim().split('.');if(p.length!==6||p[0]!=='SON1R')throw Error('Invalid results code.');const d=decodeForm(['SON1A',...p.slice(1,5)].join('.'));if(p[5].length!==d.seq.length||!/^[CINS-]+$/.test(p[5]))throw Error('Invalid marks.');return {form:d,marks:[...p[5]].map(c=>c==='-'?null:V.fromWire(c))};}
  function formUrl(d,base){const u=new URL('companion.html',base);u.hash='form='+encodeForm(d);return u.href;}
  function resultUrl(code,base){decodeResults(code);const u=new URL('sonelire-practice.html',base);u.hash='sonelire-result='+code;return u.href;}
  function renderQR(el,value){el.replaceChildren();if(!root.SonelireQR)throw Error('QR library unavailable. Use the link or results code instead.');const qr=new root.SonelireQR.QRCode(-1,root.SonelireQR.levels.M);qr.addData(value);qr.make();const n=qr.getModuleCount(),ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 ${n+8} ${n+8}`);svg.setAttribute('role','img');svg.setAttribute('aria-label','Scannable QR code');svg.setAttribute('shape-rendering','crispEdges');svg.style.cssText='display:block;width:100%;max-width:320px;height:auto;background:white';const bg=document.createElementNS(ns,'rect');bg.setAttribute('width',n+8);bg.setAttribute('height',n+8);bg.setAttribute('fill','white');svg.append(bg);let path='';for(let y=0;y<n;y++)for(let x=0;x<n;x++)if(qr.isDark(y,x))path+=`M${x+4} ${y+4}h1v1h-1z`;const ink=document.createElementNS(ns,'path');ink.setAttribute('d',path);ink.setAttribute('fill','black');svg.append(ink);el.append(svg);}
  root.CompanionProtocol=Object.freeze({encodeForm,decodeForm,encodeResults,decodeResults,formUrl,resultUrl,renderQR});
})(globalThis);
