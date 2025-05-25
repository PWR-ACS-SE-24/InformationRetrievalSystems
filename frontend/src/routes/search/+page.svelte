<script lang="ts">
  import * as Pagination from "$lib/components/ui/pagination";
  import type { PageProps } from "./$types";
  import { Paper } from "$lib/components/custom/paper";
  import { Search } from "$lib/components/custom/search";
  import { Separator } from "$lib/components/ui/separator";
  import { goto } from "$app/navigation";

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
    <div class="w-1/6 bg-slate-200">
      <center>
        <p>
          Results: {data.pagination.total_records
            .toString()
            .replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
        </p>
        <p>Search time: {(data.time_to_search / 1000).toFixed(2)}s</p>
      </center>
    </div>

    <div class="w-4/6 overflow-auto">
      <Separator class="bg-slate-950" />

      {#each data.papers as paper}
        <div class="mb-4">
          <Paper {paper} />
        </div>
      {/each}

      <Pagination.Root
        count={data.pagination.total_records}
        perPage={data.pagination.size}
        page={data.pagination.current_page + 1}
        let:pages
      >
        <Pagination.Content>
          <Pagination.Item>
            <Pagination.PrevButton
              on:click={() => {
                goToPage(data.pagination.current_page - 1);
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
                  isActive={data.pagination.current_page + 1 === page.value}
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
                goToPage(data.pagination.current_page + 1);
              }}
            />
          </Pagination.Item>
        </Pagination.Content>
      </Pagination.Root>
    </div>

    <div class="w-1/6"></div>
  </div>
</div>
