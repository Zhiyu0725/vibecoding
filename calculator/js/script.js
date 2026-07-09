// Interaction scripts: nav toggle, smooth scroll, calculator logic, forms, FAQ
document.addEventListener('DOMContentLoaded', () => {
  // Year
  document.getElementById('year').textContent = new Date().getFullYear();

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const navList = document.getElementById('nav-list');
  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!expanded));
    navList.style.display = expanded ? 'none' : 'flex';
  });

  // Smooth links
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click', (e)=>{
      const href = a.getAttribute('href');
      if(href.length>1){
        e.preventDefault();
        const el = document.querySelector(href);
        if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
        // close nav on mobile
        if(window.innerWidth<900) { navList.style.display='none'; toggle.setAttribute('aria-expanded','false'); }
      }
    });
  });

  // Calculator logic
  const display = document.querySelector('.calc-display');
  const keys = document.querySelectorAll('.calc-grid button');
  let current = '';

  function updateDisplay(v){ display.value = v===''? '0' : v }

  keys.forEach(k=>{
    k.addEventListener('click', ()=>{
      const val = k.getAttribute('data-value');
      const action = k.getAttribute('data-action');
      if(action==='clear'){ current=''; updateDisplay(current); return }
      if(action==='back'){ current = current.slice(0,-1); updateDisplay(current); return }
      if(action==='equals'){
        try{ // evaluate safely
          const result = Function('return ('+current.replace('×','*').replace('÷','/')+')')();
          current = String(result);
        }catch(e){ current = 'Error' }
        updateDisplay(current); return
      }
      // input value
      current += val;
      updateDisplay(current);
    })
  });

  // FAQ accordion
  document.querySelectorAll('.faq-item').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      btn.classList.toggle('open');
      const panel = btn.nextElementSibling;
      if(panel.style.display==='block'){ panel.style.display='none' }
      else{ panel.style.display='block' }
    })
  });

  // Contact form
  const contact = document.getElementById('contact-form');
  contact.addEventListener('submit', (e)=>{
    e.preventDefault();
    const fd = new FormData(contact);
    // minimal validation
    const name = fd.get('name');
    const email = fd.get('email');
    const msg = fd.get('message');
    const feedback = document.getElementById('contact-feedback');
    if(!name||!email||!msg){ feedback.textContent = 'Please complete all fields.'; return }
    feedback.textContent = 'Thanks — message sent (demo).';
    contact.reset();
  });

  // Newsletter
  const news = document.getElementById('newsletter');
  news.addEventListener('submit', (e)=>{
    e.preventDefault();
    const email = news.querySelector('input[name="email"]').value;
    const fb = document.getElementById('news-feedback');
    if(!email){ fb.textContent='Enter a valid email.'; return }
    fb.textContent = 'Subscribed — demo.';
    news.reset();
  });

});