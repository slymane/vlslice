<script>
	let rand = -1;
	function getRand() {
	  fetch("./rand")
		.then(d => d.text())
		.then(d => (rand = d));
	}
  </script>

<main>
	<h1>Your number is {rand}!</h1>
	<button on:click={getRand}>Get a random number</button>
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