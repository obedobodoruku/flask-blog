const button = document.getElementById("myBtn");
const mainBody = document.querySelector(".main")
const navContainer = document.querySelector(".nav-container");

console.log(navContainer);

button.addEventListener("click", () => { 
    navContainer.style.display = "block"; 
    mainBody.style.display = "none";
})