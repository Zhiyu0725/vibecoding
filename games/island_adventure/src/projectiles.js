import * as THREE from 'three';

export class ProjectileSystem {
  constructor(scene) {
    this.scene = scene;
    this.projectiles = [];
    this.bursts = [];
  }

  shoot(position, quaternion) {
    const b = new THREE.Mesh(
      new THREE.SphereGeometry(0.06, 4, 4),
      new THREE.MeshBasicMaterial({ color: 0x66ffcc })
    );
    b.position.copy(position);
    b.position.y += 0;
    const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(quaternion);
    this.scene.add(b);
    this.projectiles.push({ mesh: b, vel: dir.multiplyScalar(30), life: 0 });
  }

  spawnBurst(position) {
    const g = new THREE.Group();
    const count = 6;
    for (let i = 0; i < count; i++) {
      const p = new THREE.Mesh(
        new THREE.SphereGeometry(0.04, 3, 3),
        new THREE.MeshBasicMaterial({ color: 0x88ffdd, transparent: true, opacity: 1 })
      );
      const angle = (i / count) * Math.PI * 2;
      p.position.set(Math.cos(angle) * 0.1, Math.sin(angle) * 0.1, 0);
      g.add(p);
    }
    g.position.copy(position);
    this.scene.add(g);
    this.bursts.push({ group: g, life: 0 });
  }

  update(dt, onHit) {
    for (let i = this.bursts.length - 1; i >= 0; i--) {
      const burst = this.bursts[i];
      burst.life += dt;
      const s = 1 + burst.life * 6;
      burst.group.scale.set(s, s, s);
      burst.group.children.forEach(c => { c.material.opacity = 1 - burst.life * 2; });
      if (burst.life > 0.5) {
        this.scene.remove(burst.group);
        this.bursts.splice(i, 1);
      }
    }

    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      const p = this.projectiles[i];
      p.mesh.position.add(p.vel.clone().multiplyScalar(dt));
      p.life += dt;

      let destroyed = false;
      if (p.life > 1.5) destroyed = true;

      if (!destroyed && onHit) {
        destroyed = onHit(p.mesh.position);
      }

      if (destroyed) {
        this.spawnBurst(p.mesh.position);
        this.scene.remove(p.mesh);
        this.projectiles.splice(i, 1);
      }
    }
  }
}
