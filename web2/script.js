const storage = {
  users: 'photoMarketUsers',
  items: 'photoMarketItems',
  orders: 'photoMarketOrders',
  session: 'photoMarketSession',
  cart: 'photoMarketCart',
  favorites: 'photoMarketFavorites',
};

const categories = ['All categories', 'Nature', 'Travel', 'Portraits', 'Wildlife', 'Architecture', 'Street Photography'];
const orientations = ['All orientation', 'horizontal', 'vertical', 'square'];
const colors = ['All color', 'colorful', 'monochrome', 'warm', 'cool'];

const sampleItems = [
  {
    id: 'photo-1',
    title: 'Golden Hour Horizon',
    category: 'Nature',
    price: 28,
    orientation: 'horizontal',
    color: 'warm',
    photographer: 'Maya Chen',
    rating: 4.9,
    reviews: [
      { user: 'Avery', rating: 5, comment: 'Beautiful detail and vibrant tone.' },
      { user: 'Jordan', rating: 5, comment: 'Perfect for my landing page hero section.' },
    ],
    description: 'A warm landscape captured at golden hour with dramatic light and rolling hills.',
    image: 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80',
    sellerId: 'seller-1',
    downloads: 18,
    isFeatured: true,
  },
  {
    id: 'photo-2',
    title: 'City Nights',
    category: 'Street Photography',
    price: 22,
    orientation: 'horizontal',
    color: 'cool',
    photographer: 'Lena Ortiz',
    rating: 4.8,
    reviews: [
      { user: 'Harper', rating: 5, comment: 'Stylish urban atmosphere and crisp shadows.' },
    ],
    description: 'A rainy city street captured with neon reflections and cinematic mood.',
    image: 'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80',
    sellerId: 'seller-2',
    downloads: 12,
    isFeatured: true,
  },
  {
    id: 'photo-3',
    title: 'Mountain Ascent',
    category: 'Travel',
    price: 34,
    orientation: 'vertical',
    color: 'colorful',
    photographer: 'Ella Rivera',
    rating: 4.7,
    reviews: [
      { user: 'Noah', rating: 4, comment: 'A breathtaking travel shot with great composition.' },
    ],
    description: 'A mountain vista with sweeping clouds, ideal for outdoor and adventure projects.',
    image: 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80',
    sellerId: 'seller-3',
    downloads: 9,
    isFeatured: false,
  },
  {
    id: 'photo-4',
    title: 'Portrait in Motion',
    category: 'Portraits',
    price: 26,
    orientation: 'vertical',
    color: 'warm',
    photographer: 'Nina Park',
    rating: 4.9,
    reviews: [
      { user: 'Mason', rating: 5, comment: 'Soft highlights and an emotional feel.' },
    ],
    description: 'A portrait capturing movement and intimacy with fine editorial style.',
    image: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=1200&q=80',
    sellerId: 'seller-1',
    downloads: 23,
    isFeatured: true,
  },
  {
    id: 'photo-5',
    title: 'Wild Safari',
    category: 'Wildlife',
    price: 31,
    orientation: 'horizontal',
    color: 'colorful',
    photographer: 'Rafael Soto',
    rating: 4.8,
    reviews: [
      { user: 'Camila', rating: 5, comment: 'The animal motion is captured perfectly.' },
    ],
    description: 'An expressive wildlife portrait shot on safari with natural motion and color.',
    image: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=80',
    sellerId: 'seller-2',
    downloads: 14,
    isFeatured: false,
  },
  {
    id: 'photo-6',
    title: 'Modern Architecture',
    category: 'Architecture',
    price: 27,
    orientation: 'horizontal',
    color: 'monochrome',
    photographer: 'Claire Bennett',
    rating: 4.6,
    reviews: [
      { user: 'Leo', rating: 5, comment: 'Clean lines and impressive geometry.' },
    ],
    description: 'A monochrome architectural photo with crisp angles and premium design appeal.',
    image: 'https://images.unsplash.com/photo-1486304895045-9f0d1f89a104?auto=format&fit=crop&w=1200&q=80',
    sellerId: 'seller-3',
    downloads: 7,
    isFeatured: false,
  },
];

