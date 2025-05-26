<script lang="ts">
  import { BarChart } from "layerchart";
  import * as Card from "$lib/components/ui/card";

  const { chartData } = $props<{
    chartData: { year: string; value: number }[];
  }>();
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Papers per year</Card.Title>
  </Card.Header>
  <Card.Content>
    <div class="h-[750px] p-4 border rounded">
      <BarChart
        data={chartData}
        x="value"
        y="year"
        orientation="horizontal"
        yReverse
        axis="y"
        props={{ bars: { class: "fill-primary " } }}
      />
    </div>
  </Card.Content>
</Card.Root>
