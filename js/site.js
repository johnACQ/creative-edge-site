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
      // wbraid / gbraid are what Google sends INSTEAD of gclid on privacy-restricted
      // (largely iOS) clicks. Without them those conversions cannot be matched back at
      // all. They are distinct fields in Google's import, NOT interchangeable with gclid,
      // so they are cookied and sent under their own names — never folded into _gclid.
      if(p.get('wbraid'))setC('_wbraid',p.get('wbraid'));
      if(p.get('gbraid'))setC('_gbraid',p.get('gbraid'));
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
      /* timeframe NOT gated (2026-08-21). The HTML `required` attr is only half the
         lock — this line blocked independently, so unrequiring the field alone would
         have shipped nothing. Same defect fixed on KDT 2026-08-20. */
      if(!val('reason')||!val('town')){err.classList.add('on');return;}
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
    /* email + timeframe dropped from the submit gate. CE's SMS is live and delivering
       [v 2026-08-21 - TYPE_SMS conversations on the sub], so phone alone reaches the
       customer AND alerts Brad. ⛔ Do NOT copy this to a client whose SMS is dead —
       KDT keeps email REQUIRED for exactly that reason. Both are still SENT when given. */
    if(!this.name.value||!this.phone.value||!reason||!town){
      this.reportValidity&&this.reportValidity();return;}
    function getC(n){var v=('; '+document.cookie).split('; '+n+'=');return v.length===2?v.pop().split(';').shift():'';}
    var eid='ce-'+Date.now()+'-'+Math.floor(Math.random()*1e6);       // shared id: browser + server dedupe
    var payload={name:this.name.value,phone:this.phone.value,email:this.email.value,
      town:town,reason:reason,timeframe:timeframe,
      page:(location.pathname.split('/').pop()||'lp').replace('.html',''),
      gclid:getC('_gclid'),wbraid:getC('_wbraid'),gbraid:getC('_gbraid'),
      fbp:getC('_fbp'),fbc:getC('_fbc'),event_id:eid,source:(location.pathname.split('/').pop()||'').indexOf('lp-')===0?'meta-lp':'website',
      utm_source:getC('_utm_source'),utm_medium:getC('_utm_medium'),utm_campaign:getC('_utm_campaign')};
    // (1) browser signal — Google live (conv action 7704636228).
    // Meta browser-side stays PageView-only BY DESIGN: `Lead` fires server-side via
    // Railway CAPI on qualified submits (event_id above is the dedupe key if that
    // ever changes). Do not add fbq('track','Lead') here.
    // Enhanced Conversions: hand gtag the raw values BEFORE the conversion event —
    // Google hashes them client-side. Email is the strongest key; phone + name/city back it up.
    try{
      var nm=this.name.value.trim(), sp=nm.indexOf(' ');
      gtag('set','user_data',{
        email:this.email.value.trim(),
        phone_number:this.phone.value.trim(),
        address:{first_name:(sp>0?nm.slice(0,sp):nm),last_name:(sp>0?nm.slice(sp+1):''),
                 city:town,country:'CA'}
      });
    }catch(_){}
    try{gtag('event','conversion',{send_to:'AW-18360839838/TmuOCMTW7dkcEJ7dkLNE'});}catch(_){}
    /* GA4 generate_lead. Added 2026-08-20 — it was missing, so Google ADS could see
       leads and GA4 could not, and the funnel had no terminal event. That makes
       "zero leads" and "we cannot see leads" produce identical output, which is
       exactly how KDT's $452/week of zero went undiagnosed for a week.
       send_to is PINNED to the GA4 id deliberately: an unpinned gtag('event') fans
       out to every configured target including the AW- above, which would
       double-count the Ads conversion fired on the previous line. */
    try{gtag('event','generate_lead',{send_to:'G-0YEVFG52V0',event_id:eid,
      page:(location.pathname.split('/').pop()||'index').replace(/\.html$/,''),
      value:0,currency:'CAD'});}catch(_){}
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
