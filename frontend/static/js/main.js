'use strict';
/* ============================================================
   ДОЛООДОЙ СУРГУУЛЬ — main.js v3.0
   All frontend logic: data fetching, rendering, dark/lang
   ============================================================ */

let lang = localStorage.getItem('lang') || 'mn';
let allClasses = [], allAch = [], achByClass = {}, galleryData = [];
let newsPage = 1;

/* ── API ────────────────────────────────────────────────────── */
async function api(url) {
  try {
    const r = await fetch(url, { credentials: 'include' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) { console.error('API', url, e); return null; }
}

/* ── Dark mode ──────────────────────────────────────────────── */
function toggleDark() {
  const html = document.documentElement;
  const dark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', dark ? 'light' : 'dark');
  document.getElementById('dark-btn').textContent = dark ? '🌙' : '☀️';
  localStorage.setItem('darkMode', !dark);
}
if (localStorage.getItem('darkMode') === 'true') {
  document.documentElement.setAttribute('data-theme', 'dark');
  document.addEventListener('DOMContentLoaded', () => {
    const b = document.getElementById('dark-btn');
    if (b) b.textContent = '☀️';
  });
}

/* ── Language ───────────────────────────────────────────────── */
function toggleLang() {
  lang = lang === 'mn' ? 'en' : 'mn';
  localStorage.setItem('lang', lang);
  document.getElementById('lang-btn').textContent = lang === 'mn' ? 'EN' : 'МН';
  applyLang();
}
function applyLang() {
  document.querySelectorAll('[data-mn]').forEach(el => {
    el.textContent = lang === 'mn' ? el.dataset.mn : (el.dataset.en || el.dataset.mn);
  });
}

/* ── Utils ──────────────────────────────────────────────────── */
function fmtDate(d) {
  if (!d) return '';
  return new Date(d).toLocaleDateString('mn-MN', { year:'numeric', month:'long', day:'numeric' });
}
function closeOv(id) { document.getElementById(id).classList.remove('open'); }
function closeLB()   { document.getElementById('lb').classList.remove('open'); }
function openLB(src) {
  document.getElementById('lb-img').src = src;
  document.getElementById('lb').classList.add('open');
}

const DEG  = { bachelor:'Бакалавр', master:'Магистр', doctorate:'Доктор', other:'Бусад' };
const DEGE = { bachelor:'Bachelor', master:'Master',  doctorate:'PhD',    other:'Other'  };
const LVL  = { school:'Сургуулийн', district:'Дүүргийн', city:'Хотын', national:'Улсын', international:'Олон улсын' };
const LVLE = { school:'School', district:'District', city:'City', national:'National', international:'International' };

/* ── Scroll fade-in ─────────────────────────────────────────── */
function initFade() {
  const obs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  }), { threshold: 0.08 });
  document.querySelectorAll('.fade-in').forEach(el => obs.observe(el));
  setTimeout(() => document.querySelector('.hero .fade-in')?.classList.add('visible'), 80);
}

/* ── SCHOOL ─────────────────────────────────────────────────── */
async function loadSchool() {
  const d = await api('/api/school');
  if (!d?.full_name) return;
  document.getElementById('nav-name').textContent     = d.full_name;
  document.getElementById('about-name').textContent   = d.full_name;
  document.getElementById('ft-brand').textContent     = d.full_name;
  document.getElementById('ft-copy').textContent      = `© ${new Date().getFullYear()} ${d.full_name}`;
  document.getElementById('ft-sub').textContent       = `${d.district || 'Дорнод аймаг'} · Хэрлэн сум`;
  if (d.founded_date) document.getElementById('founded-yr').textContent = d.founded_date.substring(0,4);
  if (d.mission)   document.getElementById('about-mission').textContent = d.mission;
  if (d.vision)    document.getElementById('about-vision').textContent  = d.vision;
  if (d.values_text) document.getElementById('about-values').textContent = d.values_text;
  if (d.phone)   { document.getElementById('ic-phone').textContent  = d.phone;  document.getElementById('ci-phone').textContent  = d.phone;  }
  if (d.email)   { document.getElementById('ic-email').textContent  = d.email;  document.getElementById('ci-email').textContent  = d.email;  }
  if (d.district) document.getElementById('ic-district').textContent = d.district;
  if (d.street || d.building) {
    const addr = `${d.street||''} ${d.building||''}`.trim();
    document.getElementById('ic-address').textContent = addr;
    document.getElementById('ci-addr').textContent    = `${d.district||''}, ${addr}`;
  }
  if (d.facebook_url) {
    const w = document.getElementById('ci-fb'), a = document.getElementById('ci-fblink');
    w.style.display = 'flex'; a.textContent = d.facebook_url; a.href = d.facebook_url;
  }
  if (d.logo_path) {
    document.getElementById('nav-logo').innerHTML = `<img src="${d.logo_path}" alt="logo"/>`;
  }
  loadSchoolPhoto();
}

