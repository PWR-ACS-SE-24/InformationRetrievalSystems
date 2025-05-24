import type { PageLoad } from "./$types";

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

  return {
    q,
    author,
    published,
    minYear: minYear,
    maxYear: maxYear,
    selectedSubjects,
  };
};
