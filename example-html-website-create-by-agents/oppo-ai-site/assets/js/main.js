document.addEventListener('DOMContentLoaded',function(){
  var toggle=document.querySelector('.nav-toggle');
  var navList=document.getElementById('nav-list');
  if(toggle&&navList){
    toggle.addEventListener('click',function(){
      var expanded=toggle.getAttribute('aria-expanded')==='true';
      toggle.setAttribute('aria-expanded',(!expanded).toString());
      if(navList.style.display==='block'){navList.style.display=''}else{navList.style.display='block'}
    });
  }

  // Simple form handler for Formspree
  var form=document.getElementById('contact-form');
  var status=document.getElementById('form-status');
  if(form){
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var data=new FormData(form);
      // simple honeypot check
      if(data.get('website')){status.textContent='Spam detected';return}
      fetch(form.action,{method:'POST',body:data,headers:{'Accept':'application/json'}}).then(function(resp){
        if(resp.ok){status.textContent='Thanks! Your message was sent.';form.reset()}else{return resp.json().then(function(data){throw new Error(data.error||'Form submission failed')})}
      }).catch(function(err){status.textContent='Error sending message. Please try mailto:hello@oppoai.example or try again later.'})
    })
  }
});