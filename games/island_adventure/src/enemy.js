import * as THREE from 'three';
import { getGroundHeight } from './world.js';

function random(min, max) { return Math.random() * (max - min) + min; }

const ANIMAL_TYPES = [
  { name: 'deer', hp: 4, speed: 3.5, color: 0xccaa88, belly: 0xffeecc, scale: 1.2, reward: 30, drops: { meat: { min: 2, max: 4 } } },
  { name: 'boar', hp: 6, speed: 2.8, color: 0x6b4c3b, belly: 0x8b5c3b, scale: 0.9, reward: 50, drops: { meat: { min: 2, max: 4 } } },
  { name: 'wolf', hp: 5, speed: 4, color: 0x777788, belly: 0x9999aa, scale: 1, reward: 80, drops: { meat: { min: 1, max: 2 } } },
];

function makeMeatDrop(position) {
  const g = new THREE.Group();
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.15, 6),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.01;
  g.add(shadow);

  const chunk = new THREE.Mesh(
    new THREE.SphereGeometry(0.08, 5, 5),
    new THREE.MeshStandardMaterial({ color: 0xcc4444, roughness: 0.9 })
  );
  chunk.position.y = 0.08;
  chunk.scale.set(1.2, 0.7, 0.9);
  g.add(chunk);

  const fat = new THREE.Mesh(
    new THREE.SphereGeometry(0.04, 4, 4),
    new THREE.MeshStandardMaterial({ color: 0xeeddcc, roughness: 0.9 })
  );
  fat.position.set(0.03, 0.1, 0.02);
  fat.scale.set(0.8, 0.5, 0.8);
  g.add(fat);

  g.position.copy(position);
  g.position.y = Math.max(0, getGroundHeight(position.x, position.z));
  g.rotation.y = random(0, Math.PI * 2);
  return g;
}

function makeHealthBar() {
  const group = new THREE.Group();
  const bg = new THREE.Mesh(
    new THREE.PlaneGeometry(0.5, 0.06),
    new THREE.MeshBasicMaterial({ color: 0x222222, depthTest: false, transparent: true, opacity: 0.8 })
  );
  bg.position.y = 1.4;
  group.add(bg);
  const fill = new THREE.Mesh(
    new THREE.PlaneGeometry(0.46, 0.04),
    new THREE.MeshBasicMaterial({ color: 0x44ff44, depthTest: false, transparent: true })
  );
  fill.position.set(0, 1.4, 0.001);
  group.add(fill);
  return group;
}

function updateBar(bar, health, maxHealth) {
  const fill = bar.children[1];
  const ratio = health / maxHealth;
  fill.scale.x = Math.max(0, ratio);
  fill.position.x = (Math.max(0, ratio) - 1) * 0.23;
  fill.material.color.setHex(ratio > 0.5 ? 0x44ff44 : ratio > 0.25 ? 0xffaa44 : 0xff4444);
}

