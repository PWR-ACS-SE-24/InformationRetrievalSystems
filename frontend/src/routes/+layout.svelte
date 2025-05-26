<script lang="ts">
  import "../app.css";
  let { children } = $props();
</script>

<div class="min-h-screen flex flex-col bg-slate-50">
  <main class="flex-grow">
    {@render children()}
  </main>
  <footer class="bg-slate-200 text-center text-sm text-slate-700 py-4">
    © 2025 Przemysław Barcicki 260324, Jakub Zehner 260285. All rights
    reserved.
  </footer>
</div>
