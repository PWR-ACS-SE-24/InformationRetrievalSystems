<script lang="ts">
  import { BarChart } from "layerchart";

  const { chartData } = $props<{
    chartData: { year: string; value: number }[];
  }>();
</script>

<div class="h-[750px] p-4 border rounded">
  <BarChart data={chartData} x="value" y="year" orientation="horizontal" />
</div>
