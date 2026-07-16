export class HUD {
  constructor() {
    this.healthFill = document.getElementById('health-fill');
    this.scoreEl = document.getElementById('score');
    this.hungerFill = document.getElementById('hunger-fill');
    this.thirstFill = document.getElementById('thirst-fill');
    this.actionHint = document.getElementById('action-hint');
    this.inventoryEl = document.getElementById('inventory');
    this.selectedSlot = 0;
  }

  setHealth(value) {
    this.healthFill.style.width = Math.max(0, value) + '%';
    this.healthFill.style.background = value > 50
      ? 'linear-gradient(90deg, #4c4, #4e4)'
      : value > 25
        ? 'linear-gradient(90deg, #fc4, #f84)'
        : 'linear-gradient(90deg, #f44, #f22)';
  }

  setScore(value) {
    this.scoreEl.textContent = value;
  }

  setHunger(value) {
    this.hungerFill.style.width = Math.max(0, value) + '%';
  }

  setThirst(value) {
    this.thirstFill.style.width = Math.max(0, value) + '%';
  }

  showAction(text) {
    this.actionHint.textContent = text;
    this.actionHint.classList.add('show');
  }

  hideAction() {
    this.actionHint.classList.remove('show');
  }

  setSelectedSlot(idx) {
    this.selectedSlot = idx;
    this.updateInventoryFromState();
  }

  updateInventoryFromState() {
  }

  updateInventory(items) {
    this.inventoryEl.innerHTML = '';
    if (items.length === 0) {
      this.inventoryEl.classList.remove('show');
      return;
    }
    this.inventoryEl.classList.add('show');
    for (let i = 0; i < 6; i++) {
      const slot = document.createElement('div');
      slot.className = 'slot' + (i === this.selectedSlot ? ' selected' : '');
      const hint = document.createElement('span');
      hint.className = 'key-hint';
      hint.textContent = i + 1;
      slot.appendChild(hint);
      if (i < items.length) {
        const item = items[i];
        slot.textContent = item.icon || item.name[0].toUpperCase();
        slot.title = item.name;
        if (item.count > 1) {
          const c = document.createElement('span');
          c.className = 'count';
          c.textContent = item.count;
          slot.appendChild(c);
        }
        slot._item = item;
      }
      this.inventoryEl.appendChild(slot);
    }
  }

  resize() {
  }
}
