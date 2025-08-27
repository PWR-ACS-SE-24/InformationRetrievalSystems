# ArXiv Search 🎓 (Information Retrieval System)
<div align="center">

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Svelte](https://img.shields.io/badge/Svelte-%23FF3E00.svg?logo=svelte&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![ElasticSearch](https://img.shields.io/badge/Elasticsearch-%23005571.svg?logo=elasticsearch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)
![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)
</div>

"Arxiv Search" is a system designed to retrieve scientific papers from the open-access repository arXiv. It allows users to search publications by keywords in titles and abstracts, as well as filter results by categories, publication dates, or authors. The system uses Elasticsearch to provide advanced features like full-text search, faceted filtering, and trend analysis. Its goal is to help researchers, students, and specialists efficiently discover relevant scientific works and analyze publication trends across disciplines. This application was developed using Elasticsearch, TypeScript, Svelte, Python, FastAPI, and PostgreSQL as part of the Information Retrieval Systems course at the Wrocław University of Science and Technology.

<table align="center">
  <thead>
    <tr>
      <th colspan="2">ArXiv Search Team</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">
        <img src="https://github.com/mlodybercik.png?size=64" alt="@mlodybercik"><br>
        <b>Przemysław Barcicki</b><br>
        <a href="https://github.com/mlodybercik">@mlodybercik</a>
      </td>
      <td align="center">
        <img src="https://github.com/jakubzehner.png?size=64" alt="@jakubzehner"><br>
        <b>Jakub Zehner</b><br>
        <a href="https://github.com/jakubzehner">@jakubzehner</a>
      </td>
    </tr>
  </tbody>
</table>

## Screenshots 📸

Main page
![Main page](./docs/img/main-page.png)

Search page
![Search page](./docs/img/search-page.png)

Categories
![Categories](./docs/img/dropdown.png)

Faceted navigation
![Faceted1](./docs/img/facet1.png)
![Faceted2](./docs/img/facet2.png)

Papers per year
![Faceted2](./docs/img/years.png)

## Diagrams 📝

Architecture diagram
![Architecture](./docs/img/architecture.drawio.png)

Component diagram
![Component](./docs/img/component.drawio.png)

## Benchmarks 📈

Ram usage
![Ram](./docs/img/ram-1.png)

Indexing time
![Czas](./docs/img/czas-1.png)

Retrieval times
![Times](./docs/img/times-1.png)
