<script>	
	import * as d3 from "d3";
	import { fade } from 'svelte/transition';
	import HistogramFilter from './components/HistogramFilter.svelte';
    import ClusterRow from './components/ClusterRow.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import Section from './components/Section.svelte';
	import { clusterStore, selectedStore } from './store.js';
	import { clickOutside } from './util.js'

	// Filtering variables
	let enableFilter = true;
	let fltrBounds = {'mean': null, 'variance': null, 'size': null};

	// Cluster Summary
	let scaleMean = d3.scaleLinear().domain([0, 1]);
	let scaleSize = d3.scaleLinear();
	let scaleVariance = d3.scaleLinear();

	// Clusters and cluster metadata
	let nClustersDisplayed = null;
	let nListsDisplayed = null;

	// Filters
	let filterMean;
	let filterVar;
	let filterSize;

	let hoveredList = null;
	let selectedList = null;

	let selectedImagesToAdd = [];
	let selectedImagesToRem = [];
	$: {
		selectedImagesToAdd = []; 
		selectedImagesToRem = [];

		for (let i = 0; i < $selectedStore.length; i++) {
			let img = $selectedStore[i];

			if (selectedList != null && selectedList.images.includes(img)) {
				selectedImagesToRem.push(img);
			} else {
				selectedImagesToAdd.push(img);
			}
		}
	}

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
			let clusters = jsonData;
			for (let i = 0; i < clusters.length; i++) {
				clusters[i].showMore = false;
				clusters[i].showSimilar = false;
				clusters[i].showCounter = false;
				clusters[i].isDisplayed = true;
				clusters[i].isUserList = false;
			}

			sortClusters(e, clusters)
			.then(function(clusters) {
				clusterStore.set(clusters);
			})
			.then(function() {
				// Setup scaling for summary bars
				let vMax = Math.max(...$clusterStore.map(c => c.variance));
				let cMax = Math.max(...$clusterStore.map(c => c.size));

				let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
				let range = [0, cw - 115];
				scaleMean = scaleMean.range(range);
				scaleVariance = scaleVariance.domain([0, vMax]).range(range);
				scaleSize = scaleSize.domain([0, cMax]).range(range);
			});

			enableFilter = true;
			filterMean.updateHistogram(clusters);
			filterVar.updateHistogram(clusters);
			filterSize.updateHistogram(clusters);

		});
	}

	async function sortClusters(e, clusters) {
		if (e.detail.sortKey == "text" && e.detail.sortText != null) {
			await fetch('./textrank', {
				method: 'POST',
				headers: {'Content-Type': 'Application/json'},
				body: JSON.stringify({
					text: e.detail.sortText
				})
			})
			.then(r => (r.json()))
			.then(function(jsonData) {
				clusters.sort(function(a, b) {
					let x = jsonData[a.id];
					let y = jsonData[b.id];
					return ((x < y) ? -1 : ((x > y) ? 1 : 0));
				})
			});
		} else {
			clusters.sort(function(a, b) {
				let x = a[e.detail.sortKey];
				let y = b[e.detail.sortKey];
				return ((x < y) ? -1 : ((x > y) ? 1 : 0));
			});
		}

		if (e.detail.sortReverse) {
			clusters.reverse();
		}

		return clusters;
	}

	function reverseClusters(e) {
		clusterStore.update(v => v.reverse())
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

	function unSelectAll() {
		for (let i = 0; i < $clusterStore.length; i++) {
			let cluster = $clusterStore[i];
			for (let j = 0; j < cluster.images.length; j++) {
				cluster.images[j].selected = false;
			}
		}

		$clusterStore = $clusterStore
	}

	function addNewList() {
		fetch('./userlist', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				idxs: $selectedStore.map(img => img.idx),
			})
		})
		.then(r => (r.json()))
		.then(function(jsonData) {
			jsonData.showMore = false;
			jsonData.showSimilar = false;
			jsonData.showCounter = false;
			jsonData.isDisplayed = true;
			jsonData.isUserList = true;
			jsonData.images = $selectedStore;

			$clusterStore = [...$clusterStore, jsonData];
		})
		.then(function() {
			// Setup scaling for summary bars
			let vMax = Math.max(...$clusterStore.map(c => c.variance));
			let cMax = Math.max(...$clusterStore.map(c => c.size));

			let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
			let range = [0, cw - 115];
			scaleMean = scaleMean.range(range);
			scaleVariance = scaleVariance.domain([0, vMax]).range(range);
			scaleSize = scaleSize.domain([0, cMax]).range(range);
		});
	}

	function addSelection() {
		let update = [...new Set([...selectedList.images, ...selectedImagesToAdd])];
		updateSelection(update);
	}

	function remSelection() {
		let update = selectedList.images.filter(img => !selectedImagesToRem.includes(img));
		updateSelection(update);
	}

	function updateSelection(updatedImages) {
		fetch('./userlist', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				c: selectedList.id,
				idxs: updatedImages.map(img => img.idx)
			})
		})
		.then(r => (r.json()))
		.then(function(jsonData) {
			selectedList.mean = jsonData['mean']
			selectedList.variance = jsonData['variance']
			selectedList.size = jsonData['size']
			selectedList.images = updatedImages;
			$clusterStore = $clusterStore
		}).then(function() {
			// Update scaling for summary bars
			let vMax = Math.max(...$clusterStore.map(c => c.variance));
			let cMax = Math.max(...$clusterStore.map(c => c.size));

			let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
			let range = [0, cw - 115];
			scaleMean = scaleMean.range(range);
			scaleVariance = scaleVariance.domain([0, vMax]).range(range);
			scaleSize = scaleSize.domain([0, cMax]).range(range);
		});
	}

	// Reactivly set some cluster attributes
	$: {
		let display;
		nClustersDisplayed = 0;
		nListsDisplayed = 0;
		for (let i = 0; i < $clusterStore.length; i++) {
			let cluster = $clusterStore[i];
			if (cluster.isUserList) {
				cluster.isDisplayed = true;
				nListsDisplayed += 1;
			} else {
				display = isDisplayed(cluster, fltrBounds);
				cluster.isDisplayed = display;
				nClustersDisplayed += display;
			}
		}

		$clusterStore = $clusterStore;
	}
