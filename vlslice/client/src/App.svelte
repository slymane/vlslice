<script>
	// Filtering Variables
	let fltrBaseline = null;
	let fltrAugment = null;
	let fltrK = null;
	let enableFilter = true;

	// Image store
	let clusters = [];

	function filter() {
		if (fltrBaseline != null && fltrAugment != null && fltrK != null) {
			console.log('Fetching filtered photos...')
			enableFilter = false;
			clusters = [];

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
				enableFilter = true;
			});
		} else {
			console.log('Null values...')
			enableFilter = true;
		}
	}
  </script>

<main class="max-w-none">
	<!-- TITLE/NAV BAR -->
	<div class="navbar bg-neutral text-neutral-content">
		<h1 class="normal-case text-4xl p-4">VLSlice</h1>
	</div>

	<!-- MAIN CONTENT -->
	<div id="content" class="p-4">

	<!-- CLUSTER QUERY CONTROLS -->
	<div id='controls' class="form-control w-full">

		<!-- Baseline text Input -->
		<div class="w-full max-w-xs">
			<label class="label" for="filter-baseline" >
				<span class="label-text">Baseline Text</span>
			</label>
			<input id="filter-baseline" class="input input-bordered w-full" 
				type="text" placeholder="A photo of a person" bind:value={fltrBaseline}/>
		</div>

		<!-- Augmented Text Input -->
		<div class="w-full max-w-xs">
			<label class="label" for="filter-augment" >
				<span class="label-text">Augmented Text</span>
			</label>
			<input id="filter-augment" class="input input-bordered w-full" 
				type="text" placeholder="A photo of a ceo" bind:value={fltrAugment}/>
		</div>

		<!-- TopK to Return -->
		<div class="w-auto max-w-xs">
			<label class="label" for="filter-topk" >
				<span class="label-text">TopK</span>
			</label>
			<input id="filter-topk" class="input input-bordered w-full" 
				type="number" placeholder="1000" bind:value={fltrK}/>
		</div>

		<!-- Submit -->
		<div>
			<progress class:hidden="{enableFilter}" class="progress"></progress>
			<button class="btn" disabled="{enableFilter ? null : 'disabled'}" type="submit" on:click={filter}>Filter</button>
		</div>
	</div>

	<!-- CLUSTER DISPLAY -->
	{#each clusters as clstr (clstr.id)}
		<div class="cluster gap-px" id="cluster-{clstr.id}">
			{#each clstr.images as img (img.id)}
				<img id="img-{img.id}" class="m-1 p-0" alt="Filtered dataset sample" on:click="{() => console.log(img.id)}"  
					src="data:image/png;base64,{img.b64}" width="128" height="128"/>
			{/each}
		</div>
	{/each}

	</div>
</main>

<style>
	.cluster {
		display: flex;
		flex-wrap: wrap;
		border: 1px solid black;
	}

	#controls {
		display: flex;
		justify-content: flex-start;
		align-items: flex-end;
		flex-direction: row;
	}

	#controls > * {
		margin: 5px 5px 5px 5px;
	}

	#images {
		display: flex;
		justify-content: flex-start;
		align-content: center;
		flex-wrap: wrap;
	}
</style>