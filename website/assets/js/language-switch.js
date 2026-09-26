/* Both language copies are embedded during the Quarto build.
 * The inline head script selects the saved language before the first paint.
 * This controller updates the switch, title, preference, and internal links.
 */
(function () {
  const root = document.documentElement;

  function apply(language, button) {
    root.lang = language === "zh" ? "zh-CN" : "en";
    root.setAttribute("xml:lang", root.lang);
    const title = root.getAttribute("data-pace-title-" + language);
    if (title) document.title = title;
    try { window.localStorage.setItem("pace-language", language); } catch (_) {}

    const url = new URL(window.location.href);
    if (language === "zh") url.searchParams.set("lang", "zh");
    else url.searchParams.delete("lang");
    window.history.replaceState(window.history.state, "", url.pathname + url.search + url.hash);

    document.querySelectorAll("a[href]").forEach(function (link) {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || link.hasAttribute("download")) return;
      const target = new URL(href, window.location.href);
      if (target.origin !== window.location.origin ||
          !(target.pathname.endsWith("/") || target.pathname.endsWith(".html"))) return;
      target.searchParams.set("lang", language);
      link.href = target.pathname + target.search + target.hash;
    });

    const label = language === "zh" ? "切换到英文" : "Switch to Chinese";
    button.setAttribute("aria-pressed", language === "zh" ? "true" : "false");
    button.setAttribute("aria-label", label);
    button.title = label;
  }

  function initialize() {
    const button = document.querySelector(".pace-language-switch");
    if (!button) return;
    apply(root.lang === "zh-CN" ? "zh" : "en", button);
    button.addEventListener("click", function () {
      apply(root.lang === "zh-CN" ? "en" : "zh", button);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
