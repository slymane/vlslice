<script>	
	import * as d3 from "d3";
	import HistogramFilter from './components/HistogramFilter.svelte';
    import ClusterRow from './components/ClusterRow.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import { clusterStore } from './store.js';

	// Filtering variables
	let enableFilter = true;
	let fltrBounds = {'mean': null, 'variance': null, 'size': null};

	// Cluster Summary
	let scaleMean = d3.scaleLinear().domain([0, 1]);
	let scaleSize = d3.scaleLinear();
	let scaleVariance = d3.scaleLinear();

	// Reactivly set store for clusters for easy access in components
	let clusters = [];

	function filter(e) {
		enableFilter = false;
	
		// Fetch new clustering from the server
		fetch('./filter', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				baseline: e.detail.baseline,
				augment: e.detail.augment,
				k: e.detail.topk,
				w: 0.95,
				dt: 0.18
			})
		})
		.then(r => (r.json()))
		.then(function(jsonData) {
			console.log('Assigning new clusters...')
			clusters = jsonData;
			for (let i = 0; i < clusters.length; i++) {
				clusters[i].showMore = false;
				clusters[i].showSimilar = false;
				clusters[i].showCounter = false;
				clusters[i].userList = false;
			}
			sortClusters(e);
			clusterStore.set(clusters)
			console.log(clusters);
		}).then(function() {
			// Setup scaling for summary bars
			let vMax = Math.max(...clusters.map(c => c.variance));
			let cMax = Math.max(...clusters.map(c => c.size));

			let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
			let range = [0, cw - 115];
			scaleMean = scaleMean.range(range);
			scaleVariance = scaleVariance.domain([0, vMax]).range(range);
			scaleSize = scaleSize.domain([0, cMax]).range(range);
			enableFilter = true;
		});
	}

	function sortClusters(e) {
		clusters.sort(function(a, b) {
			let x = a[e.detail.sortKey];
			let y = b[e.detail.sortKey];
			return ((x < y) ? -1 : ((x > y) ? 1 : 0));
		});
		if (e.detail.sortReverse) {
			clusters.reverse();
		}
		clusters = clusters;
	}

	function reverseClusters(e) {
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

	<!-- TOOL BAR -->
	<Toolbar {enableFilter} on:filter={filter} on:sort={sortClusters} on:reverse={reverseClusters}/>
	<br>

	<!-- Histogram Based Filtering -->
	<div>
		<HistogramFilter fieldName="mean" bind:bounds={fltrBounds['mean']}/>
		<HistogramFilter fieldName="variance" bind:bounds={fltrBounds['variance']} scaleY="symlog"/>
		<HistogramFilter fieldName="size" bind:bounds={fltrBounds['size']} scaleY="symlog"/>
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

</style>
