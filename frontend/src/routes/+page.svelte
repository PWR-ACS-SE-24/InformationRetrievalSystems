<script lang="ts">
  import search from "$lib/assets/search.svg";
  import { subjects } from "$lib/subjects";
  import RangeSlider from "svelte-range-slider-pips";

  const slider_min = 1986;
  const slider_max = new Date().getFullYear();

  let searchQuery = "";
  let author = "";
  let subject = "";

  let values = [1986, 2025];

  function handleSelectChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    subject = target.value;
    target.classList.remove("untouched");
  }
</script>

<div class="search-container">
  <h1>arXiv paper search</h1>

  <div class="input-group search-bar">
    <span class="icon">
      <img src={search} alt="Search icon" width="16" height="16" />
    </span>
    <input
      type="text"
      placeholder="Search"
      bind:value={searchQuery}
      aria-label="Query"
    />
  </div>

  <div class="input-group">
    <input
      type="text"
      placeholder="Author"
      bind:value={author}
      aria-label="Author"
    />

    <select
      bind:value={subject}
      on:change={handleSelectChange}
      class="untouched"
      aria-label="Subject"
    >
      <option selected hidden disabled value="">Subject</option>
      {#each subjects as category}
        <option value={category.id}>{category.name}</option>
        {#each category.subcategories as subcat}
          <option value={subcat.id}>&nbsp;&nbsp;{subcat.name}</option>
        {/each}
      {/each}
    </select>
  </div>

  <div class="range-wrapper">
    <RangeSlider
      range
      float
      pips
      pushy
      first="label"
      last="label"
      min={slider_min}
      max={slider_max}
      bind:values
    />
  </div>

  <button class="search-button">Search</button>
</div>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin="anonymous"
  />
  <link
    href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100..900;1,100..900&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<style>
  :global(body) {
    background: #f5f5f5;
    font-family: "Roboto", sans-serif;
    font-optical-sizing: auto;
    font-style: normal;
    font-variation-settings: "wdth" 100;
  }

  :global(input) {
    font-family: unset;
  }

  ::placeholder {
    /* TODO: placeholder color is set by hand */
    color: #999;
  }

  .search-container {
    max-width: 400px;
    margin: auto;
    text-align: center;

    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100vh;
    padding: 0rem;
  }

  h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .input-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .input-group input,
  .input-group select {
    flex: 1;
    padding: 0.5rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid #ccc;
    outline: none;
    transition: border-color 0.2s ease;
  }

  .input-group input:focus,
  .input-group select:focus {
    border-color: #0c8ce9;
  }

  .search-bar {
    position: relative;
  }

  .search-bar .icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    width: 16px;
    height: 16px;
    fill: #888;
  }

  .search-bar input {
    padding-left: 2rem;
    width: 100%;
  }

  select.untouched {
    color: #999;
  }
  select option {
    padding-left: 3rem;
    color: #000;
  }

  /* Wcięcie dla podkategorii w dropdown */
  select option[value^="cs."],
  select option[value^="econ."],
  select option[value^="eess."],
  select option[value^="math."],
  select option[value^="physics."],
  select option[value^="astro-ph."],
  select option[value^="q-bio."],
  select option[value^="q-fin."],
  select option[value^="stat."] {
    padding-left: 1.5rem;
  }

  .range-wrapper {
    padding-top: 0.5rem;
    width: 100%;
    max-width: 100%;
    margin-bottom: 1rem;
  }

  .search-button {
    background-color: #0c8ce9;
    color: white;
    padding: 0.6rem 1.2rem;
    border: none;
    font-size: 1rem;
    border-radius: 6px;
    cursor: pointer;
  }

  .search-button:hover {
    background-color: #086bbd;
  }

  :root {
    --range-slider: #d7dada;
    --range-handle-inactive: #0c8ce9;
    --range-handle: #0c8ce9;
    --range-handle-focus: #0c8ce9;
  }
</style>
