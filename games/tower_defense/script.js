const startBtn = document.getElementById('startBtn');
const goldEl = document.getElementById('gold');
const livesEl = document.getElementById('lives');
const waveEl = document.getElementById('wave');
const scoreEl = document.getElementById('score');
const messageEl = document.getElementById('message');
const container = document.getElementById('gameContainer');

const TOWER_CONFIG = {
  basic: { cost: 40, range: 22, fireRate: 650, damage: 18, color: 0x22c55e },
  sniper: { cost: 70, range: 40, fireRate: 2200, damage: 35, color: 0xa78bfa },
  aoe: { cost: 60, range: 24, fireRate: 1800, damage: 14, color: 0xf43f5e },
  freeze: { cost: 80, range: 26, fireRate: 1400, damage: 12, color: 0x38bdf8 },
  laser: { cost: 90, range: 30, fireRate: 320, damage: 6, color: 0xfb7185 },
  mine: { cost: 100, range: 20, fireRate: 2400, damage: 28, color: 0xf59e0b },
  storm: { cost: 110, range: 34, fireRate: 2000, damage: 20, color: 0x818cf8 }
};
TOWER_CONFIG.trap = { cost: 30, range: 10, fireRate: 0, damage: 80, color: 0x94a3b8 };

const MENU_PRICE_MULTIPLIER = 7;
const UPGRADE_DAMAGE_MULT = 1.12;
const UPGRADE_FIRE_RATE_MULT = 0.9;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111f);
scene.fog = new THREE.Fog(0x07111f, 80, 160);

const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 300);
camera.position.set(0, 50, 70);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(40, 80, 30);
dirLight.castShadow = true;
scene.add(dirLight);

const gamePath = [
  { x: -34, z: -20 },
  { x: -18, z: -20 },
  { x: -18, z: 6 },
  { x: 0, z: 6 },
  { x: 0, z: -20 },
  { x: 18, z: -20 },
  { x: 18, z: 20 },
  { x: 34, z: 20 }
];

let towers = [];
let enemies = [];
let projectiles = [];
let gold = 180;
let menuGold = 0;
let lives = 20;
let availableTowers = { basic: true };
let upgrades = {};
let wave = 0;
let score = 0;
let running = false;
let gameStarted = false;
let spawnTimer = 0;
let enemyCount = 0;
let selectedTowerType = 'basic';
let lastTime = 0;
let animationTime = 0;
let towerGroup = new THREE.Group();
let enemyGroup = new THREE.Group();
let projectileGroup = new THREE.Group();
scene.add(towerGroup, enemyGroup, projectileGroup);

function createBoard() {
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(90, 90),
    new THREE.MeshStandardMaterial({ color: 0x2f5e2f, roughness: 0.95 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(8, 6, 8),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0x4a2c00, emissiveIntensity: 0.35 })
  );
  base.position.set(34, 3, 20);
  base.castShadow = true;
  base.receiveShadow = true;
  scene.add(base);

  const pathMaterial = new THREE.MeshStandardMaterial({ color: 0x444444, roughness: 1 });
  for (let i = 0; i < gamePath.length - 1; i++) {
    const p1 = gamePath[i];
    const p2 = gamePath[i + 1];
    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const dist = Math.hypot(dx, dz);
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(6, 0.2, dist), pathMaterial);
    mesh.position.set((p1.x + p2.x) / 2, 0.11, (p1.z + p2.z) / 2);
    mesh.rotation.y = Math.atan2(dx, dz);
    mesh.receiveShadow = true;
    scene.add(mesh);
  }
}

createBoard();

function clearArray(objects) {
  for (const obj of objects) {
    if (obj.mesh) scene.remove(obj.mesh);
    if (obj.group) scene.remove(obj.group);
  }
}

function resetGame() {
  clearArray(towers);
  clearArray(enemies);
  clearArray(projectiles);
  towers = [];
  enemies = [];
  projectiles = [];
  gold = 180;
  lives = 20;
  availableTowers = { basic: true };
  upgrades = {};
  wave = 0;
  score = 0;
  running = true;
  gameStarted = true;
  spawnTimer = 0;
  enemyCount = 0;
  selectedTowerType = 'basic';
  lastTime = 0;
  animationTime = 0;
  updateTowerButtons();
  renderTowerPicker();
  renderUpgrades();
  messageEl.textContent = 'Wave 1 incoming!';
  updateHud();
}

