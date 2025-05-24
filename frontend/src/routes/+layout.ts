import type { LayoutLoad } from "./$types";
import { subjects } from "$lib/subjects";

export const load = (async () => {
  return {
    subjects: subjects, // This allows to easily swap it to backend call later
  };
}) satisfies LayoutLoad;
