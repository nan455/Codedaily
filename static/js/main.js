document.getElementById('btn-sub').addEventListener('click', async () => {
  const name  = document.getElementById('inp-name').value.trim();
  const email = document.getElementById('inp-email').value.trim();
  const diff  = document.querySelector('input[name="difficulty"]:checked')?.value || 'Easy';
  const flash = document.getElementById('flash-msg');
  const btn   = document.getElementById('btn-sub');
  flash.style.display = 'none';
  if (!name)  { showFlash('Please enter your name.','error'); return; }
  if (!email.includes('@')) { showFlash('Please enter a valid Gmail.','error'); return; }
  btn.disabled = true; btn.textContent = 'Subscribing…';
  const fd = new FormData();
  fd.append('name',name); fd.append('email',email); fd.append('difficulty',diff);
  try {
    const res = await fetch('/subscribe',{method:'POST',body:fd});
    const d   = await res.json();
    if (d.ok) { showFlash('All set! Taking you to your dashboard…','success'); btn.textContent='Loading…'; setTimeout(()=>location.href='/dashboard',900); }
    else { showFlash(d.error||'Something went wrong.','error'); btn.disabled=false; btn.textContent='Subscribe free →'; }
  } catch { showFlash('Network error. Try again.','error'); btn.disabled=false; btn.textContent='Subscribe free →'; }
});

function showFlash(msg,type) {
  const el=document.getElementById('flash-msg');
  el.textContent=msg; el.className='flash '+type; el.style.display='block';
}