(() => {
  const forms = document.querySelectorAll('.lang-form');
  forms.forEach((form) => {
    const sel = form.querySelector('select');
    if (!sel) return;
    sel.addEventListener('change', () => form.submit());
  });
})();