function updateHud() {
  goldEl.textContent = gold;
  livesEl.textContent = lives;
  waveEl.textContent = wave;
  scoreEl.textContent = score;
  const menuGoldEl = document.getElementById('menuGold');
  if (menuGoldEl) menuGoldEl.textContent = menuGold;
}

function addGold(reward) {
  gold += reward + Math.floor(wave * 2);
  updateHud();
}

function addMenuGold(amount) {
  menuGold += amount;
  updateHud();
}

function getPathPosition(progress) {
  const total = gamePath.length - 1;
  const index = Math.min(total - 1, Math.floor(progress * total));
  const p1 = gamePath[index];
  const p2 = gamePath[index + 1];
  const local = progress * total - index;
  return {
    x: p1.x + (p2.x - p1.x) * local,
    z: p1.z + (p2.z - p1.z) * local
  };
}

function createTower(x, z, type) {
  const config = TOWER_CONFIG[type];
  const group = new THREE.Group();
  const base = new THREE.Mesh(
    new THREE.CylinderGeometry(2.8, 3.4, 2.4, 10),
    new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 0.6 })
  );
  const body = new THREE.Mesh(
    new THREE.CylinderGeometry(1.2, 1.6, 4.2, 10),
    new THREE.MeshStandardMaterial({ color: config.color, metalness: 0.5, roughness: 0.4 })
  );
  body.position.y = 3.2;
  body.castShadow = true;
  base.castShadow = true;
  base.receiveShadow = true;
  group.add(base, body);
  group.position.set(x, 0, z);
  scene.add(group);
  towerGroup.add(group);
  return { group, x, z, type, ...config, cooldown: 0, projectileCooldown: 0 };
}

function createEnemy() {
  const enemyType = wave >= 2 ? (Math.random() < 0.3 ? 1 : Math.random() < 0.6 ? 2 : 0) : Math.floor(Math.random() * 3);
  const config = [
    { hp: 40, speed: 1.6, radius: 1.2, color: 0xef4444, reward: 12 },
    { hp: 70, speed: 1.1, radius: 1.5, color: 0xf59e0b, reward: 18 },
    { hp: 30, speed: 2.2, radius: 0.9, color: 0x38bdf8, reward: 14 }
  ][enemyType];
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(config.radius * 1.7, config.radius * 1.7, config.radius * 1.7),
    new THREE.MeshStandardMaterial({ color: config.color, emissive: config.color, emissiveIntensity: 0.2 })
  );
  mesh.position.set(-34, 1.8, -20);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);
  enemyGroup.add(mesh);
  enemies.push({ mesh, hp: config.hp + wave * 10, maxHp: config.hp + wave * 10, speed: config.speed + wave * 0.05, reward: config.reward, progress: 0, slow: 0 });
}

function createProjectile(fromX, fromZ, target, damage, type) {
  const color = TOWER_CONFIG[type].color;
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.45, 10, 10),
    new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.35 })
  );
  mesh.position.set(fromX, 2.5, fromZ);
  mesh.castShadow = true;
  scene.add(mesh);
  projectileGroup.add(mesh);
  projectiles.push({ mesh, x: fromX, z: fromZ, target, damage, type });
}

function placeTower(x, z) {
  if (!running || !gameStarted) return;
  const config = TOWER_CONFIG[selectedTowerType];
  if (!config) return;
  if (!availableTowers[selectedTowerType]) {
    messageEl.textContent = 'This tower is locked. Buy it from Equip first.';
    return;
  }
  if (gold < config.cost) {
    messageEl.textContent = 'Not enough gold for this tower.';
    return;
  }
  for (const tower of towers) {
    if (Math.hypot(tower.x - x, tower.z - z) < 6) {
      messageEl.textContent = 'Too close to another tower.';
      return;
    }
  }

  const level = upgrades[selectedTowerType]?.level || 0;
  const damage = Math.round(config.damage * Math.pow(UPGRADE_DAMAGE_MULT, level));
  const fireRate = Math.max(80, Math.round(config.fireRate * Math.pow(UPGRADE_FIRE_RATE_MULT, level)));
  const tower = createTower(x, z, selectedTowerType);
  tower.damage = damage;
  tower.fireRate = fireRate;
  towers.push(tower);
  gold -= config.cost;
  updateHud();
  messageEl.textContent = `${selectedTowerType} tower placed.`;
}

