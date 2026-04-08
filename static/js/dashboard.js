// ── State ─────────────────────────────────────────────────────
let currentType = null;
let currentLang = 'python';
let hintIdx     = 0;
let solVisible  = false;

const DEFAULT_CODE = {
  python:     '# Write your Python solution here\n\n',
  javascript: '// Write your JavaScript solution here\n\n',
  java:       '// Write your Java solution here\nclass Solution {\n    \n}\n',
  sql:        '-- Write your SQL query here\n\n',
};

// ── Tab switching ─────────────────────────────────────────────
function showTab(name, btn) {
  ['today','history','awards'].forEach(t =>
    document.getElementById('tab-'+t).style.display = t === name ? '' : 'none'
  );
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  if (btn) btn.classList.add('active');
}

// ── Open solver modal ─────────────────────────────────────────
async function openSolver(type) {
  currentType = type;
  hintIdx     = 0;
  solVisible  = false;

  // Track open time for Speed Solver award
  try {
    await fetch('/open-problem', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type}),
    });
  } catch(_) {}

  const q       = QUESTIONS[type];
  const isDone  = PROGRESS[type + '_done'];
  const saved   = PROGRESS[type + '_code'];
  const savedLang = PROGRESS[type + '_lang'] || (type === 'sql' ? 'sql' : 'python');

  document.getElementById('modal-cat').textContent   = {dsa:'DSA / Algorithm', js:'JavaScript', sql:'SQL'}[type];
  document.getElementById('modal-title').textContent = q.title;

  const diffEl = document.getElementById('modal-diff');
  diffEl.textContent = q.difficulty;
  diffEl.className = 'diff-chip ' + q.difficulty.toLowerCase();

  document.getElementById('modal-desc').innerHTML = q.description || '';

  // Test cases
  const tests = q.test_cases || [];
  document.getElementById('modal-tests').innerHTML = tests.map(t =>
    `<div class="test-case"><span class="test-in">Input: ${t.input}</span> → <span class="test-out">Expected: ${t.expected}</span></div>`
  ).join('');

  // Reset hints & solution
  const hintBox = document.getElementById('hint-box');
  hintBox.style.display = 'none'; hintBox.textContent = '';
  const btnHint = document.getElementById('btn-hint');
  btnHint.disabled = false;
  btnHint.textContent = '💡 Get hint (1/' + (q.hints || []).length + ')';
  document.getElementById('solution-box').style.display = 'none';
  solVisible = false;

  // Show/hide LC submit button
  const lcSec = document.getElementById('lc-submit-section');
  if (lcSec) lcSec.style.display = (LC_USERNAME && LC_HAS_SESSION) ? 'block' : 'none';
  const lcMsg = document.getElementById('lc-submit-msg');
  if (lcMsg) lcMsg.style.display = 'none';
  const lcBtn = document.getElementById('btn-lc-submit');
  if (lcBtn) { lcBtn.disabled = false; lcBtn.textContent = '🚀 Also submit on LeetCode'; }

  // Set language
  setLang(type === 'sql' ? 'sql' : savedLang, null, true);

  // Load code
  const editor = document.getElementById('code-editor');
  editor.value = (saved && saved.trim()) ? saved : DEFAULT_CODE[currentLang] || '';

  // Submit button state
  const note    = document.getElementById('submit-note');
  const subBtn  = document.getElementById('btn-submit');
  if (isDone) {
    note.innerHTML = '<span class="submit-success">✓ Already solved! You can still edit & resubmit.</span>';
    subBtn.textContent = '▶ Resubmit';
  } else {
    note.textContent = 'Write your solution above, then click Submit.';
    subBtn.textContent = '▶ Submit solution';
  }
  subBtn.disabled = false;

  document.getElementById('solve-modal').style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('solve-modal').style.display = 'none';
  document.body.style.overflow = '';
}
document.getElementById('solve-modal').addEventListener('click', e => {
  if (e.target.id === 'solve-modal') closeModal();
});

// ── Language switching ────────────────────────────────────────
function setLang(lang, btn, silent) {
  currentLang = lang;
  const langs = ['python','javascript','java','sql'];
  document.querySelectorAll('#editor-lang-tabs .lang-tab').forEach((t, i) =>
    t.classList.toggle('active', langs[i] === lang)
  );
  if (!silent) {
    const editor = document.getElementById('code-editor');
    if (!editor.value.trim() || Object.values(DEFAULT_CODE).includes(editor.value))
      editor.value = DEFAULT_CODE[lang] || '';
  }
}

