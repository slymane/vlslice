<script>
	import { onMount } from 'svelte';

	// Filtering Variables
	let fltrBaseline = null;
	let fltrAugment = null;
	let fltrK = null;

	// Image store
	let clusters = [];

	function filter() {
		if (fltrBaseline != null && fltrAugment != null && fltrK != null) {
			console.log('Fetching filtered photos...')
			fetch('./filter', {
				method: 'POST',
				headers: {'Content-Type': 'Application/json'},
				body: JSON.stringify({
					baseline: fltrBaseline,
					augment: fltrAugment,
					k: fltrK,
					w: 0.95,
					dt: 0.18
				})
			})
			.then(r => (r.json()))
			.then(function(jsonData) {
				clusters = jsonData;
			});
		} else {
			console.log('Null values...')
		}
	}
  </script>

<main>
	<h1>VLSlice</h1>

	<div id='controls'>
		<input bind:value={fltrBaseline} placeholder="Baseline...">
		<input bind:value={fltrAugment} placeholder="Augment...">
		<input type=number bind:value={fltrK} placeholder="topk..." min=1 max=10000>
		<button on:click={filter}>Filter</button>
	</div>

	{#each clusters as clstr (clstr.id)}
		<div class="cluster" id="cluster-{clstr.id}">
			{#each clstr.images as img (img.id)}
				<img id="img-{img.id}" alt="Filtered dataset sample" 
					src="data:image/png;base64,{img.b64}" width="128" height="128">
			{/each}
		</div>
	{/each}
</main>

<style>
	.cluster {
		border: 1px solid black;
		margin: 5px;
	}

	img {
		margin: 2px;
		padding: 0px;
	}

	main {
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	#controls {
		display: flex;
		justify-content: flex-start;
		align-content: center;
		align-items: center;
	}

	#images {
		display: flex;
		justify-content: flex-start;
		align-content: center;
		flex-wrap: wrap;
	}

	#controls > * {
		margin: 5px 5px 5px 5px;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>