function updateEnemies(dt) {
  for (let i = enemies.length - 1; i >= 0; i--) {
    const enemy = enemies[i];
    const speed = enemy.speed * (enemy.slow > 0 ? 0.45 : 1);
    enemy.progress = Math.min(1, enemy.progress + (speed * dt) / 1000);
    const pos = getPathPosition(enemy.progress);
    enemy.mesh.position.set(pos.x, 1.8, pos.z);
    if (enemy.slow > 0) enemy.slow = Math.max(0, enemy.slow - dt);
    if (enemy.progress >= 1) {
      scene.remove(enemy.mesh);
      enemies.splice(i, 1);
      lives -= 1;
      if (lives <= 0) {
        running = false;
        messageEl.textContent = 'Game over!';
      }
      updateHud();
    }
  }
}

function updateTowers(dt) {
  for (const tower of towers) {
    tower.cooldown -= dt;
    if (tower.cooldown <= 0) {
      let target = null;
      let closestDist = Infinity;
      for (const enemy of enemies) {
        const dist = Math.hypot(tower.x - enemy.mesh.position.x, tower.z - enemy.mesh.position.z);
        if (dist <= tower.range && dist < closestDist) {
          closestDist = dist;
          target = enemy;
        }
      }
      if (target) {
        tower.cooldown = tower.fireRate;
        createProjectile(tower.x, tower.z, target, tower.damage, tower.type);
      }
    }
  }
}

function updateProjectiles(dt) {
  for (let i = projectiles.length - 1; i >= 0; i--) {
    const proj = projectiles[i];
    const enemy = proj.target;
    if (!enemy) {
      scene.remove(proj.mesh);
      projectiles.splice(i, 1);
      continue;
    }
    const dx = enemy.mesh.position.x - proj.x;
    const dz = enemy.mesh.position.z - proj.z;
    const dist = Math.hypot(dx, dz);
    if (dist < 0.8) {
      enemy.hp -= proj.damage;
      if (proj.type === 'freeze') enemy.slow = 1300;
      if (enemy.hp <= 0) {
        scene.remove(enemy.mesh);
        const idx = enemies.indexOf(enemy);
        if (idx >= 0) enemies.splice(idx, 1);
        addGold(enemy.reward);
        score += 10;
        updateHud();
      }
      scene.remove(proj.mesh);
      projectiles.splice(i, 1);
      continue;
    }
    const moveAmount = (1.8 + dt / 600) * dt / 1000;
    proj.x += (dx / dist) * moveAmount;
    proj.z += (dz / dist) * moveAmount;
    proj.mesh.position.set(proj.x, 2.5, proj.z);
  }
}

function updateWave(dt) {
  if (!running || !gameStarted) return;
  spawnTimer += dt;
  const count = 4 + wave * 2;
  if (enemyCount < count && spawnTimer > 900) {
    createEnemy();
    enemyCount += 1;
    spawnTimer = 0;
  }
  if (enemyCount >= count && enemies.length === 0) {
    wave += 1;
    enemyCount = 0;
    spawnTimer = 0;
    addMenuGold(20 + Math.floor(wave * 5));
    messageEl.textContent = `Wave ${wave} complete.`;
    updateHud();
  }
}

function renderShop() {
  const shopList = document.getElementById('shopList');
  shopList.innerHTML = '';
  const options = { sniper: 70, aoe: 60, freeze: 80, laser: 90, mine: 100, storm: 110, trap: 30 };
  Object.entries(options).forEach(([key, cost]) => {
    const row = document.createElement('div');
    row.className = 'shop-item';
    const menuCost = cost * MENU_PRICE_MULTIPLIER;
    row.innerHTML = `<div>${key} - ${menuCost}g</div>`;
    const btn = document.createElement('button');
    btn.textContent = availableTowers[key] ? 'Owned' : 'Buy';
    btn.disabled = availableTowers[key];
    btn.addEventListener('click', () => buyTower(key, menuCost));
    row.appendChild(btn);
    shopList.appendChild(row);
  });
}

