import type { LayoutLoad } from "./$types";
import type { components } from "$lib/generated/backend-openapi";
import { subjects } from "$lib/subjects";
type CategoryModel = components["schemas"]["CategoryModel"];

function processSubjects(subjects: CategoryModel[]): CategoryModel[] {
  const [withSubcategories, withoutSubcategories] = subjects.reduce(
    ([withSubs, withoutSubs], subject) =>
      subject.subcategories.length > 0
        ? [[...withSubs, subject], withoutSubs]
        : [withSubs, [...withoutSubs, subject]],
    [[], []] as [CategoryModel[], CategoryModel[]]
  );

  return withoutSubcategories.length === 0
    ? withSubcategories
    : [
        ...withSubcategories,
        {
          id: "others",
          name: "Others",
          subcategories: withoutSubcategories.map(({ id, name }) => ({
            id,
            name,
          })),
        },
      ];
}

export const load = (async () => {
  return {
    subjects: processSubjects(subjects), // This allows to easily swap it to backend call later
  };
}) satisfies LayoutLoad;
