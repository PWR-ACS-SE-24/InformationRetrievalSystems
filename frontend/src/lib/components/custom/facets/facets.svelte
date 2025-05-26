<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import type { extendedFacetByResult, FacetBy } from "$lib/types";
  import { Button } from "$lib/components/ui/button";
  import { goto } from "$app/navigation";
  import { Separator } from "$lib/components/ui/separator";
  import { onMount } from "svelte";
  import { X } from "lucide-svelte";

  const { name, field, content, rawQuery } = $props<{
    name: string;
    field: string;
    content: extendedFacetByResult[];
    rawQuery: string;
  }>();

  const urlParams = new URLSearchParams(rawQuery);

  const facets = urlParams.get("facets");
  let currentFacets: FacetBy[] = $state([]);
  let currentFacetsInField: {
    field: string;
    value: string;
    displayValue: string;
  }[] = $state([]);
  let filteredContent: extendedFacetByResult[] = $state([]);

  onMount(() => {
    if (facets) {
      try {
        currentFacets = JSON.parse(decodeURIComponent(facets));
      } catch (e) {
        console.error("Invalid facets param:", e);
      }
    }
    currentFacetsInField = currentFacets
      .filter((f) => f.field === field)
      .map((f) => {
        const contentItem = content.find(
          (item: { field: string; value: string }) =>
            item.field === f.field && item.value === f.value
        );
        return {
          ...f,
          displayValue: contentItem ? contentItem.displayValue : f.value,
        };
      }) as {
      field: string;
      value: string;
      displayValue: string;
    }[];

    filteredContent = content.filter(
      (item: { field: string; value: string }) =>
        !currentFacets.some(
          (f) => f.field === item.field && f.value === item.value
        )
    );

    $inspect(currentFacets, "currentFacets");
    $inspect(currentFacetsInField, "currentFacetsInField");
  });

  function addFacets(facet: extendedFacetByResult) {
    const existingFacet = currentFacets.find(
      (f) => f.field === facet.field && f.value === facet.value
    );
    if (!existingFacet) {
      currentFacets.push({
        field: facet.field,
        value: facet.value,
      });

      goToFacets();
    }
  }

  function removeFacets(facet: { field: string; value: string }) {
    currentFacets = currentFacets.filter(
      (f) => f.field !== facet.field || f.value !== facet.value
    );
    goToFacets();
  }

  function goToFacets() {
    urlParams.set("facets", JSON.stringify(currentFacets));
    goto(`/search?${urlParams.toString()}`);
  }
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>{name}</Card.Title>
  </Card.Header>
  <Card.Content>
    {#if currentFacetsInField && currentFacetsInField.length > 0}
      <div class="space-y-1">
        {#each currentFacetsInField as curr}
          <Button
            on:click={() => removeFacets(curr)}
            variant="outline"
            class="w-full text-sm h-auto py-2 whitespace-normal"
          >
            <div class="flex justify-between w-full text-left">
              <span class="break-words whitespace-normal"
                >{curr.displayValue}</span
              >
              <span class="text-right text-gray-500 ml-2 shrink-0"><X /></span>
            </div>
          </Button>
        {/each}
      </div>
      <Separator class="my-2" />
    {/if}

    <div>
      {#each filteredContent as item}
        <Button
          on:click={() => addFacets(item)}
          variant="ghost"
          class="w-full text-sm h-auto py-2 whitespace-normal"
        >
          <div class="flex justify-between w-full text-left">
            <span class="break-words whitespace-normal"
              >{item.displayValue}</span
            >
            <span class="text-right text-gray-500 ml-2 shrink-0"
              >({item.count})</span
            >
          </div>
        </Button>
      {/each}
    </div>
  </Card.Content>
</Card.Root>
