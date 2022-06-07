<script>	
	import { onMount } from 'svelte';
	import * as d3 from "d3";
	import HistogramFilter from './components/HistogramFilter.svelte';
    import ClusterRow from './components/ClusterRow.svelte'

	// Variables to make Eric's life easier
	const DEV = true;

	// Filtering variables
	let fltrBaseline = null;
	let fltrAugment = null;
	let fltrK = null;
	let enableFilter = true;
	let sortReverse = true;
	let sortKey = 'mean';
	let fltrBounds = {'mean': null, 'variance': null, 'size': null};

	// Cluster Summary
	let scaleMean = d3.scaleLinear().domain([0, 1]);
	let scaleSize = d3.scaleLinear();
	let scaleVariance = d3.scaleLinear();

	// Image store
	let clusters = [];

	onMount(async () => {
		// Run a default query if developing
		if (DEV) {
			fltrBaseline = 'A photo of a person';
			fltrAugment = 'A photo of a CEO';
			fltrK = 100;
			filter();
		}
	});

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
				let vMax = Math.max(...clusters.map(c => c.variance));
				let cMax = Math.max(...clusters.map(c => c.size));

				let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
				let range = [0, cw - 115];
				scaleMean = scaleMean.range(range);
				scaleVariance = scaleVariance.domain([0, vMax]).range(range);
				scaleSize = scaleSize.domain([0, cMax]).range(range);

				// Re-enable the filter
				enableFilter = true;
			});
		} else {
			console.log('Null values...')
			enableFilter = true;
		}
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
					<option value="variance">DC Variance</option>
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

	<!-- Histogram Based Filtering -->
	<div>
		<HistogramFilter data={clusters} fieldName="mean" bind:bounds={fltrBounds['mean']}/>
		<HistogramFilter data={clusters} fieldName="variance" bind:bounds={fltrBounds['variance']} scaleY="symlog"/>
		<HistogramFilter data={clusters} fieldName="size" bind:bounds={fltrBounds['size']} scaleY="symlog"/>
	</div>


	<!-- USER CLUSTER DISPLAY -->
	<div class="collapse">
		<input type="checkbox"/> 
		<div class="collapse-title text-2xl font-medium">
			<div class="indicator" on:click="{(e) => e.target.parentElement.previousElementSibling.click()}">
				<span class="indicator-item badge badge-primary">{0}</span> 
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
				<span class="indicator-item badge badge-primary">{clusters.length}</span> 
				Clusters
			</div>
			<div class="divider"></div>
		</div>
		<div class="collapse-content"> 
			{#each clusters as cluster (cluster.id)}
			{#if (!fltrBounds['mean'] 
					|| (fltrBounds['mean'][0] <= cluster.mean && cluster.mean <= fltrBounds['mean'][1])) 
			&& (!fltrBounds['variance'] 
					|| (fltrBounds['variance'][0] <= cluster.variance && cluster.variance <= fltrBounds['variance'][1]))
			&& (!fltrBounds['size'] 
					|| (fltrBounds['size'][0] <= cluster.size && cluster.size <= fltrBounds['size'][1]))}
                <ClusterRow {cluster} {scaleMean} {scaleVariance} {scaleSize}/>
			{/if}
			{/each}
		</div>
	</div>
</main>

<style>
	#controls {
		display: flex;
		justify-content: flex-start;
		align-items: flex-end;
		flex-direction: row;
	}

	#controls > * {
		margin: 5px 5px 5px 5px;
	}
</style>
