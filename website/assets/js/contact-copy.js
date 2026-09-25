/* Keep the email link as a fallback; an ordinary click copies its address. */
(function () {
  let feedbackTimer;

  function fallbackCopy(value) {
    const field = document.createElement("textarea");
    field.value = value;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    document.body.appendChild(field);
    field.select();
    let copied = false;
    try {
      copied = document.execCommand("copy");
    } catch (_) {
      // The mailto link remains available if clipboard access is blocked.
    }
    field.remove();
    return copied;
  }

  function showFeedback(link) {
    let feedback = document.querySelector(".contact-copy-feedback");
    if (!feedback) {
      feedback = document.createElement("p");
      feedback.className = "contact-copy-feedback small text-muted";
      feedback.setAttribute("role", "status");
      feedback.setAttribute("aria-live", "polite");
      link.closest("p").insertAdjacentElement("afterend", feedback);
    }
    feedback.textContent = document.documentElement.lang === "zh-CN"
      ? "邮箱地址已复制"
      : "Email address copied";
    clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(function () { feedback.textContent = ""; }, 3000);
  }

  document.addEventListener("click", async function (event) {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = event.target instanceof Element ? event.target : event.target.parentElement;
    const link = target && target.closest(".page-intro a[href^='mailto:']");
    if (!link) return;

    event.preventDefault();
    const email = decodeURIComponent(link.getAttribute("href").slice("mailto:".length));
    let copied = false;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(email);
        copied = true;
      }
    } catch (_) {
      // Try the synchronous fallback below.
    }
    if (!copied) copied = fallbackCopy(email);
    if (copied) showFeedback(link);
    else window.location.href = link.href;
  });
})();
