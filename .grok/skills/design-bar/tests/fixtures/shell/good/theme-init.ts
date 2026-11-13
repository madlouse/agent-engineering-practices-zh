export function initTheme() {
  const root = document.documentElement;
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) document.documentElement.classList.add('dark');
  if (localStorage.getItem('fam-theme') === 'dark') {
    document.documentElement.classList.add('dark');
  }
  return root;
}
