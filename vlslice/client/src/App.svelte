<script>
	import { slide } from 'svelte/transition';
	import { onMount } from 'svelte';
	import * as d3 from "d3";

	// Vars to make Eric's life easier
	const DEV = true;

	// Filtering Variables
	let fltrBaseline = null;
	let fltrAugment = null;
	let fltrK = null;
	let enableFilter = true;
	let sortReverse = true;
	let sortKey = 'mean';
	let fltrBounds = {'mean': null, 'var': null, 'size': null};

	// Cluster Summary
	const fields = ['mean', 'size', 'var'];
	const fieldsLong = {'mean': 'mean', 'size': 'size', 'var': 'variance'};
	let scaleMean = d3.scaleLinear().domain([0, 1]);
	let scaleSize = d3.scaleLinear();
	let scaleVar = d3.scaleLinear();

	// Image store
	let clusters = [];
	$: userClusters = clusters.filter((c) => c.userList);
	$: filteredClusters = clusters.filter((c) => 
		   (!fltrBounds['mean'] || (fltrBounds['mean'][0] <= c.mean && c.mean <= fltrBounds['mean'][1])) 
		&& (!fltrBounds['var']  || (fltrBounds['var'][0]  <= c.var  && c.var  <= fltrBounds['var'][1]))
		&& (!fltrBounds['size'] || (fltrBounds['size'][0] <= c.size && c.size <= fltrBounds['size'][1]))
	);

	onMount(async () => {
		// Run a default query if developing
		if (DEV) {
			fltrBaseline = 'A photo of a person';
			fltrAugment = 'A photo of a CEO';
			fltrK = 100;
			filter();
		}
	});

	function createFilters() {
		fltrBounds = {'mean': null, 'var': null, 'size': null};
		fields.forEach(f => {
			const spec = {
				$schema: 'https://vega.github.io/schema/vega-lite/v5.json',
				description: `Histogram for ${f}`,
				data: {values: clusters},
				params: [{
						name: "select",
						select: {type: "interval", encoding: ["x"]}
					}],
				mark: {
					type: 'bar',
					fill: cssToHSL('--n'),
					stroke: cssToHSL('--s')
				},
				encoding: {
					x: {
						title : fieldsLong[f],
						bin: {maxbins: 50},
						field: f,
					},
					y: {
						title: 'count',
						aggregate: 'count',
						scale: {type: f == 'mean' ? 'linear' : 'symlog'}
					},
					strokeWidth: {
						condition: [
							{
								param: "select",
								empty: false,
								value: 1
							}

						],
						value: 0
					}
				}
			};
			vegaEmbed(`#filter-${f}`, spec, {"actions": false}).then(function(result) {
				result.view.addSignalListener('select', function(signalName, e) {
					if (f in e) {
						fltrBounds[f] = e[f];
					} else {
						fltrBounds[f] = null;
					}
					console.log(signalName + " " + e);
					console.log(e);
				})
			});
		});
	}

	function cssToHSL(varId) {
		let hsl = getComputedStyle(document.querySelector(':root')).getPropertyValue(varId);
		return `hsl(${hsl})`;
	}

	function filter() {
		if (fltrBaseline != null && fltrAugment != null && fltrK != null) {
			console.log('Fetching filtered photos...')

			// Disable filtering and clear clusters
			enableFilter = false;

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
				console.log('Assigning new clusters...')
				clusters = jsonData;
				sort()
				for (let i = 0; i < clusters.length; i++) {
					clusters[i].showMore = false;
					clusters[i].showSimilar = false;
					clusters[i].showCounter = false;
					clusters[i].userList = false;
				}
				console.log(clusters);
			}).then(function() {
				console.log('Scaling to new clusters...')

				// Setup scaling for summary bars
				let vMax = Math.max(...clusters.map(c => c.var));
				let cMax = Math.max(...clusters.map(c => c.size));

				let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
				let range = [0, cw - 115];
				scaleMean = scaleMean.range(range);
				scaleVar = scaleVar.domain([0, vMax]).range(range);
				scaleSize = scaleSize.domain([0, cMax]).range(range);

				// Re-enable the filter
				createFilters();
				enableFilter = true;
			});
		} else {
			console.log('Null values...')
			createFilters();
			enableFilter = true;
		}
	}

	function showSimilar(clstr, enable) {
		clstr.showSimilar = enable;
		clusters = clusters;
	}

	function showCounter(clstr, enable) {
		clstr.showCounter = enable;
		clusters = clusters;
	}

	function sort() {
		clusters.sort(function(a, b) {
			let x = a[sortKey];
			let y = b[sortKey];
			return ((x < y) ? -1 : ((x > y) ? 1 : 0));
		});
		if (sortReverse) {
			clusters.reverse();
		}
		clusters = clusters;
	}

	function reverseSort() {
		sortReverse = !sortReverse;
		clusters.reverse();
		clusters = clusters;
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

		<!-- Filter to TopK -->
		<div class="w-full w-auto max-w-xs">
			<label class="label" for="filter-topk" >
				<span class="label-text">TopK</span>
			</label>
			<div id="filter-topk" class="input-group">
				<input class="input input-bordered w-full" type="number" placeholder="1000" bind:value={fltrK}/>
				<button class="btn" disabled="{enableFilter ? null : 'disabled'}" type="submit" on:click={filter}>
					Filter
					<i class="fa-solid fa-cog ml-1" class:fa-spin={!enableFilter}></i>
				</button>
			</div>
		</div>

		<!-- Sorting -->
		<div class="w-full max-w-xs">
			<label class="label" for="sort" >
				<span class="label-text">Sort Clusters By...</span>
			</label>
			<div id="sort" class="input-group">
				<select class="select select-bordered" bind:value={sortKey} on:change={sort}>
					<option value="mean" selected>DC Mean</option>
					<option value="var">DC Variance</option>
					<option value="size">Size</option>
				</select>
				<button class="btn" on:click={reverseSort}>
					{#if sortReverse}
						<i class="fa-solid fa-arrow-down"></i>
					{:else}
						<i class="fa-solid fa-arrow-up"></i>
					{/if}
				</button>
			</div>
		</div>
	</div>
	<br>

	<div id="filter-mean"></div>
	<div id="filter-var"></div>
	<div id="filter-size"></div>

	<!-- USER CLUSTER DISPLAY -->
	<div class="collapse">
		<input type="checkbox"/> 
		<div class="collapse-title text-2xl font-medium">
			<div class="indicator" on:click="{(e) => e.target.parentElement.previousElementSibling.click()}">
				<span class="indicator-item badge badge-primary">{userClusters.length}</span> 
				User List
			</div>
			<div class="divider"></div>
		</div>
		<div class="collapse-content"> 
			TODO
		</div>
	</div>

	<!-- AI CLUSTER DISPLAY -->
	<div class="collapse">
		<input type="checkbox"/> 
		<div class="collapse-title text-2xl font-medium">
			<div class="indicator" on:click="{(e) => e.target.parentElement.previousElementSibling.click()}">
				<span class="indicator-item badge badge-primary">{filteredClusters.length}</span> 
				Clusters
			</div>
			<div class="divider"></div>
		</div>
		<div class="collapse-content"> 
		{#each filteredClusters as clstr (clstr.id)}
			<div class="cluster w-full grid grid-cols-8 mb-24">
				<!-- Summary -->
				<div class="col-span-2 cluster-summary">

					<!-- Bars -->
					<svg id="summary-{clstr.id}" width="100%" height="60">

						<!-- Cluster mean -->
						<g transform="translate(0, 0)">
							<text x="60" y="10" dominant-baseline="middle" text-anchor="end" fill="hsl(var(--bc))">
								Mean</text>
							<rect x="65" y="5" width="{scaleMean(Math.abs(clstr.mean))}" height="10" 
								fill={clstr.mean > 0 ? "hsl(var(--su))" : "hsl(var(--er))"}/>
							<text x="{70 + scaleMean(Math.abs(clstr.mean))}" y="10" dominant-baseline="middle" 
								fill="hsl(var(--b3))">({clstr.mean > 0 ? '+' : ''}{clstr.mean.toFixed(2)})</text>
						</g>

						<!-- Cluster variance -->
						<g transform="translate(0, 20)">
							<text x="60" y="10" dominant-baseline="middle" text-anchor="end" fill="hsl(var(--bc))">
								Variance</text>
							<rect x="65" y="5" fill="hsl(var(--n))" width="{scaleVar(clstr.var)}" height="10"/>
							<text x="{70 + scaleVar(clstr.var)}" y="10" dominant-baseline="middle" 
								fill="hsl(var(--b3))">({clstr.var.toFixed(2)})</text>
						</g>

						<!-- Cluster size -->
						<g transform="translate(0, 40)">
							<text x="60" y="10" dominant-baseline="middle" text-anchor="end" fill="hsl(var(--bc))">
								Size</text>
							<rect x="65" y="5" fill="hsl(var(--n))" width="{scaleSize(clstr.size)}" height="10"/>
							<text x="{70 + scaleSize(clstr.size)}" y="10" dominant-baseline="middle" 
								fill="hsl(var(--b3))">({clstr.size})</text>
						</g>
					</svg>
					

					<!-- Selector Buttons -->
					<div class="flex flex-wrap justify-center">
						<button class="btn btn-xs w-1/3 mx-2 my-1" on:click="{() => clstr.userList = true}">Add to List</button>
						<button class="btn btn-xs w-1/3 mx-2 my-1" on:click="{() => clstr.userList = false}">Add to Last</button>
						<button class="btn btn-xs btn-outline btn-success w-1/3 mx-2 my-1">Select All</button>
						<button class="btn btn-xs btn-outline btn-error w-1/3 mx-2 my-1">Deselect All</button>
					</div>
				</div>

				<!-- Images -->
				<div class="col-span-5" id="cluster-{clstr.id}">
					<div class="grid grid-cols-12 gap-px mb-px">
						{#each clstr.images.slice(0, 12) as img (img.id)}
							<img id="img-{img.id}" alt="Filtered dataset sample" on:click="{() => console.log(img.id)}"  
								src="data:image/png;base64,{img.b64}" width="128" height="128"/>
						{/each}
					</div>

					{#if clstr.showMore}
						<div class="grid grid-cols-12 gap-px" transition:slide>
							{#each clstr.images.slice(13, clstr.images.length) as img (img.id)}
								<img id="img-{img.id}" alt="Filtered dataset sample" on:click="{() => console.log(img.id)}"  
									src="data:image/png;base64,{img.b64}" width="128" height="128"/>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Drop Downs -->
				<div class="form-control justify-start">
					<label class="label cursor-pointer justify-start">
						<input type="checkbox" class="toggle mr-1" bind:checked={clstr.showMore} 
							disabled={clstr.images.length <= 12}/>
						<span class="label-text" class:disable-span="{clstr.images.length <= 12 ? 'hsl(var(--b3))' : ''}">
							Show More</span> 
					</label>
					<label disabled class="label cursor-pointer justify-start">
						<input type="checkbox" class="toggle mr-1" bind:checked={clstr.showSimilar} />
						<span class="label-text">Show Similar</span> 
					</label>
					<label class="label cursor-pointer justify-start">
						<input type="checkbox" class="toggle mr-1" bind:checked={clstr.showCounter} />
						<span class="label-text">Show Counterfactual</span> 
					</label>
				</div>
			</div>
		{/each}
		</div>
	</div>
	</div>
</main>

<style>
	.cluster-summary {
		display: flex;
		flex-direction: column;
	}

	.disable-span {
		color: hsl(var(--b3));
		cursor: not-allowed;
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
