// Toggle sound on/off and update button text
const soundToggle = document.getElementById('soundToggle');
let soundEnabled = true;

soundToggle?.addEventListener('click', () => {
  soundEnabled = !soundEnabled;
  soundToggle.textContent = soundEnabled ? 'Sound On' : 'Sound Off';
});

// Store leaderboard scores in localStorage
const leaderboardKey = 'escape-mansion-leaderboard';
const leaderboardForm = document.getElementById('leaderboardForm');
const leaderboardList = document.getElementById('leaderboardList');

function getLeaderboard() {
  return JSON.parse(localStorage.getItem(leaderboardKey) || '[]');
}

function saveLeaderboardEntry(entry) {
  const leaderboard = getLeaderboard();
  leaderboard.push(entry);
  leaderboard.sort((a, b) => a.time - b.time);
  localStorage.setItem(leaderboardKey, JSON.stringify(leaderboard.slice(0, 10)));
}

function renderLeaderboard() {
  const leaderboard = getLeaderboard();
  if (!leaderboard.length) {
    leaderboardList.innerHTML = '<li>No scores yet. Be the first to escape!</li>';
    return;
  }

  leaderboardList.innerHTML = leaderboard
    .map((entry) => `<li><span>${entry.name}</span><strong>${entry.time}s</strong></li>`)
    .join('');
}

leaderboardForm?.addEventListener('submit', (event) => {
  event.preventDefault();
  const nameInput = document.getElementById('leaderName');
  const timeInput = document.getElementById('leaderTime');

  const name = nameInput?.value.trim();
  const time = Number(timeInput?.value);

  if (!name || !time) return;

  saveLeaderboardEntry({ name, time });
  renderLeaderboard();
  nameInput.value = '';
  timeInput.value = '';
});

// Smooth scroll for nav links
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = event.currentTarget.getAttribute('href');
    if (target?.startsWith('#')) {
      event.preventDefault();
      const section = document.querySelector(target);
      section?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// Room tabs switching
const tabButtons = document.querySelectorAll('.tab-button');
const roomPanels = document.querySelectorAll('.room-panel');

function setActiveRoom(roomNumber) {
  tabButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.room === roomNumber);
  });
  roomPanels.forEach((panel) => {
    panel.classList.toggle('active', panel.dataset.room === roomNumber);
  });
}

tabButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setActiveRoom(button.dataset.room);
  });
});

setActiveRoom('1');

// Countdown timers for three rooms
const timers = {
  1: { minutes: 3, seconds: 0, interval: null, element: document.getElementById('timer1') },
  2: { minutes: 4, seconds: 0, interval: null, element: document.getElementById('timer2') },
  3: { minutes: 5, seconds: 0, interval: null, element: document.getElementById('timer3') },
};

