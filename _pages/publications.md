---
layout: default
permalink: /research/
title: research
nav: true
nav_order: 2
---

<div class="post">
  <header class="post-header">
    <h1 class="post-title">selected research</h1>
  </header>

  <article>
    <p>
      Please see
      <a href="https://scholar.google.com/citations?user=uoy11ZgAAAAJ&amp;hl=en">Google Scholar</a>
      for my most up-to-date list of publications.
    </p>

    <div class="publications">{% bibliography --query @*[selected=true]* %}</div>

  </article>
</div>
