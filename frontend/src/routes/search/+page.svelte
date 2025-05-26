<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import * as Pagination from "$lib/components/ui/pagination";
  import LoaderCircle from "lucide-svelte/icons/loader-circle";
  import type { PageProps } from "./$types";
  import { Facets } from "$lib/components/custom/facets";
  import { Paper } from "$lib/components/custom/paper";
  import { Search } from "$lib/components/custom/search";
  import { Separator } from "$lib/components/ui/separator";
  import { Skeleton } from "$lib/components/ui/skeleton";
  import { goto } from "$app/navigation";
  import { YearChart } from "$lib/components/custom/year-chart";

  let { data }: PageProps = $props();

  function goToPage(newPage: number) {
    const urlParams = new URLSearchParams(data.rawQuery);
    urlParams.set("page", newPage.toString());
    goto(`/search?${urlParams.toString()}`);
  }
</script>

<div class="min-h-[calc(100vh-64px)] flex flex-col">
  <div class="flex items-center justify-center mb-1">
    <div><Search availableSubjects={data.subjects} /></div>
  </div>

  <div class="flex flex-grow gap-4 p-4">
    <div class="w-1/6 p-4">
      <Card.Root>
        <Card.Content class="text-sm font-medium">
          <p>
            {#await data.pagination}
              <span class="font-semibold flex">
                Results:&nbsp; <LoaderCircle
                  class="mr-2 mt-1 h-3 w-3 animate-spin"
                />
              </span>
            {:then pagination}
              Results: <span class="font-normal"
                >{pagination.total_records
                  .toString()
                  .replace(/\B(?=(\d{3})+(?!\d))/g, ",")}</span
              >
            {/await}
          </p>

          <p>
            {#await data.timeToSearch}
              <span class="font-semibold flex">
                Search time:&nbsp; <LoaderCircle
                  class="mr-2 mt-1 h-3 w-3 animate-spin"
                />
              </span>
            {:then timeToSearch}
              Search time: <span class="font-normal">
                {(timeToSearch / 1000).toFixed(2)}s</span
              >
            {/await}
          </p>
        </Card.Content>
      </Card.Root>

      {#await data.categories}
        <center class="mt-10">
          <LoaderCircle class="h-10 w-10 animate-spin" />
        </center>
      {:then categories}
        <div class="mt-4">
          <Facets
            name="Subjects"
            field="categories"
            content={categories}
            rawQuery={data.rawQuery}
          />
        </div>
      {/await}

      {#await data.authors}
        <center class="mt-10">
          <LoaderCircle class="h-10 w-10 animate-spin" />
        </center>
      {:then authors}
        <div class="mt-4">
          <Facets
            name="Authors"
            field="authors"
            content={authors}
            rawQuery={data.rawQuery}
          />
        </div>
      {/await}

      {#await data.foundPerYear}
        <center class="mt-10">
          <LoaderCircle class="h-10 w-10 animate-spin" />
        </center>
      {:then foundPerYear}
        <div class="mt-4">
          <YearChart chartData={foundPerYear} />
        </div>
      {/await}
    </div>

    <div class="w-4/6 overflow-auto">
      <Separator class="bg-slate-950" />

      {#await data.papers}
        <div class="w-full flex items-center space-x-4 mt-5">
          <div class="space-y-2 w-full">
            <Skeleton class="h-4 w-[30%] bg-slate-700" />
            <span class="flex justify-between">
              <Skeleton class="h-4 w-[40%] bg-slate-700" />
              <Skeleton class="h-4 w-[5%] bg-slate-700" />
            </span>
            <Skeleton class="ml-[1%] h-4 w-[99%] bg-slate-700" />
            <Skeleton class="ml-[1%] h-4 w-[99%] bg-slate-700" />
            <Skeleton class="ml-[1%] h-4 w-[99%] bg-slate-700" />
            <Skeleton class="ml-[1%] h-4 w-[80%] bg-slate-700" />
            <Skeleton class="h-4 w-[20%] bg-slate-700" />
          </div>
        </div>
      {:then papers}
        {#each papers as paper}
          <div class="mb-4">
            <Paper {paper} />
          </div>
        {/each}
      {/await}

      {#await data.pagination then pagination}
        <Pagination.Root
          count={pagination.total_records}
          perPage={pagination.size}
          page={pagination.current_page + 1}
          let:pages
        >
          <Pagination.Content>
            <Pagination.Item>
              <Pagination.PrevButton
                on:click={() => {
                  goToPage(pagination.current_page - 1);
                }}
              />
            </Pagination.Item>

            {#each pages as page (page.key)}
              {#if page.type === "ellipsis"}
                <Pagination.Item>
                  <Pagination.Ellipsis />
                </Pagination.Item>
              {:else}
                <Pagination.Item>
                  <Pagination.Link
                    {page}
                    isActive={pagination.current_page + 1 === page.value}
                    on:click={() => goToPage(page.value - 1)}
                  >
                    {page.value}
                  </Pagination.Link>
                </Pagination.Item>
              {/if}
            {/each}

            <Pagination.Item>
              <Pagination.NextButton
                on:click={() => {
                  goToPage(pagination.current_page + 1);
                }}
              />
            </Pagination.Item>
          </Pagination.Content>
        </Pagination.Root>
      {/await}
    </div>

    <div class="w-1/6"></div>
  </div>
</div>
