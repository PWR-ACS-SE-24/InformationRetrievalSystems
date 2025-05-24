<script lang="ts">
  import { Search } from "$lib/components/custom/search";
  import { Paper } from "$lib/components/custom/paper";
  import { Separator } from "$lib/components/ui/separator";
  import SuperDebug from "sveltekit-superforms";
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();
</script>

<div class="min-h-[calc(100vh-64px)] flex flex-col">
  <div class="flex items-center justify-center mb-1">
    <div><Search availableSubjects={data.subjects} /></div>
  </div>

  <div class="flex flex-grow gap-4 p-4">
    <div class="w-1/6 bg-slate-200">Panel boczny</div>
    <div class="w-4/6 overflow-auto">
      <Separator class="bg-slate-950" />
      {#each data.papers as paper}
        <div class="mb-4">
          <Paper {paper} />
        </div>
      {/each}
    </div>
    <div class="w-1/6"></div>
  </div>
</div>
