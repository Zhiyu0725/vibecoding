import * as THREE from 'three';

function random(min, max) { return Math.random() * (max - min) + min; }

const ISLAND_RADIUS = 46;

export function getGroundHeight(x, z) {
  const dist = Math.sqrt(x * x + z * z);
  const t = Math.min(1, dist / ISLAND_RADIUS);
  const dome = Math.cos(t * Math.PI / 2);
  const noise = Math.sin(x * 0.08) * Math.cos(z * 0.08) * 0.35 +
                Math.sin(x * 0.15 + z * 0.12) * 0.15 +
                Math.sin(x * 0.05 + z * 0.07) * 0.1;
  const peak = Math.exp(-dist * dist * 0.002) * 0.4;
  return dome * 2.2 + noise + peak - 0.5;
}

export function createWorld(scene) {
  const ambient = new THREE.AmbientLight(0x556688, 0.6);
  scene.add(ambient);

  const sun = new THREE.DirectionalLight(0xffeecc, 1.0);
  sun.position.set(40, 50, -20);
  sun.castShadow = true;
  sun.shadow.mapSize.width = 1024;
  sun.shadow.mapSize.height = 1024;
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 100;
  sun.shadow.camera.left = -50;
  sun.shadow.camera.right = 50;
  sun.shadow.camera.top = 50;
  sun.shadow.camera.bottom = -50;
  scene.add(sun);

  const fill = new THREE.DirectionalLight(0x88aacc, 0.3);
  fill.position.set(-20, 10, 30);
  scene.add(fill);

  const size = 120;
  const seg = 60;
  const verts = [];
  const cols = [];
  const idxs = [];

  const sand = new THREE.Color(0xd4b87a);
  const sandLight = new THREE.Color(0xe8d5a3);
  const grass = new THREE.Color(0x3a7a3a);
  const grassDark = new THREE.Color(0x2d6a2d);
  const grassLight = new THREE.Color(0x5a9a4a);
  const underwater = new THREE.Color(0x6a8a6a);
  const underwaterDark = new THREE.Color(0x4a6a5a);

  for (let iz = 0; iz <= seg; iz++) {
    const z = -size / 2 + (iz / seg) * size;
    for (let ix = 0; ix <= seg; ix++) {
      const x = -size / 2 + (ix / seg) * size;
      const h = getGroundHeight(x, z);

      verts.push(x, h, z);

      let c;
      if (h < -0.08) {
        c = underwater.clone().lerp(underwaterDark, (-h) * 2);
      } else {
        const t = Math.min(1, (h + 0.08) / 2.5);
        c = grassDark.clone().lerp(grassLight, t);
      }
      cols.push(c.r, c.g, c.b);
    }
  }

  for (let iz = 0; iz < seg; iz++) {
    for (let ix = 0; ix < seg; ix++) {
      const a = iz * (seg + 1) + ix;
      const b = iz * (seg + 1) + ix + 1;
      const c = (iz + 1) * (seg + 1) + ix;
      const d = (iz + 1) * (seg + 1) + ix + 1;
      idxs.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
  geo.setIndex(idxs);
  geo.computeVertexNormals();

  const ground = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    vertexColors: true, roughness: 1, metalness: 0, flatShading: true,
  }));
  ground.receiveShadow = true;
  scene.add(ground);

  const waterGeo = new THREE.PlaneGeometry(160, 160);
  waterGeo.rotateX(-Math.PI / 2);
  const waterMat = new THREE.MeshBasicMaterial({
    color: 0x2a8ab8, transparent: true, opacity: 0.55, side: THREE.DoubleSide,
  });
  const water = new THREE.Mesh(waterGeo, waterMat);
  water.position.y = -0.05;
  scene.add(water);

  const treePositions = [];
  for (let i = 0; i < 160; i++) {
    const x = random(-42, 42);
    const z = random(-42, 42);
          const h = getGroundHeight(x, z);
    if (h < 0.2 || h > 2.5) continue;
    let good = true;
    for (const p of treePositions) {
      if (Math.hypot(x - p.x, z - p.z) < 3) { good = false; break; }
    }
    if (!good) continue;
    treePositions.push({ x, z });
    scene.add(createTree(x, z, h));
  }

  for (let i = 0; i < 60; i++) {
    const x = random(-40, 40);
    const z = random(-40, 40);
    const h = getGroundHeight(x, z);
    if (h < 0.1 || h > 2.0) continue;
    let good = true;
    for (const p of treePositions) {
      if (Math.hypot(x - p.x, z - p.z) < 1.5) { good = false; break; }
    }
    if (!good) continue;
    scene.add(createRock(x, z));
  }

  const berryBushes = [];
  for (let i = 0; i < 50; i++) {
    const x = random(-38, 38);
    const z = random(-38, 38);
    const h = getGroundHeight(x, z);
    if (h < 0.15 || h > 1.2) continue;
    let good = true;
    for (const p of treePositions) {
      if (Math.hypot(x - p.x, z - p.z) < 2) { good = false; break; }
    }
    if (!good) continue;
    const bush = createBerryBush(x, z, h);
    scene.add(bush.mesh);
    const berryCount = 2 + Math.floor(random(0, 3));
    for (let j = 0; j < berryCount; j++) {
      const a = random(0, Math.PI * 2);
      const r = random(0.3, 0.7);
      const gx = x + Math.cos(a) * r;
      const gz = z + Math.sin(a) * r;
      const gh = getGroundHeight(gx, gz);
      const mesh = makeGroundBerryMesh(gx, gz);
      mesh.position.set(gx, gh, gz);
      mesh.rotation.y = random(0, Math.PI * 2);
      scene.add(mesh);
      bush.groundItems.push(mesh);
    }
    const stickCount = 3 + Math.floor(random(0, 3));
    for (let j = 0; j < stickCount; j++) {
      const a = random(0, Math.PI * 2);
      const r = random(0.3, 0.8);
      const gx = x + Math.cos(a) * r;
      const gz = z + Math.sin(a) * r;
      const gh = getGroundHeight(gx, gz);
      const mesh = makeGroundStickMesh();
      mesh.position.set(gx, gh, gz);
      mesh.rotation.y = random(0, Math.PI * 2);
      scene.add(mesh);
      bush.groundItems.push(mesh);
    }
    berryBushes.push(bush);
  }

  const coconutTrees = [];
  for (let i = 0; i < 20; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = ISLAND_RADIUS * (0.7 + Math.random() * 0.2);
    const x = Math.cos(angle) * dist;
    const z = Math.sin(angle) * dist;
    const h = getGroundHeight(x, z);
    if (h < 0.05 || h > 0.6) continue;
    const tree = createCoconutTree(x, z, h);
    scene.add(tree.mesh);
    const nutCount = 1 + Math.floor(random(0, 2));
    for (let j = 0; j < nutCount; j++) {
      const a = random(0, Math.PI * 2);
      const r = random(0.4, 0.8);
      const gx = x + Math.cos(a) * r;
      const gz = z + Math.sin(a) * r;
      const gh = getGroundHeight(gx, gz);
      const mesh = makeGroundCoconutMesh(gx, gz);
      mesh.position.set(gx, gh, gz);
      mesh.rotation.y = random(0, Math.PI * 2);
      scene.add(mesh);
      tree.groundItems.push(mesh);
    }
    const treeStickCount = 2 + Math.floor(random(0, 2));
    for (let j = 0; j < treeStickCount; j++) {
      const a = random(0, Math.PI * 2);
      const r = random(0.3, 0.7);
      const gx = x + Math.cos(a) * r;
      const gz = z + Math.sin(a) * r;
      const gh = getGroundHeight(gx, gz);
      const mesh = makeGroundStickMesh();
      mesh.position.set(gx, gh, gz);
      mesh.rotation.y = random(0, Math.PI * 2);
      scene.add(mesh);
      tree.groundItems.push(mesh);
    }
    coconutTrees.push(tree);
  }

  const stickPiles = [];
  for (let i = 0; i < 40; i++) {
    const x = random(-40, 40);
    const z = random(-40, 40);
    const h = getGroundHeight(x, z);
    if (h < 0.1 || h > 1.8) continue;
    const pile = [];
    const count = 2 + Math.floor(random(0, 3));
    for (let j = 0; j < count; j++) {
      const a = random(0, Math.PI * 2);
      const r = random(0.1, 0.3);
      const sx = x + Math.cos(a) * r;
      const sz = z + Math.sin(a) * r;
      const sh = getGroundHeight(sx, sz);
      const mesh = makeGroundStickMesh();
      mesh.position.set(sx, sh, sz);
      mesh.rotation.y = random(0, Math.PI * 2);
      scene.add(mesh);
      pile.push(mesh);
    }
    stickPiles.push(pile);
  }

  addShoreRocks(scene);

  return { berryBushes, coconutTrees, stickPiles };
}

