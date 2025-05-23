<script>
  import { DoubleRangeSlider } from "$components";

  let slider_min = 1986; // Found in the dataset using script that probably works just fine
  let slider_max = new Date().getFullYear();

  let start = slider_min;
  let end = slider_max;
</script>

<DoubleRangeSlider
  min={slider_min}
  max={slider_max}
  width="300px"
  bind:start
  bind:end
/>
