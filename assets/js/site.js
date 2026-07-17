(function () {
  "use strict";

  var root = document.documentElement;

  function applyTheme(theme) {
    var nextTheme = theme === "dark" ? "dark" : "light";
    root.dataset.theme = nextTheme;
    try { localStorage.setItem("theme", nextTheme); } catch (error) {}

    document.querySelectorAll(".theme-toggle").forEach(function (button) {
      var isDark = nextTheme === "dark";
      button.setAttribute("aria-pressed", String(isDark));
      button.setAttribute("aria-label", isDark ? "라이트 모드 켜기" : "다크 모드 켜기");
      var icon = button.querySelector("[data-theme-icon]");
      if (icon) icon.textContent = isDark ? "☼" : "◐";
    });
  }

  function initTheme() {
    if (document.body.dataset.page === "post" && document.querySelector(".theme-toggle-text")) return;
    applyTheme(root.dataset.theme === "dark" ? "dark" : "light");
    document.querySelectorAll(".theme-toggle").forEach(function (button) {
      if (button.dataset.themeReady === "true") return;
      button.dataset.themeReady = "true";
      button.addEventListener("click", function () {
        applyTheme(root.dataset.theme === "dark" ? "light" : "dark");
      });
    });
  }

  function initArchiveFilter() {
    var buttons = Array.from(document.querySelectorAll("[data-filter]"));
    var posts = Array.from(document.querySelectorAll("[data-archive-item]"));
    if (!buttons.length || !posts.length) return;

    var params = new URLSearchParams(window.location.search);
    var requested = params.get("tag") || "전체";

    function normalizeFilter(value) {
      var aliases = {
        "업무 프로세스": "시스템·업무 설계",
        "사업기획": "시스템·업무 설계",
        "문서/결재": "시스템·업무 설계",
        "데이터 구조": "데이터·AI 시스템",
        "AI 자동화": "데이터·AI 시스템",
        "공공데이터": "데이터·AI 시스템",
        "회고": "전체"
      };
      return aliases[value] || value;
    }

    function render(filter) {
      var normalized = normalizeFilter(filter);
      var effective = filter === "전체" ? "전체" : filter;
      var visible = 0;
      posts.forEach(function (post) {
        var tags = (post.dataset.tags || "").split("|");
        var show = effective === "전체" || tags.includes(effective);
        post.hidden = !show;
        if (show) visible += 1;
      });

      buttons.forEach(function (button) {
        var active = button.dataset.filter === normalized;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });

      var count = document.querySelector("[data-archive-count]");
      if (count) count.textContent = visible + "개의 글";
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var nextFilter = button.dataset.filter;
        var url = new URL(window.location.href);
        if (nextFilter === "전체") url.searchParams.delete("tag");
        else url.searchParams.set("tag", nextFilter);
        window.history.replaceState({}, "", url);
        render(nextFilter);
      });
    });

    render(requested);
  }

  function initPostMetadata() {
    if (document.body.dataset.page !== "post") return;
    var container = document.querySelector("article") || document.querySelector("main");
    if (!container || container.querySelector(".technical-meta")) return;

    var anchor = container.querySelector(".tags") || container.querySelector(".lead");
    if (!anchor) return;

    var metadata = document.createElement("div");
    metadata.className = "technical-meta";
    metadata.setAttribute("aria-label", "게시글 정보");
    var published = document.body.dataset.published || "";
    var updated = document.body.dataset.updated || "";
    var category = document.body.dataset.category || "기술 기록";
    var readTime = document.body.dataset.readTime || "";
    metadata.innerHTML =
      '<span><strong>분야</strong>' + category + "</span>" +
      (published ? '<span><strong>작성</strong><time datetime="' + published + '">' + published + "</time></span>" : "") +
      (updated ? '<span><strong>수정</strong><time datetime="' + updated + '">' + updated + "</time></span>" : "") +
      (readTime ? '<span><strong>읽는 시간</strong>' + readTime + "</span>" : "");
    anchor.insertAdjacentElement("afterend", metadata);
  }

  function initTableOfContents() {
    if (document.body.dataset.page !== "post") return;
    var container = document.querySelector("article") || document.querySelector("main");
    if (!container || container.querySelector(".toc")) return;

    var headings = Array.from(container.querySelectorAll(":scope > h2")).filter(function (heading) {
      return !heading.closest("footer");
    });
    if (headings.length < 4) return;

    headings.forEach(function (heading, index) {
      if (!heading.id) heading.id = "section-" + (index + 1);
    });

    var nav = document.createElement("nav");
    nav.className = "toc";
    nav.setAttribute("aria-label", "이 글의 목차");
    var items = headings.map(function (heading) {
      var label = heading.textContent.replace(/^\d+\.\s*/, "");
      return '<li><a href="#' + heading.id + '">' + label + "</a></li>";
    }).join("");
    nav.innerHTML = '<p class="toc-title">이 글의 목차</p><ol>' + items + "</ol>";

    var anchor = container.querySelector(".technical-meta") || container.querySelector(".tags") || container.querySelector(".lead");
    if (anchor) anchor.insertAdjacentElement("afterend", nav);
  }

  function initFooterYear() {
    document.querySelectorAll("[data-current-year]").forEach(function (node) {
      node.textContent = String(new Date().getFullYear());
    });
  }

  initTheme();
  initArchiveFilter();
  initPostMetadata();
  initTableOfContents();
  initFooterYear();
})();
