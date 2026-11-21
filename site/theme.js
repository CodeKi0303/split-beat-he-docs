try {
  const saved = localStorage.getItem("guide-theme");
  if (saved) document.documentElement.dataset.theme = saved;
} catch {}
