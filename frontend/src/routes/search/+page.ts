import type { PageLoad } from "./$types";
import { response } from "$lib/response";

export const load: PageLoad = ({ url }: { url: URL }) => {
  const q = url.searchParams.get("q") ?? "";
  const author = url.searchParams.get("author") ?? "";
  const published = url.searchParams.get("published") === "true";
  const minYear = url.searchParams.get("min_year");
  const maxYear = url.searchParams.get("max_year");

  let selectedSubjects: Record<string, string[]> = {};

  const subjectsParam = url.searchParams.get("subjects");
  if (subjectsParam) {
    try {
      selectedSubjects = JSON.parse(decodeURIComponent(subjectsParam));
    } catch (e) {
      console.error("Invalid subjects param:", e);
    }
  }

  // TODO: Call to API
  const time_to_search = response.time_to_search;
  const total = response.total;
  const papers = response.papers;
  const available_facets = response.available_facets;
  const categories = available_facets
    .filter((facet) => facet.field === "categories")
    .map((facet) => ({
      value: facet.value,
      count: facet.count,
    }));
  const authors = available_facets
    .filter((facet) => facet.field === "authors")
    .map((facet) => ({
      value: facet.value,
      count: facet.count,
    }));

  return {
    q,
    author,
    published,
    minYear: minYear,
    maxYear: maxYear,
    selectedSubjects,
    time_to_search,
    total,
    papers,
    categories,
    authors,
  };
};
