// Count visits only on the official site, never in local or GitHub previews.
(() => {
  if (!['thepacelab.org', 'www.thepacelab.org'].includes(window.location.hostname)) return;
  if (document.querySelector('script[data-cf-beacon]')) return;

  const beacon = document.createElement('script');
  beacon.type = 'module';
  beacon.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  // Public Cloudflare site identifier, not an account API credential.
  beacon.setAttribute('data-cf-beacon', JSON.stringify({token: 'a78ba08f75db440f930326439852b2bf'}));
  document.body.appendChild(beacon);
})();
