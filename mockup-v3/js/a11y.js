/* Barre d'accessibilité et lecteur audio pré-enregistré de Bulle Bleue. */
(function(){
  var root=document.documentElement,KEY='bb-a11y',prefs={};
  try{prefs=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(error){}
  delete prefs.voice;
  prefs.speed=prefs.speed||'normal';
  function save(){try{localStorage.setItem(KEY,JSON.stringify(prefs))}catch(error){}}
  var mq=function(q){return window.matchMedia&&matchMedia(q).matches};
  if(prefs.hc===undefined&&mq('(prefers-contrast: more)'))prefs.hc=true;
  if(prefs.rm===undefined&&mq('(prefers-reduced-motion: reduce)'))prefs.rm=true;
  function applyAll(){
    ['fs-1','fs-2','fs-3'].forEach(function(c){root.classList.remove(c)});
    if(prefs.fs)root.classList.add('fs-'+prefs.fs);
    ['dys','sp','hc','rm','calm'].forEach(function(k){root.classList.toggle(k,!!prefs[k])});
    document.dispatchEvent(new Event('a11ychange'));
  }

  /* Read pre-generated French (France) MP3 files; never synthesize in the visitor's browser. */
  var canSpeak=typeof window.Audio==='function';
  var speechManifest=null,speechLoading=false,speechLoadError=null;
  var speechStatus=null,voiceSelect=null,live=null,audio=null,currentButton=null,playbackRun=0;
  var panel=null;
  function say(message){
    if(live){live.textContent='';window.setTimeout(function(){live.textContent=message},40)}
  }
  function setSpeechStatus(message){if(speechStatus)speechStatus.textContent=message}
  function buttonState(button,state){
    var label=state==='playing'?'Mettre en pause':state==='paused'?'Reprendre':(button.getAttribute('data-label')||'Écouter');
    var text=button.querySelector('.listen-t');
    if(text)text.textContent=label;
    button.setAttribute('aria-label',label);
    button.setAttribute('aria-pressed',String(state==='playing'));
  }
  function stop(silent){
    playbackRun++;
    var oldAudio=audio,oldButton=currentButton;
    audio=null;currentButton=null;
    if(oldAudio){
      oldAudio.pause();
      oldAudio.removeAttribute('src');
      try{oldAudio.load()}catch(error){}
    }
    if(oldButton)buttonState(oldButton,'idle');
    if(!silent)setSpeechStatus('Lecture arrêtée.');
  }
  function pageKey(){
    var name=window.location.pathname.split('/').pop();
    return name||'index.html';
  }
  function checkedAudioPath(path){
    if(typeof path!=='string'||!/^\/?assets\/speech\/fr-FR\/[a-z0-9-]+\/(?:sample|pages\/[a-z0-9-]+)\.mp3$/.test(path))
      throw new Error('Chemin audio invalide.');
    return path.charAt(0)==='/'?path:'/'+path;
  }
  function refreshSpeechControls(){
    if(!speechStatus||!panel)return;
    var buttons=panel.querySelectorAll('[data-audio="sample"],[data-audio="page"]');
    if(speechLoading){
      setSpeechStatus('Chargement de la liste des voix françaises…');
      buttons.forEach(function(button){button.disabled=true});
      if(voiceSelect)voiceSelect.disabled=true;
      return;
    }
    if(!speechManifest){
      setSpeechStatus(speechLoadError?
        'Les enregistrements audio ne sont pas encore disponibles. Ils seront activés après leur génération.':
        'Les voix françaises (France) sont en cours de préparation.');
      buttons.forEach(function(button){button.disabled=true});
      if(voiceSelect)voiceSelect.disabled=true;
      return;
    }
    if(voiceSelect){
      voiceSelect.disabled=false;
      voiceSelect.innerHTML='';
      Object.keys(speechManifest.voices).forEach(function(key){
        var option=document.createElement('option');
        option.value=key;option.textContent=speechManifest.voices[key].label;
        voiceSelect.appendChild(option);
      });
      var preferred=prefs.ttsVoice||'siwis';
      voiceSelect.value=speechManifest.voices[preferred]?preferred:Object.keys(speechManifest.voices)[0];
      prefs.ttsVoice=voiceSelect.value;
    }
    if(speechManifest.status!=='ready'){
      buttons.forEach(function(button){button.disabled=true});
      setSpeechStatus('Les enregistrements audio sont en attente de génération. La voix française Siwis sera disponible après la génération des fichiers.');
      return;
    }
    buttons.forEach(function(button){
      var voice=speechManifest.voices[voiceSelect.value];
      var source=button.getAttribute('data-audio')==='sample'?voice.sample:(voice.pages||{})[pageKey()];
      button.disabled=!source;
    });
    setSpeechStatus('Voix Siwis prête · français de France. Le MP3 est lu directement, sans synthèse sur votre appareil.');
  }
  function loadSpeechManifest(){
    if(!canSpeak)return;
    speechLoading=true;refreshSpeechControls();
    fetch('/assets/speech/fr-FR/manifest.json',{cache:'no-cache'})
      .then(function(response){
        if(!response.ok)throw new Error('Enregistrements indisponibles ('+response.status+').');
        return response.json();
      })
      .then(function(manifest){
        if(!manifest||manifest.locale!=='fr-FR'||!manifest.voices||!manifest.voices.siwis)
          throw new Error('Le catalogue audio français est incomplet.');
        speechManifest=manifest;speechLoading=false;speechLoadError=null;
        refreshSpeechControls();
      })
      .catch(function(error){
        speechLoading=false;speechLoadError=error;
        refreshSpeechControls();
        if(window.console&&console.info)console.info('French page audio is not generated yet:',error.message);
      });
  }
  function finishReading(button,run,message){
    if(currentButton!==button||run!==playbackRun)return;
    currentButton=null;audio=null;
    buttonState(button,'idle');
    setSpeechStatus(message||'Lecture terminée.');
    say(message||'Lecture terminée.');
  }
  function playAudio(kind,button){
    if(kind==='stop'){stop(false);return}
    if(!speechManifest){setSpeechStatus('Les enregistrements audio ne sont pas encore disponibles.');return}
    if(currentButton===button&&audio){
      if(audio.paused){
        var resumeRun=playbackRun;
        audio.play().then(function(){
          if(currentButton===button&&resumeRun===playbackRun)buttonState(button,'playing');
        }).catch(function(){
          if(currentButton===button&&resumeRun===playbackRun)setSpeechStatus('La reprise de la lecture a échoué. Réessayez.');
        });
      }else audio.pause();
      return;
    }
    stop(true);
    var voice=speechManifest.voices[voiceSelect.value];
    var source=kind==='sample'?voice.sample:(voice.pages||{})[pageKey()];
    if(!source){setSpeechStatus('Aucun enregistrement n’est encore disponible pour cette page.');return}
    var url;
    try{url=checkedAudioPath(source)}catch(error){setSpeechStatus('Le chemin de cet enregistrement est invalide.');return}
    var run=playbackRun,player=new Audio();
    audio=player;currentButton=button;player.preload='none';
    player.playbackRate=({lent:0.9,rapide:1.1})[prefs.speed]||1;
    try{player.preservesPitch=true;player.mozPreservesPitch=true;player.webkitPreservesPitch=true}catch(error){}
    player.addEventListener('playing',function(){
      if(currentButton!==button||run!==playbackRun)return;
      buttonState(button,'playing');
      setSpeechStatus(kind==='sample'?'Exemple en cours · '+voice.label+'.':'Lecture de la page en cours · '+voice.label+'.');
      say('Lecture démarrée.');
    });
    player.addEventListener('pause',function(){
      if(currentButton!==button||run!==playbackRun||player.ended)return;
      buttonState(button,'paused');setSpeechStatus('Lecture en pause.');
    });
    player.addEventListener('waiting',function(){
      if(currentButton===button&&run===playbackRun)setSpeechStatus('Chargement de l’enregistrement audio…');
    });
    player.addEventListener('ended',function(){finishReading(button,run,'Lecture terminée.')});
    player.addEventListener('error',function(){
      if(currentButton!==button||run!==playbackRun)return;
      currentButton=null;audio=null;buttonState(button,'idle');
      setSpeechStatus('Impossible de charger cet enregistrement. Vérifiez votre connexion puis réessayez.');
    });
    button.setAttribute('aria-pressed','false');
    player.src=url;setSpeechStatus('Ouverture de l’enregistrement audio…');
    var playPromise=player.play();
    if(playPromise&&typeof playPromise.catch==='function'){
      playPromise.catch(function(error){
        if(currentButton!==button||run!==playbackRun)return;
        currentButton=null;audio=null;buttonState(button,'idle');
        setSpeechStatus(error&&error.name==='NotAllowedError'?
          'Le navigateur a bloqué la lecture. Appuyez à nouveau sur Écouter.':
          'La lecture audio n’a pas pu démarrer. Réessayez.');
      });
    }
  }

  var ICON='<svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/><path d="M19 6a8.5 8.5 0 0 1 0 12"/></svg>';
  function listenButton(label,kind){
    var button=document.createElement('button');
    button.type='button';button.className='listen';button.setAttribute('aria-pressed','false');
    button.setAttribute('data-label',label);button.setAttribute('data-audio',kind);
    button.setAttribute('aria-label',label);button.setAttribute('title',label);button.disabled=true;
    button.innerHTML=ICON+'<span class="listen-t">'+label+'</span>';
    return button;
  }

  /* ---------- barre d'accessibilité ---------- */
  var wrap=document.createElement('div');wrap.className='a11y-ui';
  var open=document.createElement('button');open.type='button';open.className='a11y-btn';open.id='a11y-open';open.setAttribute('aria-expanded','false');open.setAttribute('aria-controls','a11y-panel');
  open.innerHTML='<svg aria-hidden="true" focusable="false" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="4.5" r="2"/><path d="M5 8.5l7 1.5 7-1.5M12 10v5m0 0l-3.5 5.5M12 15l3.5 5.5"/></svg><span>Accessibilité</span>';
  panel=document.createElement('section');panel.id='a11y-panel';panel.className='a11y-panel';panel.hidden=true;panel.setAttribute('aria-labelledby','a11y-title');
  var rows='<h2 id="a11y-title">Rendre le site plus confortable</h2>'+
    '<div class="a11y-row"><span id="l-fs">Taille du texte</span><div class="a11y-group" role="group" aria-labelledby="l-fs"><button type="button" data-fs="0">Normal</button><button type="button" data-fs="1">Grand</button><button type="button" data-fs="2">Très grand</button><button type="button" data-fs="3">Immense</button></div></div>'+
    '<div class="a11y-row"><span id="l-opt">Lecture et confort</span><div class="a11y-group" role="group" aria-labelledby="l-opt"><button type="button" data-k="dys">Police pour la dyslexie</button><button type="button" data-k="sp">Texte plus aéré</button><button type="button" data-k="hc">Contraste renforcé</button><button type="button" data-k="rm">Sans animation</button><button type="button" data-k="calm">Mode calme (moins de décor)</button></div></div>';
  if(canSpeak)rows+='<div class="a11y-row"><label id="l-voix" for="a11y-voice-choice">Voix française (France)</label><select id="a11y-voice-choice" class="a11y-select" aria-labelledby="l-voix" disabled><option>Chargement des voix…</option></select><div class="a11y-group" id="a11y-voice" role="group" aria-label="Écoute des enregistrements" style="margin-top:8px"></div><div class="a11y-group" role="group" aria-label="Vitesse de lecture" style="margin-top:8px"><button type="button" data-sp="lent">Lente</button><button type="button" data-sp="normal">Normale</button><button type="button" data-sp="rapide">Rapide</button><button type="button" data-audio="stop">Arrêter</button></div></div>';
  if(canSpeak)rows+='<div class="a11y-row a11y-voice-quality"><span id="l-voice-quality">Enregistrements audio</span><p class="voice-help">La voix Siwis est préparée à l’avance avec Piper pour le français de France. Votre navigateur lit directement un fichier MP3 : aucun modèle vocal n’est téléchargé et aucune synthèse n’est exécutée sur votre appareil.</p><p class="voice-status" id="a11y-voice-status" aria-live="polite">Chargement des enregistrements…</p></div>';
  rows+='<div class="a11y-row"><div class="a11y-group"><a href="accessibilite.html#signaler" class="a11y-link">Signaler un problème</a></div><div class="a11y-group" style="margin-top:12px"><button type="button" class="reset" id="a11y-reset">Tout remettre par défaut</button><button type="button" class="reset" id="a11y-close">Fermer</button></div></div>';
  panel.innerHTML=rows;
  if(canSpeak){
    speechStatus=panel.querySelector('#a11y-voice-status');
    voiceSelect=panel.querySelector('#a11y-voice-choice');
    var controls=panel.querySelector('#a11y-voice');
    controls.appendChild(listenButton('Écouter un exemple','sample'));
    controls.appendChild(listenButton('Écouter toute la page','page'));
  }
  live=document.createElement('p');live.className='sr-only';live.setAttribute('role','status');live.setAttribute('aria-live','polite');
  wrap.appendChild(open);wrap.appendChild(panel);wrap.appendChild(live);
  open.setAttribute('aria-label','Accessibilité');open.setAttribute('title','Accessibilité');
  var headerBar=document.querySelector('header .bar');
  if(headerBar)headerBar.insertBefore(wrap,headerBar.firstElementChild);else document.body.insertBefore(wrap,document.body.firstChild);

  function refresh(){
    panel.querySelectorAll('[data-fs]').forEach(function(button){button.setAttribute('aria-pressed',String((+button.getAttribute('data-fs'))===(prefs.fs||0)))});
    panel.querySelectorAll('[data-sp]').forEach(function(button){button.setAttribute('aria-pressed',String(button.getAttribute('data-sp')===prefs.speed))});
    panel.querySelectorAll('[data-k]').forEach(function(button){button.setAttribute('aria-pressed',String(!!prefs[button.getAttribute('data-k')]))});
    refreshSpeechControls();
  }
  panel.addEventListener('click',function(event){
    var audioButton=event.target.closest('[data-audio]');
    if(audioButton){
      if(audioButton.getAttribute('data-audio')==='stop')stop(false);
      else if(!audioButton.disabled)playAudio(audioButton.getAttribute('data-audio'),audioButton);
      return;
    }
    var button=event.target.closest('button');if(!button)return;
    if(button.hasAttribute('data-fs'))prefs.fs=+button.getAttribute('data-fs');
    else if(button.hasAttribute('data-sp')){
      prefs.speed=button.getAttribute('data-sp');
      if(audio)audio.playbackRate=({lent:0.9,rapide:1.1})[prefs.speed]||1;
    }else if(button.hasAttribute('data-k')){
      var key=button.getAttribute('data-k');prefs[key]=!prefs[key];
    }else if(button.id==='a11y-reset'){
      prefs={hc:false,rm:false,ttsVoice:'denise',speed:'normal'};stop(true);
    }else if(button.id==='a11y-close'){toggle(false);open.focus();return}
    save();applyAll();refresh();
  });
  panel.addEventListener('change',function(event){
    if(event.target===voiceSelect){prefs.ttsVoice=voiceSelect.value;save();if(currentButton)stop(true)}
  });
  function toggle(value){
    panel.hidden=!value;open.setAttribute('aria-expanded',String(value));
    if(value){var first=panel.querySelector('button');if(first)first.focus()}
  }
  open.addEventListener('click',function(){toggle(panel.hidden)});
  document.addEventListener('keydown',function(event){
    if(event.key==='Escape'&&!panel.hidden){toggle(false);open.focus()}
  });
  window.addEventListener('pagehide',function(){stop(true)});
  applyAll();refresh();
  /* Only the small manifest is checked on page entry; an MP3 is fetched after a visitor presses Play. */
  if(canSpeak)loadSpeechManifest();
})();