function formatTime(minutes, seconds) {
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function startTimer(roomId) {
  const timer = timers[roomId];
  if (!timer) return;
  timer.element.textContent = formatTime(timer.minutes, timer.seconds);
  timer.interval = setInterval(() => {
    if (timer.seconds === 0) {
      if (timer.minutes === 0) {
        clearInterval(timer.interval);
        timer.element.textContent = '00:00';
        return;
      }
      timer.minutes -= 1;
      timer.seconds = 59;
    } else {
      timer.seconds -= 1;
    }
    timer.element.textContent = formatTime(timer.minutes, timer.seconds);
  }, 1000);
}

startTimer('1');
startTimer('2');
startTimer('3');

// Inventory management
const inventory = new Set();
const inventoryList = document.getElementById('inventoryList');
const inventoryList2 = document.getElementById('inventoryList2');
const inventoryList3 = document.getElementById('inventoryList3');

function addInventoryItem(listElement, item) {
  inventory.add(item);
  if (!listElement) return;
  listElement.innerHTML = `<li>${item}</li>`;
}

const collectBookBtn = document.getElementById('collectBookBtn');
const collectPaperBtn = document.getElementById('collectPaperBtn');
const collectCandleBtn = document.getElementById('collectCandleBtn');

collectBookBtn?.addEventListener('click', () => {
  addInventoryItem(inventoryList, 'Library Key');
});

collectPaperBtn?.addEventListener('click', () => {
  addInventoryItem(inventoryList2, 'Code Fragment');
});

collectCandleBtn?.addEventListener('click', () => {
  addInventoryItem(inventoryList3, 'Haunted Candle');
});

// Puzzle logic and feedback
const puzzleForm1 = document.getElementById('puzzleForm1');
const puzzleAnswer1 = document.getElementById('puzzleAnswer1');
const puzzleFeedback1 = document.getElementById('puzzleFeedback1');

const puzzleForm2 = document.getElementById('puzzleForm2');
const puzzleAnswer2 = document.getElementById('puzzleAnswer2');
const puzzleFeedback2 = document.getElementById('puzzleFeedback2');

const puzzleFeedback3 = document.getElementById('puzzleFeedback3');
const patternGrid = document.getElementById('patternGrid');
const solvePatternBtn = document.getElementById('solvePatternBtn');

const patternSolution = [1, 3, 5, 7];
let selectedPattern = new Set();

function createPatternGrid() {
  if (!patternGrid) return;
  patternGrid.innerHTML = '';
  for (let i = 1; i <= 9; i += 1) {
    const tile = document.createElement('button');
    tile.type = 'button';
    tile.className = 'pattern-tile';
    tile.textContent = i;
    tile.addEventListener('click', () => {
      if (selectedPattern.has(i)) {
        selectedPattern.delete(i);
        tile.classList.remove('selected');
      } else {
        selectedPattern.add(i);
        tile.classList.add('selected');
      }
    });
    patternGrid.appendChild(tile);
  }
}

createPatternGrid();

puzzleForm1?.addEventListener('submit', (event) => {
  event.preventDefault();
  const answer = puzzleAnswer1.value.trim().toLowerCase();

  if (answer === 'pencil lead' || answer === 'lead') {
    puzzleFeedback1.textContent = 'Correct! The book unlocks the chest.';
    puzzleFeedback1.style.color = '#a3d17f';
  } else {
    puzzleFeedback1.textContent = 'Not quite. Try again.';
    puzzleFeedback1.style.color = '#e08b7d';
  }
});

puzzleForm2?.addEventListener('submit', (event) => {
  event.preventDefault();
  const answer = puzzleAnswer2.value.trim();

  if (answer === '1891') {
    puzzleFeedback2.textContent = 'Correct! The study door swings open.';
    puzzleFeedback2.style.color = '#a3d17f';
  } else {
    puzzleFeedback2.textContent = 'Wrong code. Check the clue again.';
    puzzleFeedback2.style.color = '#e08b7d';
  }
});

solvePatternBtn?.addEventListener('click', () => {
  const isCorrect = patternSolution.every((value) => selectedPattern.has(value)) && selectedPattern.size === patternSolution.length;
  if (isCorrect) {
    puzzleFeedback3.textContent = 'Well done! The attic pattern is complete.';
    puzzleFeedback3.style.color = '#a3d17f';
  } else {
    puzzleFeedback3.textContent = 'That pattern is incorrect. Adjust the glowing tiles.';
    puzzleFeedback3.style.color = '#e08b7d';
  }
});

// Enable light sound effects when toggled on
function playSound(type) {
  if (!soundEnabled) return;
  const audio = new Audio();
  if (type === 'correct') {
    audio.src = 'https://freesound.org/data/previews/240/240777_4024259-lq.mp3';
  } else if (type === 'wrong') {
    audio.src = 'https://freesound.org/data/previews/109/109662_945474-lq.mp3';
  }
  audio.volume = 0.25;
  audio.play().catch(() => null);
}

puzzleForm1?.addEventListener('submit', () => playSound('correct'));
puzzleForm2?.addEventListener('submit', () => playSound('correct'));
solvePatternBtn?.addEventListener('click', () => playSound('correct'));

renderLeaderboard();
