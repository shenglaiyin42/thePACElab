/* The feed remains readable without JavaScript. Set data-pinned="true" on a
 * post in posts.qmd to place it above unpinned posts on every page.
 * Tag labels and assignments are embedded by the bilingual build. */
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
    if (!feed || feed.dataset.postsInitialized === "true") return;
    feed.dataset.postsInitialized = "true";

    const posts = Array.from(feed.querySelectorAll(":scope > .posts-feed-item"));
    posts.sort((a, b) => {
      const pinOrder = Number(b.dataset.pinned === "true") - Number(a.dataset.pinned === "true");
      if (pinOrder) return pinOrder;
      return (b.querySelector("time")?.dateTime || "").localeCompare(
        a.querySelector("time")?.dateTime || ""
      );
    });
    posts.forEach((post) => feed.append(post));

    const sidebar = document.querySelector(".posts-tag-sidebar");
    const filterButtons = Array.from(
      sidebar?.querySelectorAll("button[data-post-tag-filter]") || []
    );
    const knownTags = new Set(filterButtons.map(button => button.dataset.postTagFilter));
    const tagsByPost = new Map(posts.map(post => [post,
      new Set((post.dataset.postTags || "").split(/\s+/).filter(Boolean))
    ]));
    const filterStatus = document.querySelector(".posts-filter-status");
    const emptyState = document.querySelector(".posts-empty-state");

    filterButtons.forEach(button => {
      const tag = button.dataset.postTagFilter;
      const count = tag === "all" ? posts.length : posts.filter(post => tagsByPost.get(post).has(tag)).length;
      const badge = button.querySelector(".posts-tag-count");
      if (badge) badge.textContent = String(count);
    });

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
    let selectedTag = "all";
    let matchingPosts = posts;

    function normalizedTag(tag) {
      return tag && knownTags.has(tag) ? tag : "all";
    }

    function updateAddress(replace) {
      const url = new URL(window.location.href);
      if (selectedTag === "all") url.searchParams.delete("tag");
      else url.searchParams.set("tag", selectedTag);
      const address = url.pathname + url.search + url.hash;
      if (address !== window.location.pathname + window.location.search + window.location.hash) {
        window.history[replace ? "replaceState" : "pushState"](window.history.state, "", address);
      }
    }

    function showPage(scroll) {
      const pageCount = Math.max(1, Math.ceil(matchingPosts.length / PAGE_SIZE));
      page = Math.min(page, pageCount - 1);
      const visible = new Set(matchingPosts.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE));
      posts.forEach(post => { post.hidden = !visible.has(post); });
      previous.disabled = page === 0;
      next.disabled = page === pageCount - 1;
      navigation.hidden = pageCount <= 1;
      status.replaceChildren(pair(
        `Page ${page + 1} of ${pageCount}`,
        `第 ${page + 1} / ${pageCount} 页`
      ));
      if (emptyState) emptyState.hidden = matchingPosts.length !== 0;
      if (scroll) feed.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function setFilter(tag, updateHistory) {
      selectedTag = normalizedTag(tag);
      page = 0;
      matchingPosts = selectedTag === "all" ? posts : posts.filter(post => tagsByPost.get(post).has(selectedTag));
      filterButtons.forEach(button => {
        const active = button.dataset.postTagFilter === selectedTag;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });
      if (filterStatus) {
        filterStatus.replaceChildren(pair(
          `${matchingPosts.length} ${matchingPosts.length === 1 ? "post" : "posts"}`,
          `共 ${matchingPosts.length} 篇文章`
        ));
      }
      if (updateHistory) updateAddress(false);
      showPage(false);
    }

    sidebar?.addEventListener("click", event => {
      const button = event.target.closest("button[data-post-tag-filter]");
      if (button && sidebar.contains(button)) setFilter(button.dataset.postTagFilter, true);
    });

    feed.addEventListener("click", event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const badge = event.target.closest("a.posts-tag-badge[data-post-tag]");
      if (!badge || !feed.contains(badge) || !knownTags.has(badge.dataset.postTag)) return;
      event.preventDefault();
      setFilter(badge.dataset.postTag, true);
    });

    previous.addEventListener("click", () => {
      if (page > 0) { page -= 1; showPage(true); }
    });
    next.addEventListener("click", () => {
      const pageCount = Math.ceil(matchingPosts.length / PAGE_SIZE);
      if (page < pageCount - 1) { page += 1; showPage(true); }
    });
    window.addEventListener("popstate", () => {
      setFilter(new URLSearchParams(window.location.search).get("tag"), false);
    });
    const requestedTag = new URLSearchParams(window.location.search).get("tag");
    setFilter(requestedTag, false);
    if (requestedTag && selectedTag === "all") updateAddress(true);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
