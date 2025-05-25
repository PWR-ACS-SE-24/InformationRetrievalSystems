<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import * as Card from "$lib/components/ui/card";

  const { name, content } = $props<{
    name: string;
    content: { displayValue: string; value: string; count: number }[];
  }>();
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>{name}</Card.Title>
  </Card.Header>
  <Card.Content>
    <div>
      {#each content as item}
        <Button variant="ghost" class="w-full text-sm">
          <div class="flex justify-between w-full">
            <span class="break-words whitespace-normal text-left"
              >{item.displayValue}</span
            >
            <span class="text-right text-gray-500 ml-2">({item.count})</span>
          </div>
        </Button>
      {/each}
    </div>
  </Card.Content>
</Card.Root>
