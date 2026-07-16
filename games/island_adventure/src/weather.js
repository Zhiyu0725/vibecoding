import * as THREE from 'three';

export class Weather {
  constructor(scene) {
    this.scene = scene;
    this.time = 0;
    this.rainIntensity = 0;
    this.cloudCover = 0.3;
    this.rainDrops = [];
    this.targetRain = 0;
    this.rainChangeTimer = 0;

    const rainGeo = new THREE.BufferGeometry();
    const count = 2000;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 120;
      positions[i * 3 + 1] = Math.random() * 40;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 120;
    }
    rainGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.rainMesh = new THREE.Points(
      rainGeo,
      new THREE.PointsMaterial({
        color: 0x88aacc,
        size: 0.15,
        transparent: true,
        opacity: 0,
      })
    );
    this.rainMesh.frustumCulled = false;
    scene.add(this.rainMesh);
  }

  update(dt, playerPos) {
    this.time += dt;
    this.rainChangeTimer -= dt;

    if (this.rainChangeTimer <= 0) {
      this.rainChangeTimer = 10 + Math.random() * 20;
      this.targetRain = Math.random() < 0.3 ? 0.4 + Math.random() * 0.6 : 0;
    }

    this.rainIntensity += (this.targetRain - this.rainIntensity) * dt * 0.1;

    this.rainMesh.material.opacity = this.rainIntensity * 0.4;

    const positions = this.rainMesh.geometry.attributes.position.array;
    for (let i = 0; i < positions.length / 3; i++) {
      positions[i * 3 + 1] -= 15 * dt * (0.5 + this.rainIntensity);
      if (positions[i * 3 + 1] < -2) {
        positions[i * 3 + 1] = 35 + Math.random() * 5;
        positions[i * 3] = (playerPos.x || 0) + (Math.random() - 0.5) * 80;
        positions[i * 3 + 2] = (playerPos.z || 0) + (Math.random() - 0.5) * 80;
      }
    }
    this.rainMesh.geometry.attributes.position.needsUpdate = true;

    if (playerPos) {
      this.rainMesh.position.x = playerPos.x || 0;
      this.rainMesh.position.z = playerPos.z || 0;
    }

    const hour = (this.time % 600) / 600 * 24;
    const dayFactor = Math.sin((hour - 6) / 24 * Math.PI * 2);
    const brightness = Math.max(0.15, Math.min(1, 0.5 + dayFactor * 0.5));

    return {
      brightness,
      isRaining: this.rainIntensity > 0.1,
      rainIntensity: this.rainIntensity,
    };
  }
}
