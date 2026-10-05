(() => {
  const sticky = document.querySelector('.sticky-cta');
  const hero = document.querySelector('#hero-cta');
  const final = document.querySelector('#final-cta');
  if (sticky && hero && final && 'IntersectionObserver' in window) {
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
  }

  const params = new URLSearchParams(window.location.search);
  const source = params.has('gclid') || params.has('gbraid') || params.has('wbraid') ||
    (['google', 'googleads', 'google-ads', 'adwords'].includes((params.get('utm_source') || '').toLowerCase()) &&
      ['cpc', 'ppc', 'paidsearch', 'paid-search'].includes((params.get('utm_medium') || '').toLowerCase()))
    ? 'ads-tagged' : 'unattributed';
  const events = new Set(['page-view', 'hero', 'individual', 'familia', 'duvidas', 'academia', 'garantia', 'final', 'rodape', 'fixo']);
  const record = (event) => {
    if (!events.has(event)) return;
    const path = `/lp-events/${source}/${event}`;
    if (navigator.sendBeacon && navigator.sendBeacon(path)) return;
    if (window.fetch) fetch(path, { method: 'POST', keepalive: true, credentials: 'omit', cache: 'no-store' }).catch(() => {});
  };

  record('page-view');
  document.addEventListener('click', (event) => {
    if (!(event.target instanceof Element)) return;
    const link = event.target.closest('a[data-cta]');
    if (link) record(link.dataset.cta);
  }, { capture: true });
})();
