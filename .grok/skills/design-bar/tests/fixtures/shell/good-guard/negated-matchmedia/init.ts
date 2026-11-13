if (!matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.dataset.theme = 'light';
}
