<script>
  import RangeSlider from "svelte-range-slider-pips";

  let slider_min = 1986; // Found in the dataset using script that probably works just fine
  let slider_max = new Date().getFullYear();

  let values = [1986, 2025];
</script>

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

  <code>DEBUG: bind:values={"{values}"}</code> ( <code>{values}</code> )
</div>

<style>
  :root {
    --range-slider: #d7dada; /* slider main background color */
    --range-handle-inactive: #0c8ce9; /* inactive handle color */
    --range-handle: #0c8ce9; /* non-focussed handle color */
    --range-handle-focus: #0c8ce9; /* focussed handle color */
  }

  .range-wrapper {
    margin-left: 20vw;
    margin-right: 20vw;
    margin-top: 20vh;
  }
</style>
