/* Appliqué dès le chargement, avant l'affichage : évite le « clignotement » des réglages d'accessibilité.
   Respecte aussi les réglages du système (contraste renforcé, mouvement réduit). */
(function(){
  var r=document.documentElement,p={};
  r.classList.add('js');
  try{p=JSON.parse(localStorage.getItem('bb-a11y')||'{}')}catch(e){}
  var mq=function(q){return window.matchMedia&&matchMedia(q).matches};
  if(p.hc===undefined&&mq('(prefers-contrast: more)'))p.hc=true;
  if(p.rm===undefined&&mq('(prefers-reduced-motion: reduce)'))p.rm=true;
  if(p.fs)r.classList.add('fs-'+p.fs);
  ['dys','sp','hc','rm','calm'].forEach(function(k){if(p[k])r.classList.add(k)});
})();
