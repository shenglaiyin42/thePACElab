/* Draft bilingual layer for the PACE Lab website.
 * English remains in the Quarto source files. Editable Chinese copy lives in
 * assets/i18n/zh.json. Publication citations are intentionally never changed.
 */
(function () {
  const script = document.currentScript;
  const translationsUrl = new URL("../i18n/zh.json", script.src);
  const page = (window.location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "");
  const original = new Map();
  const originalTitle = document.title;
  let translations = null;
  let currentLanguage = "en";

  function savedLanguage() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (requested === "zh" || requested === "en") return requested;
    // Direct homepage visits start in English; explicit ?lang=zh still works.
    if (page === "index") return "en";
    try {
      return window.localStorage.getItem("pace-language") === "zh" ? "zh" : "en";
    } catch (_) {
      return "en";
    }
  }

  function setUrlLanguage(language) {
    const url = new URL(window.location.href);
    if (language === "zh") url.searchParams.set("lang", "zh");
    else url.searchParams.delete("lang");
    window.history.replaceState({}, "", url.pathname + url.search + url.hash);
  }

  function updateInternalLinks(language) {
    document.querySelectorAll("a[href]").forEach(function (link) {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || link.hasAttribute("download")) return;
      const url = new URL(href, window.location.href);
      if (url.origin !== window.location.origin ||
          !(url.pathname === "/" || url.pathname.endsWith(".html"))) return;
      if (language === "zh") {
        url.searchParams.set("lang", "zh");
      } else {
        url.searchParams.delete("lang");
      }
      link.href = url.pathname + url.search + url.hash;
    });
  }

  function apply(language, button) {
    const copy = (translations.pages || {})[page] || {};
    const selectors = Object.assign({}, page.startsWith("topic-") ? (translations.topicCommon || {}) : {}, copy.selectors || {});
    Object.entries(selectors).forEach(function ([selector, value]) {
      const elements = document.querySelectorAll(selector);
      if (elements.length !== 1) {
        console.warn("PACE translation selector should match once:", page, selector, elements.length);
      }
      elements.forEach(function (element) {
        if (!original.has(element)) original.set(element, element.innerHTML);
        if (language === "zh") {
          if (typeof value === "string") element.textContent = value;
          else if (value && typeof value.html === "string") element.innerHTML = value.html;
        } else {
          element.innerHTML = original.get(element);
        }
      });
    });

    document.querySelectorAll(".navbar-nav .menu-text").forEach(function (element) {
      if (!original.has(element)) original.set(element, element.innerHTML);
      const english = original.get(element).replace(/<[^>]+>/g, "").trim();
      const chinese = translations.navigation[english];
      element.textContent = language === "zh" && chinese ? chinese : english;
    });

    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    document.title = language === "zh" && copy.title ? copy.title + " | PACE Lab" : originalTitle;
    document.querySelectorAll(".topic-publication, .publications-page ol").forEach(function (element) {
      element.lang = "en";
    });
    button.setAttribute("aria-pressed", language === "zh" ? "true" : "false");
    button.setAttribute("aria-label", language === "zh" ? "切换到英文" : "Switch to Chinese");
    button.title = language === "zh" ? "切换到英文" : "Switch to Chinese";
    currentLanguage = language;
    try { window.localStorage.setItem("pace-language", language); } catch (_) {}
    setUrlLanguage(language);
    updateInternalLinks(language);
  }

  function releasePendingChinesePage() {
    document.documentElement.classList.remove("pace-zh-pending");
  }

  function cachedTranslations() {
    try {
      const cached = window.sessionStorage.getItem("pace-zh-translations");
      const copy = cached ? JSON.parse(cached) : null;
      return copy && copy.pages && copy.navigation ? copy : null;
    } catch (_) {
      return null;
    }
  }

  document.addEventListener("DOMContentLoaded", async function () {
    const nav = document.querySelector(".navbar-nav");
    if (!nav) {
      releasePendingChinesePage();
      return;
    }
    const item = document.createElement("li");
    item.className = "nav-item pace-language-item";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "pace-language-switch";
    button.textContent = "EN / 中文";
    button.disabled = true;
    item.appendChild(button);
    nav.appendChild(item);
    button.addEventListener("click", function () {
      if (translations) apply(currentLanguage === "en" ? "zh" : "en", button);
    });

    // Reuse the translation from this browser tab before the next page paints.
    const cached = cachedTranslations();
    if (cached) {
      translations = cached;
      button.disabled = false;
      apply(savedLanguage(), button);
      releasePendingChinesePage();
    }

    try {
      // Refresh in the background so manual edits to zh.json still appear.
      const response = await fetch(translationsUrl, { cache: "no-cache" });
      if (!response.ok) throw new Error("Translation file returned " + response.status);
      const fresh = await response.json();
      const serialized = JSON.stringify(fresh);
      const changed = !cached || serialized !== JSON.stringify(cached);
      translations = fresh;
      try { window.sessionStorage.setItem("pace-zh-translations", serialized); } catch (_) {}
      button.disabled = false;
      if (changed) apply(cached ? currentLanguage : savedLanguage(), button);
    } catch (error) {
      console.error("PACE language switch could not load Chinese translations:", error);
      if (!cached) button.title = "Translations unavailable";
    } finally {
      releasePendingChinesePage();
    }
  });
})();