// ── Hint ──────────────────────────────────────────────────────
function getNextHint() {
  const q = QUESTIONS[currentType];
  const hints = q.hints || [];
  if (hintIdx >= hints.length) return;
  const hintBox = document.getElementById('hint-box');
  hintBox.innerHTML = `<strong>Hint ${hintIdx+1}/${hints.length}:</strong> ${hints[hintIdx]}`;
  hintBox.style.display = 'block';
  hintIdx++;
  const btn = document.getElementById('btn-hint');
  if (hintIdx >= hints.length) { btn.disabled = true; btn.textContent = 'No more hints'; }
  else btn.textContent = `💡 Next hint (${hintIdx+1}/${hints.length})`;
}

// ── Solution ──────────────────────────────────────────────────
function toggleSolution() {
  const box = document.getElementById('solution-box');
  solVisible = !solVisible;
  box.style.display = solVisible ? 'block' : 'none';
  if (solVisible) showSolLang('python', null);
}
function showSolLang(lang, btn) {
  const q = QUESTIONS[currentType];
  const sol = (q.solutions || {})[lang] || (q.solutions || {}).python || '-- No solution';
  document.getElementById('solution-code').textContent = sol;
  document.querySelectorAll('#sol-lang-tabs .lang-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  else {
    const langs = ['python','javascript','java','sql'];
    document.querySelectorAll('#sol-lang-tabs .lang-tab').forEach((t,i) => {
      if (langs[i] === lang) t.classList.add('active');
    });
  }
}

// ── Submit code to CodeDaily ──────────────────────────────────
async function submitCode() {
  const code   = document.getElementById('code-editor').value.trim();
  const btn    = document.getElementById('btn-submit');
  const note   = document.getElementById('submit-note');

  if (!code || code === DEFAULT_CODE[currentLang].trim()) {
    note.innerHTML = '<span class="submit-error">⚠ Please write your solution first.</span>'; return;
  }
  btn.disabled = true; btn.textContent = '⏳ Submitting…';
  note.textContent = 'Saving your solution…';

  try {
    const res  = await fetch('/solve', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type: currentType, code, lang: currentLang}),
    });
    const data = await res.json();
    if (data.ok) {
      markCardSolved(currentType);
      updateProgressUI(data.count, data.streak);
      showNewAwards(data.new_awards);
      note.innerHTML = '<span class="submit-success">✅ Saved! Problem marked as solved.</span>';
      btn.textContent = '▶ Resubmit'; btn.disabled = false;
      PROGRESS[currentType+'_done'] = true;
      PROGRESS[currentType+'_code'] = code;
      PROGRESS[currentType+'_lang'] = currentLang;
      if (data.all_done) setTimeout(() => { closeModal(); launchConfetti(); }, 800);
    } else {
      note.innerHTML = `<span class="submit-error">Error: ${data.error}</span>`;
      btn.disabled = false; btn.textContent = '▶ Submit solution';
    }
  } catch {
    note.innerHTML = '<span class="submit-error">Network error. Try again.</span>';
    btn.disabled = false; btn.textContent = '▶ Submit solution';
  }
}

// ── Submit TO LeetCode ────────────────────────────────────────
async function submitToLeetCode() {
  const code = document.getElementById('code-editor').value.trim();
  const btn  = document.getElementById('btn-lc-submit');
  const msg  = document.getElementById('lc-submit-msg');
  if (!code) { showLCSubmitMsg('Write your solution first.', 'error'); return; }

  btn.disabled = true; btn.textContent = '⏳ Submitting to LeetCode…';
  msg.style.display = 'none';

  const q = QUESTIONS[currentType];
  try {
    const res  = await fetch('/submit-to-leetcode', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        type: currentType, code, lang: currentLang,
        slug: q.slug, question_id: q.id,
      }),
    });
    const data = await res.json();
    if (data.ok) {
      showLCSubmitMsg(
        `✅ Submitted! <a href="${data.lc_url}" target="_blank" style="color:var(--blue)">View on LeetCode →</a>`,
        'success'
      );
    } else if (data.need_session) {
      showLCSubmitMsg('Session expired. <button onclick="openLCModal()" style="background:none;border:none;color:var(--blue);cursor:pointer;text-decoration:underline;font-size:12px">Re-link account →</button>', 'warn');
    } else {
      showLCSubmitMsg(data.error || 'Submission failed.', 'error');
    }
  } catch {
    showLCSubmitMsg('Network error. Try again.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = '🚀 Also submit on LeetCode';
  }
}

