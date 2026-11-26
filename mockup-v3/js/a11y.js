/* Barre d'accessibilité : taille du texte, police et espacement, contraste, animations, lecture à voix haute.
   Les réglages sont gardés dans le navigateur (localStorage), jamais envoyés. */
(function(){
  var root=document.documentElement, KEY='bb-a11y', prefs={};
  try{prefs=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  /* Start with the neural French voice: eSpeak remains an explicit lightweight fallback. */
  if(!prefs.voice)prefs.voice='natural';
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
  /* eSpeak NG runs in this browser through WebAssembly. No system French voice
     is required, and neither the text nor the generated audio leaves the device. */
  var AudioContextCtor=window.AudioContext||window.webkitAudioContext;
  var canSpeak=!!AudioContextCtor;
  var current=null,live,audioContext=null,activeSource=null,playbackRun=0;
  var speechEngine=null,speechEnginePromise=null;
  var naturalWorker=null,naturalJobId=0,naturalJobs=Object.create(null);
  var naturalLoadPromise=null,naturalReady=false,naturalLoading=false,naturalSpeakJob=0;
  var naturalSources=[],naturalScheduleAt=0,naturalButton=null,naturalLightButton=null,naturalStatus=null;
  var TTS_BASE='https://cdn.jsdelivr.net/npm/@spelling-creator/spellophone@0.2.1/dist/';

  function loadFrenchEngine(){
    if(speechEngine)return Promise.resolve(speechEngine);
    if(!speechEnginePromise){
      speechEnginePromise=import(TTS_BASE+'browser.js').then(function(api){
        return api.createEspeak({
          cdn:'jsdelivr',
          languages:['fr'],
          fallback:function(){return import(TTS_BASE+'wasm2js.js')}
        }).then(function(engine){
          return engine.loadVoice('fr-fr').then(function(){
            return {engine:engine,toFloat32:api.toFloat32};
          });
        });
      }).then(function(ready){
        speechEngine=ready;
        return ready;
      }).catch(function(error){
        speechEnginePromise=null;
        throw error;
      });
    }
    return speechEnginePromise;
  }

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
  function playChunk(ready,part,run,rate){
    return new Promise(function(resolve,reject){
      if(run!==playbackRun||!current){resolve();return}
      try{
        var result=ready.engine.synthesize(part,{rate:rate});
        if(!result||!result.samples||!result.samples.length){resolve();return}
        var buffer=audioContext.createBuffer(1,result.samples.length,result.sampleRate);
        buffer.copyToChannel(ready.toFloat32(result.samples),0);
        var source=audioContext.createBufferSource();
        source.buffer=buffer;
        source.connect(audioContext.destination);
        activeSource=source;
        var ended=false;
        source.onended=function(){
          if(ended)return;
          ended=true;
          if(activeSource===source)activeSource=null;
          resolve();
        };
        source.start(0);
      }catch(error){reject(error)}
    });
  }
  function playChunks(ready,list,index,btn,run,rate){
    if(run!==playbackRun||current!==btn)return Promise.resolve();
    if(index>=list.length){finishReading(btn,run);return Promise.resolve()}
    return playChunk(ready,list[index],run,rate).then(function(){
      return playChunks(ready,list,index+1,btn,run,rate);
    });
  }

  /* ---------- voix neuronale française, calculée sur l'appareil ---------- */
  function refreshNaturalControls(){
    if(!naturalButton)return;
    naturalButton.disabled=naturalLoading;
    naturalButton.textContent=naturalReady
      ? (prefs.voice==='natural'?'Voix naturelle activée':'Activer la voix naturelle')
      : (naturalLoading?'Chargement de la voix naturelle…':'Télécharger et activer la voix naturelle (≈ 134 Mo)');
    naturalButton.setAttribute('aria-pressed',String(prefs.voice==='natural'));
    if(naturalLightButton)naturalLightButton.hidden=prefs.voice!=='natural';
    if(naturalStatus&&!naturalLoading){
      if(prefs.voice==='natural')naturalStatus.textContent=naturalReady
        ? 'Voix naturelle activée. Le texte est synthétisé directement sur cet appareil.'
        : 'Voix naturelle sélectionnée. Le premier chargement représente environ 134 Mo ; il commence à la première écoute.';
      else naturalStatus.textContent='Voix légère active. Elle se charge rapidement, mais son timbre est plus synthétique.';
    }
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
      naturalWorker=null;naturalLoadPromise=null;naturalReady=false;naturalLoading=false;
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
    naturalLoading=true;refreshNaturalControls();
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
      naturalLoading=false;refreshNaturalControls();return Promise.reject(error);
    }
    naturalLoadPromise=request.promise.then(function(){
      naturalReady=true;naturalLoading=false;
      if(naturalStatus)naturalStatus.textContent='Voix naturelle prête. Le texte est synthétisé directement sur cet appareil.';
      refreshNaturalControls();
    }).catch(function(error){
      naturalLoading=false;naturalLoadPromise=null;
      if(naturalStatus)naturalStatus.textContent='La voix naturelle n’a pas pu être chargée. Vérifiez votre connexion ; la voix légère reste disponible.';
      refreshNaturalControls();throw error;
    });
    return naturalLoadPromise;
  }
  function enableNaturalVoice(){
    if(naturalReady){
      prefs.voice='natural';save();refreshNaturalControls();
      if(naturalStatus)naturalStatus.textContent='Voix naturelle activée. Appuyez sur « Écouter toute la page » pour l’essayer.';
      say('Voix naturelle activée.');return;
    }
    if(naturalStatus)naturalStatus.textContent='Premier chargement : environ 134 Mo. Les fichiers du modèle seront mis en cache lorsque le navigateur le permet.';
    say('Téléchargement de la voix naturelle française. Le premier chargement représente environ 134 mégaoctets.');
    loadNaturalVoice().then(function(){
      prefs.voice='natural';save();refreshNaturalControls();
      if(naturalStatus)naturalStatus.textContent='Voix naturelle prête et activée. Appuyez sur « Écouter toute la page » pour l’essayer.';
      say('La voix naturelle est prête.');
    }).catch(function(error){
      if(window.console&&console.error)console.error('Pocket TTS unavailable:',error);
    });
  }
  function playNatural(text,btn,run){
    naturalScheduleAt=audioContext.currentTime+0.06;naturalSources=[];
    var request=requestNatural('speak',{text:text,lang:'fr'},null,function(message){
      if(run!==playbackRun||current!==btn)return;
      try{
        var samples=message.audio instanceof Float32Array?message.audio:new Float32Array(message.audio);
        var buffer=audioContext.createBuffer(1,samples.length,message.rate||24000);
        buffer.copyToChannel(samples,0);
        var source=audioContext.createBufferSource();
        source.buffer=buffer;source.playbackRate.value=({lent:0.9,rapide:1.1})[prefs.speed]||1;
        source.connect(audioContext.destination);
        var startAt=Math.max(naturalScheduleAt,audioContext.currentTime+0.04);
        source.start(startAt);
        naturalScheduleAt=startAt+buffer.duration/source.playbackRate.value;
        naturalSources.push(source);
      }catch(error){if(window.console&&console.error)console.error('Natural voice audio chunk failed:',error)}
    });
    naturalSpeakJob=request.id;
    return request.promise.then(function(){
      if(naturalSpeakJob===request.id)naturalSpeakJob=0;
      var wait=Math.max(0,naturalScheduleAt-audioContext.currentTime)*1000;
      return new Promise(function(resolve){setTimeout(resolve,wait+60)});
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
    /* Create/resume audio synchronously in the click gesture; browsers may
       otherwise block playback after the asynchronous engine download. */
    var resume=Promise.resolve();
    try{
      if(!audioContext||audioContext.state==='closed')audioContext=new AudioContextCtor();
      if(audioContext.state==='suspended'&&audioContext.resume)resume=audioContext.resume();
    }catch(error){
      current=null;btn.setAttribute('aria-pressed','false');setLabel(btn,false);
      say('La lecture audio n’est pas disponible dans ce navigateur.');
      return;
    }
    if(prefs.voice==='natural'){
      say(naturalReady?'Lecture avec la voix naturelle…':'Préparation de la voix naturelle française…');
      Promise.all([loadNaturalVoice(),resume]).then(function(){
        if(current!==btn||run!==playbackRun)return;
        say('Lecture démarrée avec la voix naturelle.');
        return playNatural(text,btn,run);
      }).then(function(){
        if(current===btn&&run===playbackRun)finishReading(btn,run);
      }).catch(function(error){
        if(window.console&&console.error)console.error('Natural French voice failed; using the lightweight voice:',error);
        if(current!==btn||run!==playbackRun)return;
        stopNatural();
        say('La voix naturelle est indisponible. Utilisation de la voix légère.');
        return Promise.all([loadFrenchEngine(),resume]).then(function(values){
          if(current!==btn||run!==playbackRun)return;
          var rate=({lent:130,rapide:210})[prefs.speed]||165;
          return playChunks(values[0],chunks(text),0,btn,run,rate);
        }).catch(function(fallbackError){
          if(window.console&&console.error)console.error('French fallback unavailable:',fallbackError);
          if(current===btn&&run===playbackRun){
            current=null;btn.setAttribute('aria-pressed','false');setLabel(btn,false);
            say('Aucune voix de lecture n’a pu être chargée. Vérifiez votre connexion, puis réessayez.');
          }
        });
      });
      return;
    }
    say('Chargement de la voix française…');
    Promise.all([loadFrenchEngine(),resume]).then(function(values){
      if(current!==btn||run!==playbackRun)return;
      say('Lecture démarrée.');
      var rate=({lent:130,rapide:210})[prefs.speed]||165;
      return playChunks(values[0],chunks(text),0,btn,run,rate);
    }).catch(function(error){
      if(window.console&&console.error)console.error('French read-aloud unavailable:',error);
      if(current===btn&&run===playbackRun){
        current=null;
        btn.setAttribute('aria-pressed','false');
        setLabel(btn,false);
        say('La voix française n’a pas pu être chargée. Vérifiez votre connexion, puis réessayez.');
      }
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
  if(canSpeak)rows+='<div class="a11y-row a11y-voice-quality"><span id="l-voice-quality">Qualité de la voix</span><p class="voice-help">La voix légère est rapide et peu volumineuse, mais plus mécanique. Une voix française plus naturelle est disponible en option : son premier téléchargement représente environ 134 Mo, puis la synthèse se fait sur cet appareil.</p><div class="a11y-group" role="group" aria-labelledby="l-voice-quality"><button type="button" id="a11y-natural-enable">Télécharger et activer la voix naturelle (≈ 134 Mo)</button><button type="button" id="a11y-light-enable" hidden>Utiliser la voix légère</button></div><p class="voice-status" id="a11y-voice-status" aria-live="polite"></p></div>';
  rows+='<div class="a11y-row"><div class="a11y-group"><a href="accessibilite.html#signaler" class="a11y-link">Signaler un problème</a></div><div class="a11y-group" style="margin-top:12px"><button type="button" class="reset" id="a11y-reset">Tout remettre par défaut</button><button type="button" class="reset" id="a11y-close">Fermer</button></div></div>';
  panel.innerHTML=rows;
  if(canSpeak){naturalButton=panel.querySelector('#a11y-natural-enable');naturalLightButton=panel.querySelector('#a11y-light-enable');naturalStatus=panel.querySelector('#a11y-voice-status');}
  if(canSpeak){panel.querySelector('#a11y-voice').insertBefore(listenButton('Écouter toute la page',function(){return textOf(document.getElementById('contenu'))}),panel.querySelector('#a11y-voice').firstChild)}
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
    else if(b.id==='a11y-natural-enable'){enableNaturalVoice();return;}
    else if(b.id==='a11y-light-enable'){prefs.voice='light';save();stop(true);refresh();say('Voix légère activée.');return;}
    else if(b.id==='a11y-reset'){prefs={hc:false,rm:false,voice:'natural'};stop(true)}
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
