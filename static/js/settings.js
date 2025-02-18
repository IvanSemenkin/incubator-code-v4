const mode = document.getElementById("mode");
const temp = document.getElementById("temp");
const spanMode = document.getElementById("span-mode");
const motorStat = document.getElementById("motor_stat");

document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle");
    const navList = document.querySelector(".nav-list");
  
    menuToggle.addEventListener("click", function () {
      navList.classList.toggle("active");
    });
  });
async function json() {
  let response = await fetch("/json_file");
  res = await response.json()
  console.log(res.motor_stat + ' - motor_stat');
  console.log(res.heater_stat + ' - heater_stat');
  console.log(res.fan_stat + ' - fan_stat');

  temp.textContent = res.heater_stat
  hum.textContent = res.fan_stat
  motorStat.textContent = res.motor_stat
}

setInterval(json, 1000)