function makeAnimalMesh(typeIdx) {
  const type = ANIMAL_TYPES[typeIdx];
  const s = type.scale;
  const group = new THREE.Group();

  const bodyMat = new THREE.MeshStandardMaterial({ color: type.color, roughness: 0.9, flatShading: true });
  const bellyMat = new THREE.MeshStandardMaterial({ color: type.belly, roughness: 0.9, flatShading: true });

  const body = new THREE.Mesh(new THREE.SphereGeometry(0.3 * s, 6, 6), bodyMat);
  body.scale.set(1.3, 0.9, 0.8);
  body.position.y = 0.35 * s;
  body.castShadow = true;
  group.add(body);

  const belly = new THREE.Mesh(new THREE.SphereGeometry(0.22 * s, 5, 5), bellyMat);
  belly.scale.set(1.1, 0.4, 0.7);
  belly.position.set(0, 0.15 * s, 0);
  group.add(belly);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.14 * s, 5, 5), bodyMat);
  head.position.set(0, 0.38 * s, -0.28 * s);
  head.scale.set(0.9, 0.8, 0.7);
  group.add(head);

  const snout = new THREE.Mesh(new THREE.SphereGeometry(0.06 * s, 4, 4), bellyMat);
  snout.position.set(0, 0.32 * s, -0.4 * s);
  snout.scale.set(0.8, 0.7, 1.2);
  group.add(snout);

  if (typeIdx === 1) {
    const tusk = new THREE.Mesh(
      new THREE.ConeGeometry(0.02 * s, 0.06 * s, 4),
      new THREE.MeshBasicMaterial({ color: 0xffeecc })
    );
    tusk.position.set(-0.05 * s, 0.28 * s, -0.42 * s);
    tusk.rotation.z = 0.3;
    group.add(tusk);
    const tuskR = tusk.clone();
    tuskR.position.x = 0.05 * s;
    tuskR.rotation.z = -0.3;
    group.add(tuskR);
  }

  if (typeIdx === 2) {
    const earL = new THREE.Mesh(
      new THREE.ConeGeometry(0.04 * s, 0.06 * s, 4),
      new THREE.MeshBasicMaterial({ color: 0x555566 })
    );
    earL.position.set(-0.1 * s, 0.46 * s, -0.2 * s);
    group.add(earL);
    const earR = earL.clone();
    earR.position.x = 0.1 * s;
    group.add(earR);
  }

  if (typeIdx === 0) {
    const antlerL = new THREE.Mesh(
      new THREE.CylinderGeometry(0.01 * s, 0.015 * s, 0.12 * s, 3),
      new THREE.MeshBasicMaterial({ color: 0xaa9966 })
    );
    antlerL.position.set(-0.1 * s, 0.48 * s, -0.18 * s);
    antlerL.rotation.z = 0.3;
    antlerL.rotation.x = -0.2;
    group.add(antlerL);
    const antlerR = antlerL.clone();
    antlerR.position.x = 0.1 * s;
    antlerR.rotation.z = -0.3;
    group.add(antlerR);
  }

  const legMat = new THREE.MeshStandardMaterial({ color: 0x665544, roughness: 0.9, flatShading: true });
  for (let i = 0; i < 4; i++) {
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.03 * s, 0.04 * s, 0.2 * s, 4),
      legMat
    );
    const lx = (i < 2 ? -0.18 : 0.18) * s;
    const lz = (i % 2 === 0 ? -0.1 : 0.1) * s;
    leg.position.set(lx, 0.1 * s, lz);
    group.add(leg);
  }

  const hpBar = makeHealthBar();
  group.add(hpBar);

  return group;
}

export function spawnAnimalAt(scene, nearPlayerPos, typeIdx) {
  if (typeIdx === undefined) {
    const weights = [0.45, 0.35, 0.2];
    const r = Math.random();
    typeIdx = r < weights[0] ? 0 : r < weights[0] + weights[1] ? 1 : 2;
  }

  let x, z;
  if (nearPlayerPos) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 15 + Math.random() * 15;
    x = nearPlayerPos.x + Math.cos(angle) * dist;
    z = nearPlayerPos.z + Math.sin(angle) * dist;
  } else {
    const angle = Math.random() * Math.PI * 2;
    const dist = 15 + Math.random() * 25;
    x = Math.cos(angle) * dist;
    z = Math.sin(angle) * dist;
  }

  const h = getGroundHeight(x, z);
  if (h < -0.05 || h > 2) return null;

  const mesh = makeAnimalMesh(typeIdx);
  mesh.position.set(x, Math.max(0, h), z);
  mesh.rotation.y = Math.random() * Math.PI * 2;
  scene.add(mesh);

  const type = ANIMAL_TYPES[typeIdx];
  return {
    mesh, typeIdx, alive: true,
    health: type.hp, maxHealth: type.hp,
    speed: type.speed + random(-0.3, 0.3),
    reward: type.reward,
    wanderAngle: Math.random() * Math.PI * 2,
    wanderTimer: 0,
    hitFlash: 0,
    provoked: false,
    provokedTimer: 0,
    fleeAngle: 0,
    chargeTimer: 0,
    isCharging: false,
    damageCooldown: 0,
  };
}

function getDropItems(animal) {
  const type = ANIMAL_TYPES[animal.typeIdx];
  const items = [];
  for (const [item, range] of Object.entries(type.drops)) {
    const count = range.min + Math.floor(Math.random() * (range.max - range.min + 1));
    for (let i = 0; i < count; i++) {
      items.push({ type: item, idx: animal.typeIdx });
    }
  }
  return items;
}