function renderTowerPicker() {
  const picker = document.getElementById('towerPicker');
  picker.innerHTML = '';
  Object.keys(TOWER_CONFIG).forEach((key) => {
    if (!availableTowers[key]) return;
    const btn = document.createElement('button');
    btn.className = 'tower-btn' + (key === selectedTowerType ? ' active' : '');
    btn.type = 'button';
    btn.textContent = `${key.charAt(0).toUpperCase() + key.slice(1)} (${TOWER_CONFIG[key].cost})`;
    btn.addEventListener('click', () => {
      selectedTowerType = key;
      updateTowerButtons();
      messageEl.textContent = `${selectedTowerType} selected.`;
    });
    picker.appendChild(btn);
  });
}

function renderUpgrades() {
  const upgradeList = document.getElementById('upgradeList');
  upgradeList.innerHTML = '';
  Object.keys(availableTowers).filter((key) => availableTowers[key]).forEach((key) => {
    const level = upgrades[key]?.level || 0;
    const cost = 50 + level * 60;
    const row = document.createElement('div');
    row.className = 'upgrade-item';
    row.innerHTML = `<div>${key} - level ${level}</div>`;
    const btn = document.createElement('button');
    btn.textContent = `Upgrade (${cost}g)`;
    btn.addEventListener('click', () => upgradeTower(key, cost));
    row.appendChild(btn);
    upgradeList.appendChild(row);
  });
}

function buyTower(key, cost) {
  if (availableTowers[key]) {
    messageEl.textContent = `${key} already available.`;
    return;
  }
  if (menuGold < cost) {
    messageEl.textContent = 'Not enough menu gold to buy this tower.';
    return;
  }
  menuGold -= cost;
  availableTowers[key] = true;
  updateHud();
  renderShop();
  renderTowerPicker();
  messageEl.textContent = `${key} unlocked.`;
}

function upgradeTower(key, cost) {
  if (menuGold < cost) {
    messageEl.textContent = 'Not enough menu gold to upgrade.';
    return;
  }
  menuGold -= cost;
  upgrades[key] = upgrades[key] || { level: 0 };
  upgrades[key].level += 1;
  updateHud();
  renderUpgrades();
  messageEl.textContent = `${key} upgraded.`;
}

function updateTowerButtons() {
  document.querySelectorAll('#towerPicker .tower-btn').forEach((button) => {
    button.classList.toggle('active', button.textContent.toLowerCase().startsWith(selectedTowerType));
  });
}

const mainMenu = document.getElementById('mainMenu');
const equipBtn = document.getElementById('equipBtn');
const playMenuBtn = document.getElementById('playMenuBtn');
const upgradeBtn = document.getElementById('upgradeBtn');
const shopOverlay = document.getElementById('shopOverlay');
const closeShop = document.getElementById('closeShop');
const upgradeOverlay = document.getElementById('upgradeOverlay');
const closeUpgrade = document.getElementById('closeUpgrade');
const menuBtn = document.getElementById('menuBtn');

function showMenu() { mainMenu.classList.remove('hidden'); }
function hideMenu() { mainMenu.classList.add('hidden'); }

equipBtn.addEventListener('click', () => {
  renderShop();
  shopOverlay.classList.remove('hidden');
});
closeShop.addEventListener('click', () => shopOverlay.classList.add('hidden'));
upgradeBtn.addEventListener('click', () => {
  renderUpgrades();
  upgradeOverlay.classList.remove('hidden');
});
closeUpgrade.addEventListener('click', () => upgradeOverlay.classList.add('hidden'));
menuBtn.addEventListener('click', () => {
  showMenu();
  updateHud();
});
playMenuBtn.addEventListener('click', () => {
  hideMenu();
  resetGame();
});
startBtn.addEventListener('click', () => {
  resetGame();
  messageEl.textContent = 'New game started!';
});

showMenu();
renderTowerPicker();
renderUpgrades();
updateHud();

container.addEventListener('click', (event) => {
  if (!running || !gameStarted) return;
  const rect = container.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  const z = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(new THREE.Vector2(x, z), camera);
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  const point = new THREE.Vector3();
  raycaster.ray.intersectPlane(plane, point);
  if (point) placeTower(point.x, point.z);
});

function animate(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const dt = timestamp - lastTime;
  lastTime = timestamp;
  animationTime += dt;

  if (running && gameStarted) {
    updateEnemies(dt);
    updateTowers(dt);
    updateProjectiles(dt);
    updateWave(dt);
  }

  towers.forEach((tower) => {
    if (tower.group) tower.group.rotation.y += 0.01;
  });

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

window.addEventListener('resize', () => {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
});

requestAnimationFrame(animate);

updateTowerButtons();
updateHud();
