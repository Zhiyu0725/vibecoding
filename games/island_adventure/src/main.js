import * as THREE from 'three';
import { PlayerController } from './player.js';
import { createWorld, updateWorld, getGroundHeight } from './world.js';
import { spawnAnimalAt, updateAnimals, spawnMeatDrops } from './enemy.js';
import { createCollectibles, updateCollectibles, spawnHealthOrb } from './collectibles.js';
import { ProjectileSystem } from './projectiles.js';
import { HUD } from './hud.js';
import { Weather } from './weather.js';
import { createRabbits, createBirds, updateRabbits, updateBirds } from './creatures.js';
import {
  makeSword, makePistol, makeDamageNumber, updateDamageNumbers,
  getMeleeCandidates, applyKnockback,
  SWING_DURATION, SWING_COOLDOWN, MELEE_DAMAGE
} from './combat.js';
import { getRecipes, canCraft, craft } from './crafting.js';

const blocker = document.getElementById('blocker');
const hud = new HUD();

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x7ec8e3);
scene.fog = new THREE.Fog(0x7ec8e3, 60, 120);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 200);
const spawnHeight = getGroundHeight(0, 12) + 1.6;
camera.position.set(0, spawnHeight, 12);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.body.prepend(renderer.domElement);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  hud.resize();
});

const player = new PlayerController(camera, renderer.domElement, (x, z) => Math.max(0, getGroundHeight(x, z)));
const proj = new ProjectileSystem(scene);
const weather = new Weather(scene);

const sword = makeSword();
const pistol = makePistol();
sword.visible = false;
pistol.visible = false;
camera.add(sword);
camera.add(pistol);
let equippedWeapon = null;
let swingTimer = 0;
let swingCooldownTimer = 0;
let isSwinging = false;
let isBlocking = false;
const damageNumbers = [];

const animals = [];
const gems = [];
const healthOrbs = [];
let berryBushes = [];
let coconutTrees = [];
let rabbits = [];
let birds = [];

const MAX_ANIMALS = 12;
let score = 0;
let killCount = 0;
let shootCooldown = 0;
let hitCooldown = 0;

let hunger = 100;
let thirst = 100;

let craftingOpen = false;
let isFishing = false;
let fishingTimer = 0;
let fishingTime = 0;
let bobber = null;

const inventory = [];
const groundItems = [];
const campfires = [];
const HOTBAR_SIZE = 6;
let selectedSlot = 0;

addItem('Sword', '\u2694\uFE0F', () => {});
addItem('Gun', '\uD83D\uDD2B', () => {});
selectedSlot = 0;
updateEquippedWeapon();
hud.updateInventory(inventory);

function addItem(name, icon, useFn) {
  const existing = inventory.find(i => i.name === name);
  if (existing) {
    existing.count += 1;
  } else {
    inventory.push({ name, icon, count: 1, use: useFn });
  }
  hud.updateInventory(inventory);
}

function removeItem(name) {
  const idx = inventory.findIndex(i => i.name === name);
  if (idx >= 0) {
    inventory[idx].count -= 1;
    if (inventory[idx].count <= 0) inventory.splice(idx, 1);
  }
  if (selectedSlot >= inventory.length) selectedSlot = Math.max(0, inventory.length - 1);
  hud.setSelectedSlot(selectedSlot);
  hud.updateInventory(inventory);
}

function useSelectedItem() {
  const item = inventory[selectedSlot];
  if (item) item.use?.();
}

function useFood(amount, name) {
  return () => {
    hunger = Math.min(100, hunger + amount);
    hud.setHunger(hunger);
    removeItem(name || 'Berry');
  };
}

