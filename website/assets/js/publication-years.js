// Count the published bibliography entries so the bars scale to the busiest year.
(function () {
  function renderPublicationYears() {
    const chart = document.querySelector(".publication-year-bars");
    const summary = document.querySelector(".publication-year-summary");
    if (!chart || !summary) return;

    const counts = new Map();
    document.querySelectorAll(".publication-bibliography ol > li").forEach((entry) => {
      const citation = entry.textContent;
      if (/\b(in preparation|in revision|under review|submitted|in press|preprint)\b/i.test(citation)) return;
      const match = citation.match(/\(((?:19|20)\d{2})\)/);
      if (!match) return;
      const year = Number(match[1]);
      counts.set(year, (counts.get(year) || 0) + 1);
    });
    if (counts.size === 0) return;

    const years = [...counts.keys()];
    const earliest = Math.min(...years);
    const latest = Math.max(...years);
    const maximum = Math.max(...counts.values());
    const total = [...counts.values()].reduce((sum, count) => sum + count, 0);
    const rows = document.createDocumentFragment();

    for (let year = latest; year >= earliest; year--) {
      const count = counts.get(year) || 0;
      const row = document.createElement("div");
      row.className = "publication-year-row";

      const label = document.createElement("span");
      label.textContent = year;
      const track = document.createElement("span");
      track.className = "publication-year-track";
      track.setAttribute("aria-hidden", "true");
      const fill = document.createElement("span");
      fill.className = "publication-year-fill";
      fill.style.width = `${(count / maximum) * 100}%`;
      track.append(fill);
      const value = document.createElement("span");
      value.className = "publication-year-count";
      value.textContent = count;
      row.append(label, track, value);
      rows.append(row);
    }
    chart.replaceChildren(rows);

    const english = summary.querySelector('[data-pace-copy="en"]');
    const chinese = summary.querySelector('[data-pace-copy="zh"]');
    if (english) english.textContent = `${total} published papers (${earliest}–${latest})`;
    if (chinese) chinese.textContent = `${earliest}-${latest} 年，共 ${total} 篇已发表论文`;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderPublicationYears, { once: true });
  } else {
    renderPublicationYears();
  }
  window.addEventListener("pace:publications-updated", renderPublicationYears);
})();
