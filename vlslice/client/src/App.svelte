<script>
	import VLSlice from './vlslice.svelte';
	import SimpleInterface from './simple.svelte';
	import { fly } from 'svelte/transition';

	let useSimpleInterface = false;
	let showSuccess = false;
	let showWarning = false;

	let si;
	let vls;
	let code = "";

	function snapshot() {
		console.log("Taking snapshot")
		let data = useSimpleInterface ? si.snapshot() : vls.snapshot();
		data["code"] = code;

		if (code == "") {
			showWarning = true;
			setTimeout(() => showWarning = false, 4000);
		} else {
			fetch('./snapshot', {
				method: 'POST',
				headers: {'Content-Type': 'Application/json'},
				body: JSON.stringify(data)
			})
			.then(r => (r.json()))
			.then(function(jsonData) {
				if (jsonData["status"] == "success") {
					showSuccess = true;
					setTimeout(() => showSuccess = false, 4000);
				}
			});
		}
	}
</script>

<main class="max-w-none relative">

	<!-- TITLE/NAV BAR -->
	<div class="navbar bg-neutral text-neutral-content flex justify-between">
		<h1 class="normal-case text-4xl p-4">
			VLSlice
			<span class="mx-2 opacity-75">|</span>
			<span class="mx-2 opacity-75">
				{#if useSimpleInterface}
					Interface-B
				{:else}
					Interface-A
				{/if}
			</span>
		</h1>

		<div>
			<button class="btn mx-2" on:click={() => useSimpleInterface = !useSimpleInterface}>
				Switch Interfaces
			</button>

			<button class="btn mx-2" on:click={snapshot}>
				Save Snapshot
			</button>

			<input 
				bind:value={code}
				type="text mx-2" 
				placeholder="Code number" 
				class="input input-ghost w-full max-w-xs" 
			/>
		</div>
	</div>

	<!-- MAIN CONTENT -->
	<div id="content" class="p-4">
		{#if useSimpleInterface}
			<SimpleInterface bind:this={si}/>
		{:else}
			<VLSlice bind:this={vls}/>
		{/if}
	</div>

	{#if showSuccess}
		<div transition:fly class="alert alert-success shadow-lg fixed bottom-0">
			<div>
				<i class="fa-regular fa-circle-check"></i>
				<span>Snapshot saved!</span>
			</div>
		</div>
	{/if}

	{#if showWarning}
		<div transition:fly class="alert alert-warning shadow-lg fixed bottom-0">
			<div>
				<i class="fa-solid fa-triangle-exclamation"></i>
				<span>Study code number not entered.</span>
			</div>
		</div>
	{/if}
</main>

<style>

</style>