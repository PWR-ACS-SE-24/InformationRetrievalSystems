export const ssr = false;

import type { CategoryModel } from "$lib/types";
import type { LayoutLoad } from "./$types";
import { processSubjects } from "$lib/helpers";

export const load = (async ({ fetch }) => {
  const data = (await fetch("http://localhost:2137/api/categories")
    .then((res) => res.json())
    .then((data) => {
      if (data?.error) {
        console.error("Error fetching categories:", data.error);
        return [];
      }
      return processSubjects(data as CategoryModel[]);
    })) as CategoryModel[];

  return {
    subjects: data,
  };
}) satisfies LayoutLoad;
