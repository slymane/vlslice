<script>
	import VLSlice from './vlslice.svelte';
	import SimpleInterface from './simple.svelte'

	let useSimpleInterface = false;
</script>

<main class="max-w-none overflow-y-scroll relative">

	<!-- TITLE/NAV BAR -->
	<div class="navbar bg-neutral text-neutral-content flex justify-between">
		<h1 class="normal-case text-4xl p-4">
			VLSlice
			{#if useSimpleInterface}
				(Interface-B)
			{:else}
				(Interface-A)
			{/if}
		</h1>

		<button class="btn" on:click={() => useSimpleInterface = !useSimpleInterface}>
			Switch Interfaces
		</button>
	</div>

	<!-- MAIN CONTENT -->
	<div id="content" class="p-4">
		{#if useSimpleInterface}
			<SimpleInterface />
		{:else}
			<VLSlice />
		{/if}
	</div>
</main>

<style>

</style>