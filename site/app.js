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

  // O local digitado entra somente na mensagem do WhatsApp; nada é enviado a este site.
  const field = document.querySelector('.academy-field');
  const place = document.querySelector('#academia-local');
  const academyLink = document.querySelector('#academia-cta');
  if (field && place && academyLink) {
    const [base, query] = academyLink.href.split('?text=');
    const fallback = decodeURIComponent(query);
    const compose = () => {
      const value = place.value.replace(/\s+/g, ' ').trim().replace(/[.!?;,]+$/, '');
      const message = value ? `Olá! Quero consultar qual plano atende à minha academia: ${value}.` : fallback;
      academyLink.href = `${base}?text=${encodeURIComponent(message)}`;
      academyLink.dataset.cta = value ? 'consulta' : 'academia';
    };
    field.hidden = false;
    place.addEventListener('input', compose);
    place.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' || event.isComposing) return;
      event.preventDefault();
      compose();
      academyLink.click();
    });
  }

  // Celular: abrir o WhatsApp na mesma aba. Em navegadores embutidos (ex.: app do Google no iPhone),
  // links de nova aba podem não abrir o app ou deixar uma aba vazia; sem JavaScript, fica target=_blank.
  if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) {
    document.querySelectorAll('a[href^="https://wa.me/"]').forEach((link) => link.removeAttribute('target'));
  }

  // Fora do horário de resposta (seg. a sex., 10h às 20h em Brasília, UTC-3 sem horário de verão), convida a enviar mesmo assim.
  const brasilia = new Date(Date.now() - 3 * 60 * 60 * 1000);
  const weekday = brasilia.getUTCDay();
  const hour = brasilia.getUTCHours();
  if (weekday === 0 || weekday === 6 || hour < 10 || hour >= 20) {
    document.querySelectorAll('[data-hours]').forEach((node) => { node.textContent = 'Pode enviar agora. Respondemos de seg. a sex., das 10h às 20h.'; });
  }

  const params = new URLSearchParams(window.location.search);
  const source = params.has('gclid') || params.has('gbraid') || params.has('wbraid') ||
    (['google', 'googleads', 'google-ads', 'adwords'].includes((params.get('utm_source') || '').toLowerCase()) &&
      ['cpc', 'ppc', 'paidsearch', 'paid-search'].includes((params.get('utm_medium') || '').toLowerCase()))
    ? 'ads-tagged' : 'unattributed';
  const events = new Set(['page-view', 'hero', 'individual', 'familia', 'duvidas', 'academia', 'consulta', 'garantia', 'faq', 'final', 'rodape', 'fixo', 'topo']);
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
