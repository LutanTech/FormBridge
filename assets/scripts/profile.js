function sendOTPEmail(){
    const btn = document.querySelector('.send-reset-otp')
if(btn){
    btn.disabled = true
    btn.innerHTML = 'Sending... <i class="fas fa-spinner fa-spin"></i>'
    const user = getCookie('user')
    if(user){
        fetch(`${baseUrl}/send_reset_otp/${user}`)
        .then(res=>res.json())
        .then(data=>{
            data = jdf(data)
            if(data.error){
                alert('Error', data.error, 'error')
                btn.disabled = false
                 btn.innerHTML = 'Sent <i class="fas fa-ckeck-circle"></i>'
                 setTimeout(() => {
                 btn.innerHTML = 'Request Again'
                 }, 2000);

            } if(data.msg){
                alert('Success', data.msg, 'success')
                btn.disabled = false
                btn.innerHTML = 'Send OTP'

            }
        })
        .catch(e=>{
            alert('Connection error', e.message, 'error')
            btn.disabled = false
            btn.innerHTML = 'Send OTP'

        })
    }
}

}
document.addEventListener('DOMContentLoaded', ()=>{
    const form = document.querySelector('#reset-password')
    if(form){
        form.addEventListener('submit', (e)=>{
            e.preventDefault()
            const oldP = form.querySelector('#oldP').value.trim()
            const newP = form.querySelector('#newP').value.trim()
            const newCP = form.querySelector('#newCP').value.trim()
            const otp = form.querySelector('#otp').value.trim()

            if(oldP && newP && newCP && otp){
                if(oldP.length > 6 || newCP.length > 6 || newP.length > 6 || otp.length > 6){
                  alert('Error', 'Maximum length is 6. Please confirm', 'error')
                  return
                }
                if(newP != newCP){
                    alert('Error', 'Passwords do not match', 'error')
                    return
                }
                const user = getCookie('user')
                const payload = {
                    'user_data':user,
                    'form_data':jof({
                        'oldP':oldP,
                        'newP':newP,
                        'newCP':newCP,
                        'otp':otp
                    })

                }
                console.log(payload)
                if(payload && user){
                    fetch(`${baseUrl}/reset_password`, {
                        method:'POST',
                        headers:{
                            'Content-Type':'application/json'
                        },
                        body:JSON.stringify({data:jof(payload)})
                    })
                    .then(res=>res.json())
                    .then(data=>{
                        data = jdf(data)
                        if(data.error){
                            alert('Error', data.error, 'error')
                        }
                        if(data.msg){
                            alert('Success', data.msg, 'success')
                        }
                    })
                    .catch(e=>{
                        alert('Connection Error', e.message, 'error')
                    })
                }

            } else{
                alert('Error', 'Missing details. Please Confirm all inputs', 'error')
            }
        })
    }
    function initAccountInfo(){
        const loader = document.querySelector('.accountLoader')
        const user = getCookie('user')
        const token = getCookie('token')
        if(user){
            const payload = {
                'user_data':user,
                'token':token,
            }
            fetch(`${baseUrl}/account/info`,{
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify({data:jof(payload)})
            })
            .then(res=>res.json())
            .then(data=>{
                data = jdf(data)
                if(data.error){
                    alert('Error', data.error, 'error')
                    loader.classList.toggle('flex')
                    loader.classList.toggle('none')

                }
                if(data.user){
                    updateAccountInfo(data)
                    loader.classList.toggle('flex')
                    loader.classList.toggle('none')
                }
            })
            .catch(e=>{
                alert('Error', e.message, 'error')
                loader.classList.toggle('flex')
                loader.classList.toggle('none')
            })
        }

    }
    setTimeout(() => {
            initAccountInfo()
    }, 2000);

    function updateAccountInfo(data){
        const user = data.user
        console.log(user)
        const usn = document.querySelector('.p-usn')
        const email = document.querySelector('.p-email')
        const phone = document.querySelector('.p-phone')
        const ld = document.querySelector('.p-ldevices')
        const dv = document.querySelector('.p-devices')
        const ve = document.querySelector('.p-verified')
        const pj = document.querySelector('.p-joined')
        const bd = document.querySelector('.b-devices')
        const rd = document.querySelector('.r-devices')
        const tfa = document.querySelector('.p-2fa-status')

        usn.textContent = user.username
        email.textContent = user.email
        phone.textContent = user.phone ? user.phone : 'Not yet added'
        ld.textContent = data.ld ? data.ld : '0'
        dv.textContent = user.devices ? user.devices : '0'
        bd.textContent = user.blocked ? `(${user.blocked.length})` : '0'
        rd.textContent = user.reported ? `(${user.reported.length})` : '0'
        dv.textContent = user.devices ? user.devices : '0'
        ve.innerHTML = user.is_verified ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-x"></i>'
        tfa.innerHTML = user.two_fa ? '<b style="color:#0f0">Active</b>' : '<b style="color:red">Not Active</b>'
        pj.textContent = new Date(user.joined).toLocaleString()

           updateAccountDevices(user.blocked, user.reported)
    }
    function updateAccountDevices(blocked, reported){
        if(blocked && reported){
            const bparent = document.querySelector('.bdl')
            const rparent = document.querySelector('.rdl')
            bparent.innerHTML = ''
            rparent.innerHTML = ''
            blocked.forEach(b => {
                const li = document.createElement('li')
                li.innerHTML = `<div class="name">${deobf(b)}</div> <div class="d-actions">
              <div class="unblock" data-id="${b}" t="Unblock">
              <i class="fas fa-play" style="color: #0f0;"></i>
            </div>
            </div>`
                bparent.appendChild(li)
                const unb = li.querySelector('.unblock')
                if(unb){
                    unb.addEventListener('click', ()=>{
                        confirmAction(
                            'Attention !!!',
                            `You are about to unblock this device `
                          ).then(resp => {
                            if(resp){
                              unblockDevice(b)
                            }
                          })
                    })
                }
            });
            reported.forEach(r => {
                const li = document.createElement('li')
                li.innerHTML = `<div class="name">${deobf(r)}</div> <div class="d-actions">
              <div class="delete" data-id="${r}" t="Delete">
              <i class="fas fa-trash" style="color: red;"></i>
            </div>
            </div>`
                rparent.appendChild(li)
                const unr = li.querySelector('.delete')
                if(unr){
                    unr.addEventListener('click', ()=>{
                        confirmAction(
                            'Attention !!!',
                            `You are about to delete this device from reported devices`
                          ).then(resp => {
                            if(resp){
                              unReportDevice(r)
                            }
                          })
                    })
                }
            });
        }
    }
    function unblockDevice(ua){
        if(ua && deobf(ua)){
            fetch(`${baseUrl}/unblock/${ua}/${user}/${token}`)
            .then(r=>r.json())
            .then(data=>{
                if(data.error){
                    alert('Error', data.error, 'error')
                }
                if(data.msg){
                    alert('Success', data.msg, 'success')
                initAccountInfo()
                }
            })
            .catch(err=>{
                alert('Error', err.message, 'error')
            })
        }
    }

function unReportDevice(ua){
    if(ua && deobf(ua)){
        fetch(`${baseUrl}/unreport/${ua}/${user}/${token}`)
        .then(r=>r.json())
        .then(data=>{
            if(data.error){
                alert('Error', data.error, 'error')
            }
            if(data.msg){
                alert('Success', data.msg, 'success')
                initAccountInfo()
            }
        })
        .catch(err=>{
            alert('Error', err.message, 'error')
        })
    }
}

})
