const text = document.querySelector('#moodText');
const button = document.querySelector('#createButton');
const status = document.querySelector('#status');
const result = document.querySelector('#result');
const gameShell = document.querySelector('#gameShell');
const gameArea = document.querySelector('#gameArea');
const moodLabel = document.querySelector('#moodLabel');
const moodConfidence = document.querySelector('#moodConfidence');
const gameTitle = document.querySelector('#gameTitle');
const gameMessage = document.querySelector('#gameMessage');
const activeGameTitle = document.querySelector('#activeGameTitle');
const restartButton = document.querySelector('#restartButton');

let currentConfig = null;
let cleanup = () => {};

button.addEventListener('click', analyse);
restartButton.addEventListener('click', () => currentConfig && startGame(currentConfig));

async function analyse() {
  const value = text.value.trim();
  if (value.length < 2) {
    status.textContent = 'Please add a little more detail.';
    return;
  }

  button.disabled = true;
  status.textContent = 'Reading emotional cues…';
  try {
    const response = await fetch('/api/analyse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: value })
    });
    if (!response.ok) throw new Error('Unable to analyse text');
    const data = await response.json();
    moodLabel.textContent = titleCase(data.mood);
    moodConfidence.textContent = `${Math.round(data.confidence * 100)}% confidence`;
    gameTitle.textContent = data.game.title;
    gameMessage.textContent = data.game.message;
    activeGameTitle.textContent = data.game.title;
    result.classList.remove('hidden');
    gameShell.classList.remove('hidden');
    currentConfig = data.game;
    startGame(currentConfig);
    setTimeout(() => {
  gameShell.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });
}, 150);
    status.textContent = '';
  } catch (error) {
    status.textContent = 'Something went wrong. Please try again.';
  } finally {
    button.disabled = false;
  }
}

function startGame(config) {
  cleanup();
  gameArea.innerHTML = '';
  const starters = {
    'catch-stars': catchTargets,
    'break-blocks': breakBlocks,
    'quick-reaction': quickReaction,
    'breathing-orbs': breathingOrbs,
    'gentle-garden': gentleGarden,
    'clear-the-space': clearSpace,
    'memory-match': memoryMatch,
  };
  cleanup = (starters[config.game] || memoryMatch)(config) || (() => {});
}

function scoreBadge(label = 'Score') {
  const badge = document.createElement('div');
  badge.className = 'game-score';
  badge.textContent = `${label}: 0`;
  gameArea.appendChild(badge);
  return badge;
}

function place(el, padding = 12) {
  const maxX = Math.max(padding, gameArea.clientWidth - el.offsetWidth - padding);
  const maxY = Math.max(52, gameArea.clientHeight - el.offsetHeight - padding);
  el.style.left = `${random(padding, maxX)}px`;
  el.style.top = `${random(52, maxY)}px`;
}

function catchTargets(config) {
  let score = 0;
  const badge = scoreBadge();
  const target = document.createElement('button');
  target.className = 'target star';
  target.textContent = '✦';
  target.setAttribute('aria-label', 'Catch star');
  gameArea.appendChild(target);
  target.addEventListener('click', () => {
    score += 1;
    badge.textContent = `Score: ${score}`;
    place(target);
  });
  requestAnimationFrame(() => place(target));
  const timer = setInterval(() => place(target), 1800 / config.speed);
  return () => clearInterval(timer);
}

function breakBlocks(config) {
  let score = 0;
  const badge = scoreBadge('Broken');
  const interval = setInterval(spawn, 800 / config.speed);
  spawn();
  function spawn() {
    const block = document.createElement('button');
    block.className = 'target block';
    block.textContent = '×';
    gameArea.appendChild(block);
    requestAnimationFrame(() => place(block));
    block.addEventListener('click', () => {
      score += 1;
      badge.textContent = `Broken: ${score}`;
      block.remove();
    });
    setTimeout(() => block.remove(), 2500);
  }
  return () => clearInterval(interval);
}