function showLCSubmitMsg(html, type) {
  const msg = document.getElementById('lc-submit-msg');
  if (!msg) return;
  msg.innerHTML = html;
  const colors = {success: 'var(--green)', error: 'var(--red)', warn: 'var(--amber)'};
  msg.style.cssText = `display:block;font-size:12px;margin-top:6px;color:${colors[type]||'var(--muted)'}`;
}

// ── Card & progress UI update ─────────────────────────────────
function markCardSolved(type) {
  const card = document.getElementById('card-'+type);
  if (!card) return;
  card.classList.add('solved');
  const btn = card.querySelector('.btn-solve');
  if (btn) { btn.textContent = '👁 Review / Edit'; btn.classList.replace('btn-solve','btn-review'); }
  const top = card.querySelector('.q-card-top');
  if (top && !top.querySelector('.solved-badge')) {
    const badge = document.createElement('div');
    badge.className = 'solved-badge'; badge.textContent = '✓ Solved'; top.appendChild(badge);
  }
  updateProgressDots();
}
function updateProgressDots() {
  const dots  = document.querySelectorAll('.pdot');
  const types = ['dsa','js','sql'];
  dots.forEach((dot, i) => { if (PROGRESS[types[i]+'_done']) dot.classList.add('done'); });
}
function updateProgressUI(count, streak) {
  document.getElementById('prog-fill').style.width = Math.round(count/3*100) + '%';
  document.getElementById('prog-text').textContent = count + '/3 solved';
  const ss = document.getElementById('stat-streak'); if (ss) ss.textContent = streak;
  const sv = document.getElementById('streak-val');  if (sv) sv.textContent = streak;
  updateProgressDots();
  if (count === 3 && !document.querySelector('.done-banner')) {
    const b = document.createElement('div'); b.className = 'done-banner';
    b.textContent = '🎉 All 3 problems solved today! You\'re on fire. Come back tomorrow!';
    document.querySelector('.tabs').insertAdjacentElement('beforebegin', b);
  }
}

// ── Difficulty modal ──────────────────────────────────────────
function openDiffModal()  { document.getElementById('diff-modal').style.display = 'flex'; }
function closeDiffModal() { document.getElementById('diff-modal').style.display = 'none'; }
async function saveDiff() {
  const diff = document.querySelector('input[name="pdiff"]:checked')?.value || 'Easy';
  const msg  = document.getElementById('pdiff-msg'); msg.style.display = 'none';
  try {
    const res  = await fetch('/update-profile', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({difficulty:diff})});
    const data = await res.json();
    if (data.ok) { msg.textContent='Saved! Reloading…'; msg.className='flash success'; msg.style.display='block'; setTimeout(()=>location.reload(),900); }
    else { msg.textContent=data.error||'Error'; msg.className='flash error'; msg.style.display='block'; }
  } catch { msg.textContent='Network error.'; msg.className='flash error'; msg.style.display='block'; }
}

// ── LeetCode modal ────────────────────────────────────────────
function openLCModal()  { document.getElementById('lc-modal').style.display='flex'; document.body.style.overflow='hidden'; }
function closeLCModal() { document.getElementById('lc-modal').style.display='none'; document.body.style.overflow=''; }

function showLCMsg(txt, type) {
  const msg = document.getElementById('lc-msg'); if (!msg) return;
  msg.textContent = txt;
  const styles = {success:'var(--green)',error:'var(--red)',warn:'var(--amber)','':`var(--muted)`};
  msg.style.cssText = `display:block;padding:10px 14px;border-radius:var(--rs);font-size:13px;color:${styles[type]||styles['']}`;
  if (type==='success') msg.style.background='var(--green-dim)';
  if (type==='error')   msg.style.background='var(--red-dim)';
}

async function saveLCUsername() {
  const usernameInp = document.getElementById('lc-username-inp');
  const sessionInp  = document.getElementById('lc-session-inp');
  const username    = usernameInp ? usernameInp.value.trim() : '';
  const lc_session  = sessionInp  ? sessionInp.value.trim()  : '';

  // If already linked, only session update is needed
  if (!username && !lc_session) { showLCMsg('Enter a username or session cookie.', 'error'); return; }
  if (!username && !LC_USERNAME) { showLCMsg('Enter your LeetCode username.', 'error'); return; }

  const finalUsername = username || LC_USERNAME;
  showLCMsg('Verifying…', '');

  try {
    const res  = await fetch('/link-leetcode', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username: finalUsername, lc_session}),
    });
    const data = await res.json();
    if (data.ok) {
      showLCMsg(
        `✅ Linked${data.has_session ? ' with session cookie' : ''}! Reloading…`,
        'success'
      );
      showNewAwards(data.new_awards || []);
      setTimeout(() => location.reload(), 1200);
    } else {
      showLCMsg(data.error || 'Error linking account.', 'error');
    }
  } catch { showLCMsg('Network error. Try again.', 'error'); }
}