function makeGroundBerryMesh(x, z) {
  const g = new THREE.Group();
  g.userData.type = 'berry';
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.2, 8),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.25, depthWrite: false, side: THREE.DoubleSide })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.01;
  g.add(shadow);

  const berry = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 8, 8),
    new THREE.MeshStandardMaterial({ color: 0xee3333, emissive: 0x991111, emissiveIntensity: 0.2, roughness: 0.3 })
  );
  berry.position.y = 0.12;
  berry.scale.set(1, 0.85, 1);
  g.add(berry);

  const leaf = new THREE.Mesh(
    new THREE.SphereGeometry(0.035, 5, 5),
    new THREE.MeshStandardMaterial({ color: 0x4caf4c })
  );
  leaf.position.set(0.07, 0.2, 0);
  leaf.scale.set(1, 0.4, 0.6);
  g.add(leaf);

  return g;
}

function makeGroundCoconutMesh(x, z) {
  const g = new THREE.Group();
  g.userData.type = 'coconut';
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.25, 8),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.25, depthWrite: false, side: THREE.DoubleSide })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.01;
  g.add(shadow);

  const nut = new THREE.Mesh(
    new THREE.SphereGeometry(0.18, 8, 8),
    new THREE.MeshStandardMaterial({ color: 0x7a5c3a, roughness: 0.7 })
  );
  nut.scale.set(0.8, 1, 0.8);
  nut.position.y = 0.16;
  g.add(nut);

  const cap = new THREE.Mesh(
    new THREE.SphereGeometry(0.08, 6, 6),
    new THREE.MeshStandardMaterial({ color: 0x5a7a3a, roughness: 0.9 })
  );
  cap.scale.set(0.9, 0.3, 0.9);
  cap.position.set(0, 0.26, 0.02);
  g.add(cap);

  return g;
}

