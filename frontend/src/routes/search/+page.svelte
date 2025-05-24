<script lang="ts">
  import { Search } from "$lib/components/custom/search";
  import SuperDebug from "sveltekit-superforms";
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();
</script>

<div class="min-h-[calc(100vh-64px)] flex items-center justify-center">
  <div>
    <center><h1>In progress search</h1></center>
    <br />
    <Search availableSubjects={data.subjects} />
    <br />
    <SuperDebug
      data={{
        query: data.q,
        author: data.author,
        published: data.published,
        min_year: data.minYear,
        max_year: data.maxYear,
        subjects: data.selectedSubjects,
      }}
    />
  </div>
</div>