function spawnGroundItem(x, z, type) {
  const h = Math.max(0, getGroundHeight(x, z));
  const group = new THREE.Group();
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.2, 8),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.25, depthWrite: false, side: THREE.DoubleSide })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.01;
  group.add(shadow);

  if (type === 'berry') {
    const berry = new THREE.Mesh(
      new THREE.SphereGeometry(0.12, 8, 8),
      new THREE.MeshStandardMaterial({ color: 0xee3333, emissive: 0x991111, emissiveIntensity: 0.2, roughness: 0.3 })
    );
    berry.position.y = 0.12;
    berry.scale.set(1, 0.85, 1);
    group.add(berry);
    const leaf = new THREE.Mesh(
      new THREE.SphereGeometry(0.035, 5, 5),
      new THREE.MeshStandardMaterial({ color: 0x4caf4c })
    );
    leaf.position.set(0.07, 0.2, 0);
    leaf.scale.set(1, 0.4, 0.6);
    group.add(leaf);
  } else {
    const nut = new THREE.Mesh(
      new THREE.SphereGeometry(0.18, 8, 8),
      new THREE.MeshStandardMaterial({ color: 0x7a5c3a, roughness: 0.7 })
    );
    nut.scale.set(0.8, 1, 0.8);
    nut.position.y = 0.16;
    group.add(nut);
    const cap = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 6, 6),
      new THREE.MeshStandardMaterial({ color: 0x5a7a3a, roughness: 0.9 })
    );
    cap.scale.set(0.9, 0.3, 0.9);
    cap.position.set(0, 0.26, 0.02);
    group.add(cap);
  }
  const yBase = h;
  const phase = Math.random() * Math.PI * 2;
  group.position.set(x, yBase, z);
  group.rotation.y = Math.random() * Math.PI * 2;
  scene.add(group);
  return { mesh: group, x, z, yBase, phase, type, collected: false };
}

function makeCampfireMesh(x, y, z) {
  const group = new THREE.Group();
  const logMat = new THREE.MeshStandardMaterial({ color: 0x6b4a2e, roughness: 0.9 });
  for (let i = 0; i < 4; i++) {
    const log = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 0.2, 5), logMat);
    log.position.y = 0.02;
    log.rotation.z = Math.PI / 2 + (i / 4) * Math.PI;
    log.rotation.y = Math.PI / 4;
    group.add(log);
  }
  const fireMat = new THREE.MeshStandardMaterial({ color: 0xff6600, emissive: 0xff4400, emissiveIntensity: 0.6 });
  const flame = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.12, 6), fireMat);
  flame.position.y = 0.12;
  group.add(flame);
  const glowMat = new THREE.MeshBasicMaterial({ color: 0xff6600, transparent: true, opacity: 0.15, side: THREE.DoubleSide, depthWrite: false });
  const glow = new THREE.Mesh(new THREE.CircleGeometry(0.25, 8), glowMat);
  glow.rotation.x = -Math.PI / 2;
  glow.position.y = 0.01;
  group.add(glow);
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(0.2, 8), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide }));
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.005;
  group.add(shadow);
  group.scale.set(6, 6, 6);
  group.position.set(x, y, z);
  scene.add(group);
  return { mesh: group, x, z, y };
}

function placeCampfire() {
  const pos = player.camera.position;
  const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(player.camera.quaternion);
  dir.y = 0;
  dir.normalize();
  const dist = 2;
  const x = pos.x + dir.x * dist;
  const z = pos.z + dir.z * dist;
  const y = Math.max(0, getGroundHeight(x, z));
  const cf = makeCampfireMesh(x, y, z);
  campfires.push(cf);
  removeItem('Campfire');
  showMessage('Campfire placed', 1000);
}

function cookAtCampfire() {
  const pos = player.camera.position;
  const nearCF = campfires.find(cf => Math.hypot(cf.x - pos.x, cf.z - pos.z) < 2.5);
  if (!nearCF) return false;
  const rawMeat = inventory.find(i => i.name === 'Raw Meat');
  if (!rawMeat) return false;
  removeItem('Raw Meat');
  addItem('Cooked Meat', '\uD83E\uDD5A', () => {
    hunger = Math.min(100, hunger + 35);
    hud.setHunger(hunger);
    removeItem('Cooked Meat');
  });
  showMessage('Cooked meat over campfire!', 1200);
  return true;
}