function createBerryBush(x, z, groundH) {
  const group = new THREE.Group();
  const s = random(0.15, 0.25);
  const bush = new THREE.Mesh(
    new THREE.SphereGeometry(s, 5, 5),
    new THREE.MeshStandardMaterial({ color: 0x3a8a3a, roughness: 0.9, flatShading: true })
  );
  bush.position.y = s + groundH;
  bush.scale.set(1, 0.6, 1);
  bush.castShadow = true;
  group.add(bush);

  return { mesh: group, x, z, type: 'berry', harvested: false, respawnTimer: 0, groundItems: [] };
}

function makeGroundStickMesh() {
  const g = new THREE.Group();
  g.userData.type = 'stick';
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.12, 6),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.005;
  g.add(shadow);

  const stickMat = new THREE.MeshStandardMaterial({ color: 0x8b6b4b, roughness: 0.9 });
  const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.02, 0.14, 4), stickMat);
  stick.rotation.z = random(0.5, 1.2);
  stick.rotation.x = random(0.5, 1.2);
  stick.position.y = 0.02;
  g.add(stick);

  const stick2 = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.018, 0.12, 4), stickMat);
  stick2.rotation.z = random(-1.2, -0.5);
  stick2.rotation.x = random(-1.2, -0.5);
  stick2.position.set(0.03, 0.015, -0.02);
  g.add(stick2);

  return g;
}

