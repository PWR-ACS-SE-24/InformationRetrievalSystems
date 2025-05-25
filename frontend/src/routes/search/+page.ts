import type { PageLoad } from "./$types";
import { response } from "$lib/response";

type Subcategory = {
  id: string;
  name: string;
};

type Subject = {
  id: string;
  name: string;
  subcategories: Subcategory[];
};

function translateCategories(
  categories: string[],
  subjects: Subject[]
): string[] {
  return categories.map((category) => {
    const subject = subjects.find((s) => s.id === category);
    if (subject) {
      return subject.name;
    }
    const subcategory = subjects
      .flatMap((s) => s.subcategories)
      .find((sc) => sc.id === category);
    return subcategory ? subcategory.name : category;
  });
}

export const load: PageLoad = async ({ url, parent }) => {
  const { subjects } = await parent();

  const page = url.searchParams.get("page") ?? "0";
  const pageSize = url.searchParams.get("page_size") ?? "10";
  const q = url.searchParams.get("q") ?? "";
  const author = url.searchParams.get("author") ?? null;
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

  // TODO: Call to API, for now we use the mock response
  const time_to_search = response.time_to_search;
  const pagination = response.pagination;
  // const papers = response.papers;
  const papers = response.papers.map((paper) => ({
    ...paper,
    categories: translateCategories(paper.categories, subjects),
  }));
  const available_facets = response.available_facets;
  const categories = available_facets
    .filter((facet) => facet.field === "categories")
    .map((facet) => ({
      displayValue: translateCategories([facet.value], subjects)[0],
      value: facet.value,
      count: facet.count,
    }));
  const authors = available_facets
    .filter((facet) => facet.field === "authors")
    .map((facet) => ({
      displayValue: facet.value,
      value: facet.value,
      count: facet.count,
    }));

  return {
    rawQuery: url.searchParams.toString(),
    q,
    author,
    published,
    minYear: minYear,
    maxYear: maxYear,
    selectedSubjects,
    time_to_search,
    pagination,
    papers,
    categories,
    authors,
  };
};
