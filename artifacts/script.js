// Subtle micro-interactions
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s';
  });
});
