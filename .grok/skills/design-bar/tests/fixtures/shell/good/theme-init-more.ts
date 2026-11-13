window.matchMedia('(prefers-color-scheme: dark)').matches && document.documentElement.classList.add('dark');
window.matchMedia('(prefers-color-scheme: dark)').matches ? document.documentElement.classList.add('dark') : null;
if (window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.add('dark');
try {
  if (!localStorage.getItem('fam-theme')) {
    document.documentElement.dataset.theme = 'dark';
  }
} catch (e) {}
if (localStorage.getItem('fam-theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
