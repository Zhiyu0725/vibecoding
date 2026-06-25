// Theme toggle and mobile nav
const themeToggle = document.getElementById('themeToggle');
const navToggle = document.getElementById('navToggle');
const navList = document.getElementById('navList');

themeToggle && themeToggle.addEventListener('click', ()=>{
  const current = document.documentElement.getAttribute('data-theme');
  if(current === 'light'){
    document.documentElement.removeAttribute('data-theme');
    themeToggle.textContent = '🌙';
  } else {
    document.documentElement.setAttribute('data-theme','light');
    themeToggle.textContent = '☀️';
  }
});

navToggle && navToggle.addEventListener('click', ()=>{
  if(navList.style.display === 'flex') navList.style.display = 'none';
  else navList.style.display = 'flex';
});

// Smooth scrolling for internal links
document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click', e=>{
    const href = a.getAttribute('href');
    if(href.length>1){
      e.preventDefault();
      document.querySelector(href).scrollIntoView({behavior:'smooth'});
      if(window.innerWidth<=880) navList.style.display='none';
    }
  })
});
