<script>
	import { onMount } from 'svelte';

	let txtBaseline = '';
	let txtAugment = '';
	let images = [];

	function filter(baseline, augment) {
		console.log("Running Post")
		fetch('./filter', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				baseline: txtBaseline,
				augment: txtAugment,
				k: 10,
				w: 0.95,
				dt: 0.18
			})
		})
		.then(r => (r.json()))
		.then(function(jsonData) {
			images = jsonData;
		});
	}
  </script>

<main>
	<h1>VLSlice</h1>
	<input bind:value={txtBaseline} placeholder="Baseline...">
	<input bind:value={txtAugment} placeholder="Augment...">
	<button on:click={filter}>Filter</button>
	<div id='images'>
		{#each images as img (img.id)}
			<img id="img-{img.id}" alt="Filtered dataset sample" src="data:image/png;base64,{img.b64}" width="224" height="224">
		{/each}
	</div>
</main>

<style>
	img {
		padding: 5px;
	}

	main {
		text-align: center;
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

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>