async function loadSchoolPhoto() {
  const photos = await api('/api/school-photos');
  if (!photos?.length) return;
  const el = document.getElementById('about-img');
  el.innerHTML = `<img src="${photos[0].photo_path}" alt="${photos[0].caption||'Сургуулийн зураг'}"/>`;
}

/* ── STATS ──────────────────────────────────────────────────── */
async function loadStats() {
  const [t, c, a] = await Promise.all([api('/api/teachers'), api('/api/classes'), api('/api/achievements')]);
  if (t) document.getElementById('hs-t').textContent = t.length;
  if (c) document.getElementById('hs-c').textContent = c.length;
  if (a) document.getElementById('hs-a').textContent = a.length;
}

/* ── DIRECTOR ───────────────────────────────────────────────── */
async function loadDirector() {
  const d = await api('/api/director');
  if (!d?.full_name) return;
  document.getElementById('dir-name').textContent  = d.full_name;
  if (d.greeting_text) document.getElementById('dir-quote').textContent = `"${d.greeting_text}"`;
  if (d.biography)     document.getElementById('dir-bio').textContent   = d.biography;
  if (d.photo_path)
    document.getElementById('dir-photo').innerHTML =
      `<img src="${d.photo_path}" class="dir-ph" style="object-fit:cover" alt="${d.full_name}"/>`;
}

/* ── TEACHERS ───────────────────────────────────────────────── */
async function loadTeachers() {
  const data = await api('/api/teachers');
  const g = document.getElementById('t-grid');
  if (!data?.length) { g.innerHTML = empty('👩‍🏫'); return; }
  g.innerHTML = data.map(t => `
    <div class="t-card">
      ${t.photo_path ? `<img src="${t.photo_path}" class="t-photo" alt="${t.full_name}"/>`
                     : `<div class="t-ph">👤</div>`}
      <div class="t-info">
        <div class="t-name">${t.full_name}</div>
        <div class="t-subj">${t.subject}</div>
        <div class="t-badges">
          <span class="bdg b-deg">${lang==='mn'?DEG[t.degree]:DEGE[t.degree]||t.degree}</span>
          <span class="bdg b-exp">${t.experience_years}+ жил</span>
        </div>
      </div>
    </div>`).join('');
}

/* ── CLASSES ────────────────────────────────────────────────── */
async function loadClasses() {
  [allClasses, achByClass] = await Promise.all([
    api('/api/classes'), api('/api/achievements/by-class')
  ]);
  allClasses   = allClasses   || [];
  achByClass   = achByClass   || {};
  buildGradeTabs();
  renderClasses('all');
}

function buildGradeTabs() {
  const grades = [...new Set(allClasses.map(c => c.grade))].sort((a,b) => a-b);
  document.getElementById('gtabs').innerHTML =
    `<button class="gtab active" onclick="filterGrade('all',this)">${lang==='mn'?'Бүгд':'All'}</button>` +
    grades.map(g => `<button class="gtab" onclick="filterGrade(${g},this)">${g}-р анги</button>`).join('');
}

