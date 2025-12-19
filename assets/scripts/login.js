document.addEventListener('DOMContentLoaded', () => {

    const eye = document.querySelector('.eye');
    const form = document.querySelector('#form');
    const pass = form.querySelector('#password')

    eye.addEventListener('click', () => {
      eye.classList.toggle('closed')
      eye.classList.contains('closed') ? pass.setAttribute('type', 'text') :
        pass.setAttribute('type', 'password')

      if (eye.classList.contains('closed')) {
        eye.innerHTML = '<i style="color: rgb(224, 223, 223) !important" class="fas fa-eye-slash"></i>'
      } else {
        eye.innerHTML = '<i style="color: rgb(224, 223, 223) !important"  class="fas fa-eye"></i>'
      }

    });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();

      const username = form.querySelector('#username').value.trim();
      const password = form.querySelector('#password').value.trim();
      const ua = navigator.userAgent;
      if (!ua) {
        alert('Error', 'Please reload the page or disable any extension', 'error')
        return
      }

      if (username && password) {
        const payload = {
          username: username,
          password: password,
          ua: ua
        };
        login(jof(payload));
      }
    });

    function login(payload) {
      toggleBtn('lbtn', 'Loading...', true)
      fetch(`${baseUrl}/login`, {
          headers: {
            'Content-Type': 'application/json'
          },
          method: 'POST',
          body: JSON.stringify({
            data: payload
          })
        })
        .then(res => res.json())
        .then(data => {
          if(data.error){
            data = data
          } else{
          data = jdf(data)
          }

          if (data.error) {
            alert('Error', data.error, 'error')
            toggleBtn('lbtn', 'Login', false)
            return
          }
          if (data.user) {
            const exp = data.expiry || 1
            setCookie('user', data.user, exp)
            setCookie('token', data.token, exp)
            setCookie('expiry', data.expiry, exp)
            const user = jdf(data.user)
            alert('Logged In', `Welcome ${user.username}. Redirecting...`, 'success')
            toggleBtn('lbtn', 'Login', false)
            setTimeout(() => {
              window.location.href = '/account'
            }, 2000)
          } else {
            alert('Attention', data.info, 'info')
            showOTPField(data.temp_token || data.tt)
          }

        })
        .catch(err => {
          alert('Network Error', 'Please Make sure you have an internet connection', 'error')
          toggleBtn('lbtn', 'Login', false)
        })

    }

    function showOTPField(token) {
      const p = document.querySelector('.otpField')
      p.classList.toggle('none')
      p.classList.toggle('flex')
      p.querySelector('form').setAttribute('data-token', token)
    }

    function toggleBtn(btn, text, toggle) {
      if (btn && text) {
        var btn = document.querySelector(`#${btn}`)
        btn.disabled = toggle
        toggle ? btn.setAttribute('data-loading', '') : btn.removeAttribute('data-loading', '')
        if (btn.hasAttribute('data-loading')) {
          btn.innerHTML = `${text} <i class="fas fa-spinner fa-spin"></i> `
        } else {
          btn.innerHTML = text
        }
      }
    }

  })
  document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.otp-inputs');

    inputs.forEach((input, idx) => {
      input.addEventListener('input', () => {
        if (input.value.trim().length === 1 && idx < inputs.length - 1) {
          inputs[idx + 1].focus();
        }
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !input.value && idx > 0) {
          inputs[idx - 1].focus();
        }
      });

      input.addEventListener('focus', () => {
        input.select();
      });
    });
    const form1 = document.querySelector('#tfaform')
    form1.addEventListener('submit', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();

      let domOtp = '';
      const tt = form1.getAttribute('data-token')
      inputs.forEach(inp => {
        domOtp += inp.value.trim();
      });

      const ua = navigator.userAgent;
      if (!ua) {
        alert('Error', 'Please reload the page or disable any extension', 'error')
        return
      }

      if (ua) {
        const payload = {
          otp: domOtp,
          tt: tt,
          ua: ua
        };
        console.log(ua)

        login_2fa(payload);
      }
    });

    function login_2fa(payload) {
      toggleBtn('confirm-tfa', true)
      fetch(`${baseUrl}/login/two_fa`, {
          headers: {
            'Content-Type': 'application/json'
          },
          method: 'POST',
          body: JSON.stringify({
            data: jof(payload)
          })
        })
        .then(res => res.json())
        .then(data => {
          console.log(data)

          if (data.error) {
            alert('Failed', data.error, 'error')
            toggleBtn('confirm-tfa', false)
          }
          if (data) {
            data = jdf(data)
            if (data.error) {
              data = data
            }
            console.log(data)
            console.log(data.user ? 'true' : 'false')
            setTimeout(() => {
              if (data.user) {
                const exp = data.expiry || 1
                setCookie('user', data.user, exp)
                setCookie('token', data.token, exp)
                setCookie('expiry', data.expiry, exp)
                const user = jdf(data.user)
                alert('Logged In', `Welcome ${user.username}. Redirecting...`, 'success')
                toggleBtn('confirm-tfa', false)
                setTimeout(() => {
                  window.location.href = '/account'
                }, 2000)
              }
            }, 100)
          }
        })
        .catch(err => {
          alert('Network Error', 'Please Make sure you have an internet connection', 'error')
          toggleBtn('confirm-tfa', false)
        })

    }

  })