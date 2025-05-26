import type { components } from "$lib/generated/backend-openapi";

export type CategoryModel = components["schemas"]["CategoryModel"];
export type SearchQuery = components["schemas"]["SearchQuery"];
export type SearchResponse = components["schemas"]["SearchResponse"];
export type FacetBy = components["schemas"]["FacetBy"];
export type FacetByResult = components["schemas"]["FacetByResult"];

export type extendedFacetByResult = FacetByResult & {
  displayValue: string;
};
