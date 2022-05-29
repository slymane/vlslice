<script>
	import * as d3 from "d3";

	// Filtering Variables
	let fltrBaseline = null;
	let fltrAugment = null;
	let fltrK = null;
	let enableFilter = true;

	// Cluster Summary
	let scaleMean = d3.scaleLinear().domain([0, 1]);
	let scaleSize = d3.scaleLinear();
	let scaleVar = d3.scaleLinear();

	// Image store
	let clusters = [];

	function filter() {
		if (fltrBaseline != null && fltrAugment != null && fltrK != null) {
			console.log('Fetching filtered photos...')

			// Disable filtering and clear clusters
			enableFilter = false;
			clusters = [];

			// Fetch new clustering from the server
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
				console.log('Asigning new clusters...')
				clusters = jsonData;
				console.log(clusters);
			}).then(function() {
				console.log('Scaling to new clusters...')

				// Setup scaling for summary bars
				let vMax = Math.max(...clusters.map(c => c.var));
				let cMax = Math.max(...clusters.map(c => c.count));

				let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
				let range = [0, 0.70 * cw]
				scaleMean = scaleMean.range(range);
				scaleVar = scaleVar.domain([0, vMax]).range(range);
				scaleSize = scaleSize.domain([0, cMax]).range(range);

				// Re-enable the filter
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
	<br>

	<!-- CLUSTER DISPLAY -->
	{#each clusters as clstr (clstr.id)}
		<div class="cluster w-full grid grid-cols-4">
			<!-- Summary -->
			<div class="cluster-summary col-span-1" bind>

				<!-- Bars -->
				<div id="summary-{clstr.id}" class="grid grid-rows-3 grid-cols-5 gap-x-4">
					<div class="text-right">Mean</div>
					<div class="col-span-4 summary-bar">
						<svg width="100%" height="20">
							<rect y="5" width="{scaleMean(Math.abs(clstr.mean))}" height="10" 
								fill={clstr.mean > 0 ? "hsl(var(--su))" : "hsl(var(--er))"}
							/>
							<text dominant-baseline="middle" x="{scaleMean(Math.abs(clstr.mean)) + 5}" y="50%" fill="lightgray">
								({clstr.mean > 0 ? '+' : ''}{clstr.mean.toFixed(2)})
							</text>
						</svg>
					</div>

					<div class="text-right">Variance</div>
					<div class="col-span-4 summary-bar">
						<svg width="100%" height="20">
							<rect y="5" width="{scaleVar(clstr.var)}" height="10"/>
							<text dominant-baseline="middle" x="{scaleVar(clstr.var) + 5}" y="50%" fill="lightgray">
								({clstr.var.toFixed(2)})
							</text>
						</svg>
					</div>

					<div class="text-right">Size</div>
					<div class="col-span-4 summary-bar">
						<svg width="100%" height="20">
							<rect y="5" width="{scaleSize(clstr.count)}px" height="10"/>
							<text dominant-baseline="middle" x="{scaleSize(clstr.count) + 5}px" y="50%" fill="lightgray">
								({clstr.count})
							</text>
						</svg>
					</div>
				</div>

				<!-- Selector Buttons -->
				<div>
					TODO
				</div>
			</div>

			<!-- Images -->
			<div class="cluster-images col-span-3 gap-px" id="cluster-{clstr.id}">
				{#each clstr.images as img (img.id)}
					<img id="img-{img.id}" class="m-1 p-0" alt="Filtered dataset sample" on:click="{() => console.log(img.id)}"  
						src="data:image/png;base64,{img.b64}" width="128" height="128"/>
				{/each}
			</div>
		</div>

	{/each}

	</div>
</main>

<style>
	.cluster-summary {
		display: flex;
		flex-direction: column;
	}

	.summary-bar {
		display: flex;
		align-items: center;
	}

	.cluster-images {
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