function createCoconutTree(x, z, groundH) {
  const group = new THREE.Group();
  const scale = random(0.8, 1.1);

  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06 * scale, 0.1 * scale, 1.2 * scale, 5),
    new THREE.MeshStandardMaterial({ color: 0x6b4c3b, roughness: 1, flatShading: true })
  );
  trunk.position.y = 0.6 * scale + groundH;
  trunk.castShadow = true;
  group.add(trunk);

  const leaves = new THREE.Mesh(
    new THREE.SphereGeometry(0.35 * scale, 4, 4),
    new THREE.MeshStandardMaterial({ color: 0x2a7a2a, flatShading: true })
  );
  leaves.scale.set(1, 0.2, 1.6);
  leaves.position.y = 1.3 * scale + groundH;
  group.add(leaves);

  for (let i = 0; i < 3; i++) {
    const frond = new THREE.Mesh(
      new THREE.ConeGeometry(0.25 * scale, 0.4 * scale, 4),
      new THREE.MeshStandardMaterial({ color: 0x2a7a2a, flatShading: true })
    );
    const a = (i / 3) * Math.PI * 2 + random(-0.3, 0.3);
    frond.position.set(Math.cos(a) * 0.1, 1.4 * scale + groundH, Math.sin(a) * 0.1);
    frond.rotation.x = 0.6;
    frond.rotation.z = a;
    group.add(frond);
  }

  return { mesh: group, x, z, type: 'coconut', harvested: false, respawnTimer: 0, groundItems: [] };
}

function addShoreRocks(scene) {
  for (let i = 0; i < 30; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = ISLAND_RADIUS * (0.85 + Math.random() * 0.15);
    const x = Math.cos(angle) * dist;
    const z = Math.sin(angle) * dist;
    const h = getGroundHeight(x, z);
    if (h > 0.3 || h < -0.1) continue;
    const s = random(0.1, 0.25);
    const mesh = new THREE.Mesh(
      new THREE.DodecahedronGeometry(s, 0),
      new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.07, 0.06, random(0.3, 0.5)),
        roughness: 1, flatShading: true,
      })
    );
    mesh.position.set(x, s * 0.3, z);
    mesh.rotation.set(random(0, 6), random(0, 6), random(0, 6));
    mesh.scale.set(random(0.8, 1.2), random(0.4, 0.7), random(0.8, 1.2));
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);
  }
}

function createTree(x, z, groundH) {
  const g = new THREE.Group();
  const scale = random(0.6, 1.1);

  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5c3f2e, roughness: 1, flatShading: true });
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.08 * scale, 0.14 * scale, 1.0 * scale, 5),
    trunkMat
  );
  trunk.position.y = 0.5 * scale + groundH;
  trunk.castShadow = true;
  g.add(trunk);

  const levels = 2 + Math.floor(random(0, 3));
  for (let i = 0; i < levels; i++) {
    const r = (1.3 - i * 0.25) * scale;
    const h = (1.0 - i * 0.15) * scale;
    const y = groundH + 0.8 * scale + i * 0.9 * h;
    const hue = random(0.22, 0.38);
    const sat = random(0.35, 0.55);
    const light = random(0.18, 0.32);
    const c = new THREE.Color().setHSL(hue, sat, light);
    const cone = new THREE.Mesh(
      new THREE.ConeGeometry(r, h, 6),
      new THREE.MeshStandardMaterial({ color: c, roughness: 1, flatShading: true })
    );
    cone.position.y = y + h / 2;
    cone.rotation.y = random(0, Math.PI);
    cone.castShadow = true;
    cone.receiveShadow = true;
    g.add(cone);
  }

  g.position.set(x, 0, z);
  return g;
}

function createRock(x, z) {
  const s = random(0.2, 0.5);
  const h = getGroundHeight(x, z);
  const mesh = new THREE.Mesh(
    new THREE.DodecahedronGeometry(s, 0),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(0.07, 0.04, random(0.25, 0.45)),
      roughness: 1, flatShading: true,
    })
  );
  mesh.position.set(x, s * 0.3 + h, z);
  mesh.rotation.set(random(0, 6), random(0, 6), random(0, 6));
  mesh.scale.set(random(0.8, 1.2), random(0.5, 0.9), random(0.8, 1.2));
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

export function updateWorld(dt) {
}
