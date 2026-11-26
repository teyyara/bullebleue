/* Barre d'accessibilité : taille du texte, police et espacement, contraste, animations, lecture à voix haute.
   Les réglages sont gardés dans le navigateur (localStorage), jamais envoyés. */
(function(){
  var root=document.documentElement, KEY='bb-a11y', prefs={};
  try{prefs=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  // Pocket TTS is the sole read-aloud engine; discard the former light-voice setting.
  delete prefs.voice;
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
  /* Pocket TTS runs in a dedicated worker; text and generated audio stay on-device. */
  var AudioContextCtor=window.AudioContext||window.webkitAudioContext;
  var canSpeak=!!AudioContextCtor;
  var current=null,live,audioContext=null,activeSource=null,playbackRun=0;
  var naturalWorker=null,naturalJobId=0,naturalJobs=Object.create(null);
  var naturalLoadPromise=null,naturalReady=false,naturalLoading=false,naturalSpeakJob=0;
  var naturalSources=[],naturalScheduleAt=0,naturalStatus=null,naturalLoadError=null;

  function textOf(el){
    var c=el.cloneNode(true);
    c.querySelectorAll('.listen,.a11y-ui,[aria-hidden="true"],script,style,button,svg,.sr-only').forEach(function(n){n.remove()});
    c.querySelectorAll('h1,h2,h3,p,li,figcaption,.day,.when').forEach(function(n){n.appendChild(document.createTextNode('. '))});
    c.querySelectorAll('abbr[title]').forEach(function(a){a.textContent=a.getAttribute('title')});
    return c.textContent.replace(/\s+/g,' ').replace(/([.!?…:;])\s*\.\s/g,'$1 ').replace(/\s+\./g,'.').trim();
  }
  function say(msg){if(live){live.textContent='';setTimeout(function(){live.textContent=msg},50)}}
  function setLabel(btn,on){
    var t=btn.querySelector('.listen-t');
    if(t)t.textContent=on?'Arrêter la lecture':(btn.getAttribute('data-label')||'Écouter');
    btn.setAttribute('aria-label',on?'Arrêter la lecture':(btn.getAttribute('data-aria-label')||btn.getAttribute('data-label')||'Écouter'));
  }
  function finishReading(btn,run){
    if(current!==btn||run!==playbackRun)return;
    current=null;
    btn.setAttribute('aria-pressed','false');
    setLabel(btn,false);
    say('Lecture terminée.');
  }
  function stop(silent){
    playbackRun++;
    stopNatural();
    if(activeSource){
      var source=activeSource;
      activeSource=null;
      try{source.stop(0)}catch(e){}
    }
    if(current){
      current.setAttribute('aria-pressed','false');
      setLabel(current,false);
      current=null;
    }
    if(!silent)say('Lecture arrêtée.');
  }
  /* ---------- voix neuronale française, calculée sur l'appareil ---------- */
  function refreshNaturalControls(){
    if(!naturalStatus)return;
    if(naturalLoading)naturalStatus.textContent='Téléchargement automatique de la voix française en cours…';
    else if(naturalReady)naturalStatus.textContent='Voix naturelle prête. La synthèse se fait directement sur cet appareil.';
    else if(naturalLoadError)naturalStatus.textContent='Le téléchargement de la voix naturelle a échoué. Vérifiez la connexion puis rechargez la page.';
    else naturalStatus.textContent='La voix naturelle française se télécharge automatiquement à l’ouverture de la page (environ 134 Mo au premier chargement).';
  }
  function ensureNaturalWorker(){
    if(naturalWorker)return;
    naturalWorker=new Worker('/mockup-v3/js/voice/reader-worker.mjs',{type:'module'});
    naturalWorker.addEventListener('message',function(event){
      var message=event.data||{},job=naturalJobs[message.id];
      if(!job)return;
      if(message.type==='progress'){if(job.progress)job.progress(message);return}
      if(message.type==='chunk'){if(job.chunk)job.chunk(message);return}
      delete naturalJobs[message.id];
      if(message.type==='error')job.reject(new Error(message.message||'La voix naturelle a rencontré une erreur.'));
      else job.resolve(message);
    });
    naturalWorker.addEventListener('error',function(event){
      var error=new Error(event.message||'Le moteur de voix naturelle ne peut pas démarrer.');
      Object.keys(naturalJobs).forEach(function(id){naturalJobs[id].reject(error);delete naturalJobs[id]});
      try{naturalWorker.terminate()}catch(e){}
      naturalWorker=null;naturalLoadPromise=null;naturalReady=false;naturalLoading=false;naturalLoadError=error;
      refreshNaturalControls();
    });
  }
  function requestNatural(type,data,progress,chunk){
    ensureNaturalWorker();
    var id=++naturalJobId,resolveJob,rejectJob;
    var promise=new Promise(function(resolve,reject){resolveJob=resolve;rejectJob=reject});
    naturalJobs[id]={resolve:resolveJob,reject:rejectJob,progress:progress,chunk:chunk};
    naturalWorker.postMessage(Object.assign({id:id,type:type},data||{}));
    return {id:id,promise:promise};
  }
  function loadNaturalVoice(){
    if(naturalReady)return Promise.resolve();
    if(naturalLoadPromise)return naturalLoadPromise;
    naturalLoading=true;naturalLoadError=null;refreshNaturalControls();
    var lastMegabyte=-4,request;
    try{
      request=requestNatural('load',{lang:'fr'},function(message){
        if(!naturalStatus)return;
        var loaded=Math.floor((message.loaded||0)/1048576);
        var total=Math.ceil((message.total||106413542)/1048576);
        if(loaded>=lastMegabyte+4||message.loaded>=message.total){
          lastMegabyte=loaded;
          naturalStatus.textContent='Téléchargement de la voix française : '+loaded+' Mo sur '+total+' Mo. Préparation du moteur…';
        }
      });
    }catch(error){
      naturalLoading=false;naturalLoadError=error;refreshNaturalControls();return Promise.reject(error);
    }
    naturalLoadPromise=request.promise.then(function(){
      naturalReady=true;naturalLoading=false;
      if(naturalStatus)naturalStatus.textContent='Voix naturelle prête. Le texte est synthétisé directement sur cet appareil.';
      refreshNaturalControls();
    }).catch(function(error){
      naturalLoading=false;naturalLoadPromise=null;
      naturalLoadError=error;
      if(naturalStatus)naturalStatus.textContent='Le téléchargement de la voix naturelle a échoué. Vérifiez la connexion puis rechargez la page.';
      refreshNaturalControls();throw error;
    });
    return naturalLoadPromise;
  }
  function playNatural(text,btn,run){
    /* Start after a short safety buffer, then schedule compact PCM batches in
       sequence while the worker synthesizes the rest of the page. This avoids
       waiting for the whole document and avoids creating one source per tiny
       model packet. */
    var pendingParts=[],pendingSamples=0,totalSamples=0,sampleRate=24000;
    var started=false,synthesisDone=false,settled=false;
    var startBufferSamples=Math.round(sampleRate*0.75);
    var batchSamples=Math.round(sampleRate*0.42);
    var playbackRate=({lent:0.9,rapide:1.1})[prefs.speed]||1;
    naturalScheduleAt=audioContext.currentTime;naturalSources=[];
    if(naturalStatus)naturalStatus.textContent='Préparation du premier extrait… la lecture commencera dès qu’il sera prêt.';
    return new Promise(function(resolve,reject){
      function settle(){
        if(settled||!synthesisDone||pendingSamples||naturalSources.length)return;
        settled=true;
        if(!totalSamples)reject(new Error('Pocket TTS did not return any audio samples.'));
        else resolve();
      }
      function flush(force){
        if(!pendingSamples||(!force&&pendingSamples<batchSamples))return;
        var samples=new Float32Array(pendingSamples),offset=0;
        pendingParts.forEach(function(part){samples.set(part,offset);offset+=part.length});
        pendingParts=[];pendingSamples=0;
        var buffer=audioContext.createBuffer(1,samples.length,sampleRate);
        buffer.copyToChannel(samples,0);
        var source=audioContext.createBufferSource();
        source.buffer=buffer;
        source.playbackRate.value=playbackRate;
        source.connect(audioContext.destination);
        var startAt=Math.max(naturalScheduleAt,audioContext.currentTime+0.04);
        naturalScheduleAt=startAt+buffer.duration/playbackRate;
        naturalSources.push(source);
        source.onended=function(){
          naturalSources=naturalSources.filter(function(one){return one!==source});
          settle();
        };
        try{
          source.start(startAt);
          if(!started){
            started=true;
            say('Lecture démarrée avec la voix naturelle.');
          }
          if(naturalStatus)naturalStatus.textContent='Lecture en cours · la suite du texte est préparée.';
        }catch(error){
          naturalSources=naturalSources.filter(function(one){return one!==source});
          reject(error);
        }
      }
      var request;
      try{
        request=requestNatural('speak',{text:text,lang:'fr'},function(message){
          if(run!==playbackRun||current!==btn||message.phase!=='synthesis'||!naturalStatus)return;
          var progress='Partie '+message.part+' sur '+message.parts;
          naturalStatus.textContent=started?'Lecture en cours · '+progress+' en préparation…':'Préparation du premier extrait · '+progress+'…';
        },function(message){
          if(run!==playbackRun||current!==btn)return;
          try{
            var samples=message.audio instanceof Float32Array?message.audio:new Float32Array(message.audio);
            if(!samples.length)return;
            sampleRate=message.rate||sampleRate;
            pendingParts.push(samples);
            pendingSamples+=samples.length;
            totalSamples+=samples.length;
            if(!started&&pendingSamples>=startBufferSamples){
              started=true;
              flush(true);
            }else if(started)flush(false);
          }catch(error){reject(error)}
        });
      }catch(error){reject(error);return}
      naturalSpeakJob=request.id;
      request.promise.then(function(){
        if(naturalSpeakJob===request.id)naturalSpeakJob=0;
        synthesisDone=true;
        if(run===playbackRun&&current===btn){
          if(!started&&pendingSamples)started=true;
          flush(true);
        }
        settle();
      }).catch(function(error){
        if(naturalSpeakJob===request.id)naturalSpeakJob=0;
        reject(error);
      });
    });
  }
  function stopNatural(){
    if(naturalSpeakJob&&naturalWorker){
      naturalWorker.postMessage({id:++naturalJobId,type:'abort',of:naturalSpeakJob});
      naturalSpeakJob=0;
    }
    naturalSources.forEach(function(source){try{source.stop(0)}catch(e){}});
    naturalSources=[];naturalScheduleAt=audioContext?audioContext.currentTime:0;
  }

  function speak(text,btn){
    if(current===btn){stop();return}
    stop(true);
    var run=playbackRun;
    current=btn;
    btn.setAttribute('aria-pressed','true');
    setLabel(btn,true);
    if(!text){
      finishReading(btn,run);
      say('Aucun texte à lire sur cette page.');
      return;
    }
    /* Resume AudioContext inside the user gesture. Model downloading starts
       automatically on page entry and never attempts to autoplay sound. */
    var resume=Promise.resolve();
    try{
      if(!audioContext||audioContext.state==='closed')audioContext=new AudioContextCtor();
      if(audioContext.state==='suspended'&&audioContext.resume)resume=audioContext.resume();
    }catch(error){
      current=null;btn.setAttribute('aria-pressed','false');setLabel(btn,false);
      say('La lecture audio n’est pas disponible dans ce navigateur.');
      return;
    }
    say(naturalReady?'Préparation de la lecture avec la voix naturelle…':'La voix naturelle française se prépare…');
    Promise.all([loadNaturalVoice(),resume]).then(function(){
      if(current!==btn||run!==playbackRun)return;
      return playNatural(text,btn,run);
    }).then(function(){
      if(current===btn&&run===playbackRun)finishReading(btn,run);
    }).catch(function(error){
      if(window.console&&console.error)console.error('Pocket TTS French voice failed:',error);
      if(current!==btn||run!==playbackRun)return;
      stopNatural();
      current=null;
      btn.setAttribute('aria-pressed','false');
      setLabel(btn,false);
      naturalLoadError=error;
      refreshNaturalControls();
      say('La voix naturelle n’a pas pu être chargée. Vérifiez votre connexion puis réessayez.');
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
  if(canSpeak)rows+='<div class="a11y-row a11y-voice-quality"><span id="l-voice-quality">Voix naturelle française</span><p class="voice-help">Pocket TTS est la seule voix de lecture. Son téléchargement (environ 134 Mo) commence automatiquement à l’ouverture de la page et les fichiers sont conservés dans le cache du navigateur lorsque celui-ci le permet. La lecture commence dès que les premières secondes sont prêtes ; la suite est préparée pendant l’écoute.</p><p class="voice-status" id="a11y-voice-status" aria-live="polite"></p></div>';
  rows+='<div class="a11y-row"><div class="a11y-group"><a href="accessibilite.html#signaler" class="a11y-link">Signaler un problème</a></div><div class="a11y-group" style="margin-top:12px"><button type="button" class="reset" id="a11y-reset">Tout remettre par défaut</button><button type="button" class="reset" id="a11y-close">Fermer</button></div></div>';
  panel.innerHTML=rows;
  if(canSpeak){naturalStatus=panel.querySelector('#a11y-voice-status');}
  if(canSpeak){
    var voiceControls=panel.querySelector('#a11y-voice');
    voiceControls.appendChild(listenButton('Écouter un exemple',function(){return 'Bonjour et bienvenue à la Bulle Bleue. Ici, on prend le temps de se retrouver, de s’écouter et de créer ensemble. Chacun vient comme il est.'}));
    voiceControls.appendChild(listenButton('Écouter toute la page',function(){return textOf(document.getElementById('contenu'))}));
  }
  live=document.createElement('p');live.className='sr-only';live.setAttribute('role','status');live.setAttribute('aria-live','polite');
  wrap.appendChild(open);wrap.appendChild(panel);wrap.appendChild(live);open.setAttribute('aria-label','Accessibilité');open.setAttribute('title','Accessibilité');var headerBar=document.querySelector('header .bar');if(headerBar)headerBar.insertBefore(wrap,headerBar.firstElementChild);else document.body.insertBefore(wrap,document.body.firstChild);

  function refresh(){
    panel.querySelectorAll('[data-fs]').forEach(function(b){b.setAttribute('aria-pressed',String((+b.getAttribute('data-fs'))===(prefs.fs||0)))});
    panel.querySelectorAll('[data-sp]').forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-sp')===(prefs.speed||'normal')))});
    panel.querySelectorAll('[data-k]').forEach(function(b){b.setAttribute('aria-pressed',String(!!prefs[b.getAttribute('data-k')]))});
    refreshNaturalControls();
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
  /* Begin downloading the pinned model immediately on page entry. */
  if(canSpeak){
    if(navigator.storage&&navigator.storage.persist)navigator.storage.persist().catch(function(){});
    loadNaturalVoice().catch(function(error){
      if(window.console&&console.warn)console.warn('Pocket TTS preload failed:',error);
      refreshNaturalControls();
    });
  }
})();
