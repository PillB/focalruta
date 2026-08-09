
(function(){
 const app=document.getElementById('field-card-app'); if(!app) return;
 const KEY='canon6d-fieldcard-v4';
 const checks=[...app.querySelectorAll('.fc-check')];
 function sync(){checks.forEach(c=>c.closest('.fc-shot')?.classList.toggle('fc-done',c.checked)); const n=checks.filter(c=>c.checked).length; const count=app.querySelector('#fc-count'); if(count) count.textContent=`${n}/10`; try{localStorage.setItem(KEY,JSON.stringify(checks.map(c=>c.checked)))}catch(e){}}
 try{const saved=JSON.parse(localStorage.getItem(KEY)||'[]'); checks.forEach((c,i)=>c.checked=!!saved[i])}catch(e){}
 checks.forEach(c=>c.addEventListener('change',sync)); sync();
 app.querySelector('#fc-reset')?.addEventListener('click',()=>{checks.forEach(c=>c.checked=false);sync()});
 function tab(id){app.querySelectorAll('.fc-tab').forEach(b=>b.classList.toggle('fc-active',b.dataset.fcTab===id)); app.querySelectorAll('.fc-panel').forEach(p=>p.classList.toggle('fc-active',p.id===id)); const scroller=app.closest('.fc-modal-scroll'); if(scroller) scroller.scrollTo({top:0,behavior:'auto'}); else window.scrollTo({top:0,behavior:'auto'});}
 app.querySelectorAll('.fc-tab').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.fcTab)));
 app.querySelector('[data-fc-open-field]')?.addEventListener('click',()=>tab('fc-field'));
 window.Canon6DFieldCard={tab,sync};
})();
