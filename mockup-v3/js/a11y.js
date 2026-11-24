/* Barre d'accessibilité : taille du texte, police et espacement, contraste, animations, lecture à voix haute.
   Les réglages sont gardés dans le navigateur (localStorage), jamais envoyés. */
(function(){
  var root=document.documentElement, KEY='bb-a11y', prefs={};
  try{prefs=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(prefs))}catch(e){}}
  var mq=function(q){return window.matchMedia&&matchMedia(q).matches};
  if(prefs.hc===undefined&&mq('(prefers-contrast: more)'))prefs.hc=true;
  if(prefs.rm===undefined&&mq('(prefers-reduced-motion: reduce)'))prefs.rm=true;

  function applyAll(){
    ['fs-1','fs-2','fs-3'].forEach(function(c){root.classList.remove(c)});
    if(prefs.fs)root.classList.add('fs-'+prefs.fs);
    ['dys','sp','hc','rm','calm'].forEach(function(k){root.classList.toggle(k,!!prefs[k])});
    document.dispatchEvent(new Event('a11ychange'));
  }

  /* ---------- lecture à voix haute ---------- */
  var synth=window.speechSynthesis, canSpeak=!!(synth&&window.SpeechSynthesisUtterance);
  var voice=null, current=null, live;
  function pickVoice(){
    if(!canSpeak)return;
    var v=synth.getVoices().filter(function(x){return /^fr/i.test(x.lang)});
    voice=v.filter(function(x){return /fr[-_]FR/i.test(x.lang)&&x.localService})[0]||v.filter(function(x){return /fr[-_]FR/i.test(x.lang)})[0]||v[0]||null;
  }
  if(canSpeak){pickVoice();if(synth.addEventListener)synth.addEventListener('voiceschanged',pickVoice);else synth.onvoiceschanged=pickVoice}

  function textOf(el){
    var c=el.cloneNode(true);
    c.querySelectorAll('.listen,.a11y-ui,[aria-hidden="true"],script,style,button,svg,.sr-only').forEach(function(n){n.remove()});
    c.querySelectorAll('h1,h2,h3,p,li,figcaption,.day,.when').forEach(function(n){n.appendChild(document.createTextNode('. '))});
    c.querySelectorAll('abbr[title]').forEach(function(a){a.textContent=a.getAttribute('title')});
    return c.textContent.replace(/\s+/g,' ').replace(/([.!?…:;])\s*\.\s/g,'$1 ').replace(/\s+\./g,'.').trim();
  }
  function chunks(t){
    var parts=t.match(/[^.!?…]+[.!?…]*\s*/g)||[t],out=[],cur='';
    parts.forEach(function(p){if((cur+p).length>180&&cur){out.push(cur);cur=p}else cur+=p});
    if(cur)out.push(cur);return out;
  }
  function say(msg){if(live){live.textContent='';setTimeout(function(){live.textContent=msg},50)}}
  function stop(silent){
    if(!canSpeak)return;
    synth.cancel();
    if(current){current.setAttribute('aria-pressed','false');setLabel(current,false);current=null}
    if(!silent)say('Lecture arrêtée.');
  }
  function setLabel(btn,on){var t=btn.querySelector('.listen-t');if(t)t.textContent=on?'Arrêter la lecture':(btn.getAttribute('data-label')||'Écouter');btn.setAttribute('aria-label',on?'Arrêter la lecture':(btn.getAttribute('data-aria-label')||btn.getAttribute('data-label')||'Écouter'))}
  function speak(text,btn){
    if(current===btn){stop();return}
    stop(true);
    current=btn;btn.setAttribute('aria-pressed','true');setLabel(btn,true);say('Lecture démarrée.');
    var list=chunks(text);
    list.forEach(function(c,i){
      var u=new SpeechSynthesisUtterance(c);
      u.lang='fr-FR';if(voice)u.voice=voice;u.rate=({lent:0.6,rapide:1.4})[prefs.speed]||0.95;
      if(i===list.length-1){u.onend=u.onerror=function(){if(current===btn){btn.setAttribute('aria-pressed','false');setLabel(btn,false);current=null}}}
      synth.speak(u);
    });
  }
  var ICON='<svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/><path d="M19 6a8.5 8.5 0 0 1 0 12"/></svg>';
  function listenButton(label,getText){
    var b=document.createElement('button');b.type='button';b.className='listen';b.setAttribute('aria-pressed','false');b.setAttribute('data-label',label);
    var accessibleLabel=label==='Écouter'?'Écouter cette partie':label;
    b.setAttribute('data-aria-label',accessibleLabel);b.setAttribute('aria-label',accessibleLabel);b.setAttribute('title',accessibleLabel);
    b.innerHTML=ICON+'<span class="listen-t">'+label+'</span>';
    b.addEventListener('click',function(){speak(getText(),b)});return b;
  }

  /* ---------- barre d'accessibilité ---------- */
  var wrap=document.createElement('div');wrap.className='a11y-ui';
  var open=document.createElement('button');open.type='button';open.className='a11y-btn';open.id='a11y-open';open.setAttribute('aria-expanded','false');open.setAttribute('aria-controls','a11y-panel');
  open.innerHTML='<svg aria-hidden="true" focusable="false" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="4.5" r="2"/><path d="M5 8.5l7 1.5 7-1.5M12 10v5m0 0l-3.5 5.5M12 15l3.5 5.5"/></svg><span>Accessibilité</span>';
  var panel=document.createElement('section');panel.id='a11y-panel';panel.className='a11y-panel';panel.hidden=true;panel.setAttribute('aria-labelledby','a11y-title');
  var rows='<h2 id="a11y-title">Rendre le site plus confortable</h2>'+
   '<div class="a11y-row"><span id="l-fs">Taille du texte</span><div class="a11y-group" role="group" aria-labelledby="l-fs">'+
     '<button type="button" data-fs="0">Normal</button><button type="button" data-fs="1">Grand</button><button type="button" data-fs="2">Très grand</button><button type="button" data-fs="3">Immense</button></div></div>'+
   '<div class="a11y-row"><span id="l-opt">Lecture et confort</span><div class="a11y-group" role="group" aria-labelledby="l-opt">'+
     '<button type="button" data-k="dys">Police pour la dyslexie</button><button type="button" data-k="sp">Texte plus aéré</button><button type="button" data-k="hc">Contraste renforcé</button><button type="button" data-k="rm">Sans animation</button><button type="button" data-k="calm">Mode calme (moins de décor)</button></div></div>';
  if(canSpeak)rows+='<div class="a11y-row"><span id="l-voix">Lecture à voix haute</span><div class="a11y-group" id="a11y-voice"></div><div class="a11y-group" role="group" aria-label="Vitesse de la voix" style="margin-top:8px"><button type="button" data-sp="lent">Lente</button><button type="button" data-sp="normal">Normale</button><button type="button" data-sp="rapide">Rapide</button></div></div>';
  rows+='<div class="a11y-row"><div class="a11y-group"><a href="accessibilite.html#signaler" class="a11y-link">Signaler un problème</a></div><div class="a11y-group" style="margin-top:12px"><button type="button" class="reset" id="a11y-reset">Tout remettre par défaut</button><button type="button" class="reset" id="a11y-close">Fermer</button></div></div>';
  panel.innerHTML=rows;
  if(canSpeak){panel.querySelector('#a11y-voice').insertBefore(listenButton('Écouter toute la page',function(){return textOf(document.getElementById('contenu'))}),panel.querySelector('#a11y-voice').firstChild)}
  live=document.createElement('p');live.className='sr-only';live.setAttribute('role','status');live.setAttribute('aria-live','polite');
  wrap.appendChild(open);wrap.appendChild(panel);wrap.appendChild(live);document.body.appendChild(wrap);

  function refresh(){
    panel.querySelectorAll('[data-fs]').forEach(function(b){b.setAttribute('aria-pressed',String((+b.getAttribute('data-fs'))===(prefs.fs||0)))});
    panel.querySelectorAll('[data-sp]').forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-sp')===(prefs.speed||'normal')))});
    panel.querySelectorAll('[data-k]').forEach(function(b){b.setAttribute('aria-pressed',String(!!prefs[b.getAttribute('data-k')]))});
  }
  panel.addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b||b.classList.contains('listen'))return;
    if(b.hasAttribute('data-fs'))prefs.fs=+b.getAttribute('data-fs');
    else if(b.hasAttribute('data-sp')){prefs.speed=b.getAttribute('data-sp');if(current){var c=current;stop(true);c.click()}}
    else if(b.hasAttribute('data-k')){var k=b.getAttribute('data-k');prefs[k]=!prefs[k]}
    else if(b.id==='a11y-reset'){prefs={hc:false,rm:false};stop(true)}
    else if(b.id==='a11y-close'){toggle(false);open.focus();return}
    save();applyAll();refresh();
  });
  function toggle(v){panel.hidden=!v;open.setAttribute('aria-expanded',String(v));if(v){var f=panel.querySelector('button');f&&f.focus()}}
  open.addEventListener('click',function(){toggle(panel.hidden)});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!panel.hidden){toggle(false);open.focus()}});
  window.addEventListener('pagehide',function(){stop(true)});

  /* La lecture à voix haute reste accessible depuis le panneau dédié.
     Ne pas répéter un bouton sous chaque titre : cela alourdit le parcours visuel. */
  applyAll();refresh();
})();
