(() => {
  const sticky = document.querySelector('.sticky-cta');
  const hero = document.querySelector('#hero-cta');
  const final = document.querySelector('#final-cta');
  if (!sticky || !hero || !final || !('IntersectionObserver' in window)) return;
  let heroPassed = false;
  let finalVisible = false;
  const update = () => { sticky.hidden = !heroPassed || finalVisible; };
  new IntersectionObserver(([entry]) => {
    heroPassed = !entry.isIntersecting && entry.boundingClientRect.bottom < 0;
    update();
  }).observe(hero);
  new IntersectionObserver(([entry]) => {
    finalVisible = entry.isIntersecting || entry.boundingClientRect.bottom < 0;
    update();
  }).observe(final);
})();
