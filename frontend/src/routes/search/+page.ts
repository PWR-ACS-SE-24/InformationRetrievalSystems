export const ssr = false;

import type { PageLoad } from "./$types";
import type { SearchResponse, SearchQuery } from "$lib/types";
import { translateCategories } from "$lib/helpers";

export const load: PageLoad = async ({ fetch, url, parent }) => {
  const { subjects } = await parent();

  const page = url.searchParams.get("page") ?? "0";
  const perpage = url.searchParams.get("page_size") ?? "10";

  const q = url.searchParams.get("q") ?? "";
  const author = url.searchParams.get("author") ?? null;
  const published = url.searchParams.get("published") === "true";
  const minYear = url.searchParams.get("min_year");
  const maxYear = url.searchParams.get("max_year");
  const subjectsParam = url.searchParams.get("subjects");

  let selectedSubjects: string[] = [];
  if (subjectsParam) {
    try {
      selectedSubjects = JSON.parse(decodeURIComponent(subjectsParam));
    } catch (e) {
      console.error("Invalid subjects param:", e);
    }
  }

  const data = {
    search: q,
    author: author ? author : undefined,
    subject:
      selectedSubjects && selectedSubjects.length > 0 ? selectedSubjects : null,
    year_start: minYear ? parseInt(minYear, 10) : undefined,
    year_end: maxYear ? parseInt(maxYear, 10) : undefined,
    published: published ? published : false,
    facet_by: [], // TODO: Implement facets
  } as SearchQuery;

  const searchResponse = fetch(
    `http://localhost:2137/api/search?page=${page}&perpage=${perpage}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  ).then((res) => res.json() as Promise<SearchResponse>);

  const timeToSearch = searchResponse.then((res) => res.time_to_search);
  const pagination = searchResponse.then((res) => res.pagination);
  const availableFacets = searchResponse.then((res) => res.available_facets);
  const foundPerYear = searchResponse.then((res) => res.found_per_year);
  const papers = searchResponse.then((res) =>
    res.papers.map((paper) => ({
      ...paper,
      categories: translateCategories(paper.categories ?? [], subjects),
    }))
  );

  const categories = availableFacets.then((facets) =>
    facets
      .filter((facet) => facet.field === "categories")
      .map((facet) => ({
        displayValue: translateCategories([facet.value], subjects)[0],
        value: facet.value,
        count: facet.count,
      }))
  );

  const authors = availableFacets.then((facets) =>
    facets
      .filter((facet) => facet.field === "authors")
      .map((facet) => ({
        displayValue: facet.value,
        value: facet.value,
        count: facet.count,
      }))
  );

  return {
    rawQuery: url.searchParams.toString(),
    timeToSearch,
    pagination,
    foundPerYear,
    papers,
    categories,
    authors,
  };
};
