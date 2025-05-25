import type { components } from "$lib/generated/backend-openapi";

type CategoryModel = components["schemas"]["CategoryModel"];

export function processSubjects(subjects: CategoryModel[]): CategoryModel[] {
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

export function translateCategories(
  categories: string[],
  subjects: CategoryModel[]
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
