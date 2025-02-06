const themeToggle = document.getElementById('theme-toggle');
const dotsContainer = document.getElementById('dots-container');
const mode = document.getElementById('mode')
const modeButtonFirst = document.getElementById('first-mode')
const modeButtonSecond = document.getElementById('second-mode')
const modeButtonTherd = document.getElementById('therd-mode')
const spanMode = document.getElementById('span-mode')

themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  const isDark = document.body.classList.contains('dark');
  themeToggle.textContent = isDark ? 'Светлая тема' : 'Темная тема';

  if (isDark) {
    generateRandomDots();
  } else {
    clearDots();
  }
});


function generateRandomDots() {
  clearDots(); 
  const numDots = 20;
  const containerWidth = window.innerWidth;
  const containerHeight = window.innerHeight;

  for (let i = 0; i < numDots; i++) {
    const dot = document.createElement('div');
    dot.classList.add('dot');


    const randomX = Math.random() * containerWidth;
    const randomY = Math.random() * containerHeight;

    dot.style.left = `${randomX}px`;
    dot.style.top = `${randomY}px`;

    dotsContainer.appendChild(dot);
  }
}


function clearDots() {
  dotsContainer.innerHTML = '';
}

function modeChange() {
  console.log('click');
  console.log(mode.value);
  
  if (mode.value == '1') {
    modeButtonFirst.className = 'active-button';
    modeButtonSecond.className = 'list-button';
    modeButtonTherd.className = 'list-button';
    spanMode.textContent = 1
  }if (mode.value == '2') {
    modeButtonFirst.className = 'list-button';
    modeButtonSecond.className = 'active-button';
    modeButtonTherd.className = 'list-button';
    spanMode.textContent = 2
  }if (mode.value == '3') {
    modeButtonFirst.className = 'list-button';
    modeButtonSecond.className = 'list-button';
    modeButtonTherd.className = 'active-button';
    spanMode.textContent = 3
  } 
  mode.value = ''

}


