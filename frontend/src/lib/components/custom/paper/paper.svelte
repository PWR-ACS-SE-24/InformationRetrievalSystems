<script lang="ts">
  import { Separator } from "$lib/components/ui/separator/index.js";

  type ArxivEntry = {
    doi: string | null;
    submitter: string;
    abstract: string;
    categories: string[];
    title: string;
    arxiv_id: string;
    authors: string[];
    journal_ref: string | null;
    comments: string;
    update_date: string;
  };

  const { paper } = $props<{ paper: ArxivEntry }>();
</script>

<div class="">
  <h1 class="text-2xl font-bold">{paper.title}</h1>

  <!-- To make <p> inside next to each other, first aligned to the left, second to the right -->
  <div class="flex justify-between">
    <p>
      <span class="font-bold">Authors:</span>
      {#each paper.authors as author, i}
        {author}{#if i < paper.authors.length - 1}{", "}{/if}
      {/each}
    </p>

    <p class="font-bold ml-4">{paper.update_date.substring(0, 4)}</p>
  </div>

  <p>
    <span class="font-bold">Subjects:</span>
    {#each paper.categories as category, i}
      {category}{#if i < paper.categories.length - 1}{", "}{/if}
    {/each}
  </p>

  <p class="text-xs text-justify">
    <span class="font-bold">Abstract:</span>
    {paper.abstract}
  </p>

  <center><Separator class="bg-slate-400 w-1/2 mt-2" /></center>
</div>
