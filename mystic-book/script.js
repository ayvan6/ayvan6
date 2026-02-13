document.addEventListener("DOMContentLoaded", function(){

const PASSWORD="arya";

const unlockBtn=document.getElementById("unlock-btn");
const input=document.getElementById("password-input");
const error=document.getElementById("error-msg");
const passwordScreen=document.getElementById("password-screen");
const bookArea=document.getElementById("book-area");
const pages=document.querySelectorAll(".page");
const cover=document.getElementById("cover");
const nextBtn=document.getElementById("next-btn");
const prevBtn=document.getElementById("prev-btn");

let currentPage=0;

/* Show Page with Animation */
function showPage(index){
pages.forEach(page=>{
page.style.display="none";
page.classList.remove("slide-in");
});
pages[index].style.display="block";
pages[index].classList.add("slide-in");
}

/* Unlock */
unlockBtn.onclick=function(){
if(input.value===PASSWORD){
passwordScreen.style.display="none";
bookArea.classList.remove("hidden");
showPage(0);
}else{
error.innerText="Wrong password";
}
};

/* Cover Tap */
cover.onclick=function(){
currentPage=1;
showPage(currentPage);
};

/* Next */
nextBtn.onclick=function(){
if(currentPage < pages.length-1){
currentPage++;
showPage(currentPage);
}
};

/* Previous */
prevBtn.onclick=function(){
if(currentPage>0){
currentPage--;
showPage(currentPage);
}
};

/* Keyboard */
document.addEventListener("keydown",function(e){
if(e.key==="ArrowRight") nextBtn.onclick();
if(e.key==="ArrowLeft") prevBtn.onclick();
});

/* Swipe */
let startX=0;
document.addEventListener("touchstart",e=>{
startX=e.touches[0].clientX;
});
document.addEventListener("touchend",e=>{
let endX=e.changedTouches[0].clientX;
if(startX-endX>50) nextBtn.onclick();
if(endX-startX>50) prevBtn.onclick();
});

});