const worldData = createWorld(scene);
berryBushes = worldData.berryBushes || [];
coconutTrees = worldData.coconutTrees || [];
const stickPiles = worldData.stickPiles || [];

for (const bush of berryBushes) {
  for (const m of bush.groundItems) {
    const type = m.userData.type || 'berry';
    groundItems.push({ mesh: m, x: m.position.x, z: m.position.z, yBase: m.position.y, phase: Math.random() * Math.PI * 2, type, collected: false, source: bush });
  }
}
for (const tree of coconutTrees) {
  for (const m of tree.groundItems) {
    const type = m.userData.type || 'coconut';
    groundItems.push({ mesh: m, x: m.position.x, z: m.position.z, yBase: m.position.y, phase: Math.random() * Math.PI * 2, type, collected: false, source: tree });
  }
}

const standaloneSticks = [];
for (const pile of stickPiles) {
  for (const m of pile) {
    const gi = { mesh: m, x: m.position.x, z: m.position.z, yBase: m.position.y, phase: Math.random() * Math.PI * 2, type: 'stick', collected: false, respawnTimer: 60 + Math.random() * 30 };
    groundItems.push(gi);
    standaloneSticks.push(gi);
  }
}

const { collectibles: createdGems } = createCollectibles(scene);
gems.push(...createdGems);

for (let i = 0; i < MAX_ANIMALS; i++) {
  const a = spawnAnimalAt(scene);
  if (a) animals.push(a);
}

rabbits = createRabbits(scene, 8);
birds = createBirds(scene, 12);

blocker.addEventListener('click', () => {
  blocker.style.display = 'none';
  player.lock();
});

function showMessage(text, duration) {
  const el = document.getElementById('message');
  el.textContent = text;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration || 1500);
}

const clock = new THREE.Clock();
let dead = false;

const mouseButtons = { 0: false, 2: false };

function updateEquippedWeapon() {
  const item = inventory[selectedSlot];
  const name = item ? item.name : null;
  isBlocking = false;
  if (name === 'Sword') {
    sword.visible = true;
    pistol.visible = false;
    equippedWeapon = 'sword';
  } else if (name === 'Gun') {
    sword.visible = false;
    pistol.visible = true;
    equippedWeapon = 'gun';
  } else if (name === 'Fishing Rod') {
    sword.visible = false;
    pistol.visible = false;
    equippedWeapon = 'fishing';
  } else {
    sword.visible = false;
    pistol.visible = false;
    equippedWeapon = null;
  }
}

document.addEventListener('mousedown', (e) => {
  if (!player.isLocked || dead || craftingOpen) return;
  mouseButtons[e.button] = true;
  if (e.button === 0) {
    if (equippedWeapon === 'sword' && !isSwinging && swingCooldownTimer <= 0) {
      isSwinging = true;
      swingTimer = SWING_DURATION;
    } else if (equippedWeapon === 'gun' && shootCooldown <= 0) {
      proj.shoot(player.camera.position.clone(), player.camera.quaternion.clone());
      shootCooldown = 0.25;
    } else if (!equippedWeapon) {
      useSelectedItem();
      hud.updateInventory(inventory);
    }
  }
  if (e.button === 2) {
    if (equippedWeapon === 'sword') {
      isBlocking = true;
    } else if (!equippedWeapon && cookAtCampfire()) {
      return;
    }
  }
});

document.addEventListener('mouseup', (e) => {
  mouseButtons[e.button] = false;
  if (e.button === 2) isBlocking = false;
});

document.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  if (craftingOpen) return;
  if (player.isLocked) {
    isBlocking = false;
    player.unlock();
    blocker.style.display = 'flex';
    blocker.querySelector('h1').textContent = 'PAUSED';
    blocker.querySelector('p').textContent = 'Right-click or click to resume';
  } else {
    blocker.style.display = 'none';
    player.lock();
  }
});

