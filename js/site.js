// ---- tap-to-call conversion (delegated: covers every tel: link on every page) ----
  // 53 tel links across the site fired NOTHING before this — gtag was healthy, the taps
  // were simply never wired, so a caller was invisible to Google Ads while a form fill
  // was not. Delegated on document so it also catches links rendered later, and so a new
  // page cannot ship an untracked call button by omission.
  // Deliberately NOT the `onclick="if(typeof gtag...)"` pattern used elsewhere: that guard
  // silently no-ops whenever gtag has not arrived yet (see the GHL 10s defer lesson). Here
  // the tag is in <head> on a static page, and the try/catch fails safe without blocking
  // the call either way — the tel: navigation is never prevented.
  (function(){
    document.addEventListener('click', function(e){
      var a = e.target && e.target.closest ? e.target.closest('a[href^="tel:"]') : null;
      if(!a) return;
      try{ gtag('event','conversion',{send_to:'AW-18360839838/TmuOCMTW7dkcEJ7dkLNE'}); }catch(_){}
    }, true);
  })();

  // ---- click-id capture -> 90 day cookie -> hidden gclid on the form-card ----
  (function(){
    function setC(n,v){document.cookie=n+'='+v+';path=/;max-age='+(90*86400)+';SameSite=Lax';}
    function getC(n){var v=('; '+document.cookie).split('; '+n+'=');return v.length===2?v.pop().split(';').shift():'';}
    try{
      var p=new URLSearchParams(location.search);
      if(p.get('gclid'))setC('_gclid',p.get('gclid'));
      if(p.get('fbclid'))setC('_fbc','fb.1.'+Date.now()+'.'+p.get('fbclid'));
      // utm capture: cookied on landing so a visitor who converts on a later page
      // (or later session, 90d) keeps campaign attribution
      ['utm_source','utm_medium','utm_campaign'].forEach(function(k){
        if(p.get(k))setC('_'+k,p.get(k));
      });
      var g=getC('_gclid'), f=document.querySelector('form.form-card');
      if(g&&f&&!f.querySelector('[name=gclid]')){var i=document.createElement('input');i.type='hidden';i.name='gclid';i.value=g;f.appendChild(i);}
    }catch(_){}
  })();

  // ---- two-step: gate step 1 on all three qualifiers, then reveal contact ----
  (function(){
    var f=document.getElementById('lead');
    // Pages without a form (About, Services, Blog, Design, Our Work, Commercial,
    // Privacy, Thank You) load this same file. Bail rather than throw.
    if(!f) return;
    function val(n){var el=f.querySelector('[name="'+n+'"]');return el?el.value:'';}
    document.getElementById('fcNext').addEventListener('click',function(){
      var err=document.getElementById('fcErr');
      if(!val('reason')||!val('timeframe')||!val('town')){err.classList.add('on');return;}
      err.classList.remove('on');
      document.getElementById('step1').classList.remove('on');
      document.getElementById('step2').classList.add('on');
      document.getElementById('pg2').classList.add('on');
      f.scrollIntoView({behavior:'smooth',block:'center'});
      // step1 -> step2 drop-off measurement (non-optional per the build spec)
      try{gtag('event','form_step_1',{reason:val('reason'),timeframe:val('timeframe'),town:val('town')});}catch(_){}
      try{fbq('trackCustom','FormStep1');}catch(_){}
      setTimeout(function(){var n=document.getElementById('name');n&&n.focus();},260);
    });
    document.getElementById('fcBack').addEventListener('click',function(){
      document.getElementById('step2').classList.remove('on');
      document.getElementById('step1').classList.add('on');
      document.getElementById('pg2').classList.remove('on');
      f.scrollIntoView({behavior:'smooth',block:'center'});
    });
  })();

  var leadForm=document.getElementById('lead');
  if(leadForm) leadForm.addEventListener('submit',function(e){
    e.preventDefault();
    if(this.company && this.company.value){return;}                  // honeypot -> drop bots
    function val(n){var el=this.querySelector('[name="'+n+'"]');return el?el.value:'';}
    val=val.bind(this);
    var reason=val('reason'), timeframe=val('timeframe'), town=val('town');
    if(!this.name.value||!this.phone.value||!this.email.value||!reason||!timeframe||!town){
      this.reportValidity&&this.reportValidity();return;}
    function getC(n){var v=('; '+document.cookie).split('; '+n+'=');return v.length===2?v.pop().split(';').shift():'';}
    var eid='ce-'+Date.now()+'-'+Math.floor(Math.random()*1e6);       // shared id: browser + server dedupe
    var payload={name:this.name.value,phone:this.phone.value,email:this.email.value,
      town:town,reason:reason,timeframe:timeframe,
      page:(location.pathname.split('/').pop()||'lp').replace('.html',''),
      gclid:getC('_gclid'),fbp:getC('_fbp'),fbc:getC('_fbc'),event_id:eid,source:(location.pathname.split('/').pop()||'').indexOf('lp-')===0?'meta-lp':'website',
      utm_source:getC('_utm_source'),utm_medium:getC('_utm_medium'),utm_campaign:getC('_utm_campaign')};
    // (1) browser signal — Google live (conv action 7704636228); Meta still blocked on pixel ownership
    // try{fbq('track','Lead',{content_name:'Creative Edge '+payload.page},{eventID:eid});}catch(_){}
    try{gtag('event','conversion',{send_to:'AW-18360839838/TmuOCMTW7dkcEJ7dkLNE'});}catch(_){}
    // (2) server side -> Railway: honeypot + phone validate -> GHL upsert + speed-to-lead -> CAPI Lead (hashed)
    // Endpoint is LIVE and verified end to end (Jul 31 2026): POST -> GHL contact.
    try{fetch('https://profound-truth-production-4190.up.railway.app/webhook/creative_edge/lp-lead',
      {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),keepalive:true});}catch(_){}
    // (3) thank you
    this.style.display='none';
    // #done lives next to the form. Guard it: a page that ships a form without
    // a success block would otherwise hide the form and tell the person nothing.
    var d=document.getElementById('done');
    if(d){d.classList.add('on'); d.scrollIntoView({behavior:'smooth',block:'center'});}
    else{location.href='thank-you.html';}
  });
