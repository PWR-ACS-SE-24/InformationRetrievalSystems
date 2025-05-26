export const ssr = false;

import { BACKEND_URL } from "$lib";
import { processSubjects } from "$lib/helpers";
import type { CategoryModel } from "$lib/types";
import type { LayoutLoad } from "./$types";

export const load = (async ({ fetch }) => {
  const data = (await fetch(`${BACKEND_URL}/api/categories`)
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