const sampleUsers = [
  { id: 'admin', username: 'admin', password: 'admin123', role: 'admin', name: 'Admin Manager' },
  { id: 'seller-1', username: 'maya', password: 'photo123', role: 'seller', name: 'Maya Chen' },
  { id: 'seller-2', username: 'lena', password: 'lena123', role: 'seller', name: 'Lena Ortiz' },
  { id: 'seller-3', username: 'ella', password: 'ella123', role: 'seller', name: 'Ella Rivera' },
  { id: 'buyer', username: 'buyer', password: 'shop123', role: 'buyer', name: 'Creative Buyer' },
];

const SELECTORS = {
  authButton: document.getElementById('authButton'),
  openAuth: document.getElementById('openAuth'),
  closeAuth: document.getElementById('closeAuth'),
  authModal: document.getElementById('authModal'),
  authForm: document.getElementById('authForm'),
  authTitle: document.getElementById('authTitle'),
  authError: document.getElementById('authError'),
  loginTab: document.getElementById('loginTab'),
  registerTab: document.getElementById('registerTab'),
  registerFields: document.getElementById('registerFields'),
  authUsername: document.getElementById('authUsername'),
  authPassword: document.getElementById('authPassword'),
  authDisplayName: document.getElementById('authDisplayName'),
  authRole: document.getElementById('authRole'),
  themeToggle: document.getElementById('themeToggle'),
  navButtons: [...document.querySelectorAll('.nav-button')],
  featuredCards: document.getElementById('featuredCards'),
  galleryGrid: document.getElementById('galleryGrid'),
  favoritesGrid: document.getElementById('favoritesGrid'),
  favoritesEmpty: document.getElementById('favoritesEmpty'),
  marketCount: document.getElementById('marketCount'),
  searchInput: document.getElementById('searchInput'),
  clearSearch: document.getElementById('clearSearch'),
  categoryFilter: document.getElementById('categoryFilter'),
  priceFilter: document.getElementById('priceFilter'),
  orientationFilter: document.getElementById('orientationFilter'),
  colorFilter: document.getElementById('colorFilter'),
  favoritesSection: document.getElementById('favorites'),
  cartPanel: document.getElementById('cartPanel'),
  cartItems: document.getElementById('cartItems'),
  cartTotal: document.getElementById('cartTotal'),
  paymentMethod: document.getElementById('paymentMethod'),
  checkoutButton: document.getElementById('checkoutButton'),
  clearCart: document.getElementById('clearCart'),
  dashboardPanel: document.getElementById('dashboard'),
  sellerStats: document.getElementById('sellerStats'),
  uploadForm: document.getElementById('uploadForm'),
  uploadTitle: document.getElementById('uploadTitle'),
  uploadCategory: document.getElementById('uploadCategory'),
  uploadPrice: document.getElementById('uploadPrice'),
  uploadOrientation: document.getElementById('uploadOrientation'),
  uploadColor: document.getElementById('uploadColor'),
  uploadDescription: document.getElementById('uploadDescription'),
  uploadImage: document.getElementById('uploadImage'),
  sellerItemsGrid: document.getElementById('sellerItemsGrid'),
  adminPanel: document.getElementById('admin'),
  adminUsers: document.getElementById('adminUsers'),
  adminItems: document.getElementById('adminItems'),
  adminOrders: document.getElementById('adminOrders'),
  itemModal: document.getElementById('itemModal'),
  closeItem: document.getElementById('closeItem'),
  detailCategory: document.getElementById('detailCategory'),
  detailTitle: document.getElementById('detailTitle'),
  detailImage: document.getElementById('detailImage'),
  detailDescription: document.getElementById('detailDescription'),
  detailPhotographer: document.getElementById('detailPhotographer'),
  detailOrientation: document.getElementById('detailOrientation'),
  detailColor: document.getElementById('detailColor'),
  detailPrice: document.getElementById('detailPrice'),
  detailCartButton: document.getElementById('detailCartButton'),
  detailFavoriteButton: document.getElementById('detailFavoriteButton'),
  detailDownloadButton: document.getElementById('detailDownloadButton'),
  detailRating: document.getElementById('detailRating'),
  detailReviews: document.getElementById('detailReviews'),
  reviewFormBlock: document.getElementById('reviewFormBlock'),
  reviewRating: document.getElementById('reviewRating'),
  reviewComment: document.getElementById('reviewComment'),
  submitReview: document.getElementById('submitReview'),
  toastMessage: document.getElementById('toastMessage'),
};

