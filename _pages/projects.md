---
layout: page
title: projects
permalink: /projects/
description: A growing collection of your cool projects.
<<<<<<< HEAD
nav: false
=======
nav: true
>>>>>>> 0af4aecf50426fc1e35696ca4c47940737175b26
nav_order: 3
display_categories: [work, fun]
horizontal: false
---

<!-- pages/projects.md -->
<div class="projects">
{% if site.enable_project_categories and page.display_categories %}
  <!-- Display categorized projects -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_projects = site.projects | where: "category", category %}
  {% assign sorted_projects = categorized_projects | sort: "importance" %}
  <!-- Generate cards for each project -->
  {% if page.horizontal %}
  <div class="container">
<<<<<<< HEAD
    <div class="row row-cols-2">
=======
    <div class="row row-cols-1 row-cols-md-2">
>>>>>>> 0af4aecf50426fc1e35696ca4c47940737175b26
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
<<<<<<< HEAD
  <div class="grid">
=======
  <div class="row row-cols-1 row-cols-md-3">
>>>>>>> 0af4aecf50426fc1e35696ca4c47940737175b26
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}

{% else %}

<!-- Display projects without categories -->

{% assign sorted_projects = site.projects | sort: "importance" %}

  <!-- Generate cards for each project -->

{% if page.horizontal %}

  <div class="container">
<<<<<<< HEAD
    <div class="row row-cols-2">
=======
    <div class="row row-cols-1 row-cols-md-2">
>>>>>>> 0af4aecf50426fc1e35696ca4c47940737175b26
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
<<<<<<< HEAD
  <div class="grid">
=======
  <div class="row row-cols-1 row-cols-md-3">
>>>>>>> 0af4aecf50426fc1e35696ca4c47940737175b26
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>
