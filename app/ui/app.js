const userInput = document.getElementById('user-id');
const saveUserButton = document.getElementById('save-user');
const createForm = document.getElementById('create-item-form');
const itemsContainer = document.getElementById('items');
const refreshButton = document.getElementById('refresh-items');
const historyList = document.getElementById('history-list');
const historyHint = document.getElementById('history-hint');
const toast = document.getElementById('toast');

let selectedItemId = null;
const storedUser = window.localStorage.getItem('bellabell-user-id') || '';
if (storedUser) {
  userInput.value = storedUser;
}

function showMessage(message, isError = false) {
  toast.textContent = message;
  toast.style.color = isError ? '#dc2626' : '#15803d';
}

function currentUserId() {
  return userInput.value.trim();
}

async function api(path, options = {}) {
  const userId = currentUserId();
  const headers = { ...(options.headers || {}) };

  if (userId) {
    headers['X-User-Id'] = userId;
  }

  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail || 'Request failed');
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function itemCard(item) {
  const card = document.createElement('article');
  card.className = 'item';

  const lastPrice = item.last_price == null ? 'No checks yet' : `$${item.last_price.toFixed(2)}`;

  card.innerHTML = `
    <div class="item-title">
      <span>${item.name}</span>
      <div class="row">
        <button type="button" data-action="history">History</button>
        <button type="button" data-action="check">Check now</button>
      </div>
    </div>
    <div class="item-meta">${lastPrice} • every ${item.check_interval_minutes} min</div>
    <div class="item-meta">${item.url}</div>
  `;

  card.querySelector('[data-action="check"]').addEventListener('click', async () => {
    try {
      const observation = await api(`/items/${item.id}/check`, { method: 'POST' });
      showMessage(`Checked ${item.name}: $${observation.price.toFixed(2)}`);
      await loadItems();
      if (selectedItemId === item.id) {
        await loadHistory(item.id, item.name);
      }
    } catch (error) {
      showMessage(error.message, true);
    }
  });

  card.querySelector('[data-action="history"]').addEventListener('click', () => {
    loadHistory(item.id, item.name);
  });

  return card;
}

async function loadItems() {
  itemsContainer.innerHTML = 'Loading...';
  try {
    const items = await api('/items');
    if (!items.length) {
      itemsContainer.textContent = 'No items yet. Add your first item above.';
      return;
    }

    itemsContainer.innerHTML = '';
    items.forEach((item) => itemsContainer.appendChild(itemCard(item)));
  } catch (error) {
    itemsContainer.textContent = 'Unable to load items.';
    showMessage(error.message, true);
  }
}

async function loadHistory(itemId, itemName) {
  selectedItemId = itemId;
  historyHint.textContent = `Recent checks for ${itemName}`;
  historyList.innerHTML = '<li>Loading...</li>';

  try {
    const entries = await api(`/items/${itemId}/history`);
    historyList.innerHTML = '';
    if (!entries.length) {
      historyList.innerHTML = '<li>No observations yet.</li>';
      return;
    }

    entries.forEach((entry) => {
      const li = document.createElement('li');
      const checkedAt = new Date(entry.checked_at).toLocaleString();
      li.textContent = `$${entry.price.toFixed(2)} at ${checkedAt}`;
      historyList.appendChild(li);
    });
  } catch (error) {
    historyList.innerHTML = '<li>Could not load history.</li>';
    showMessage(error.message, true);
  }
}

saveUserButton.addEventListener('click', async () => {
  const userId = currentUserId();
  if (!userId) {
    showMessage('Please provide a user id first.', true);
    return;
  }

  window.localStorage.setItem('bellabell-user-id', userId);
  showMessage(`Using user ${userId}`);
  await loadItems();
});

refreshButton.addEventListener('click', loadItems);

createForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(createForm);

  const payload = {
    name: formData.get('name'),
    url: formData.get('url'),
    css_selector: formData.get('css_selector'),
    check_interval_minutes: Number(formData.get('check_interval_minutes')),
    target_price: formData.get('target_price') ? Number(formData.get('target_price')) : null,
  };

  try {
    await api('/items', { method: 'POST', body: JSON.stringify(payload) });
    showMessage('Item created.');
    createForm.reset();
    await loadItems();
  } catch (error) {
    showMessage(error.message, true);
  }
});

if (storedUser) {
  loadItems();
}
