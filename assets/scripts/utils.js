// const baseUrl = 'http://127.0.0.1:6050'
// const baseUrl = "http://10.130.144.82:6500"
const baseUrl = 'https://formbridge.eu.pythonanywhere.com'
window.baseUrl = baseUrl

function obf(text){
    if (text){
     return btoa(text)
    }  else{
     return ''
    }
 }

 function deobf(text){
    if (text){
     return atob(text)
    }  else{
     return ''
    }
 }
 
 window.obf = obf
 window.deobf = deobf

 function jof(text){
    if (text){
     return btoa(JSON.stringify(text))
    }  else{
     return ''
    }
 }

 function jdf(text){
    if (text){
      const res = JSON.parse(atob(text))
     return res
    }  else{
     return ''
    }
 }
 
 window.jof = jof
 window.jdf = jdf




 document.addEventListener('DOMContentLoaded', ()=>{

 function alert(title=type, text, type='info'){
    const alertDiv = document.createElement('div') || document.querySelector('.alert-div')
    text = String(text)
    if(text.includes('Unexpected token')){
        text = 'Server configuration error. Please contact support'
    }
    alertDiv.classList.add('alert-div')
    let iconClass = '<svg width="34px" height="34px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM12 17.75C12.4142 17.75 12.75 17.4142 12.75 17V11C12.75 10.5858 12.4142 10.25 12 10.25C11.5858 10.25 11.25 10.5858 11.25 11V17C11.25 17.4142 11.5858 17.75 12 17.75ZM12 7C12.5523 7 13 7.44772 13 8C13 8.55228 12.5523 9 12 9C11.4477 9 11 8.55228 11 8C11 7.44772 11.4477 7 12 7Z" fill="#057ca3"></path> </g></svg>'
   if(type=='error'){ 
    iconClass = '<svg fill="#000" width="24px" height="24px" viewBox="0 0 32.00 32.00" version="1.1" xmlns="http://www.w3.org/2000/svg" stroke="#ffa552" stroke-width="0.00032"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <title>warning</title> <path d="M30.555 25.219l-12.519-21.436c-1.044-1.044-2.738-1.044-3.782 0l-12.52 21.436c-1.044 1.043-1.044 2.736 0 3.781h28.82c1.046-1.045 1.046-2.738 0.001-3.781zM14.992 11.478c0-0.829 0.672-1.5 1.5-1.5s1.5 0.671 1.5 1.5v7c0 0.828-0.672 1.5-1.5 1.5s-1.5-0.672-1.5-1.5v-7zM16.501 24.986c-0.828 0-1.5-0.67-1.5-1.5 0-0.828 0.672-1.5 1.5-1.5s1.5 0.672 1.5 1.5c0 0.83-0.672 1.5-1.5 1.5z"></path> </g></svg>'
   } else if(type=='success'){ 
     iconClass =  '<svg width="34px" height="34px" viewBox="0 0 24.00 24.00" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM16.0303 8.96967C16.3232 9.26256 16.3232 9.73744 16.0303 10.0303L11.0303 15.0303C10.7374 15.3232 10.2626 15.3232 9.96967 15.0303L7.96967 13.0303C7.67678 12.7374 7.67678 12.2626 7.96967 11.9697C8.26256 11.6768 8.73744 11.6768 9.03033 11.9697L10.5 13.4393L12.7348 11.2045L14.9697 8.96967C15.2626 8.67678 15.7374 8.67678 16.0303 8.96967Z" fill="#000000"></path> </g></svg>' 
   } 
    alertDiv.innerHTML = `
        <div class="alert">
            <div class="icon ${type}">
            ${iconClass}
            </div>
            <div class="content">
            <div class="text">${title}</div>
            <hr>
            <div class="m-info">${text}</div>
        </div>
        </div>
    `
    document.body.appendChild(alertDiv)
    setTimeout(() => {
        alertDiv.classList.add('move-right')
    }, 5000);

    setTimeout(() => {
        document.body.removeChild(alertDiv)
    }, 6500);

 }
 window.alert = alert
})




function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + days*24*60*60*1000);
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/; secure; samesite=strict";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i=0;i < ca.length;i++) {
        let c = ca[i].trim();
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length));
    }
    return null;
}
window.setCookie = setCookie
window.getCookie = getCookie



document.addEventListener('DOMContentLoaded', ()=>{
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if(btn){
    btn.addEventListener('click', () => {
        menu.classList.toggle('hidden');
    });
}

    document.querySelectorAll('#mobile-menu a').forEach(link => {
        link.addEventListener('click', () => {
            menu.classList.add('hidden');
        });
    });
})

function toggleBtn(id, text, toggle){
    const btn = document.querySelector(`#${id}`)
    if(btn) btn.disabled = toggle
    toggle ? btn.setAttribute('data-loading', '') : btn.removeAttribute('data-loading', '')
    if(btn.hasAttribute('data-loading')){
     btn.innerHTML = `${text} <i class="fas fa-spinner fa-spin"></i> `
        } else{
            btn.innerHTML = text
        }
}
window.toggleBtn = toggleBtn