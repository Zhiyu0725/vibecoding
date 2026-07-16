import * as THREE from 'three';

const GEM_COUNT = 15;

export function createCollectibles(scene) {
  const collectibles = [];
  for (let i = 0; i < GEM_COUNT; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 8 + Math.random() * 25;
    const x = Math.cos(angle) * dist;
    const z = Math.sin(angle) * dist;

    const gem = new THREE.Mesh(
      new THREE.OctahedronGeometry(0.2, 0),
      new THREE.MeshStandardMaterial({
        color: 0x44ddff,
        emissive: new THREE.Color(0x44aaff),
        emissiveIntensity: 0.3,
        roughness: 0.2,
        metalness: 0.8,
        flatShading: true,
      })
    );
    gem.position.set(x, 0.5, z);
    gem.castShadow = true;

    const glow = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 6, 6),
      new THREE.MeshBasicMaterial({ color: 0x88ddff, transparent: true, opacity: 0.4 })
    );
    glow.position.set(0, 0, 0);
    gem.add(glow);

    scene.add(gem);
    collectibles.push({
      mesh: gem,
      collected: false,
      bobPhase: Math.random() * Math.PI * 2,
    });
  }
  return { collectibles };
}

export function spawnHealthOrb(scene, position) {
  const orb = new THREE.Mesh(
    new THREE.SphereGeometry(0.15, 6, 6),
    new THREE.MeshStandardMaterial({
      color: 0x44ff88,
      emissive: 0x22cc66,
      emissiveIntensity: 0.4,
      roughness: 0.3,
      metalness: 0.3,
    })
  );
  orb.position.copy(position);
  orb.position.y = 0.5;
  scene.add(orb);

  const glow = new THREE.Mesh(
    new THREE.SphereGeometry(0.06, 6, 6),
    new THREE.MeshBasicMaterial({ color: 0x66ffaa, transparent: true, opacity: 0.5 })
  );
  orb.add(glow);

  return {
    mesh: orb,
    collected: false,
    bobPhase: Math.random() * Math.PI * 2,
  };
}

export function updateCollectibles(collectibles, playerPos, scene) {
  let collected = false;
  for (const c of collectibles) {
    if (c.collected) continue;
    c.bobPhase += 0.03;
    c.mesh.position.y = 0.5 + Math.sin(c.bobPhase) * 0.15;
    c.mesh.rotation.y += 0.02;

    const dist = c.mesh.position.distanceTo(playerPos);
    if (dist < 1.0) {
      c.mesh.scale.multiplyScalar(0.9);
      if (c.mesh.scale.x < 0.05) {
        scene.remove(c.mesh);
        c.collected = true;
        collected = true;
      }
    } else if (c.mesh.scale.x < 1) {
      c.mesh.scale.set(1, 1, 1);
    }
  }
  return collected;
}