async function unlinkLC() {
  if (!confirm('Unlink your LeetCode account? This will remove your session cookie too.')) return;
  await fetch('/unlink-leetcode', {method:'POST'});
  location.reload();
}

// ── LC Sync ───────────────────────────────────────────────────
async function syncLC() {
  const btnNav    = document.getElementById('btn-lc-sync');
  const btnBanner = document.getElementById('btn-lc-sync-banner');
  const msgEl     = document.getElementById('lc-sync-msg');
  [btnNav, btnBanner].forEach(b => { if (b) { b.disabled=true; b.textContent='⟳ Syncing…'; }});

  try {
    const res  = await fetch('/sync-leetcode', {method:'POST', headers:{'Content-Type':'application/json'}});
    const data = await res.json();
    if (data.ok) {
      if (msgEl) {
        msgEl.textContent = data.message;
        msgEl.style.cssText = `display:block;padding:10px 14px;border-radius:var(--rs);font-size:13px;
          color:${data.synced.length?'var(--green)':'var(--muted)'};
          background:${data.synced.length?'var(--green-dim)':'var(--bg3)'};margin-bottom:.75rem`;
        setTimeout(() => { msgEl.style.display='none'; }, 5000);
      }
      if (data.synced.length) {
        data.synced.forEach(t => { PROGRESS[t+'_done']=true; markCardSolved(t); });
        updateProgressUI(data.count, data.streak);
        showNewAwards(data.new_awards || []);
        if (data.all_done) setTimeout(() => launchConfetti(), 400);
      }
    } else {
      if (msgEl) { msgEl.textContent=data.error||'Sync failed.'; msgEl.style.cssText='display:block;padding:10px 14px;border-radius:var(--rs);font-size:13px;color:var(--red);background:var(--red-dim);margin-bottom:.75rem'; }
    }
  } catch {
    if (msgEl) { msgEl.textContent='Network error.'; msgEl.style.display='block'; }
  } finally {
    if (btnNav)    { btnNav.disabled=false;    btnNav.textContent='⟳ LC Sync'; }
    if (btnBanner) { btnBanner.disabled=false; btnBanner.textContent='⟳ Sync now'; }
  }
}

// ── Awards toast ──────────────────────────────────────────────
function showNewAwards(awards) {
  if (!awards || !awards.length) return;
  let i = 0;
  const toast = document.getElementById('award-toast');
  function show() {
    if (i >= awards.length) return;
    const aw = awards[i++];
    document.getElementById('toast-icon').textContent = aw.icon;
    document.getElementById('toast-name').textContent = aw.name + ' — ' + aw.desc;
    toast.style.display = 'flex';
    setTimeout(() => { toast.style.display='none'; setTimeout(show, 400); }, 3000);
  }
  show();
}

// ── Confetti ──────────────────────────────────────────────────
function launchConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  canvas.style.display = 'block';
  const ctx = canvas.getContext('2d');
  canvas.width = innerWidth; canvas.height = innerHeight;
  const colors = ['#22d08c','#f5a524','#a78bfa','#f25555','#4f9cf9'];
  const pieces = Array.from({length:120}, () => ({
    x: Math.random()*canvas.width, y: Math.random()*-150,
    r: Math.random()*7+4, color: colors[Math.floor(Math.random()*colors.length)],
    tA:0, tS:Math.random()*.1+.05, speed:Math.random()*4+2, rot:Math.random()*360, rotS:Math.random()*6-3,
  }));
  let frame = 0;
  function draw() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    pieces.forEach(p => {
      p.y+=p.speed; p.tA+=p.tS; p.rot+=p.rotS;
      const tilt = Math.sin(p.tA)*12;
      ctx.save(); ctx.translate(p.x+tilt,p.y); ctx.rotate(p.rot*Math.PI/180);
      ctx.fillStyle=p.color; ctx.fillRect(-p.r/2,-p.r/2,p.r,p.r*1.6); ctx.restore();
    });
    if (++frame < 220) requestAnimationFrame(draw);
    else { canvas.style.display='none'; ctx.clearRect(0,0,canvas.width,canvas.height); }
  }
  draw();
}

// Init
updateProgressDots();