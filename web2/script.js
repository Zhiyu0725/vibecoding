const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    themeToggle.textContent = '☀️';
  }
  
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    if (current === 'light') {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'dark');
      themeToggle.textContent = '🌙';
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('theme', 'light');
      themeToggle.textContent = '☀️';
    }
  });
}

const emailBtn = document.getElementById('emailBtn');
if (emailBtn) {
  emailBtn.addEventListener('click', () => {
    alert('Email: hello@web2studio.com');
  });
}

const demoBtn = document.getElementById('demoBtn');
if (demoBtn) {
  demoBtn.addEventListener('click', () => {
    alert('Calendar link would open here. Visit our contact page!');
  });
}

const navLinks = document.querySelectorAll('.nav a');
navLinks.forEach(link => {
  link.addEventListener('click', (e) => {
    navLinks.forEach(l => l.style.color = '');
    link.style.color = 'var(--accent)';
    setTimeout(() => {
      link.style.color = '';
    }, 300);
  });
});

// Cursor glow tracker
const cursorGlow = document.getElementById('cursorGlow');

if (cursorGlow) {
  document.addEventListener('mousemove', (event) => {
    cursorGlow.style.left = `${event.clientX}px`;
    cursorGlow.style.top = `${event.clientY}px`;
    cursorGlow.classList.add('active');
  });

  document.addEventListener('mouseleave', () => {
    cursorGlow.classList.remove('active');
  });
}

// Calculator logic
const calcDisplay = document.getElementById('calcDisplay');
const calcButtons = document.querySelectorAll('.calc-buttons button');
let calcValue = '';

if (calcDisplay && calcButtons.length) {
  const updateDisplay = () => {
    calcDisplay.value = calcValue || '0';
  };

  calcButtons.forEach(button => {
    const value = button.dataset.value;
    const action = button.dataset.action;

    button.addEventListener('click', () => {
      if (action === 'clear') {
        calcValue = '';
      } else if (action === 'delete') {
        calcValue = calcValue.slice(0, -1);
      } else if (action === 'equals') {
        try {
          calcValue = String(eval(calcValue));
        } catch (err) {
          calcValue = 'Error';
        }
      } else if (value) {
        if (calcValue === 'Error') calcValue = '';
        calcValue += value;
      }
      updateDisplay();
    });
  });
}

// Typing test logic
const promptText = 'The quick brown fox jumps over the lazy dog.';
const typingPrompt = document.getElementById('typingPrompt');
const typingInput = document.getElementById('typingInput');
const typingWpm = document.getElementById('typingWpm');
const typingAccuracy = document.getElementById('typingAccuracy');
const typingReset = document.getElementById('typingReset');

let typingStartTime = null;

const updateTypingStats = () => {
  if (!typingInput || !typingWpm || !typingAccuracy) return;

  const typed = typingInput.value;
  const typedWords = typed.trim().split(/\s+/).filter(Boolean).length;
  const timeElapsed = typingStartTime ? Math.max((Date.now() - typingStartTime) / 1000, 1) : 1;
  const wpm = Math.round((typedWords / timeElapsed) * 60);

  let correctChars = 0;
  for (let i = 0; i < typed.length; i++) {
    if (typed[i] === promptText[i]) {
      correctChars += 1;
    }
  }

  const accuracy = typed.length ? Math.round((correctChars / typed.length) * 100) : 100;
  typingWpm.textContent = `${wpm} WPM`;
  typingAccuracy.textContent = `${accuracy}% accuracy`;
};

if (typingPrompt) {
  typingPrompt.textContent = `Type this phrase as quickly and accurately as you can: ${promptText}`;
}

if (typingInput) {
  typingInput.addEventListener('input', () => {
    if (!typingStartTime) {
      typingStartTime = Date.now();
    }
    updateTypingStats();
  });
}

if (typingReset) {
  typingReset.addEventListener('click', () => {
    if (typingInput) typingInput.value = '';
    typingStartTime = null;
    if (typingWpm) typingWpm.textContent = '0 WPM';
    if (typingAccuracy) typingAccuracy.textContent = '100% accuracy';
  });
}

// Click speed game logic
const gameStart = document.getElementById('gameStart');
const gameButton = document.getElementById('gameButton');
const gameScore = document.getElementById('gameScore');
const gameTimer = document.getElementById('gameTimer');

let score = 0;
let gameInterval = null;
let timeLeft = 10;

const resetGame = () => {
  score = 0;
  timeLeft = 10;
  if (gameScore) gameScore.textContent = '0';
  if (gameTimer) gameTimer.textContent = 'Time left: 10s';
  if (gameButton) gameButton.disabled = true;
};

const endGame = () => {
  clearInterval(gameInterval);
  if (gameButton) gameButton.disabled = true;
  if (gameTimer) gameTimer.textContent = `Game over: ${score} clicks`;
};

if (gameStart) {
  gameStart.addEventListener('click', () => {
    resetGame();
    if (gameButton) gameButton.disabled = false;
    typingStartTime = null;
    gameInterval = setInterval(() => {
      timeLeft -= 1;
      if (gameTimer) gameTimer.textContent = `Time left: ${timeLeft}s`;
      if (timeLeft <= 0) {
        endGame();
      }
    }, 1000);
  });
}

if (gameButton) {
  gameButton.addEventListener('click', () => {
    score += 1;
    if (gameScore) gameScore.textContent = String(score);
  });
}
