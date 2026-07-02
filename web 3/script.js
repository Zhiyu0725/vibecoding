// Toggle the mobile navigation menu for smaller screens
const navToggle = document.getElementById('navToggle');
const navList = document.getElementById('navList');
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

navToggle?.addEventListener('click', () => {
  navList?.classList.toggle('show');
});

// Theme toggle button: switch between dark and light mode
themeToggle?.addEventListener('click', () => {
  body.classList.toggle('light-mode');
  themeToggle.textContent = body.classList.contains('light-mode') ? '☀️' : '🌙';
});

// Smooth scrolling for internal anchor links
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = event.currentTarget.getAttribute('href');
    if (target && target.startsWith('#')) {
      event.preventDefault();
      const element = document.querySelector(target);
      element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      navList?.classList.remove('show');
    }
  });
});

// Carbon footprint calculator logic
const footprintForm = document.getElementById('footprintForm');
const transportInput = document.getElementById('transportMiles');
const electricityInput = document.getElementById('electricityUsage');
const dietInput = document.getElementById('dietType');
const footprintResult = document.getElementById('footprintResult');

// Mini-game elements for the ecological recycling challenge
const gameItemName = document.getElementById('gameItemName');
const gameItemHint = document.getElementById('gameItemHint');
const gameFeedback = document.getElementById('gameFeedback');
const gameScore = document.getElementById('gameScore');
const gameButtons = document.querySelectorAll('.game-buttons button');

const contactForm = document.getElementById('contactForm');
const contactStatus = document.getElementById('contactStatus');

// Simple formula to estimate carbon footprint from daily habits
function calculateFootprint(transportMiles, electricityUsage, dietType) {
  const transportEmissions = transportMiles * 0.65; // pounds CO2 per mile driven
  const electricityEmissions = electricityUsage * 0.43; // pounds CO2 per kWh
  const dietMultiplier = {
    meat: 1.0,
    mixed: 0.82,
    vegetarian: 0.66,
    vegan: 0.5,
  };
  const dietEmissions = 25 * dietMultiplier[dietType] || 20;

  return transportEmissions + electricityEmissions + dietEmissions;
}

footprintForm?.addEventListener('submit', (event) => {
  event.preventDefault();

  const transportMiles = Number(transportInput?.value || 0);
  const electricityUsage = Number(electricityInput?.value || 0);
  const dietType = dietInput?.value || 'mixed';

  const totalEmissions = calculateFootprint(transportMiles, electricityUsage, dietType);
  const rounded = totalEmissions.toFixed(1);

  footprintResult.textContent = `Your estimated weekly carbon footprint is ${rounded} lbs of CO₂. Small changes, like reducing driving and choosing plant-based meals, can make a big difference.`;
});

contactForm?.addEventListener('submit', (event) => {
  event.preventDefault();

  const name = document.getElementById('contactName')?.value.trim();
  const email = document.getElementById('contactEmail')?.value.trim();
  const message = document.getElementById('contactMessage')?.value.trim();

  if (!name || !email || !message) {
    contactStatus.textContent = 'Please fill in all fields before sending your message.';
    contactStatus.style.color = '#f7b7b7';
    return;
  }

  contactStatus.textContent = `Thank you, ${name}! Your message has been received. We will reply to ${email} soon.`;
  contactStatus.style.color = '#c6f6d5';
  contactForm.reset();
});

// Mini-game data and logic
const gameItems = [
  { name: 'Plastic Bottle', bin: 'recycle', hint: 'Plastic items usually go in recycling.' },
  { name: 'Banana Peel', bin: 'compost', hint: 'Food waste belongs in compost.' },
  { name: 'Pizza Box', bin: 'trash', hint: 'Grease can make cardboard unrecyclable.' },
  { name: 'Glass Jar', bin: 'recycle', hint: 'Glass can often be recycled.' },
  { name: 'Apple Core', bin: 'compost', hint: 'Fruits and vegetables compost well.' },
];
let currentGameIndex = 0;
let currentScore = 0;

function updateGameCard() {
  const currentItem = gameItems[currentGameIndex];
  if (!currentItem) return;
  gameItemName.textContent = currentItem.name;
  gameItemHint.textContent = currentItem.hint;
  gameFeedback.textContent = 'Choose the correct bin for this item.';
}

function updateGameScore() {
  gameScore.textContent = String(currentScore);
}

gameButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const selectedBin = button.dataset.bin;
    const currentItem = gameItems[currentGameIndex];
    if (!currentItem) return;

    if (selectedBin === currentItem.bin) {
      currentScore += 10;
      gameFeedback.textContent = `Great job! ${currentItem.name} belongs in the ${selectedBin} bin.`;
      gameFeedback.classList.remove('feedback-error');
      gameFeedback.classList.add('feedback-success');
      gameItemName.classList.add('correct');
    } else {
      gameFeedback.textContent = `Oops! ${currentItem.name} should go in the ${currentItem.bin} bin.`;
      gameFeedback.classList.remove('feedback-success');
      gameFeedback.classList.add('feedback-error');
      gameItemName.classList.add('wrong');
    }

    updateGameScore();
    currentGameIndex = (currentGameIndex + 1) % gameItems.length;
    setTimeout(() => {
      updateGameCard();
      gameItemName.classList.remove('correct', 'wrong');
      gameFeedback.classList.remove('feedback-success', 'feedback-error');
    }, 1200);
  });
});

updateGameCard();
updateGameScore();

// Set initial theme label based on current mode
themeToggle.textContent = body.classList.contains('light-mode') ? '☀️' : '🌙';
