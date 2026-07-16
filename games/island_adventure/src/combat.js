import * as THREE from 'three';

const SWING_DURATION = 0.18;
const SWING_COOLDOWN = 0.3;
const MELEE_RANGE = 2.5;
const MELEE_ARC = 1.8;
const KNOCKBACK = 3.5;
const MELEE_DAMAGE = 2;

export function makePistol() {
  const g = new THREE.Group();

  const metalMat = new THREE.MeshStandardMaterial({ color: 0x334455, metalness: 0.8, roughness: 0.2 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x222233, metalness: 0.5, roughness: 0.4 });

  const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.022, 0.22, 6), metalMat);
  barrel.rotation.x = Math.PI / 2;
  barrel.position.set(0, 0.02, -0.28);
  g.add(barrel);

  const body = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.06, 0.12), darkMat);
  body.position.set(0, 0.02, -0.1);
  g.add(body);

  const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.035, 0.08, 5), darkMat);
  grip.position.set(0, -0.04, -0.05);
  grip.rotation.x = 0.2;
  g.add(grip);

  const trigger = new THREE.Mesh(new THREE.TorusGeometry(0.013, 0.004, 4, 6), metalMat);
  trigger.position.set(0, 0.005, -0.07);
  trigger.rotation.x = 0.3;
  g.add(trigger);

  const sight = new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.012, 0.008), metalMat);
  sight.position.set(0, 0.05, -0.28);
  g.add(sight);

  g.position.set(0.25, -0.22, -0.5);
  g.rotation.set(0, 0, 0);

  return g;
}

export function makeSword() {
  const g = new THREE.Group();

  const bladeMat = new THREE.MeshStandardMaterial({ color: 0xccccdd, metalness: 0.7, roughness: 0.2 });
  const handleMat = new THREE.MeshStandardMaterial({ color: 0x5c3a1e, roughness: 0.9 });
  const guardMat = new THREE.MeshStandardMaterial({ color: 0xaa8833, metalness: 0.5, roughness: 0.3 });

  const blade = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.45, 0.008), bladeMat);
  blade.position.y = 0.31;
  blade.castShadow = true;
  g.add(blade);

  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.025, 0.08, 4), bladeMat);
  tip.position.y = 0.54;
  tip.rotation.x = 0;
  g.add(tip);

  const guard = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.02, 0.04), guardMat);
  guard.position.y = 0.09;
  g.add(guard);

  const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.03, 0.12, 6), handleMat);
  handle.position.y = 0.02;
  g.add(handle);

  const pommel = new THREE.Mesh(new THREE.SphereGeometry(0.025, 4, 4), guardMat);
  pommel.position.y = -0.05;
  g.add(pommel);

  g.position.set(0.35, -0.28, -0.5);
  g.rotation.set(-0.15, 0.1, -0.2);

  return g;
}

export function makeDamageNumber(text, color) {
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');
  ctx.font = 'bold 40px monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = 'rgba(0,0,0,0.8)';
  ctx.shadowBlur = 6;
  ctx.fillStyle = color || '#ff4444';
  ctx.fillText(text, 64, 34);

  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  const mat = new THREE.SpriteMaterial({
    map: tex,
    transparent: true,
    depthTest: false,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(0.6, 0.3, 1);
  return { sprite, lifetime: 0.8, maxLife: 0.8 };
}

export function updateSwordSwing(sword, dt, state) {
  if (state === 'idle') {
    return;
  }
  if (state === 'swing') {
    const t = 1;
    const swingAngle = -Math.PI * 0.9;
    const arc = Math.sin(t * Math.PI) * swingAngle;
    sword.rotation.x = -0.15 + arc;
    sword.rotation.z = -0.2 + Math.sin(t * Math.PI) * 0.6;
  }
}

export function updateDamageNumbers(numbers, dt) {
  for (let i = numbers.length - 1; i >= 0; i--) {
    const n = numbers[i];
    n.lifetime -= dt;
    if (n.lifetime <= 0) {
      n.sprite.parent?.remove(n.sprite);
      n.sprite.material.map?.dispose();
      n.sprite.material.dispose();
      numbers.splice(i, 1);
      continue;
    }
    const progress = 1 - n.lifetime / n.maxLife;
    n.sprite.position.y += dt * 0.5;
    n.sprite.material.opacity = 1 - progress * 0.7;
  }
}

export function getMeleeCandidates(enemies, playerPos, playerQuat) {
  const forward = new THREE.Vector3(0, 0, -1);
  forward.applyQuaternion(playerQuat);
  forward.y = 0;
  forward.normalize();

  const hits = [];
  for (const e of enemies) {
    if (!e.alive) continue;
    const toEnemy = new THREE.Vector3().copy(e.mesh.position).sub(playerPos);
    toEnemy.y = 0;
    const dist = toEnemy.length();
    if (dist < MELEE_RANGE) {
      toEnemy.normalize();
      const dot = forward.dot(toEnemy);
      if (dot > Math.cos(MELEE_ARC)) {
        hits.push(e);
      }
    }
  }
  return hits;
}

export function applyKnockback(enemy, fromPos, strength) {
  const dir = new THREE.Vector3(
    enemy.mesh.position.x - fromPos.x,
    0,
    enemy.mesh.position.z - fromPos.z
  );
  dir.normalize();
  enemy.mesh.position.x += dir.x * (strength || KNOCKBACK);
  enemy.mesh.position.z += dir.z * (strength || KNOCKBACK);
}

export { SWING_DURATION, SWING_COOLDOWN, MELEE_RANGE, MELEE_ARC, MELEE_DAMAGE, KNOCKBACK };
