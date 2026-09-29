/* First-party sharing controls. Never posts on a visitor's behalf. */
(function () {
  function initialize() {
    const share = document.querySelector(".pace-share");
    const dialog = document.querySelector(".pace-share-dialog");
    if (!share || !dialog) return;

    const language = () => document.documentElement.lang === "zh-CN" ? "zh" : "en";
    const link = () => share.dataset.shareUrl + "?lang=" + language();
    const title = () => share.dataset[language() === "zh" ? "shareTitleZh" : "shareTitleEn"];
    const status = share.querySelector(".pace-share-menu-status");

    function refreshPlatformLinks() {
      const message = title() + " " + link();
      share.querySelector(".pace-share-x").href =
        "https://x.com/intent/tweet?text=" + encodeURIComponent(title()) +
        "&url=" + encodeURIComponent(link());
      share.querySelector(".pace-share-bluesky").href =
        "https://bsky.app/intent/compose?text=" + encodeURIComponent(message);
      const poster = dialog.querySelector(".pace-share-poster-download");
      if (poster) {
        poster.href = poster.dataset[language() === "zh" ? "posterZh" : "posterEn"];
        poster.download = "PACE-Lab-" + new URL(poster.href, window.location.href).pathname
          .split("/").pop();
      }
    }

    async function copyLink(output) {
      const value = link();
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(value);
        } else {
          const field = document.createElement("textarea");
          field.value = value;
          field.style.position = "fixed";
          field.style.opacity = "0";
          document.body.append(field);
          field.select();
          if (!document.execCommand("copy")) throw new Error("Copy unavailable");
          field.remove();
        }
        output.textContent = language() === "zh" ? "链接已复制" : "Link copied";
      } catch (_) {
        output.textContent = language() === "zh" ? "请手动复制页面地址" : "Please copy the page address";
      }
    }

    refreshPlatformLinks();
    new MutationObserver(refreshPlatformLinks).observe(document.documentElement, {
      attributes: true, attributeFilter: ["lang"],
    });
    share.querySelector("summary").addEventListener("click", refreshPlatformLinks);
    share.querySelectorAll(".pace-share-x, .pace-share-bluesky").forEach(function (anchor) {
      anchor.addEventListener("click", refreshPlatformLinks);
    });
    share.querySelector(".pace-share-copy").addEventListener("click", function () {
      copyLink(status);
    });
    share.querySelector(".pace-share-wechat").addEventListener("click", function () {
      share.open = false;
      dialog.showModal();
    });
    dialog.querySelector(".pace-share-dialog-copy").addEventListener("click", function () {
      copyLink(dialog.querySelector(".pace-share-status"));
    });
    dialog.querySelector(".pace-share-dialog-close").addEventListener("click", function () {
      dialog.close();
    });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) dialog.close();
    });
    document.addEventListener("click", function (event) {
      if (!share.contains(event.target)) share.open = false;
    });

    const nativeButton = share.querySelector(".pace-share-native");
    if (typeof navigator.share === "function") {
      nativeButton.hidden = false;
      nativeButton.addEventListener("click", async function () {
        try {
          await navigator.share({ title: title(), url: link() });
        } catch (error) {
          if (error.name !== "AbortError") {
            status.textContent = language() === "zh" ? "无法打开系统分享" : "System sharing unavailable";
          }
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