document.addEventListener('pointerlockchange', () => {
  if (!document.pointerLockElement && !craftingOpen) {
    blocker.style.display = 'flex';
    blocker.querySelector('h1').textContent = 'PAUSED';
    blocker.querySelector('p').textContent = 'Right-click or click to resume';
  }
});

document.addEventListener('keydown', (e) => {
  if (e.code === 'KeyE' && !dead && !craftingOpen) {
    interact();
    return;
  }
  if (e.code === 'KeyC' && !dead) {
    toggleCrafting();
    return;
  }
  const num = parseInt(e.key);
  if (num >= 1 && num <= HOTBAR_SIZE && !dead) {
    selectedSlot = num - 1;
    hud.setSelectedSlot(selectedSlot);
    hud.updateInventory(inventory);
    updateEquippedWeapon();
  }
});

function interact() {
  if (equippedWeapon === 'fishing') {
    if (isFishing) return;
    const nearWater = checkNearWater(player.camera.position);
    if (nearWater) {
      startFishing();
    } else {
      showMessage('No water nearby', 1000);
    }
    return;
  }

  const pos = player.camera.position;

  for (const gi of groundItems) {
    if (gi.collected) continue;
    if (Math.hypot(gi.x - pos.x, gi.z - pos.z) < 2.5) {
      collectGroundItem(gi);
    }
  }

  const nearCF = campfires.find(cf => Math.hypot(cf.x - pos.x, cf.z - pos.z) < 2.5);
  if (nearCF) {
    const rawMeat = inventory.find(i => i.name === 'Raw Meat');
    if (rawMeat) {
      removeItem('Raw Meat');
      addItem('Cooked Meat', '\uD83E\uDD5A', () => {
        hunger = Math.min(100, hunger + 35);
        hud.setHunger(hunger);
        removeItem('Cooked Meat');
      });
      showMessage('Cooked meat over campfire!', 1200);
      return;
    }
  }

  if (inventory.length > 0 && inventory[selectedSlot]) {
    useSelectedItem();
    hud.updateInventory(inventory);
  }
}

function respawnAnimal() {
  const a = spawnAnimalAt(scene, player.camera.position);
  if (a) animals.push(a);
}

function handleAnimalDeath(animal) {
  animal.alive = false;
  const pos = animal.mesh.position.clone();
  scene.remove(animal.mesh);

  const meshes = spawnMeatDrops(scene, pos, animal);
  for (const m of meshes) {
    groundItems.push(m);
  }

  score += animal.reward;
  killCount += 1;
  hud.setScore(score);

  if (Math.random() < 0.2) {
    const orb = spawnHealthOrb(scene, pos);
    healthOrbs.push(orb);
  }

  setTimeout(() => {
    const alive = animals.filter(a => a.alive).length;
    if (alive < MAX_ANIMALS) {
      respawnAnimal();
    }
  }, 2000);
}

function respawnPlayer() {
  dead = false;
  player.health = 100;
  hunger = 100;
  thirst = 100;
  const sh = getGroundHeight(0, 12) + 1.6;
  player.camera.position.set(0, sh, 12);
  player.velocity.set(0, 0, 0);
  hud.setHealth(100);
  hud.setHunger(100);
  hud.setThirst(100);
  showMessage('Respawned', 1500);
}

let survivalTimer = 0;
let survivalDamageTimer = 0;

