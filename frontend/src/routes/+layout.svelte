<script lang="ts">
  import "../app.css";
  let { children } = $props();
</script>

<div class="min-h-screen flex flex-col">
  <main class="flex-grow">
    {@render children()}
  </main>
  <footer class="bg-gray-100 text-center text-sm text-gray-600 py-4">
    © 2025 Przemysław Barcicki 260324, Jakub Zehner 260285. All rights
    reserved.
  </footer>
</div>
