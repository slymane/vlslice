<script>
	import { onMount } from 'svelte';

	function filter(baseline, augment) {
		console.log("Running Post")
		fetch('./filter', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				baseline: 'A photo of a person',
				augment: 'A photo of a ceo'
			})
		})
		.then(r => (r.json()))
		.then(function(data) {
			console.log(data)
		});
	}

	let rand = "";
  </script>

<main>
	<h1>Your number is {rand}!</h1>
	<button on:click={filter}>Filter</button>
</main>

<style>
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