export function spawnMeatDrops(scene, position, animal) {
  const items = getDropItems(animal);
  const meshes = [];
  for (const item of items) {
    const mesh = makeMeatDrop(position);
    const offsetX = random(-0.3, 0.3);
    const offsetZ = random(-0.3, 0.3);
    mesh.position.x += offsetX;
    mesh.position.z += offsetZ;
    mesh.position.y = Math.max(0, getGroundHeight(mesh.position.x, mesh.position.z));
    scene.add(mesh);
    meshes.push({ mesh, x: mesh.position.x, z: mesh.position.z, yBase: mesh.position.y, phase: random(0, Math.PI * 2), type: 'meat', collected: false });
  }
  return meshes;
}

export function updateAnimals(animals, playerPos, dt) {
  const playerVec = new THREE.Vector3(playerPos.x, 0, playerPos.z);
  let attackPlayer = false;
  let attackDmg = 0;

  for (const a of animals) {
    if (!a.alive) continue;

    a.damageCooldown = Math.max(0, a.damageCooldown - dt);

    const aPos = new THREE.Vector3(a.mesh.position.x, 0, a.mesh.position.z);
    const toPlayer = new THREE.Vector3().copy(playerVec).sub(aPos);
    const dist = toPlayer.length();
    toPlayer.normalize();

    a.hitFlash = Math.max(0, a.hitFlash - dt);
    if (a.hitFlash > 0) {
      const body = a.mesh.children[0];
      body.material.emissive = new THREE.Color(0xff4400);
      body.material.emissiveIntensity = 0.4;
    } else {
      const body = a.mesh.children[0];
      body.material.emissiveIntensity = 0;
    }

    const type = ANIMAL_TYPES[a.typeIdx];

    if (a.provoked) {
      a.provokedTimer -= dt;

      const attackDmgMap = [5, 6, 8];
      const speedMultMap = [1.3, 1.4, 1.5];

      if (dist < 1.3 && a.damageCooldown <= 0) {
        attackPlayer = true;
        attackDmg = attackDmgMap[a.typeIdx] || 6;
        a.damageCooldown = 1;
      }
      a.mesh.position.x += toPlayer.x * a.speed * speedMultMap[a.typeIdx] * dt;
      a.mesh.position.z += toPlayer.z * a.speed * speedMultMap[a.typeIdx] * dt;
      a.mesh.rotation.y = Math.atan2(toPlayer.x, toPlayer.z);

      if (a.provokedTimer <= 0) {
        a.provoked = false;
      }
    } else {
      if (dist < 6) {
        const fleeX = a.mesh.position.x - playerPos.x;
        const fleeZ = a.mesh.position.z - playerPos.z;
        const fleeDist = Math.hypot(fleeX, fleeZ);
        if (fleeDist > 0) {
          a.mesh.position.x += (fleeX / fleeDist) * a.speed * dt;
          a.mesh.position.z += (fleeZ / fleeDist) * a.speed * dt;
          a.mesh.rotation.y = Math.atan2(fleeX, fleeZ);
        }
      } else {
        a.wanderTimer += dt;
        if (a.wanderTimer > 2 + Math.random() * 3) {
          a.wanderAngle += (Math.random() - 0.5) * 1.5;
          a.wanderTimer = 0;
        }
        a.mesh.position.x += Math.sin(a.wanderAngle) * a.speed * 0.3 * dt;
        a.mesh.position.z += Math.cos(a.wanderAngle) * a.speed * 0.3 * dt;
        a.mesh.rotation.y = a.wanderAngle;
      }
    }

    const h = Math.max(0, getGroundHeight(a.mesh.position.x, a.mesh.position.z));
    if (h < -0.1) { a.alive = false; scene.remove(a.mesh); continue; }
    a.mesh.position.y = h;

    updateBar(a.mesh.children[a.mesh.children.length - 1], a.health, a.maxHealth);
  }

  return attackPlayer ? attackDmg : 0;
}

export { ANIMAL_TYPES };
