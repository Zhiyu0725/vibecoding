const RECIPES = [
  {
    name: 'Fishing Rod',
    icon: '\uD83C\uDFA3',
    materials: { Stick: 3 },
    result: { name: 'Fishing Rod', icon: '\uD83C\uDFA3' },
  },
  {
    name: 'Campfire',
    icon: '\uD83D\uDD25',
    materials: { Stick: 5 },
    result: { name: 'Campfire', icon: '\uD83D\uDD25' },
  },
  {
    name: 'Cooked Fish',
    icon: '\uD83D\uDC1F',
    materials: { 'Raw Fish': 1, Stick: 2 },
    result: { name: 'Cooked Fish', icon: '\uD83D\uDC1F' },
  },
  {
    name: 'Cooked Meat',
    icon: '\uD83E\uDD5A',
    materials: { 'Raw Meat': 1, Stick: 2 },
    result: { name: 'Cooked Meat', icon: '\uD83E\uDD5A' },
  },
];

export function getRecipes() {
  return RECIPES;
}

export function canCraft(recipe, inventory) {
  for (const [material, needed] of Object.entries(recipe.materials)) {
    const item = inventory.find(i => i.name === material);
    if (!item || item.count < needed) return false;
  }
  return true;
}

export function craft(recipe, inventory, addItemFn, removeItemFn) {
  if (!canCraft(recipe, inventory)) return false;

  for (const [material, needed] of Object.entries(recipe.materials)) {
    for (let i = 0; i < needed; i++) {
      removeItemFn(material);
    }
  }

  addItemFn(recipe.result.name, recipe.result.icon, null);
  return true;
}
