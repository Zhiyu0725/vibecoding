import * as THREE from 'three';
import { getGroundHeight } from './world.js';

function random(min, max) { return Math.random() * (max - min) + min; }

export function createRabbits(scene, count) {
  const rabbits = [];
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 10 + Math.random() * 25;
    const x = Math.cos(angle) * dist;
    const z = Math.sin(angle) * dist;
    const h = getGroundHeight(x, z);
    if (h < 0.1 || h > 1.5) continue;

    const group = new THREE.Group();

    const body = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 5, 5),
      new THREE.MeshStandardMaterial({ color: 0xccaa88, roughness: 0.9, flatShading: true })
    );
    body.scale.set(1, 0.7, 1.2);
    body.position.y = 0.15;
    group.add(body);

    const head = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 5, 5),
      new THREE.MeshStandardMaterial({ color: 0xddbb99, roughness: 0.9, flatShading: true })
    );
    head.position.set(0, 0.22, 0.1);
    group.add(head);

    const earL = new THREE.Mesh(
      new THREE.ConeGeometry(0.02, 0.12, 4),
      new THREE.MeshStandardMaterial({ color: 0xccaa88, flatShading: true })
    );
    earL.position.set(-0.04, 0.28, 0.02);
    group.add(earL);
    const earR = earL.clone();
    earR.position.x = 0.04;
    group.add(earR);

    group.position.set(x, h, z);
    group.rotation.y = Math.random() * Math.PI * 2;
    scene.add(group);

    rabbits.push({
      mesh: group,
      alive: true,
      speed: 2 + Math.random(),
      fleeTimer: 0,
      wanderAngle: Math.random() * Math.PI * 2,
      wanderTimer: 0,
      hopPhase: 0,
    });
  }
  return rabbits;
}

export function createBirds(scene, count) {
  const birds = [];
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 10 + Math.random() * 30;
    const x = Math.cos(angle) * dist;
    const z = Math.sin(angle) * dist;

    const group = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.SphereGeometry(0.06, 4, 4),
      new THREE.MeshStandardMaterial({ color: 0x443322, flatShading: true })
    );
    body.scale.set(1, 0.6, 0.8);
    group.add(body);

    group.position.set(x, 5 + Math.random() * 10, z);
    scene.add(group);

    birds.push({
      mesh: group,
      angle: Math.random() * Math.PI * 2,
      radius: 5 + Math.random() * 15,
      height: 5 + Math.random() * 8,
      speed: 1 + Math.random(),
      phase: Math.random() * Math.PI * 2,
      centerX: x,
      centerZ: z,
    });
  }
  return birds;
}

export function updateRabbits(rabbits, playerPos, dt) {
  for (const r of rabbits) {
    if (!r.alive) continue;

    const dx = playerPos.x - r.mesh.position.x;
    const dz = playerPos.z - r.mesh.position.z;
    const dist = Math.sqrt(dx * dx + dz * dz);

    r.hopPhase += dt * 6;

    if (dist < 8) {
      const fleeX = -dx / dist;
      const fleeZ = -dz / dist;
      r.mesh.position.x += fleeX * r.speed * dt * 2;
      r.mesh.position.z += fleeZ * r.speed * dt * 2;
      r.mesh.rotation.y = Math.atan2(fleeX, fleeZ);
      r.fleeTimer = 2;
    } else {
      r.fleeTimer -= dt;
      if (r.fleeTimer > 0) continue;
      r.wanderTimer += dt;
      if (r.wanderTimer > 2 + Math.random() * 3) {
        r.wanderAngle += (Math.random() - 0.5) * 2;
        r.wanderTimer = 0;
      }
      r.mesh.position.x += Math.sin(r.wanderAngle) * r.speed * 0.3 * dt;
      r.mesh.position.z += Math.cos(r.wanderAngle) * r.speed * 0.3 * dt;
      r.mesh.rotation.y = r.wanderAngle;
    }

    const h = getGroundHeight(r.mesh.position.x, r.mesh.position.z);
    r.mesh.position.y = Math.max(0, h) + 0.15 + Math.abs(Math.sin(r.hopPhase)) * 0.04;
    r.mesh.scale.y = 1 - Math.abs(Math.sin(r.hopPhase)) * 0.15;
  }
}

export function updateBirds(birds, dt) {
  for (const b of birds) {
    b.phase += dt * b.speed * 0.5;
    b.angle += dt * b.speed * 0.1;
    b.mesh.position.x = b.centerX + Math.cos(b.angle) * b.radius;
    b.mesh.position.z = b.centerZ + Math.sin(b.angle) * b.radius;
    b.mesh.position.y = b.height + Math.sin(b.phase) * 0.5;
    b.mesh.rotation.y = b.angle + Math.PI / 2;
    b.mesh.rotation.z = Math.sin(b.phase) * 0.1;
  }
}
