const themeToggle = document.getElementById("theme-toggle");
const dotsContainer = document.getElementById("dots-container");
const temp = document.getElementById("temp");
const hum = document.getElementById("hum");
const modeButtonFirst = document.getElementById("first-mode");
const modeButtonSecond = document.getElementById("second-mode");
const modeButtonTherd = document.getElementById("therd-mode");
const spanMode = document.getElementById("span-mode");
const motorStat = document.getElementById("motor_stat");

document.addEventListener("DOMContentLoaded", function () {
  const menuToggle = document.getElementById("menu-toggle");
  const navList = document.querySelector(".nav-list");

  menuToggle.addEventListener("click", function () {
    navList.classList.toggle("active");
  });
});

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  const isDark = document.body.classList.contains("dark");
  themeToggle.textContent = isDark ? "Светлая тема" : "Темная тема";

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
    const dot = document.createElement("div");
    dot.classList.add("dot");

    const randomX = Math.random() * containerWidth;
    const randomY = Math.random() * containerHeight;

    dot.style.left = `${randomX}px`;
    dot.style.top = `${randomY}px`;

    dotsContainer.appendChild(dot);
  }
}

function clearDots() {
  dotsContainer.innerHTML = "";
}

async function json() {
  let response = await fetch("/api/data");
  res = await response.json();
  console.log(res.temp + " - temp");
  console.log(res.hum + " - hum");
  console.log(res.mode + " - mode");
  console.log(res.motor_stat + " - motor_stat");
  console.log(res.heater_stat + " - heater_stat");
  console.log(res.fan_stat + " - fan_stat");

  temp.textContent = res.temp + "° " + res.heater_stat;
  hum.textContent = res.hum + "% " + res.fan_stat;
  motorStat.textContent = res.motor_stat;

  if (res.mode == 1) {
    modeButtonFirst.className = "active-button";
    modeButtonSecond.className = "list-button";
    modeButtonTherd.className = "list-button";
  }
  if (res.mode == 2) {
    modeButtonFirst.className = "list-button";
    modeButtonSecond.className = "active-button";
    modeButtonTherd.className = "list-button";
  }
  if (res.mode == 3) {
    modeButtonFirst.className = "list-button";
    modeButtonSecond.className = "list-button";
    modeButtonTherd.className = "active-button";
  }
}

setInterval(json, 1000);
