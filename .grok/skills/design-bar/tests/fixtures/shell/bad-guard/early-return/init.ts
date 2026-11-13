export function initTheme() {
  if (localStorage.getItem('vc-theme')) return;
  document.documentElement.classList.add('dark');
}
