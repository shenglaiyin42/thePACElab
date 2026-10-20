/* The feed remains readable without JavaScript. Set data-pinned="true" on a
 * post in posts.qmd to place it above unpinned posts on every page. */
(function () {
  const PAGE_SIZE = 10;

  function pair(english, chinese) {
    const wrapper = document.createElement("span");
    for (const [language, text] of [["en", english], ["zh", chinese]]) {
      const span = document.createElement("span");
      span.dataset.paceCopy = language;
      span.textContent = text;
      wrapper.append(span);
    }
    return wrapper;
  }

  function initialize() {
    const feed = document.querySelector(".posts-feed");
    if (!feed) return;

    const posts = Array.from(feed.querySelectorAll(":scope > .posts-feed-item"));
    posts.sort((a, b) => {
      const pinOrder = Number(b.dataset.pinned === "true") - Number(a.dataset.pinned === "true");
      if (pinOrder) return pinOrder;
      return (b.querySelector("time")?.dateTime || "").localeCompare(
        a.querySelector("time")?.dateTime || ""
      );
    });
    posts.forEach((post) => feed.append(post));

    const pageCount = Math.ceil(posts.length / PAGE_SIZE);
    if (pageCount <= 1) return;

    const navigation = document.createElement("nav");
    navigation.className = "posts-pagination";
    navigation.setAttribute("aria-label", "Post pages / 文章分页");

    const previous = document.createElement("button");
    previous.type = "button";
    previous.append(pair("Previous", "上一页"));
    const status = document.createElement("span");
    status.className = "posts-pagination-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const next = document.createElement("button");
    next.type = "button";
    next.append(pair("Next", "下一页"));
    navigation.append(previous, status, next);
    feed.after(navigation);

    let page = 0;
    function showPage(scroll) {
      posts.forEach((post, index) => {
        post.hidden = Math.floor(index / PAGE_SIZE) !== page;
      });
      previous.disabled = page === 0;
      next.disabled = page === pageCount - 1;
      status.replaceChildren(pair(
        `Page ${page + 1} of ${pageCount}`,
        `第 ${page + 1} / ${pageCount} 页`
      ));
      if (scroll) feed.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    previous.addEventListener("click", () => {
      if (page > 0) { page -= 1; showPage(true); }
    });
    next.addEventListener("click", () => {
      if (page < pageCount - 1) { page += 1; showPage(true); }
    });
    showPage(false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
