export const ssr = false;

import { BACKEND_URL, YEAR_MAX, YEAR_MIN } from "$lib";
import { translateCategories } from "$lib/helpers";
import type {
  FacetBy,
  SearchQuery,
  SearchResponse,
  extendedFacetByResult,
} from "$lib/types";
import type { PageLoad } from "./$types";

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
  const facets = url.searchParams.get("facets");

  let selectedSubjects: string[] = [];
  if (subjectsParam) {
    try {
      selectedSubjects = JSON.parse(decodeURIComponent(subjectsParam));
    } catch (e) {
      console.error("Invalid subjects param:", e);
    }
  }

  let selectedFacets: FacetBy[] = [];
  if (facets) {
    try {
      selectedFacets = JSON.parse(decodeURIComponent(facets));
    } catch (e) {
      console.error("Invalid facets param:", e);
    }
  }

  const data = {
    search: q,
    author: author ? author : undefined,
    subject:
      selectedSubjects && selectedSubjects.length > 0 ? selectedSubjects : null,
    year_start: minYear ? Math.max(parseInt(minYear, 10), YEAR_MIN) : undefined,
    year_end: maxYear ? Math.min(parseInt(maxYear, 10), YEAR_MAX) : undefined,
    published: published ? published : false,
    facet_by: selectedFacets && selectedFacets.length > 0 ? selectedFacets : [],
  } as SearchQuery;

  const searchResponse = fetch(
    `${BACKEND_URL}/api/search?page=${page}&perpage=${perpage}`,
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
  const foundPerYearRaw = searchResponse.then((res) => res.found_per_year);
  const papers = searchResponse.then((res) =>
    res.papers.map((paper) => ({
      ...paper,
      categories: translateCategories(paper.categories ?? [], subjects),
    }))
  );

  const categories = availableFacets.then((facets) =>
    facets
      .filter((facet) => facet.field === "categories")
      .map(
        (facet) =>
          ({
            field: facet.field,
            displayValue: translateCategories([facet.value], subjects)[0],
            value: facet.value,
            count: facet.count,
          }) as extendedFacetByResult
      )
  );

  const authors = availableFacets.then((facets) =>
    facets
      .filter((facet) => facet.field === "authors")
      .map(
        (facet) =>
          ({
            field: facet.field,
            displayValue: facet.value,
            value: facet.value,
            count: facet.count,
          }) as extendedFacetByResult
      )
  );

  const foundPerYear = foundPerYearRaw.then((data) =>
    Object.entries(data).map(([year, value]) => ({
      year,
      value,
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
