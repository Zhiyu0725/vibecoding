const scoreEl = document.getElementById('score');
const timeEl = document.getElementById('time');
const startBtn = document.getElementById('startBtn');
const board = document.getElementById('board');
const target = document.getElementById('target');
const messageEl = document.getElementById('message');

let score = 0;
let timeLeft = 15;
let gameActive = false;
let timerId = null;

function updateHud() {
  scoreEl.textContent = score;
  timeEl.textContent = timeLeft;
}

function placeTarget() {
  const boardRect = board.getBoundingClientRect();
  const targetSize = 72;
  const x = Math.random() * (boardRect.width - targetSize - 12) + 6;
  const y = Math.random() * (boardRect.height - targetSize - 12) + 6;

  target.style.left = `${x}px`;
  target.style.top = `${y}px`;
}

function endGame() {
  gameActive = false;
  clearInterval(timerId);
  target.hidden = true;
  startBtn.disabled = false;
  messageEl.textContent = `Time is up! You scored ${score}. Click start to play again.`;
}

function startGame() {
  score = 0;
  timeLeft = 15;
  gameActive = true;
  updateHud();
  startBtn.disabled = true;
  target.hidden = false;
  placeTarget();
  messageEl.textContent = 'Go!';

  clearInterval(timerId);
  timerId = setInterval(() => {
    timeLeft -= 1;
    updateHud();

    if (timeLeft <= 0) {
      endGame();
    }
  }, 1000);
}

target.addEventListener('click', () => {
  if (!gameActive) return;

  score += 1;
  updateHud();
  messageEl.textContent = 'Nice! Keep going!';
  placeTarget();
});

startBtn.addEventListener('click', startGame);

target.hidden = true;
updateHud();