function updateSurvival(dt) {
  survivalTimer += dt;
  if (survivalTimer > 2) {
    survivalTimer = 0;
    thirst = Math.max(0, thirst - 1.5);
    hud.setThirst(thirst);
  }
  if (survivalTimer === 0) {
    hunger = Math.max(0, hunger - 1);
    hud.setHunger(hunger);
  }

  if (hunger <= 0 || thirst <= 0) {
    survivalDamageTimer += dt;
    if (survivalDamageTimer > 2) {
      survivalDamageTimer = 0;
      if (!dead) {
        player.takeDamage(5);
        hud.setHealth(player.health);
        if (player.health <= 0) {
          dead = true;
          showMessage('DIED OF STARVATION', 2000);
          setTimeout(respawnPlayer, 2500);
        }
      }
    }
  } else {
    survivalDamageTimer = 0;
  }
}

function updateResources(dt) {
  for (const bush of berryBushes) {
    if (bush.harvested) {
      bush.respawnTimer -= dt;
      if (bush.respawnTimer <= 0) {
        bush.harvested = false;
        bush.mesh.visible = true;
        for (const m of bush.groundItems) {
          const gi = groundItems.find(g => g.mesh === m);
          if (gi) {
            gi.collected = false;
            gi.mesh.visible = true;
          }
        }
      }
    }
  }
  for (const tree of coconutTrees) {
    if (tree.harvested) {
      tree.respawnTimer -= dt;
      if (tree.respawnTimer <= 0) {
        tree.harvested = false;
        tree.mesh.visible = true;
        for (const m of tree.groundItems) {
          const gi = groundItems.find(g => g.mesh === m);
          if (gi) {
            gi.collected = false;
            gi.mesh.visible = true;
          }
        }
      }
    }
  }

  for (const gi of standaloneSticks) {
    if (gi.collected) {
      gi.respawnTimer -= dt;
      if (gi.respawnTimer <= 0) {
        gi.collected = false;
        gi.mesh.visible = true;
        gi.respawnTimer = 60 + Math.random() * 30;
      }
    }
  }
}

let groundItemTime = 0;

function collectGroundItem(gi) {
  if (gi.collected) return;
  gi.collected = true;
  gi.mesh.visible = false;
  if (gi.type === 'berry') {
    addItem('Berry', '\uD83C\uDF47', useFood(15, 'Berry'));
    showMessage('+1 Berry');
  } else if (gi.type === 'coconut') {
    addItem('Coconut', '\uD83E\uDD65', () => {
      hunger = Math.min(100, hunger + 20);
      thirst = Math.min(100, thirst + 10);
      hud.setHunger(hunger);
      hud.setThirst(thirst);
      removeItem('Coconut');
    });
    showMessage('+1 Coconut');
  } else if (gi.type === 'stick') {
    addItem('Stick', '\uD83E\uDEB5', null);
    showMessage('+1 Stick');
  } else if (gi.type === 'meat') {
    addItem('Raw Meat', '\uD83E\uDD69', () => {
      hunger = Math.min(100, hunger + 25);
      hud.setHunger(hunger);
      player.takeDamage(10);
      hud.setHealth(player.health);
      removeItem('Raw Meat');
      if (player.health <= 0) {
        dead = true;
        showMessage('Food poisoning...', 2000);
        setTimeout(respawnPlayer, 2500);
      }
    });
    showMessage('+1 Raw Meat');
  }
  hud.setSelectedSlot(selectedSlot);
  hud.updateInventory(inventory);

  if (gi.source) {
    const src = gi.source;
    const allCollected = src.groundItems.every(m => {
      const g = groundItems.find(g => g.mesh === m);
      return g && g.collected;
    });
    if (allCollected && !src.harvested) {
      src.harvested = true;
      src.respawnTimer = src.type === 'berry' ? 30 : 60;
      src.mesh.visible = false;
    }
  }
}

function updateGroundItems() {
  const pos = player.camera.position;
  groundItemTime += 0.02;
  for (const gi of groundItems) {
    if (gi.collected) continue;
    gi.mesh.position.y = gi.yBase + 0.08 + Math.sin(groundItemTime + gi.phase) * 0.04;
    gi.mesh.rotation.y += 0.01;
    const d = Math.hypot(gi.x - pos.x, gi.z - pos.z);
    if (d < 1.5) {
      collectGroundItem(gi);
    }
  }
}