function quickReaction(config) {
  let score = 0;
  const badge = scoreBadge('Hits');
  let timer;
  const spawn = () => {
    const target = document.createElement('button');
    target.className = 'target star';
    target.textContent = '●';
    gameArea.appendChild(target);
    requestAnimationFrame(() => place(target));
    const born = performance.now();
    target.onclick = () => {
      const reaction = Math.round(performance.now() - born);
      score += 1;
      badge.textContent = `Hits: ${score} · ${reaction} ms`;
      target.remove();
      timer = setTimeout(spawn, random(300, 1000));
    };
    setTimeout(() => {
      if (target.isConnected) {
        target.remove();
        timer = setTimeout(spawn, 350);
      }
    }, 1200 / config.speed);
  };
  spawn();
  return () => clearTimeout(timer);
}

function breathingOrbs() {
  const instruction = scoreBadge('Breathe in');
  const orb = document.createElement('div');
  orb.className = 'target orb';
  gameArea.appendChild(orb);
  orb.style.left = '50%';
  orb.style.top = '50%';
  orb.style.transform = 'translate(-50%, -50%) scale(.55)';
  orb.style.transition = 'transform 4s ease-in-out';
  let inhale = true;
  const cycle = () => {
    instruction.textContent = inhale ? 'Breathe in' : 'Breathe out';
    orb.style.transform = `translate(-50%, -50%) scale(${inhale ? 1.75 : .55})`;
    inhale = !inhale;
  };
  cycle();
  const interval = setInterval(cycle, 4000);
  return () => clearInterval(interval);
}

function gentleGarden() {
  let flowers = 0;
  const badge = scoreBadge('Flowers');
  const garden = document.createElement('div');
  garden.className = 'garden';
  gameArea.appendChild(garden);
  const addFlower = (event) => {
    const rect = gameArea.getBoundingClientRect();
    const flower = document.createElement('span');
    flower.className = 'flower';
    flower.textContent = ['✿', '❀', '✾'][Math.floor(Math.random() * 3)];
    flower.style.left = `${event.clientX - rect.left}px`;
    flower.style.top = `${event.clientY - rect.top}px`;
    gameArea.appendChild(flower);
    flowers += 1;
    badge.textContent = `Flowers: ${flowers}`;
  };
  gameArea.addEventListener('click', addFlower);
  return () => gameArea.removeEventListener('click', addFlower);
}

function clearSpace(config) {
  let left = 12;
  const badge = scoreBadge('Items left');
  badge.textContent = `Items left: ${left}`;
  for (let i = 0; i < left; i += 1) {
    const item = document.createElement('button');
    item.className = 'target block';
    item.textContent = ['•', '×', '—'][i % 3];
    gameArea.appendChild(item);
    requestAnimationFrame(() => place(item));
    item.onclick = () => {
      item.remove();
      left -= 1;
      badge.textContent = left ? `Items left: ${left}` : 'All clear';
    };
  }
  return () => {};
}

function memoryMatch() {
  const symbols = ['●', '▲', '■', '◆', '★', '✚'];
  const deck = shuffle([...symbols, ...symbols]);
  const grid = document.createElement('div');
  grid.className = 'card-grid';
  gameArea.appendChild(grid);
  let open = [];
  let locked = false;
  deck.forEach((symbol) => {
    const card = document.createElement('button');
    card.className = 'card';
    card.textContent = symbol;
    grid.appendChild(card);
    card.onclick = () => {
      if (locked || card.classList.contains('open') || card.classList.contains('matched')) return;
      card.classList.add('open');
      open.push(card);
      if (open.length === 2) {
        locked = true;
        const [a, b] = open;
        if (a.textContent === b.textContent) {
          a.classList.add('matched');
          b.classList.add('matched');
          open = [];
          locked = false;
        } else {
          setTimeout(() => {
            a.classList.remove('open');
            b.classList.remove('open');
            open = [];
            locked = false;
          }, 650);
        }
      }
    };
  });
  return () => {};
}

function random(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function shuffle(items) { return items.sort(() => Math.random() - 0.5); }
function titleCase(value) { return value.charAt(0).toUpperCase() + value.slice(1); }
