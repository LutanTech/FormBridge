// --- Globals ---
let currentPage = 1;
let currentLimit = 50;
let currentDataId = null;
let windowData = null;

const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');
const limitSelect = document.getElementById('limit');

const modalOverlay = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const modalCancel = document.getElementById('modal-cancel');
const modalConfirm = document.getElementById('modal-confirm');

// --- Pagination buttons ---
prevBtn.addEventListener('click', () => changePage('prev'));
nextBtn.addEventListener('click', () => changePage('next'));

function changePage(direction){
    if(!currentDataId) return;
    const page = direction === 'next' ? currentPage + 1 : currentPage - 1;
    if(page < 1) return;
    currentPage = page;
    fetchDB(currentDataId, currentPage, currentLimit);
}

// --- Limit selector ---
limitSelect.addEventListener('change', () => {
    currentLimit = parseInt(limitSelect.value);
    currentPage = 1;
    if(currentDataId) fetchDB(currentDataId, currentPage, currentLimit);
});
document.addEventListener('DOMContentLoaded', ()=>{
    fetchDB(new URLSearchParams(window.location.search).get('i'))

})

// --- Fetch DB ---
function fetchDB(dataId, page = 1, limit = 50){
    currentDataId = dataId;
    fetch(`${baseUrl}/database/${dataId}?page=${page}&limit=${limit}`)
    .then(res => res.json())
    .then(data => {
        windowData = data;
        renderTable(data);
        prevBtn.disabled = !data.has_prev;
        nextBtn.disabled = !data.has_next;
    });
}

// --- Render table ---
function renderTable(data){
    const columns = data.inputs.map(i => i.replace(/^-/, ''));
    const thead = document.getElementById('table-head');
    const tbody = document.getElementById('table-body');

    thead.innerHTML = '<th>#</th>';
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col.charAt(0).toUpperCase() + col.slice(1);
        thead.appendChild(th);
    });
    const ac = document.createElement('th');
    ac.textContent = 'Actions';
    thead.appendChild(ac);

    tbody.innerHTML = '';
    data.submissions.forEach((sub, idx) => {
        const tr = document.createElement('tr');
        const rowNum = (currentPage - 1) * currentLimit + idx + 1;
        const cells = columns.map(col => `<td>${sub[col] ?? ''}</td>`).join('');
        const actions = `<td id="sub-actions">
            <button class="delete"><i class="fas fa-trash"></i></button>
            <button class="edit"><i class="fas fa-edit"></i></button>
            <button class="view"><i class="fas fa-eye"></i></button>
        </td>`;
        tr.innerHTML = `<td>${rowNum}</td>` + cells + actions;
        tbody.appendChild(tr);
    });

    attachActions();
}

function attachActions(){
    document.querySelectorAll('#sub-actions').forEach(td => {
        const row = td.closest('tr');
        const index = row.querySelector('td').textContent - 1;
        const submission = windowData.submissions[index];

        td.querySelector('.delete').onclick = () => openModal('delete', submission);
        td.querySelector('.edit').onclick = () => openModal('edit', submission);
        td.querySelector('.view').onclick = () => openModal('view', submission);
    });
}

// --- Modal handler ---
function openModal(type, submission){
    modalOverlay.classList.remove('hidden');
    modalConfirm.style.display = 'inline-block';

    if(type === 'delete'){
        modalTitle.textContent = 'Confirm Delete';
        modalContent.innerHTML = `Are you sure you want to delete submission by <strong style="color:aqua"> ${submission.name}</strong>?`;
        modalConfirm.onclick = () => {
            const payload={
                'sid':submission.id,
                'i':new URLSearchParams(window.location.search).get('i'),
            }
            console.log(submission.id)
            delete_sub(jof(payload))
            alert(`Deleted ${submission.id}`);
            modalOverlay.classList.add('hidden');
        };
    } else if (type === 'edit') {
        modalTitle.textContent = 'Edit Submission';
    
        const fields = windowData.inputs.map(i => i.replace(/^-/, ''));
    
        let html = "";
        fields.forEach(field => {
            html += `
                <label style="margin-top:10px; display:block;">${field.charAt(0).toUpperCase()+field.slice(1)}:</label>
                <input 
                    type="text" 
                    id="edit-${field}" 
                    value="${submission[field] ?? ''}" 
                    style="width:100%; padding:6px; margin-bottom:8px;"
                >
            `;
        });
    
        modalContent.innerHTML = html;
    
        modalConfirm.style.display = 'inline-block';
        modalConfirm.onclick = () => {
            let updated = {};
            fields.forEach(field => {
                updated[field] = document.getElementById(`edit-${field}`).value.trim();
            });
            const payload = {
                'i':new URLSearchParams(window.location.search).get('i'),
                'updated':updated,
                'sid':submission.id
            }
    
            update_sub(jof(payload));
    
            modalOverlay.classList.add('hidden');
        };
    }
     else if(type === 'view'){
        modalTitle.textContent = 'View Submission';
        let html = '<ul>';
        for(const key in submission){
            html += ` ${submission[key] ? `<li><strong>${key}:</strong> ${submission[key]}</li>` : ''}`;
        }
        html += '</ul>';
        modalContent.innerHTML = html;
        modalConfirm.style.display = 'none';
    }

    modalCancel.onclick = () => {
        modalOverlay.classList.add('hidden');
    };
}
function delete_sub(payload){
    if(payload){
        fetch(`${baseUrl}/delete_submission`, {
            method :'POST',
            headers :{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({data:payload})
        })
        .then(res=>res.json())
        .then(data=>{
            if(data.error){
                alert('Error', data.error, 'error')
            }
            if(data.msg){
                alert("Success", data.msg, 'success')
            }
        })
        .catch(e=>{
            alert('Connection Error', e.message, 'error')
        })
    }
}
function update_sub(payload){
    if(payload){
        fetch(`${baseUrl}/edit_submission`, {
            method :'POST',
            headers :{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({data:payload})
        })
        .then(res=>res.json())
        .then(data=>{
            if(data.error){
                alert('Error', data.error, 'error')
            }
            if(data.msg){
                alert("Success", data.msg, 'success')
            }
        })
        .catch(e=>{
            alert('Connection Error', e.message, 'error')
        })
    }
}

