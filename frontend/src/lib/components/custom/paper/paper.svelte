<script lang="ts">
  import type { components } from "$lib/generated/backend-openapi";
  import { Separator } from "$lib/components/ui/separator/index.js";
  type ArxivPaperModelBase = components["schemas"]["ArxivPaperModelBase"];

  const { paper } = $props<{ paper: ArxivPaperModelBase }>();
  const humanReadableDate = new Date(paper.update_date).toLocaleDateString(
    "en-UK",
    {
      year: "numeric",
      month: "numeric",
      day: "numeric",
    }
  );
</script>

<div class="">
  <a
    href={`https://arxiv.org/abs/${paper.arxiv_id}`}
    target="_blank"
    class="text-blue-500 hover:underline"
  >
    <h1 class="text-2xl font-bold">{paper.title}</h1>
  </a>

  <div class="flex justify-between">
    <p>
      {#each paper.authors as author, i}
        {author}{#if i < paper.authors.length - 1},&nbsp;{/if}
      {/each}
    </p>

    <p class="ml-4">{paper.create_date.substring(0, 4)}</p>
  </div>

  <p>
    Subjects:
    {#each paper.categories as category, i}
      {#if i === 0}
        <span class="font-medium">{category}</span
        >{#if i < paper.categories.length - 1},&nbsp;{/if}
      {:else}
        {category}{#if i < paper.categories.length - 1},&nbsp;{/if}
      {/if}
    {/each}
  </p>

  <p class="text-xs text-justify ml-2">
    {paper.abstract}
  </p>

  <div class="flex text-xs">
    Last updated: {humanReadableDate}{#if paper.comments}, Comments: {paper.comments}{/if}
  </div>

  <div class="text-xs">
    DOI:
    {#if paper.journal_ref}
      <a
        href={`https://doi.org/${paper.doi}`}
        target="_blank"
        class="text-blue-500 hover:underline"
      >
        {paper.doi}
      </a>
    {:else}
      <a
        href={`https://doi.org/10.48550/arXiv.${paper.arxiv_id}`}
        target="_blank"
        class="text-blue-500 hover:underline"
      >
        10.48550/arXiv.{paper.arxiv_id}
      </a>
    {/if}
  </div>

  <center><Separator class="bg-slate-400 w-1/2 mt-2" /></center>
</div>
