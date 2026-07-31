// ---- click-id capture -> 90 day cookie -> hidden gclid on the form-card ----
  (function(){
    function setC(n,v){document.cookie=n+'='+v+';path=/;max-age='+(90*86400)+';SameSite=Lax';}
    function getC(n){var v=('; '+document.cookie).split('; '+n+'=');return v.length===2?v.pop().split(';').shift():'';}
    try{
      var p=new URLSearchParams(location.search);
      if(p.get('gclid'))setC('_gclid',p.get('gclid'));
      if(p.get('fbclid'))setC('_fbc','fb.1.'+Date.now()+'.'+p.get('fbclid'));
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
      gclid:getC('_gclid'),fbp:getC('_fbp'),fbc:getC('_fbc'),event_id:eid,source:(location.pathname.split('/').pop()||'').indexOf('lp-')===0?'meta-lp':'website'};
    // (1) browser signal — ENABLE ONLY once the new pixel / conversion action exist (N1)
    // try{fbq('track','Lead',{content_name:'Creative Edge '+payload.page},{eventID:eid});}catch(_){}
    // try{gtag('event','conversion',{send_to:'AW-XXXXXXXXXX/LABEL'});}catch(_){}
    // (2) server side -> Railway: honeypot + phone validate -> GHL upsert + speed-to-lead -> CAPI Lead (hashed)
    // ⚠️ ENDPOINT NOT BUILT YET — /webhook/creative_edge/lp-lead must exist before launch.
    try{fetch('https://profound-truth-production-4190.up.railway.app/webhook/creative_edge/lp-lead',
      {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),keepalive:true});}catch(_){}
    // (3) thank you
    this.style.display='none';
    var d=document.getElementById('done'); d.classList.add('on'); d.scrollIntoView({behavior:'smooth',block:'center'});
  });
