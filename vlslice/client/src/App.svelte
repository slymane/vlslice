<script>	
	import * as d3 from "d3";
	import HistogramFilter from './components/HistogramFilter.svelte';
    import ClusterRow from './components/ClusterRow.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import Section from './components/Section.svelte';
	import { clusterStore } from './store.js';

	// Filtering variables
	let enableFilter = true;
	let fltrBounds = {'mean': null, 'variance': null, 'size': null};

	// Cluster Summary
	let scaleMean = d3.scaleLinear().domain([0, 1]);
	let scaleSize = d3.scaleLinear();
	let scaleVariance = d3.scaleLinear();

	// Clusters and cluster metadata
	let clusters = [];
	let nClustersDisplayed = null;

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
				clusters[i].isDisplayed = true;
			}
			sortClusters(e);
			clusterStore.set(clusters)
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

	function isBounded(x, low, high) {
		return low <= x && x <= high;
	}

	function isDisplayed(cluster, bounds) {
		let meanValid     = !bounds['mean']     || isBounded(cluster.mean,     ...bounds['mean']);
		let varianceValid = !bounds['variance'] || isBounded(cluster.variance, ...bounds['variance']);
		let sizeValid     = !bounds['size']     || isBounded(cluster.size,     ...bounds['size']);
		return meanValid && varianceValid && sizeValid;
	}

	// Reactivly set some cluster attributes
	$: {
		let display;
		nClustersDisplayed = 0;
		for (let i = 0; i < clusters.length; i++) {
			display = isDisplayed(clusters[i], fltrBounds);
			clusters[i].isDisplayed = display;
			nClustersDisplayed += display;
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
	<Section badge={0}>
		<span slot="title">User List</span>
		<svelte:fragment slot="content">TODO</svelte:fragment>
	</Section>

	<!-- GENERATED CLUSTER DISPLAY -->
	<Section badge={nClustersDisplayed}>
		<span slot="title">Clusters</span>
		<svelte:fragment slot="content">
			{#each clusters as cluster (cluster.id)}
				{#if cluster.isDisplayed}
					<ClusterRow {cluster} {scaleMean} {scaleVariance} {scaleSize}/>
				{/if}
			{/each}
		</svelte:fragment>
	</Section>
</main>
