(() => {
  const toggle = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('#navigation');
  const year = document.querySelector('#year');

  if (year) year.textContent = String(new Date().getFullYear());

  if (!toggle || !navigation) return;

  const closeMenu = () => {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Ouvrir le menu');
    navigation.classList.remove('is-open');
  };

  toggle.addEventListener('click', () => {
    const isOpen = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!isOpen));
    toggle.setAttribute('aria-label', isOpen ? 'Ouvrir le menu' : 'Fermer le menu');
    navigation.classList.toggle('is-open', !isOpen);
  });

  navigation.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', closeMenu);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (toggle.getAttribute('aria-expanded') !== 'true') return;

    closeMenu();
    toggle.focus();
  });

  document.addEventListener('click', (event) => {
    if (!navigation.contains(event.target) && !toggle.contains(event.target)) closeMenu();
  });

  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduceMotion && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('has-reveal');
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -35px 0px' });

    document.querySelectorAll('.reveal').forEach((item) => revealObserver.observe(item));
  }

  const storySteps = document.querySelectorAll('.story-step');
  if (!reduceMotion && 'IntersectionObserver' in window && storySteps.length) {
    document.documentElement.classList.add('has-scroll-story');
    const ratios = new Map(Array.from(storySteps, (step) => [step, 0]));
    const storyObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => ratios.set(entry.target, entry.isIntersecting ? entry.intersectionRatio : 0));
      let activeStep = null;
      let highestRatio = 0;
      ratios.forEach((ratio, step) => {
        if (ratio > highestRatio) {
          highestRatio = ratio;
          activeStep = step;
        }
      });
      storySteps.forEach((step) => step.classList.toggle('is-current', step === activeStep));
    }, { threshold: [0, 0.15, 0.3, 0.45], rootMargin: '-18% 0px -18% 0px' });
    storySteps.forEach((step) => storyObserver.observe(step));
  }
})();
