
// const baseUrl = 'http://127.0.0.1:6500'
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
    alertDiv.classList.add('alert-div')
    let iconClass = '<i class="fas fa-info-circle"></i>'
   if(type=='error'){ 
    iconClass = '<i class="fas fa-warning"></i>'
   } else if(type=='success'){ 
     iconClass =  '<i class="fas fa-check-circle"></i>' 
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