</script>

<!-- TOOL BAR -->
<Toolbar 
    {enableFilter} 
    on:filter={filter} 
    on:sort={e => sortClusters(e, $clusterStore).then(c => clusterStore.set(c))}
    on:reverse={reverseClusters}
/>
<br>

<!-- HISTOGRAM FILTERING -->
<div>
    <HistogramFilter bind:this={filterMean} fieldName="mean" bind:bounds={fltrBounds['mean']}/>
    <HistogramFilter bind:this={filterVar} fieldName="variance" bind:bounds={fltrBounds['variance']} scaleY="symlog"/>
    <HistogramFilter bind:this={filterSize} fieldName="size" bind:bounds={fltrBounds['size']} scaleY="symlog"/>
</div>

<!-- USER CLUSTER DISPLAY -->
<Section badge={nListsDisplayed}>
    <span slot="title">Lists</span>
    <svelte:fragment slot="content">
        {#each $clusterStore as cluster (cluster.id)}
            {#if cluster.isUserList && cluster.isDisplayed}
                <div
                    use:clickOutside
                    on:mouseenter={() => hoveredList = cluster}
                    on:mouseleave={() => hoveredList = null}
                    on:click={() => selectedList = cluster}
                    on:outclick={() => selectedList = null}
                    class:opacity-50={selectedList != null && selectedList != cluster}
                    class:opacity-75={selectedList == null && hoveredList != null && hoveredList != cluster}
                    class:shadow-lg={selectedList == cluster || hoveredList == cluster}
                    style="transition: opacity 500ms;"
                >
                    <ClusterRow {cluster} {scaleMean} {scaleVariance} {scaleSize} />
                </div>
            {/if}
        {/each}
    </svelte:fragment>
</Section>

<!-- GENERATED CLUSTER DISPLAY -->
<Section badge={nClustersDisplayed}>
    <span slot="title">Clusters</span>
    <svelte:fragment slot="content">
        {#each $clusterStore as cluster (cluster.id)}
            {#if !cluster.isUserList && cluster.isDisplayed}
                <ClusterRow {cluster} {scaleMean} {scaleVariance} {scaleSize} />
            {/if}
        {/each}
    </svelte:fragment>
</Section>

<!-- ABSOLUTE POSITION ITEMS -->
{#if selectedList != null || $selectedStore.length > 0}
    <div transition:fade class="fixed bottom-10 left-10 w-1/2">
        {#if selectedList != null}
            <button 
                class="btn w-1/4"
                class:btn-disabled={selectedImagesToAdd.length == 0}
                on:click="{addSelection}"
            >
                    Add to list ({selectedImagesToAdd.length})
            </button>

            <button 
                class="btn w-1/4"
                class:btn-disabled={selectedImagesToRem.length == 0}
                on:click="{remSelection}"
            >
                    Remove from list ({selectedImagesToRem.length})
            </button>
        {:else if $selectedStore.length > 0}
            <button 
                class="btn w-1/4" 
                on:click={addNewList}
            >
                Add new list ({$selectedStore.length})
            </button>
        {/if}

        <button 
            class="btn btn-error w-1/8" 
            class:btn-disabled={$selectedStore.length == 0}
            on:click="{unSelectAll}"
        >
            Clear
        </button>
    </div>
{/if}
	
