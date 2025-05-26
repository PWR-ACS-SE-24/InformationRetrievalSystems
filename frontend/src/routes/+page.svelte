<script lang="ts">
  import { Search } from "$lib/components/custom/search";
  import type { PageProps } from "./$types";

  let { data }: PageProps = $props();
</script>

<div class="min-h-[calc(100vh-64px)] flex items-center justify-center">
  <Search availableSubjects={data.subjects} />
</div>
