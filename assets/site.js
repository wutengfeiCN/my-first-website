(function () {
  var btn = document.getElementById('modeToggle');
  if (!btn) return;

  var glyph = btn.querySelector('span');
  var meta = document.querySelector('meta[name="theme-color"]');

  function sync() {
    var night = document.documentElement.classList.contains('night');
    if (glyph) glyph.textContent = night ? '夜' : '晝'; /* 显示当前所处模式 */
    if (meta) meta.setAttribute('content', night ? '#1a1815' : '#f7f4ee');
    btn.setAttribute('aria-checked', String(night));
  }

  btn.addEventListener('click', function () {
    var night = document.documentElement.classList.toggle('night');
    try { localStorage.setItem('theme', night ? 'night' : 'day'); } catch (e) {}
    sync();
  });

  sync();
})();
