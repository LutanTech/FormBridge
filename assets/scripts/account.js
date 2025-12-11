document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('.sidebar')
    const btn = document.querySelector('#mobile-menu-account-btn')
    const overlay = document.querySelector('.overlay')
    const cbtn = document.querySelector('.closeMenu')
    window.confirm = confirm



    function confirm(title, text, input, waitVal, proceed){
      const confirmModal = document.querySelector('.confirm-modal')
    
      if(!confirmModal) return
    
      confirmModal.classList.add('appear')
    
      const inner = confirmModal.querySelector('.confirm-inner')
    
      // Title
      inner.querySelector('.title').textContent =
        title || 'Are you sure you want to continue with this action?'
    
      inner.querySelector('.text').innerHTML = text || ''
    
      const inputField = inner.querySelector('input')
      if(input){
        if(inputField) inputField.classList.add('seen')
        inputField.focus()
      } else {
        if(inputField) inputField.classList.remove('seen')
      }
    
      // Cancel button
      const cancelBtn = inner.querySelector('[data-id="cancel"]')
      cancelBtn.onclick = () => {
        confirmModal.classList.remove('appear')
      }
    
      // Continue button
      const continueBtn = inner.querySelector('[data-id="continue"]')
      continueBtn.onclick = () => {
        if(typeof proceed === "function"){
          if(inputField.value.toUpperCase().trim() !== waitVal && waitVal){
            alert('Error', 'Please type the required text: ' + waitVal, 'error')
            return
          }
          proceed(input ? inputField?.value : null)
        }
        confirmModal.classList.remove('appear')
      }
    }
    
    function exec(fn){
      console.log("executing fn")
      fn()
    }
    
    if (nav && btn) {
      btn.addEventListener('click', () => {
        nav.classList.toggle('collapsed')
      })
      cbtn.addEventListener('click', () => {
        nav.classList.toggle('collapsed')
      })
    }

    function initAccount() {
      const content = document.querySelector('.content')
      const user = jdf(getCookie('user'))
      const token = jdf(getCookie('tokn'))
      if (user.username) {
        // pingAccount(user.username, token)
      } else{
        window.location.href = '/login'
      }
      document.querySelector('.username').textContent = user.username

    }
    initAccount()
    function ZMinus(div){

    overlay.querySelector(div).setAttribute('style', 'z-index:-1')
  }
  function ZAdd(div){
    overlay.querySelector(div).setAttribute('style', 'z-index:4')
  }
    const cards = document.querySelectorAll('.card')
    cards.forEach(c => {
      c.addEventListener('click', () => {
        const attr = c.getAttribute('data-id')
        overlay.classList.toggle('vissible')
        if(attr == 'forms'){
          ZMinus('.newForm')
          ZAdd('.forms-ov')
        }
        if(attr == 'new'){
          ZAdd('.newForm')
          ZMinus('.forms-ov')
        }
      })
    })

    const backBtn = document.querySelector('.back-btn')
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        overlay.classList.toggle('vissible')
      })
    }
    window.initForms = initForms

    function initForms(){
        const user = jdf(getCookie('user'))
        const token = getCookie('token')
        const wrapper = document.querySelector('.forms-wrapper')
        if(user){
            wrapper.innerHTML = 'Fetching your forms...'
            fetch(`${baseUrl}/get_forms/${user.id}/${token}`)
            .then(res=>res.json())
            .then(data=>{
                if(data.error){
                    alert('Error', data.error, 'error')
                }
                if(data.msg){
                    alert('No Forms Found', data.msg, 'info')
              }
              wrapper.innerHTML = ''
                const forms = data.forms
                if(forms && forms.length > 0){
                  initDbs(forms)
                    forms.forEach(f=>{
                   const div = document.createElement('div')
                   div.classList.add('form')
                   div.innerHTML = `
                   <div class="form-logo">
                  <img src="/assets/images/icon.png" alt="">
                </div>
                <div class="form-name">
                  ${f.name_str}
                </div>
                <hr>
                <div class="form-desc">
                  ${f.desc ? f.desc : 'No description added'}
                </div>
                <div class="form-created">
                  ${f.added}
                </div>
                <div class="form-actions">
                  <div class="copy" t="Copy Link">
                    <i class="fas fa-copy"></i>
                  </div>
                  <div class="delete" t="Delete">
                    <i class="fas fa-trash"></i>
                  </div>
                  <div class="edit" t="Edit">
                    <i class="fas fa-edit"></i>
                  </div>
                  <div class="info" t="Info">
                    <i class="fas fa-info-circle"></i>
                  </div>
                  <div class="toggle" t="Toggle Visibility">
                    <i class="fas fa-eye"></i>
                  </div>
                  <div class="database" t="Open Database">
                    <i class="fas fa-server"></i>
                  </div>
                </div>
                   `
                   wrapper.appendChild(div)
                   div.querySelector('.copy').addEventListener('click', ()=>{
                    const link = `${window.origin}/submit/?${f.name_str}&id=${f.id}`
                    navigator.clipboard.writeText(link)
                    alert('Link copied', link, 'success')
                   })
                   div.querySelector('.database').addEventListener('click', ()=>{
                    const db = {
                      'u':user.id,
                      'f':f.id,
                      't':token
                    }
                    const link = `${window.origin}/database/?i=${jof(db)}`
                    window.location.href= link
                   })
                   div.querySelector('.delete').addEventListener('click', ()=>{
                    confirm(
                      "Are you sure you want to delete this form?",
                      `<label for="del-pass"> Type <b>'DELETE/${f.name_str}'</b> here to proceed </label><input style="text-transform:uppercase" oninput="checkVal(this.value.trim().toUpperCase(),'DELETE/${f.name_str}' )" type="text" autocomplete="off" id="del-pass" placeholder="Type 'DELETE/${f.name_str}' here to proceed">`, 'danger',
                    `DELETE/${f.name_str}`,
                      (value)=>{
                      alert('Info', 'Deleting form' + f.id, 'info')
                      const user = jdf(getCookie('user'))
                      const token = getCookie('token')
                      if(user && token && user.id){
                        const payload = {
                          'uid':user.id,
                          'token':token,
                          'fid':f.id
                        }
                        console.table(jof(payload))
                        delete_form(jof(payload))
                      }
                    })
                   })
                   div.querySelector('.info').addEventListener('click', ()=>{
                    const ov = document.querySelector('.infoModal')
                    ov.classList.toggle('flex')
                    const user = jdf(getCookie('user'))
                    const token = getCookie('token')
                    if(user){
                    const payload = {
                        'uid':user.id,
                        'token':token,
                        'fid': f.id

                    }
                   setTimeout(() => {
                    fetchFormInfo(jof(payload))
                   }, 1000); 
                } else{
                        alert('Error', 'Please login to perform this action', 'error')
                    }
                   })
            })

                } else{
                    wrapper.innerHTML = 'No forms found. Add some'
                }
        
                
            })
            .catch(e=>{
                wrapper.innerHTML = `<i style="color:red">Network error fetching your forms : ${e.message}. Please reload</i>`
            })
        }
    }
    initForms()
    
  })
  function checkVal(val, expected) {
    const btn = document.querySelector('[data-id="continue"]')
    if (!btn) return
    btn.disabled = (val !== expected ? expected : 'false')
  }
  function delete_form(payload){
    if(payload){
      fetch(`${baseUrl}/delete_form`, {
        headers:{
          'Content-Type':'application/json'
        }, 
        method:'POST',
        body:JSON.stringify({data:payload})
      })
      .then(res=>res.json())
      .then(data=>{
        if(data.error){
          alert('Error', data.error, 'error')
          return
        }
        alert('Success', data.msg, 'success')
      })
      .catch(e=>{
        alert('Connection error', e.message, 'error')
      })
    }

  }

  document.addEventListener('DOMContentLoaded', () => {
    const checkBoxes = document.querySelectorAll('.lb input');
    const form = document.querySelector('#newFormForm');
    const allInputs = form.querySelectorAll('input');
    const ts = form.querySelectorAll('textarea');
    
        let savedData = JSON.parse(localStorage.getItem('saveData') || '{}');
    
        allInputs.forEach(i => {
            if (savedData[i.id] !== undefined) {
    
                if (i.type === 'checkbox') {
                    i.checked = savedData[i.id];
                } else {
                    i.value = savedData[i.id];
                }
    
            }
        })
            ts.forEach(i => {
                if (savedData[i.id] !== undefined) {
               i.value = savedData[i.id];
                }
    });
    

    if (form) {
        const allInputs = form.querySelectorAll('input');

        let savedData = JSON.parse(localStorage.getItem('saveData') || '{}');
        
        allInputs.forEach(i => {
            i.addEventListener('input', () => {
        
                if (i.type === 'checkbox') {
                    savedData[i.id] = i.checked;
                } else {
                    savedData[i.id] = i.value.trim();
                }
        
                localStorage.setItem('saveData', JSON.stringify(savedData));
            });
        });
        ts.forEach(i => {
            i.addEventListener('input', () => {
                    savedData[i.id] = i.value.trim();
                localStorage.setItem('saveData', JSON.stringify(savedData));
            });
        });
        
      form.addEventListener('submit', (e) => {
        e.preventDefault();

        const selected = [...checkBoxes]
          .filter(c => c.checked)
          .map(c => c.id);


        if (selected.length < 1) {
          alert('Fields Required', 'Please Select Fields', 'error')
        }
        const name = form.querySelector('#name').value.trim()
        const deadline = form.querySelector('#deadline').value.trim()
        const desc = form.querySelector('#desc').value.trim()
        const ins = form.querySelector('#instructions').value.trim()

        if (!name) {
          alert('Error', 'Form Name and Deadline Required ', 'error')
        }
        const user = jdf(getCookie('user'))
        if(user){
            const uid = user.id
            const token = getCookie('token')

            const data = {
            'deadline': deadline,
            'name': name,
            'selected': selected,
            'desc': desc ? desc : '',
            'ins': ins ? ins : '',
            'uid':uid,
            'token':token
            }
    
        createForm((data))
    } else{
        alert('Error','Please Login before continuing', 'error')
    }
      });
    }

    function createForm(data) {
      if (data) {
        toggleBtn('create-form', 'Create', true)
        fetch(`${baseUrl}/new_form`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              data: data
            })
          })
          .then(res => res.json())
          .then(data => {
            if (data.error) {
              alert('Error', data.error, 'error')
              toggleBtn('create-form', 'Create', false)
            }
            if (data.msg) {
              alert('Success', 'Form Added Successfully', 'success')
              initForms()
              toggleBtn('create-form', 'Create', false)
            }
          })
          .catch(e => {
            alert('Connection Error', e.message || 'Check your Network connection' , 'error')
            toggleBtn('create-form', 'Create', false)
          })
      }

    }
    const im = document.querySelector('.infoModal')
    const imn = im.querySelector('.infoModal .info-inner')
    if(im){
     im.addEventListener('click', (e)=>{
        if(e.target !== imn && !imn.contains(e.target) && im.classList.contains('flex')){
         im.classList.remove('flex')
         im.classList.add('none')
        }
     })
    }
    window.initDbs = initDbs
    
    function initDbs(data){
      const user = jdf(getCookie('user'))
      token = getCookie('token')
      if(data){
        const dbs = data
        dbs.forEach(db=>{
          const div = document.createElement('div')
          const parent = document.querySelector('.dbs')
          div.classList.add('db')
          div.innerHTML =  `
                <div class="db-pic">
                  <img src="/assets/images/db2.png" alt="" class="db-img">
                </div>
                <div class="db-name"><i class="fas fa-database"></i> ${db.name_str}</div>
                <hr>
                <div class="db-desc"><i class="fas fa-info-circle"></i> ${db.desc ? db.desc :'No description added'} </div>
                <div class="db-size"> <i class="fas fa-server"></i> 56.09kb</div>
                <div class="db-actions">
                  <div class="open"><i class="fas fa-eye"></i></div>
                  <div class="pause"><i class="fas fa-pause"></i></div>
                  <div class="download"><i class="fas fa-cloud-download"></i></div>
                  <div class="clear"><i class="fas fa-trash"></i></div>
                  <div class="refresh"> <i class="fas fa-refresh"></i> </div>
                </div>
          `
          parent.appendChild(div)
          const rd = div.querySelector('.refresh')
          div.querySelector('.refresh').addEventListener('click', ()=>{
            console.log(rd.innerHTML)
            if(rd.innerHTML != '<i class="fas fa-spinner fa-spin"></i>'){
                 rd.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'
            }  else{
              return
            }
            setTimeout(() => {
              rd.innerHTML = '<i class="fas fa-check-circle" style="color:#0f0; scale:1.5"></i>'
            }, 4000);
            setTimeout(() => {
                rd.innerHTML = '<i class="fas fa-refresh"></i>'
            }, 5000);
          })
          div.querySelector('.open').addEventListener('click', ()=>{
            const db_data = {
              'u':user.id,
              'f':db.id,
              't':token
            }
            const link = `${window.origin}/database/?i=${jof(db_data)}`
            window.location.href= link
          })
           div.querySelector('.clear').addEventListener('click', ()=>{
            confirm(
              "Are you sure you want to delete all data in this Database?",
              `<label for="del-pass"> Type <b>'DELETE/${db.name_str}/your_passsword'</b> here to proceed </label><input style="text-transform:uppercase" oninput="checkVal(this.value.trim().toUpperCase(),'' )" type="text" autocomplete="off" id="del-pass" placeholder="Type 'DELETE/${db.name_str}' here to proceed">`, 'danger',
            ``,
              (value)=>{
              alert('Info', 'Deleting all data in database' + db.id, 'info')
              const user = jdf(getCookie('user'))
              const token = getCookie('token')
              if(user && token && user.id){
                const payload = {
                  'uid':user.id,
                  'token':token,
                  'fid':db.id
                }
                console.table(jof(payload))
                delete_db(jof(payload))
              }
            })
            
           })

        })
        function delete_db(payload){
          if(payload){
            fetch(`${baseUrl}/delete_db_data`, {
              headers:{
                'Content-Type':'application/json'
              }, 
              method:'POST',
              body:JSON.stringify({data:payload})
            })
            .then(res=>res.json())
            .then(data=>{
              if(data.error){
                alert('Error', data.error, 'error')
                return
              }
              alert('Success', data.msg, 'success')
            })
            .catch(e=>{
              alert('Connection error', e.message, 'error')
            })
          }
      
        }
      }

    }
  });
