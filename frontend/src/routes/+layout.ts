import type { LayoutLoad } from "./$types";
import { subjects } from "$lib/subjects";

type Subcategory = {
  id: string;
  name: string;
};

type Subject = {
  id: string;
  name: string;
  subcategories: Subcategory[];
};

function processSubjects(subjects: Subject[]): Subject[] {
  const [withSubcategories, withoutSubcategories] = subjects.reduce(
    ([withSubs, withoutSubs], subject) =>
      subject.subcategories.length > 0
        ? [[...withSubs, subject], withoutSubs]
        : [withSubs, [...withoutSubs, subject]],
    [[], []] as [Subject[], Subject[]]
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
