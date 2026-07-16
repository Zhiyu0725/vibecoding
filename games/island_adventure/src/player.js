import * as THREE from 'three';

const _euler = new THREE.Euler(0, 0, 0, 'YXZ');
const _PI_2 = Math.PI / 2;
const EYE_HEIGHT = 1.6;

export class PlayerController {
  constructor(camera, domElement, getGroundHeight) {
    this.camera = camera;
    this.domElement = domElement;
    this.getGroundHeight = getGroundHeight;
    this.isLocked = false;
    this.health = 100;
    this.minPolarAngle = 0;
    this.maxPolarAngle = Math.PI;
    this.pointerSpeed = 0.002;
    this.moveSpeed = 6;
    this.jumpSpeed = 5;
    this.velocity = new THREE.Vector3();
    this.position = new THREE.Vector3();
    this.onGround = false;
    this.keys = { forward: false, backward: false, left: false, right: false, jump: false };

    this._onKeyDown = (e) => {
      switch (e.code) {
        case 'KeyW': this.keys.forward = true; break;
        case 'KeyA': this.keys.left = true; break;
        case 'KeyS': this.keys.backward = true; break;
        case 'KeyD': this.keys.right = true; break;
        case 'Space': this.keys.jump = true; break;
      }
    };
    this._onKeyUp = (e) => {
      switch (e.code) {
        case 'KeyW': this.keys.forward = false; break;
        case 'KeyA': this.keys.left = false; break;
        case 'KeyS': this.keys.backward = false; break;
        case 'KeyD': this.keys.right = false; break;
        case 'Space': this.keys.jump = false; break;
      }
    };
    this._onMouseMove = (e) => {
      if (!this.isLocked) return;
      _euler.setFromQuaternion(this.camera.quaternion);
      _euler.y -= e.movementX * this.pointerSpeed;
      _euler.x -= e.movementY * this.pointerSpeed;
      _euler.x = Math.max(_PI_2 - this.maxPolarAngle, Math.min(_PI_2 - this.minPolarAngle, _euler.x));
      this.camera.quaternion.setFromEuler(_euler);
    };
    this._onPointerlockChange = () => {
      this.isLocked = document.pointerLockElement === this.domElement;
    };
    this._onBlur = () => {
      this.keys.forward = false;
      this.keys.backward = false;
      this.keys.left = false;
      this.keys.right = false;
      this.keys.jump = false;
    };

    document.addEventListener('keydown', this._onKeyDown);
    document.addEventListener('keyup', this._onKeyUp);
    document.addEventListener('blur', this._onBlur);
    document.addEventListener('mousemove', this._onMouseMove);
    document.addEventListener('pointerlockchange', this._onPointerlockChange);
  }

  lock() { this.domElement.requestPointerLock(); }
  unlock() { document.exitPointerLock(); }

  takeDamage(amount) {
    this.health = Math.max(0, this.health - amount);
  }

  getGroundLevel(x, z) {
    const h = this.getGroundHeight(x, z);
    return Math.max(h, 0) + EYE_HEIGHT;
  }

  update(dt) {
    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(this.camera.quaternion);
    forward.y = 0;
    forward.normalize();
    const right = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion);
    right.y = 0;
    right.normalize();

    const move = new THREE.Vector3();
    if (this.keys.forward) move.add(forward);
    if (this.keys.backward) move.sub(forward);
    if (this.keys.left) move.sub(right);
    if (this.keys.right) move.add(right);

    if (move.lengthSq() > 0) {
      move.normalize();
      this.velocity.copy(move.multiplyScalar(this.moveSpeed));
    } else {
      this.velocity.set(0, this.velocity.y, 0);
    }

    if (this.keys.jump && this.onGround) {
      this.velocity.y = this.jumpSpeed;
      this.onGround = false;
    }

    this.velocity.y -= 15 * dt;
    this.camera.position.x += this.velocity.x * dt;
    this.camera.position.z += this.velocity.z * dt;
    this.camera.position.y += this.velocity.y * dt;

    const groundLevel = this.getGroundLevel(this.camera.position.x, this.camera.position.z);
    if (this.camera.position.y <= groundLevel) {
      this.camera.position.y = groundLevel;
      this.velocity.y = 0;
      this.onGround = true;
    }
  }

  dispose() {
    document.removeEventListener('keydown', this._onKeyDown);
    document.removeEventListener('keyup', this._onKeyUp);
    document.removeEventListener('blur', this._onBlur);
    document.removeEventListener('mousemove', this._onMouseMove);
    document.removeEventListener('pointerlockchange', this._onPointerlockChange);
  }
}