function updateInteractionHint() {
  const pos = player.camera.position;
  let near = false;

  for (const bush of berryBushes) {
    if (bush.harvested) continue;
    if (Math.hypot(bush.x - pos.x, bush.z - pos.z) < 3) {
      near = true;
      hud.showAction('[E] Gather berries');
      break;
    }
  }

  if (!near) {
    for (const tree of coconutTrees) {
      if (tree.harvested) continue;
      if (Math.hypot(tree.x - pos.x, tree.z - pos.z) < 3) {
        near = true;
        hud.showAction('[E] Collect coconut');
        break;
      }
    }
  }

  if (!near && inventory.length > 0 && inventory[selectedSlot] && !equippedWeapon) {
    hud.showAction('[E] Use ' + inventory[selectedSlot].name);
    near = true;
  }

  if (!near && animals.some(a => a.alive && a.mesh.position.distanceTo(pos) < 10)) {
    const hint = equippedWeapon === 'sword' ? 'LMB: Swing | RMB: Block'
      : equippedWeapon === 'gun' ? 'LMB: Shoot'
      : 'Equip a weapon (1-2)';
    hud.showAction(hint);
    near = true;
  }

  if (!near) {
    if (equippedWeapon === 'fishing') {
      const nearWater = checkNearWater(player.camera.position);
      if (nearWater) {
        hud.showAction('[E] Cast line');
      } else {
        hud.showAction('Find water to fish');
      }
      near = true;
    }
  }

  if (!near) {
    const nearCF = campfires.find(cf => Math.hypot(cf.x - pos.x, cf.z - pos.z) < 2.5);
    if (nearCF) {
      const hasMeat = inventory.some(i => i.name === 'Raw Meat');
      if (hasMeat) {
        hud.showAction('[E] Cook meat');
      } else {
        hud.showAction('Campfire — need Raw Meat');
      }
      near = true;
    }
  }

  if (!near) {
    if (!equippedWeapon) {
      hud.showAction('[C] Craft');
      near = true;
    }
  }

  if (!near) {
    hud.hideAction();
  }
}

function checkNearWater(pos) {
  for (let i = 0; i < 12; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = 2 + Math.random() * 4;
    const x = pos.x + Math.cos(a) * r;
    const z = pos.z + Math.sin(a) * r;
    if (getGroundHeight(x, z) < 0) return true;
  }
  return false;
}

function startFishing() {
  if (isFishing) return;
  const pos = player.camera.position;
  let waterX = pos.x, waterZ = pos.z;
  let found = false;
  for (let i = 0; i < 20; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = 2 + Math.random() * 5;
    const x = pos.x + Math.cos(a) * r;
    const z = pos.z + Math.sin(a) * r;
    if (getGroundHeight(x, z) < 0) {
      waterX = x;
      waterZ = z;
      found = true;
      break;
    }
  }
  if (!found) return;

  isFishing = true;
  fishingTimer = 0;
  fishingTime = 3 + Math.random() * 4;

  const bobberGroup = new THREE.Group();
  const float = new THREE.Mesh(
    new THREE.SphereGeometry(0.04, 6, 6),
    new THREE.MeshBasicMaterial({ color: 0xff4444 })
  );
  float.position.y = 0.02;
  bobberGroup.add(float);
  const line = new THREE.Mesh(
    new THREE.CylinderGeometry(0.003, 0.003, 0.15, 3),
    new THREE.MeshBasicMaterial({ color: 0x888888 })
  );
  line.position.y = -0.07;
  bobberGroup.add(line);
  bobberGroup.position.set(waterX, 0, waterZ);
  scene.add(bobberGroup);
  bobber = bobberGroup;

  showMessage('Casting line...', 800);
}