function filterGrade(grade, btn) {
  document.querySelectorAll('.gtab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderClasses(grade);
}

function renderClasses(grade) {
  const rows = grade === 'all' ? allClasses : allClasses.filter(c => c.grade === +grade);
  const tbody = document.getElementById('cls-tbody');
  if (!rows.length) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:32px">${lang==='mn'?'Мэдээлэл байхгүй':'No data'}</td></tr>`; return; }
  tbody.innerHTML = rows.map(c => {
    const key = `${c.grade}-${c.section}`;
    const top = (achByClass[key] || [])[0];
    const achHtml = top
      ? `<span class="ach-tag">${top.place_number?top.place_number+'🥇 ':''}${top.competition} — ${top.student_name}</span>`
      : `<span style="color:var(--muted);font-size:.78rem">—</span>`;
    return `<tr>
      <td><strong>${c.grade}</strong>-р анги</td>
      <td>${c.section} бүлэг</td>
      <td>${c.teacher_name||'—'}</td>
      <td>${c.academic_year}</td>
      <td>${achHtml}</td>
    </tr>`;
  }).join('');
}

/* ── NEWS ───────────────────────────────────────────────────── */
async function loadNews(page = 1) {
  newsPage = page;
  const data = await api(`/api/news?page=${page}&per_page=9`);
  const g = document.getElementById('n-grid');
  if (!data?.items?.length) { g.innerHTML = empty('📰'); document.getElementById('n-pager').innerHTML=''; return; }
  g.innerHTML = data.items.map(n => `
    <div class="n-card" onclick="openNews(${n.id})">
      ${n.photo_path ? `<img src="${n.photo_path}" class="n-img" alt="${n.title}"/>` : `<div class="n-ph">📰</div>`}
      <div class="n-body">
        <div class="n-date">${fmtDate(n.news_date)}</div>
        <div class="n-title">${n.title}</div>
        <div class="n-exc">${n.content}</div>
        <div class="n-more">${lang==='mn'?'Дэлгэрэнгүй':'Read more'} →</div>
      </div>
    </div>`).join('');
  const pages = data.pages || 1;
  document.getElementById('n-pager').innerHTML = pages > 1
    ? Array.from({length:pages},(_,i)=>i+1).map(i =>
        `<button class="pager-btn ${i===page?'active':''}" onclick="loadNews(${i})">${i}</button>`).join('')
    : '';
}

async function openNews(id) {
  const n = await api(`/api/news/${id}`);
  if (!n) return;
  document.getElementById('m-title').textContent   = n.title;
  document.getElementById('m-date').textContent    = fmtDate(n.news_date);
  document.getElementById('m-body').textContent    = n.content;
  const img = document.getElementById('m-img');
  if (n.photo_path) { img.src = n.photo_path; img.style.display = 'block'; }
  else img.style.display = 'none';
  document.getElementById('news-ov').classList.add('open');
}

/* ── ACHIEVEMENTS ───────────────────────────────────────────── */
async function loadAchievements() {
  allAch = await api('/api/achievements') || [];
  const years = await api('/api/achievements/years') || [];
  const levels = [...new Set(allAch.map(a => a.level))];
  document.getElementById('ach-filter').innerHTML =
    `<button class="fbtn active" onclick="filterAch('all',this)">${lang==='mn'?'Бүгд':'All'}</button>` +
    levels.map(l => `<button class="fbtn" onclick="filterAch('${l}',this)">${lang==='mn'?LVL[l]:LVLE[l]||l}</button>`).join('');
  renderAch('all');
  const sel = document.getElementById('lb-year');
  years.forEach(y => { const o = document.createElement('option'); o.value=y; o.textContent=y; sel.appendChild(o); });
}

function filterAch(level, btn) {
  document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderAch(level);
}

function renderAch(level) {
  const data = level==='all' ? allAch : allAch.filter(a => a.level===level);
  const g = document.getElementById('ag-grid');
  if (!data.length) { g.innerHTML = empty('🏆'); return; }
  g.innerHTML = data.map(a => {
    const pc = a.place_number===1?'pl-1':a.place_number===2?'pl-2':a.place_number===3?'pl-3':'pl-x';
    const ct = (a.class_grade&&a.class_section)
      ? `<span class="cls-tag">${a.class_grade}-р анги ${a.class_section}</span>` : '';
    return `<div class="ag-card">
      <div class="ag-place ${pc}">${a.place_number||'—'}</div>
      <div class="ag-lvl">${lang==='mn'?LVL[a.level]:LVLE[a.level]||a.level} · ${a.achieved_year}</div>
      <div class="ag-comp">${a.competition}</div>
      <div class="ag-stu">👤 ${a.student_name} ${ct}</div>
      <span class="ag-award">🏅 ${a.award}</span>
    </div>`;
  }).join('');
}

/* ── LEADERBOARD ────────────────────────────────────────────── */
async function loadLeaderboard() {
  const yr  = document.getElementById('lb-year').value;
  const url = yr ? `/api/achievements/leaderboard?year=${yr}` : '/api/achievements/leaderboard';
  const data = await api(url) || [];
  const g = document.getElementById('lb-body');
  if (!data.length) { g.innerHTML = empty('🏆'); return; }
  const ri = i => i===0?'🥇':i===1?'🥈':i===2?'🥉':`${i+1}`;
  const rc = i => i===0?'r1':i===1?'r2':i===2?'r3':'';
  g.innerHTML = `<div class="lb-wrap"><table class="lb-tbl">
    <thead><tr>
      <th>#</th>
      <th data-mn="Сурагч" data-en="Student">Сурагч</th>
      <th data-mn="Анги" data-en="Class">Анги</th>
      <th data-mn="Нийт" data-en="Total">Нийт</th>
      <th data-mn="Медаль" data-en="Medals">Медаль</th>
    </tr></thead>
    <tbody>
      ${data.map((r,i) => `<tr>
        <td><span class="lb-rank ${rc(i)}">${ri(i)}</span></td>
        <td><strong>${r.student_name}</strong></td>
        <td>${r.class_grade&&r.class_section?`${r.class_grade}${r.class_section}`:'—'}</td>
        <td><strong>${r.total}</strong></td>
        <td>
          ${r.gold   ? `<span class="medal mg">🥇${r.gold}</span>`   : ''}
          ${r.silver ? `<span class="medal ms">🥈${r.silver}</span>` : ''}
          ${r.bronze ? `<span class="medal mb_">🥉${r.bronze}</span>` : ''}
        </td>
      </tr>`).join('')}
    </tbody>
  </table></div>`;
}

/* ── ANNOUNCEMENTS ──────────────────────────────────────────── */
async function loadAnnouncements() {
  const data = await api('/api/announcements') || [];
  const list = document.getElementById('ann-list');
  if (!data.length) { list.innerHTML = empty('📢'); return; }
  list.innerHTML = data.map(a => `
    <div class="ann-card">
      <div class="ann-top">
        <div class="ann-title">${a.title}</div>
        <div class="ann-date">${fmtDate(a.published_date)}</div>
      </div>
      <div class="ann-body">${a.content}</div>
      ${a.expires_date ? `<div class="ann-exp">⏰ ${fmtDate(a.expires_date)} хүртэл</div>` : ''}
    </div>`).join('');
}

/* ── GALLERY ────────────────────────────────────────────────── */
async function loadGallery() {
  galleryData = await api('/api/gallery') || [];
  const tabs = document.getElementById('atabs');
  if (!galleryData.length) { document.getElementById('gal-grid').innerHTML = empty('🖼️'); return; }
  tabs.innerHTML = galleryData.map((a,i) =>
    `<button class="atab ${i===0?'active':''}" onclick="showAlbum(${a.id},this)">${a.name}</button>`
  ).join('');
  showAlbum(galleryData[0].id, tabs.firstChild);
}

function showAlbum(id, btn) {
  document.querySelectorAll('.atab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const album = galleryData.find(a => a.id === id);
  const g = document.getElementById('gal-grid');
  if (!album?.photos?.length) { g.innerHTML = empty('📷'); return; }
  g.innerHTML = album.photos.map(p => `
    <div class="gal-item" onclick="openLB('${p.photo_path}')">
      <img src="${p.photo_path}" alt="${p.caption||''}" loading="lazy"/>
      <div class="gal-ov">🔍</div>
    </div>`).join('');
}

/* ── GRADUATES ──────────────────────────────────────────────── */
async function loadGraduates() {
  const data = await api('/api/graduates') || [];
  const g = document.getElementById('grad-grid');
  if (!data.length) { g.innerHTML = empty('👨‍🎓'); return; }
  g.innerHTML = data.map(r => `
    <div class="grad-card">
      <div class="grad-name">${r.full_name}</div>
      <div class="grad-yr">${r.graduated_year} ${lang==='mn'?'оны төгсөгч':'Graduate'}</div>
      ${r.current_place ? `<div class="grad-place">📍 ${r.current_place}</div>` : ''}
      ${r.message ? `<div class="grad-msg">"${r.message}"</div>` : ''}
    </div>`).join('');
}

async function submitGrad() {
  const name  = document.getElementById('g-name').value.trim();
  const year  = document.getElementById('g-year').value;
  const place = document.getElementById('g-place').value.trim();
  const msg   = document.getElementById('g-msg').value.trim();
  const msgEl = document.getElementById('grad-msg');
  if (!name || !year) {
    showGradMsg(lang==='mn'?'Нэр болон онг заавал оруулна уу.':'Name and year are required.', false);
    return;
  }
  try {
    const res = await fetch('/api/graduates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name:name, graduated_year:+year, current_place:place, message:msg })
    });
    const d = await res.json();
    if (res.ok) {
      showGradMsg(lang==='mn'?d.message||'Илгээгдлээ!':'Submitted! Pending admin approval.', true);
      ['g-name','g-year','g-place','g-msg'].forEach(id => document.getElementById(id).value='');
    } else {
      showGradMsg(d.error || 'Error', false);
    }
  } catch { showGradMsg(lang==='mn'?'Холбогдох боломжгүй.':'Could not connect.', false); }
}

function showGradMsg(text, ok) {
  const el = document.getElementById('grad-msg');
  el.textContent   = text;
  el.style.cssText = `display:block;padding:10px;border-radius:8px;margin-bottom:12px;font-size:.88rem;
    background:${ok?'rgba(56,161,105,.12)':'rgba(229,62,62,.1)'};
    color:${ok?'#276749':'#c53030'};
    border:1px solid ${ok?'rgba(56,161,105,.3)':'rgba(229,62,62,.25)'}`;
}

/* ── FAQ ────────────────────────────────────────────────────── */
async function loadFAQ() {
  const data = await api('/api/faq') || [];
  const list = document.getElementById('faq-list');
  if (!data.length) { list.innerHTML = empty('❓'); return; }
  list.innerHTML = data.map((f,i) => `
    <div class="faq-item" id="fq-${i}">
      <div class="faq-q" onclick="toggleFAQ(${i})">
        <span>${lang==='mn'?f.question:(f.question_en||f.question)}</span>
        <span class="faq-arr">▼</span>
      </div>
      <div class="faq-a">${lang==='mn'?f.answer:(f.answer_en||f.answer)}</div>
    </div>`).join('');
}

function toggleFAQ(i) {
  const item = document.getElementById('fq-'+i);
  const was  = item.classList.contains('open');
  document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('open'));
  if (!was) item.classList.add('open');
}

/* ── Helpers ────────────────────────────────────────────────── */
function empty(icon) {
  return `<div class="empty"><div class="ei">${icon}</div><p>${lang==='mn'?'Мэдээлэл байхгүй':'No data available'}</p></div>`;
}

/* ── INIT ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (lang === 'en') { document.getElementById('lang-btn').textContent = 'МН'; applyLang(); }
  loadSchool();
  loadStats();
  loadDirector();
  loadTeachers();
  loadClasses();
  loadNews();
  loadAchievements();
  loadLeaderboard();
  loadAnnouncements();
  loadGallery();
  loadGraduates();
  loadFAQ();
  initFade();
});
