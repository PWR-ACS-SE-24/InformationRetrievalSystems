<script lang="ts">
  import { goto, onNavigate } from "$app/navigation";
  import { YEAR_MAX, YEAR_MIN } from "$lib";
  import { Button } from "$lib/components/ui/button/index.js";
  import { Checkbox } from "$lib/components/ui/checkbox/index.js";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  import type { components } from "$lib/generated/backend-openapi";
  import { ChevronDown, Search } from "lucide-svelte";
  import { onMount } from "svelte";
  import RangeSlider from "svelte-range-slider-pips";
  import { SvelteSet } from "svelte/reactivity";

  type CategoryModel = components["schemas"]["CategoryModel"];
  type SearchQuery = components["schemas"]["SearchQuery"];

  const { availableSubjects = [] }: { availableSubjects: CategoryModel[] } =
    $props();

  let searchQuery = $state("");
  let author = $state("");
  let checked = $state(false);
  let values = $state([YEAR_MIN, YEAR_MAX]);
  let selectedSubjects = $state(new SvelteSet<string>());
  let minYear = $derived(() => values[0]);
  let maxYear = $derived(() => values[1]);

  const parseQueryObj = (query: URLSearchParams): SearchQuery => {
    try {
      return {
        search: query.get("q") || "",
        author: query.get("author") || "",
        year_start: Number(query.get("min_year") || YEAR_MIN),
        year_end: Number(query.get("max_year") || YEAR_MAX),
        published: query.get("published") === "true",
        subject: JSON.parse(decodeURIComponent(query.get("subjects") || "[]")),
        facet_by: [],
      };
    } catch (e) {
      console.error("Failed to parse query parameters:", e);
      // Fallback to an empty object if parsing fails
      return {
        search: "",
        subject: null,
        year_start: YEAR_MIN,
        year_end: YEAR_MAX,
        published: false,
        facet_by: null,
      };
    }
  };

  const setFields = (searchOptions: SearchQuery) => {
    try {
      searchQuery = searchOptions.search;
      author = searchOptions.author || "";
      checked = searchOptions.published;
      values = [
        Math.max(searchOptions.year_start, YEAR_MIN),
        Math.min(searchOptions.year_end, YEAR_MAX),
      ];
      selectedSubjects.clear();
      (searchOptions.subject || []).forEach((sub) => {
        selectedSubjects.add(sub);
      });
    } catch (e) {
      console.error("Failed to parse search params:", e);
    }
  };

  onNavigate(() => {
    setFields(parseQueryObj(new URLSearchParams(location.search)));
  });

  onMount(() => {
    setFields(parseQueryObj(new URLSearchParams(location.search)));
  });

  function isChecked(categoryId: string) {
    const value = selectedSubjects.has(categoryId);
    return value;
  }

  function isAnyChecked(categoryId: string) {
    const cat = availableSubjects.find((c) => c.id === categoryId);
    if (!cat) return false;
    return cat.subcategories.some((sub) => selectedSubjects.has(sub.id));
  }

  function toggleCat(categoryId: string) {
    if (isChecked(categoryId)) {
      selectedSubjects.delete(categoryId);
    } else {
      selectedSubjects.add(categoryId);
    }
  }

  function isAllChecked(categoryId: string) {
    const cat = availableSubjects.find((c) => c.id === categoryId);
    if (!cat) return false;
    return cat.subcategories.every((sub) => selectedSubjects.has(sub.id));
  }

  function toggleAll(categoryId: string, checked: boolean) {
    const cat = availableSubjects.find((c) => c.id === categoryId);
    if (!cat) return;
    if (checked) {
      cat.subcategories.forEach((sub) => {
        selectedSubjects.add(sub.id);
      });
    } else {
      cat.subcategories.forEach((sub) => {
        selectedSubjects.delete(sub.id);
      });
    }
  }

  function onSearch(e: Event) {
    e.preventDefault();

    const params = new URLSearchParams();
    if (searchQuery) params.set("q", searchQuery);
    if (author) params.set("author", author);
    if (checked) params.set("published", "true");
    if (minYear && values[0] != YEAR_MIN)
      params.set("min_year", minYear().toString());
    if (maxYear && values[1] != YEAR_MAX)
      params.set("max_year", maxYear().toString());

    if (selectedSubjects.size > 0) {
      const selectedJSON = JSON.stringify(Array.from(selectedSubjects));
      params.set("subjects", encodeURIComponent(selectedJSON));
    }

    goto(`/search?${params.toString()}`);
  }
</script>

<form class="pt-4">
  <h1 class="text-5xl font-bold mb-6"><a href="/">arXiv paper search</a></h1>

  <!-- Search -->
  <div class="relative w-full mb-3">
    <div
      class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
    >
      <Search class="h-4 w-4 text-gray-500" />
    </div>
    <Input
      bind:value={searchQuery}
      type="text"
      placeholder="Search"
      class="pl-10 w-full"
    />
  </div>

  <!-- Author + Subject -->
  <div class="flex gap-4 mb-10">
    <Input
      bind:value={author}
      type="text"
      placeholder="Author"
      class="flex-1"
    />

    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild let:builder>
        <Button
          variant="outline"
          builders={[builder]}
          class="flex-1 flex items-center gap-1 justify-between"
        >
          Subject <ChevronDown class="w-4 h-4" />
        </Button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content class="w-64">
        {#each availableSubjects as category}
          <DropdownMenu.Sub>
            <DropdownMenu.SubTrigger>
              <span class={isAnyChecked(category.id) ? "font-medium" : ""}>
                {category.name}
              </span>
            </DropdownMenu.SubTrigger>

            <DropdownMenu.SubContent class="w-64 max-h-80 overflow-y-auto">
              <DropdownMenu.CheckboxItem
                checked={isAllChecked(category.id)}
                on:click={(e) => {
                  e.preventDefault();
                  toggleAll(category.id, !isAllChecked(category.id));
                }}
              >
                <span class="font-medium">Check all</span>
              </DropdownMenu.CheckboxItem>

              <DropdownMenu.Separator />

              {#each category.subcategories as sub}
                <DropdownMenu.CheckboxItem
                  checked={isChecked(sub.id)}
                  on:click={(e) => {
                    e.preventDefault();
                    toggleCat(sub.id);
                  }}
                >
                  {sub.name}
                </DropdownMenu.CheckboxItem>
              {/each}
            </DropdownMenu.SubContent>
          </DropdownMenu.Sub>
        {/each}
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>

  <!-- Slider -->
  <div class="w-full mb-4">
    <RangeSlider
      range
      float
      pips
      pushy
      first="label"
      last="label"
      min={YEAR_MIN}
      max={YEAR_MAX}
      bind:values
    />
  </div>

  <!-- Checkbox -->
  <div class="flex items-center space-x-2 mt-14">
    <Checkbox id="published" bind:checked aria-labelledby="published-only" />
    <Label id="published-only" for="published" class="text-sm">
      Published only
    </Label>
  </div>

  <!-- Button -->
  <div class="flex justify-center mt-4">
    {#if searchQuery}
      <Button class="px-8 text-xl" on:click={onSearch} type="submit"
        >Search</Button
      >
    {:else}
      <Button class="px-8 text-xl" disabled>Search</Button>
    {/if}
  </div>
</form>

<style>
  :root {
    --range-handle-inactive: hsl(var(--primary) / var(--tw-bg-opacity, 1));
    --range-handle: hsl(var(--primary) / var(--tw-bg-opacity, 1));
    --range-handle-focus: hsl(var(--primary) / var(--tw-bg-opacity, 1));
  }
</style>