function updateFishing(dt) {
  if (!isFishing || !bobber) return;
  fishingTimer += dt;
  bobber.position.y = Math.sin(fishingTimer * 3) * 0.008;
  bobber.rotation.y += dt * 0.5;

  if (fishingTimer >= fishingTime) {
    isFishing = false;
    const bPos = bobber.position.clone();
    scene.remove(bobber);
    bobber = null;
    const ripples = new THREE.Mesh(
      new THREE.RingGeometry(0.05, 0.15, 12),
      new THREE.MeshBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6, side: THREE.DoubleSide, depthWrite: false })
    );
    ripples.position.copy(bPos);
    ripples.position.y = 0.02;
    ripples.rotation.x = -Math.PI / 2;
    scene.add(ripples);
    setTimeout(() => scene.remove(ripples), 600);

    if (Math.random() < 0.75) {
      addItem('Raw Fish', '\uD83D\uDC1F', () => {
        hunger = Math.min(100, hunger + 20);
        hud.setHunger(hunger);
        player.takeDamage(5);
        hud.setHealth(player.health);
        removeItem('Raw Fish');
        if (player.health <= 0) {
          dead = true;
          showMessage('Food poisoning...', 2000);
          setTimeout(respawnPlayer, 2500);
        }
      });
      showMessage('+1 Raw Fish!');
    } else {
      showMessage('Fish got away...', 1000);
    }
  }
}

function toggleCrafting() {
  const panel = document.getElementById('crafting-panel');
  craftingOpen = !craftingOpen;
  panel.classList.toggle('open', craftingOpen);
  if (craftingOpen) {
    renderCraftingPanel();
    if (player.isLocked) {
      player.unlock();
    }
    blocker.style.display = 'none';
  } else if (!dead) {
    player.lock();
  }
}

function renderCraftingPanel() {
  const list = document.getElementById('recipes-list');
  list.innerHTML = '';
  const recipes = getRecipes();
  for (const recipe of recipes) {
    const div = document.createElement('div');
    const affordable = canCraft(recipe, inventory);
    div.className = 'recipe' + (affordable ? '' : ' cant');
    div.innerHTML = `
      <span class="r-icon">${recipe.icon}</span>
      <span class="r-name">${recipe.name}</span>
      <span class="r-cost">${Object.entries(recipe.materials).map(([m, c]) => c + ' ' + m).join(', ')}</span>
    `;
    if (affordable) {
      div.addEventListener('click', () => {
        const success = craft(recipe, inventory, (name, icon) => {
          let useFn = null;
          if (name === 'Campfire') useFn = placeCampfire;
          if (name === 'Cooked Meat') useFn = () => {
            hunger = Math.min(100, hunger + 35);
            hud.setHunger(hunger);
            removeItem('Cooked Meat');
          };
          if (name === 'Cooked Fish') useFn = () => {
            hunger = Math.min(100, hunger + 25);
            hud.setHunger(hunger);
            removeItem('Cooked Fish');
          };
          addItem(name, icon, useFn);
          hud.updateInventory(inventory);
          renderCraftingPanel();
        }, (name) => {
          removeItem(name);
          hud.updateInventory(inventory);
        });
        if (success) {
          showMessage('Crafted: ' + recipe.name);
          hud.updateInventory(inventory);
          renderCraftingPanel();
          updateEquippedWeapon();
        }
      });
    }
    list.appendChild(div);
  }
}