let appState = {
  items: [],
  users: [],
  orders: [],
  currentUser: null,
  cart: [],
  favorites: [],
  filters: {
    search: '',
    category: 'all',
    price: 'all',
    orientation: 'all',
    color: 'all',
  },
  selectedItem: null,
};

function readStorage(key, fallback) {
  const value = localStorage.getItem(key);
  if (!value) return fallback;
  try {
    return JSON.parse(value);
  } catch (error) {
    return fallback;
  }
}

function writeStorage(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

function initStore() {
  if (!readStorage(storage.users)) writeStorage(storage.users, sampleUsers);
  if (!readStorage(storage.items)) writeStorage(storage.items, sampleItems);
  if (!readStorage(storage.orders)) writeStorage(storage.orders, []);
  if (!readStorage(storage.cart)) writeStorage(storage.cart, []);
  if (!readStorage(storage.favorites)) writeStorage(storage.favorites, []);
}

function loadState() {
  appState.users = readStorage(storage.users, sampleUsers);
  appState.items = readStorage(storage.items, sampleItems);
  appState.orders = readStorage(storage.orders, []);
  appState.cart = readStorage(storage.cart, []);
  appState.favorites = readStorage(storage.favorites, []);
  appState.currentUser = readStorage(storage.session, null);
}

function saveAppState() {
  writeStorage(storage.items, appState.items);
  writeStorage(storage.orders, appState.orders);
  writeStorage(storage.cart, appState.cart);
  writeStorage(storage.favorites, appState.favorites);
  if (appState.currentUser) writeStorage(storage.session, appState.currentUser);
  else localStorage.removeItem(storage.session);
}

function showToast(message) {
  SELECTORS.toastMessage.textContent = message;
  SELECTORS.toastMessage.classList.remove('hidden');
  setTimeout(() => {
    SELECTORS.toastMessage.classList.add('hidden');
  }, 2500);
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  SELECTORS.themeToggle.textContent = theme === 'light' ? '☀️' : '🌙';
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  setTheme(currentTheme === 'light' ? 'dark' : 'light');
}

function getActiveRoleButtons() {
  SELECTORS.navButtons.forEach((button) => {
    const role = button.dataset.role;
    if (!role) return;
    button.style.display = appState.currentUser && appState.currentUser.role === role ? 'inline-flex' : 'none';
  });
}

function setActiveSection(screen) {
  const sections = document.querySelectorAll('main section.panel, main section.hero-panel');
  sections.forEach((section) => {
    if (section.id === screen || (screen === 'home' && section.id === 'home')) {
      section.classList.remove('hidden');
    } else {
      section.classList.add('hidden');
    }
  });

  SELECTORS.navButtons.forEach((button) => {
    if (button.dataset.screen === screen) button.classList.add('active');
    else button.classList.remove('active');
  });
}

function updateAuthButton() {
  if (appState.currentUser) {
    SELECTORS.authButton.textContent = `Logout (${appState.currentUser.name})`;
    SELECTORS.authButton.dataset.action = 'logout';
  } else {
    SELECTORS.authButton.textContent = 'Login / Register';
    SELECTORS.authButton.dataset.action = 'login';
  }
}

function displayError(element, message) {
  element.textContent = message;
  element.classList.remove('hidden');
}

function clearError(element) {
  element.textContent = '';
  element.classList.add('hidden');
}

function filterItems() {
  const search = appState.filters.search.trim().toLowerCase();
  return appState.items.filter((item) => {
    const matchesSearch = !search || [item.title, item.description, item.photographer, item.category].some((value) => value.toLowerCase().includes(search));
    const matchesCategory = appState.filters.category === 'all' || item.category.toLowerCase() === appState.filters.category;
    const matchesOrientation = appState.filters.orientation === 'all' || item.orientation === appState.filters.orientation;
    const matchesColor = appState.filters.color === 'all' || item.color === appState.filters.color;
    const matchesPrice =
      appState.filters.price === 'all' ||
      (appState.filters.price === 'free' && item.price === 0) ||
      (appState.filters.price === 'under30' && item.price < 30) ||
      (appState.filters.price === '30plus' && item.price >= 30);
    return matchesSearch && matchesCategory && matchesOrientation && matchesColor && matchesPrice;
  });
}

function renderFeatured() {
  const featuredItems = appState.items.filter((item) => item.isFeatured).slice(0, 4);
  SELECTORS.featuredCards.innerHTML = featuredItems
    .map(
      (item) => `
      <button class="feature-card" data-id="${item.id}" style="background-image:url('${item.image}')">
        <div class="card-copy">
          <span class="badge">${item.category}</span>
          <h3>${item.title}</h3>
          <p>${item.photographer} · $${item.price}</p>
        </div>
      </button>
    `,
    )
    .join('');
}

function renderGallery(items, container, showEmpty = false) {
  container.innerHTML = items
    .map(
      (item) => `
      <button class="photo-card" data-id="${item.id}" type="button">
        <img src="${item.image}" alt="${item.title}" loading="lazy" />
        <div class="photo-meta">
          <div>
            <h3>${item.title}</h3>
            <p>${item.photographer}</p>
          </div>
          <div class="photo-price">
            <span>$${item.price}</span>
            <span>${item.rating.toFixed(1)} ★</span>
          </div>
        </div>
        <span class="favorite-icon">♥</span>
      </button>
    `,
    )
    .join('');

  if (showEmpty) {
    SELECTORS.favoritesEmpty.classList.toggle('hidden', items.length > 0);
  }
}

function renderGalleryGrid() {
  const results = filterItems();
  SELECTORS.galleryGrid.innerHTML = results
    .map(
      (item) => `
      <button class="photo-card" data-id="${item.id}" type="button">
        <img src="${item.image}" alt="${item.title}" loading="lazy" />
        <div class="photo-meta">
          <div>
            <h3>${item.title}</h3>
            <p>${item.photographer}</p>
          </div>
          <div class="photo-price">
            <span>$${item.price}</span>
            <span>${item.rating.toFixed(1)} ★</span>
          </div>
        </div>
      </button>
    `,
    )
    .join('');

  SELECTORS.marketCount.textContent = `${results.length} photos available`;
}

function renderFavorites() {
  const favoriteItems = appState.items.filter((item) => appState.favorites.includes(item.id));
  renderGallery(favoriteItems, SELECTORS.favoritesGrid, true);
}

function renderCart() {
  if (!appState.cart.length) {
    SELECTORS.cartItems.innerHTML = '<p class="empty-state">Your cart is empty. Add photos to purchase them instantly.</p>';
    SELECTORS.cartTotal.textContent = '$0.00';
    return;
  }

  SELECTORS.cartItems.innerHTML = appState.cart
    .map((item) => {
      const photo = appState.items.find((photoItem) => photoItem.id === item.id);
      return `
      <div class="cart-item" data-id="${photo.id}">
        <img src="${photo.image}" alt="${photo.title}" />
        <div class="cart-item-details">
          <h4>${photo.title}</h4>
          <p>${photo.photographer}</p>
          <p class="text-muted">${photo.category} · ${photo.orientation}</p>
        </div>
        <div class="cart-item-actions">
          <strong>$${photo.price}</strong>
          <button class="secondary-button remove-cart" type="button">Remove</button>
        </div>
      </div>
    `;
    })
    .join('');

  const total = appState.cart.reduce((sum, item) => {
    const photo = appState.items.find((photoItem) => photoItem.id === item.id);
    return sum + (photo ? photo.price : 0);
  }, 0);
  SELECTORS.cartTotal.textContent = `$${total.toFixed(2)}`;
}

function renderSellerDashboard() {
  const sellerItems = appState.items.filter((item) => item.sellerId === appState.currentUser?.id);
  SELECTORS.sellerStats.innerHTML = `
    <div class="metric-item">
      <span class="eyebrow">Total listings</span>
      <span>${sellerItems.length}</span>
    </div>
    <div class="metric-item">
      <span class="eyebrow">Total sales</span>
      <span>${appState.orders.filter((order) => order.userId !== appState.currentUser.id && order.items.some((photo) => sellerItems.map((item) => item.id).includes(photo.id))).length}</span>
    </div>
    <div class="metric-item">
      <span class="eyebrow">Pending downloads</span>
      <span>${appState.orders.filter((order) => order.items.some((photo) => sellerItems.map((item) => item.id).includes(photo.id))).length}</span>
    </div>
  `;

  SELECTORS.sellerItemsGrid.innerHTML = sellerItems
    .map(
      (item) => `
      <button class="photo-card" data-id="${item.id}" type="button">
        <img src="${item.image}" alt="${item.title}" loading="lazy" />
        <div class="photo-meta">
          <div>
            <h3>${item.title}</h3>
            <p>$${item.price} · ${item.category}</p>
          </div>
          <div class="photo-price">
            <span>${item.downloads} downloads</span>
          </div>
        </div>
      </button>
    `,
    )
    .join('');
}

function renderAdminPanel() {
  SELECTORS.adminUsers.innerHTML = appState.users
    .map(
      (user) => `
      <div class="user-row">
        <h4>${user.name}</h4>
        <p>${user.role}</p>
        <p class="text-muted">${user.username}</p>
      </div>
    `,
    )
    .join('');

  SELECTORS.adminItems.innerHTML = appState.items
    .map(
      (item) => `
      <div class="listing-card">
        <h3>${item.title}</h3>
        <p>${item.category} · $${item.price}</p>
        <p class="text-muted">${item.photographer}</p>
      </div>
    `,
    )
    .join('');

  SELECTORS.adminOrders.innerHTML = appState.orders
    .map(
      (order) => `
      <div class="order-row">
        <h4>Order ${order.id}</h4>
        <p>${order.items.length} item(s)</p>
        <p class="text-muted">${order.method} • ${new Date(order.date).toLocaleDateString()}</p>
      </div>
    `,
    )
    .join('');
}

function openModal(modal) {
  modal.classList.remove('hidden');
}

function closeModal(modal) {
  modal.classList.add('hidden');
}

function openItemDetail(itemId) {
  const item = appState.items.find((photo) => photo.id === itemId);
  if (!item) return;
  appState.selectedItem = item;
  SELECTORS.detailCategory.textContent = item.category;
  SELECTORS.detailTitle.textContent = item.title;
  SELECTORS.detailImage.src = item.image;
  SELECTORS.detailDescription.textContent = item.description;
  SELECTORS.detailPhotographer.textContent = item.photographer;
  SELECTORS.detailOrientation.textContent = item.orientation;
  SELECTORS.detailColor.textContent = item.color;
  SELECTORS.detailPrice.textContent = `$${item.price}`;
  SELECTORS.detailRating.textContent = `${item.rating.toFixed(1)} ★`;
  SELECTORS.detailCartButton.textContent = appState.cart.some((cartItem) => cartItem.id === item.id) ? 'In cart' : 'Add to cart';
  SELECTORS.detailFavoriteButton.textContent = appState.favorites.includes(item.id) ? 'Remove favorite' : 'Add to favorites';
  SELECTORS.detailDownloadButton.disabled = !isPurchased(item.id);
  SELECTORS.detailDownloadButton.textContent = isPurchased(item.id) ? 'Download now' : 'Purchase to download';
  renderReviews(item);
  openModal(SELECTORS.itemModal);
}

function isPurchased(itemId) {
  if (!appState.currentUser) return false;
  return appState.orders.some((order) => order.userId === appState.currentUser.id && order.items.some((item) => item.id === itemId));
}

function renderReviews(item) {
  SELECTORS.detailReviews.innerHTML = item.reviews
    .map(
      (review) => `
      <div class="review-card">
        <strong>${review.user}</strong> · ${review.rating} ★
        <p>${review.comment}</p>
      </div>
    `,
    )
    .join('');
  SELECTORS.reviewFormBlock.classList.toggle('hidden', !isPurchased(item.id));
}

function addToCart(itemId) {
  if (!appState.currentUser) {
    showAuthModal();
    return;
  }
  if (appState.cart.some((cartItem) => cartItem.id === itemId)) {
    showToast('Photo already in cart');
    return;
  }
  appState.cart.push({ id: itemId });
  saveAppState();
  renderCart();
  renderItemButtons();
  showToast('Added to cart');
  setActiveSection('cartPanel');
}

function removeFromCart(itemId) {
  appState.cart = appState.cart.filter((item) => item.id !== itemId);
  saveAppState();
  renderCart();
  renderItemButtons();
}

function toggleFavorite(itemId) {
  if (!appState.currentUser) {
    showAuthModal();
    return;
  }
  if (appState.favorites.includes(itemId)) {
    appState.favorites = appState.favorites.filter((id) => id !== itemId);
    showToast('Removed from favorites');
  } else {
    appState.favorites.push(itemId);
    showToast('Added to favorites');
  }
  saveAppState();
  renderFavorites();
  renderItemButtons();
}

function showAuthModal() {
  SELECTORS.loginTab.click();
  openModal(SELECTORS.authModal);
}

function loginUser(username, password) {
  const user = appState.users.find((account) => account.username === username && account.password === password);
  if (!user) {
    displayError(SELECTORS.authError, 'Incorrect username or password.');
    return;
  }
  appState.currentUser = { ...user };
  saveAppState();
  updateAuthButton();
  getActiveRoleButtons();
  renderAfterAuth();
  closeModal(SELECTORS.authModal);
  showToast(`Welcome back, ${user.name}`);
}

function registerUser(username, password, name, role) {
  if (!username || !password || !name) {
    displayError(SELECTORS.authError, 'All fields are required.');
    return;
  }
  const existing = appState.users.find((account) => account.username === username);
  if (existing) {
    displayError(SELECTORS.authError, 'Username already taken.');
    return;
  }
  const newUser = {
    id: `user-${Date.now()}`,
    username,
    password,
    role,
    name,
  };
  appState.users.push(newUser);
  appState.currentUser = { ...newUser };
  saveAppState();
  updateAuthButton();
  getActiveRoleButtons();
  renderAfterAuth();
  closeModal(SELECTORS.authModal);
  showToast(`Welcome, ${newUser.name}`);
}

function logoutUser() {
  appState.currentUser = null;
  saveAppState();
  updateAuthButton();
  getActiveRoleButtons();
  showToast('You have logged out.');
  setActiveSection('home');
}

function renderItemButtons() {
  const itemCards = document.querySelectorAll('.photo-card');
  itemCards.forEach((card) => {
    const id = card.dataset.id;
    const favoriteIcon = card.querySelector('.favorite-icon');
    if (!favoriteIcon) return;
    favoriteIcon.textContent = appState.favorites.includes(id) ? '♥' : '♡';
  });
}

function applyFilters() {
  appState.filters.search = SELECTORS.searchInput.value;
  appState.filters.category = SELECTORS.categoryFilter.value;
  appState.filters.price = SELECTORS.priceFilter.value;
  appState.filters.orientation = SELECTORS.orientationFilter.value;
  appState.filters.color = SELECTORS.colorFilter.value;
  renderGalleryGrid();
}

function clearSearch() {
  SELECTORS.searchInput.value = '';
  appState.filters.search = '';
  renderGalleryGrid();
}

function completeCheckout() {
  if (!appState.currentUser) {
    showAuthModal();
    return;
  }
  if (!appState.cart.length) {
    showToast('Add items to your cart first.');
    return;
  }
  const order = {
    id: `order-${Date.now()}`,
    userId: appState.currentUser.id,
    items: [...appState.cart],
    date: new Date().toISOString(),
    method: SELECTORS.paymentMethod.value === 'stripe' ? 'Stripe' : 'PayPal',
  };
  appState.orders.push(order);
  appState.cart.forEach((cartItem) => {
    const photo = appState.items.find((item) => item.id === cartItem.id);
    if (photo) photo.downloads += 1;
  });
  appState.cart = [];
  saveAppState();
  renderCart();
  renderSellerDashboard();
  renderAdminPanel();
  renderItemButtons();
  showToast('Purchase complete! Your download is ready in the photo details.');
  setActiveSection('market');
}

function handleNavClick(event) {
  const button = event.target.closest('[data-screen]');
  if (!button) return;
  const screen = button.dataset.screen;
  if (screen === 'dashboard' && appState.currentUser?.role !== 'seller') {
    showToast('Seller access required.');
    return;
  }
  if (screen === 'admin' && appState.currentUser?.role !== 'admin') {
    showToast('Admin access required.');
    return;
  }
  setActiveSection(screen);
}

function setupFilters() {
  categories.forEach((category) => {
    const option = document.createElement('option');
    option.value = category === 'All categories' ? 'all' : category.toLowerCase();
    option.textContent = category;
    SELECTORS.categoryFilter.appendChild(option);
    const uploadOption = option.cloneNode(true);
    if (category !== 'All categories') {
      uploadOption.value = category;
      SELECTORS.uploadCategory.appendChild(uploadOption);
    }
  });

  orientations.forEach((orientation) => {
    const option = document.createElement('option');
    option.value = orientation === 'All orientation' ? 'all' : orientation;
    option.textContent = orientation;
    SELECTORS.orientationFilter.appendChild(option);
  });

  colors.forEach((color) => {
    const option = document.createElement('option');
    option.value = color === 'All color' ? 'all' : color;
    option.textContent = color;
    SELECTORS.colorFilter.appendChild(option);
  });
}

function handleAuthSubmit(event) {
  event.preventDefault();
  clearError(SELECTORS.authError);
  const username = SELECTORS.authUsername.value.trim();
  const password = SELECTORS.authPassword.value;
  const isRegister = SELECTORS.registerFields.classList.contains('hidden') === false;
  if (isRegister) {
    registerUser(username, password, SELECTORS.authDisplayName.value.trim(), SELECTORS.authRole.value);
  } else {
    loginUser(username, password);
  }
}

function switchToLogin() {
  SELECTORS.loginTab.classList.add('active');
  SELECTORS.registerTab.classList.remove('active');
  SELECTORS.registerFields.classList.add('hidden');
  SELECTORS.authTitle.textContent = 'Login';
  SELECTORS.authSubmit.textContent = 'Login';
  clearError(SELECTORS.authError);
}

function switchToRegister() {
  SELECTORS.loginTab.classList.remove('active');
  SELECTORS.registerTab.classList.add('active');
  SELECTORS.registerFields.classList.remove('hidden');
  SELECTORS.authTitle.textContent = 'Register';
  SELECTORS.authSubmit.textContent = 'Create account';
  clearError(SELECTORS.authError);
}

function renderAfterAuth() {
  getActiveRoleButtons();
  renderSellerDashboard();
  renderAdminPanel();
  renderFavorites();
  renderCart();
}

function handleUploadSubmit(event) {
  event.preventDefault();
  if (appState.currentUser?.role !== 'seller') {
    showToast('Only photographers can upload photos.');
    return;
  }
  const newItem = {
    id: `photo-${Date.now()}`,
    title: SELECTORS.uploadTitle.value.trim(),
    category: SELECTORS.uploadCategory.value,
    price: Number(SELECTORS.uploadPrice.value),
    orientation: SELECTORS.uploadOrientation.value,
    color: SELECTORS.uploadColor.value,
    photographer: appState.currentUser.name,
    rating: 4.8,
    reviews: [],
    description: SELECTORS.uploadDescription.value.trim(),
    image: SELECTORS.uploadImage.value.trim(),
    sellerId: appState.currentUser.id,
    downloads: 0,
    isFeatured: false,
  };
  if (!newItem.title || !newItem.image || !newItem.description) {
    showToast('Please complete all fields.');
    return;
  }
  appState.items.unshift(newItem);
  saveAppState();
  renderGalleryGrid();
  renderSellerDashboard();
  renderAdminPanel();
  SELECTORS.uploadForm.reset();
  showToast('Photo uploaded successfully.');
}

function renderAll() {
  renderFeatured();
  renderGalleryGrid();
  renderFavorites();
  renderCart();
  renderSellerDashboard();
  renderAdminPanel();
  renderItemButtons();
}

function handleCardClick(event) {
  const card = event.target.closest('[data-id]');
  if (!card) return;
  const id = card.dataset.id;
  openItemDetail(id);
}

function handleItemModalButtons(event) {
  if (event.target === SELECTORS.detailCartButton) {
    addToCart(appState.selectedItem.id);
  }
  if (event.target === SELECTORS.detailFavoriteButton) {
    toggleFavorite(appState.selectedItem.id);
    SELECTORS.detailFavoriteButton.textContent = appState.favorites.includes(appState.selectedItem.id)
      ? 'Remove favorite'
      : 'Add to favorites';
  }
  if (event.target === SELECTORS.detailDownloadButton) {
    if (isPurchased(appState.selectedItem.id)) {
      showToast('Download started.');
    } else {
      showToast('Purchase this photo to download it.');
    }
  }
  if (event.target === SELECTORS.submitReview) {
    event.preventDefault();
    if (!isPurchased(appState.selectedItem.id)) {
      showToast('You must purchase this photo before reviewing it.');
      return;
    }
    const review = {
      user: appState.currentUser.name,
      rating: Number(SELECTORS.reviewRating.value),
      comment: SELECTORS.reviewComment.value.trim(),
    };
    if (!review.comment) {
      showToast('Review text is required.');
      return;
    }
    appState.selectedItem.reviews.unshift(review);
    appState.selectedItem.rating = (
      appState.selectedItem.reviews.reduce((sum, item) => sum + item.rating, 0) / appState.selectedItem.reviews.length
    ).toFixed(1);
    saveAppState();
    renderReviews(appState.selectedItem);
    SELECTORS.reviewComment.value = '';
    showToast('Review submitted.');
  }
}

function initApp() {
  initStore();
  loadState();
  setTheme('dark');
  updateAuthButton();
  getActiveRoleButtons();
  setupFilters();
  renderAll();

  SELECTORS.searchInput.addEventListener('input', applyFilters);
  SELECTORS.clearSearch.addEventListener('click', clearSearch);
  SELECTORS.categoryFilter.addEventListener('change', applyFilters);
  SELECTORS.priceFilter.addEventListener('change', applyFilters);
  SELECTORS.orientationFilter.addEventListener('change', applyFilters);
  SELECTORS.colorFilter.addEventListener('change', applyFilters);
  document.querySelector('main').addEventListener('click', handleNavClick);
  SELECTORS.authButton.addEventListener('click', () => {
    if (SELECTORS.authButton.dataset.action === 'logout') {
      logoutUser();
    } else {
      showAuthModal();
    }
  });
  SELECTORS.openAuth.addEventListener('click', showAuthModal);
  SELECTORS.closeAuth.addEventListener('click', () => closeModal(SELECTORS.authModal));
  SELECTORS.closeItem.addEventListener('click', () => closeModal(SELECTORS.itemModal));
  SELECTORS.themeToggle.addEventListener('click', toggleTheme);
  SELECTORS.loginTab.addEventListener('click', switchToLogin);
  SELECTORS.registerTab.addEventListener('click', switchToRegister);
  SELECTORS.authForm.addEventListener('submit', handleAuthSubmit);
  SELECTORS.checkoutButton.addEventListener('click', completeCheckout);
  SELECTORS.clearCart.addEventListener('click', () => {
    appState.cart = [];
    saveAppState();
    renderCart();
    showToast('Cart cleared.');
  });
  SELECTORS.uploadForm.addEventListener('submit', handleUploadSubmit);
  SELECTORS.galleryGrid.addEventListener('click', handleCardClick);
  SELECTORS.featuredCards.addEventListener('click', handleCardClick);
  SELECTORS.favoritesGrid.addEventListener('click', handleCardClick);
  SELECTORS.cartItems.addEventListener('click', (event) => {
    const button = event.target.closest('.remove-cart');
    if (!button) return;
    const card = button.closest('[data-id]');
    removeFromCart(card.dataset.id);
  });
  SELECTORS.itemModal.addEventListener('click', (event) => {
    if (event.target === SELECTORS.itemModal) closeModal(SELECTORS.itemModal);
  });
  SELECTORS.detailCartButton.addEventListener('click', () => addToCart(appState.selectedItem.id));
  SELECTORS.detailFavoriteButton.addEventListener('click', () => toggleFavorite(appState.selectedItem.id));
  SELECTORS.detailDownloadButton.addEventListener('click', () => {
    if (isPurchased(appState.selectedItem.id)) showToast('Download ready!');
    else showToast('Purchase this photo to download it.');
  });
  SELECTORS.submitReview.addEventListener('click', handleItemModalButtons);
  SELECTORS.itemModal.addEventListener('click', (event) => {
    if (event.target.closest('.detail-actions')) return;
  });
  SELECTORS.itemModal.addEventListener('click', (event) => {
    if (event.target.closest('.review-form')) return;
  });
 
  document.body.addEventListener('click', (event) => {
    if (event.target.matches('.nav-button')) return;
  });
}

initApp();