function loop() {
  requestAnimationFrame(loop);
  const dt = Math.min(clock.getDelta(), 0.05);

  if (!dead) {
    player.update(dt);
  }
  updateWorld(dt);

  const sky = weather.update(dt, player.camera.position);
  scene.background.setHSL(0.58, 0.3, 0.5 + sky.brightness * 0.3);
  scene.fog.color.copy(scene.background);

  shootCooldown = Math.max(0, shootCooldown - dt);
  swingCooldownTimer = Math.max(0, swingCooldownTimer - dt);

  if (isSwinging) {
    swingTimer -= dt;
    const progress = 1 - swingTimer / SWING_DURATION;
    const arc = -Math.sin(progress * Math.PI) * 1.2;
    sword.rotation.x = -0.15 + arc;
    sword.rotation.z = -0.2 - Math.sin(progress * Math.PI) * 0.8;
    if (swingTimer <= 0) {
      isSwinging = false;
      swingCooldownTimer = SWING_COOLDOWN;
      sword.rotation.set(-0.15, 0.1, -0.2);
    }
    if (progress > 0.3 && progress < 0.7) {
      const hits = getMeleeCandidates(animals, player.camera.position, player.camera.quaternion);
      for (const a of hits) {
        if (a._meleeHit) continue;
        a._meleeHit = true;
        a.health -= MELEE_DAMAGE;
        a.hitFlash = 0.3;
        a.provoked = true;
        a.provokedTimer = 10;
        applyKnockback(a, player.camera.position, 3.5);
        const n = makeDamageNumber('-' + MELEE_DAMAGE, '#ff8844');
        n.sprite.position.copy(a.mesh.position);
        n.sprite.position.y += 0.6;
        scene.add(n.sprite);
        damageNumbers.push(n);
        if (a.health <= 0) {
          handleAnimalDeath(a);
        }
      }
    }
  } else {
    for (const a of animals) {
      a._meleeHit = false;
    }
  }

  if (equippedWeapon === 'sword') {
    if (isBlocking) {
      sword.rotation.x = -0.8;
      sword.rotation.z = 0.3;
      sword.position.x = 0.15;
    } else if (!isSwinging) {
      sword.rotation.set(-0.15, 0.1, -0.2);
      sword.position.set(0.35, -0.28, -0.5);
    }
  }

  updateFishing(dt);

  if (!dead) {
    updateSurvival(dt);
    updateInteractionHint();
    updateResources(dt);
    updateGroundItems();
  }

  const animalDmg = updateAnimals(animals, player.camera.position, dt);
  hitCooldown -= dt;
  if (animalDmg > 0 && hitCooldown <= 0 && !dead) {
    const dmg = isBlocking ? Math.floor(animalDmg * 0.5) : animalDmg;
    player.takeDamage(dmg);
    hud.setHealth(player.health);
    if (isBlocking) {
      const n = makeDamageNumber('BLOCK', '#44ccff');
      n.sprite.position.copy(player.camera.position);
      n.sprite.position.y += 0.5;
      scene.add(n.sprite);
      damageNumbers.push(n);
    }
    hitCooldown = 0.5;
    if (player.health <= 0) {
      dead = true;
      showMessage('YOU DIED', 2000);
      setTimeout(respawnPlayer, 2500);
    }
  }

  if (updateCollectibles(gems, player.camera.position, scene)) {
    score += 100;
    hud.setScore(score);
    showMessage('+100');
  }

  if (updateCollectibles(healthOrbs, player.camera.position, scene)) {
    player.health = Math.min(100, player.health + 20);
    hud.setHealth(player.health);
    showMessage('+20 HP', 800);
  }

  updateRabbits(rabbits, player.camera.position, dt);
  updateBirds(birds, dt);

  updateDamageNumbers(damageNumbers, dt);

  proj.update(dt, (pos) => {
    for (const a of animals) {
      if (a.alive && pos.distanceTo(a.mesh.position) < 0.8) {
        a.health -= 3;
        a.hitFlash = 0.3;
        a.provoked = true;
        a.provokedTimer = 10;
        const n = makeDamageNumber('-3', '#ff4444');
        n.sprite.position.copy(a.mesh.position);
        n.sprite.position.y += 0.6;
        scene.add(n.sprite);
        damageNumbers.push(n);
        if (a.health <= 0) {
          handleAnimalDeath(a);
        }
        return true;
      }
    }
    return false;
  });

  renderer.render(scene, camera);
}

loop();
