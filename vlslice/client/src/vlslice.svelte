<script>	
	import * as d3 from "d3";
	import HistogramFilter from './components/HistogramFilter.svelte';
    import ClusterRow from './components/ClusterRow.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import Section from './components/Section.svelte';
	import { clusterStore, selectedStore } from './store.js';

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

	let sortText = "";
	let baseline = "";
	let augment = "";
	let topk = 0;

	// Filters
	let filterMean;
	let filterVar;
	let filterSize;

	let modalOpen = false;
	let newListName = "";
	let cidToName = {};

	export function snapshot() {
		let listData = $clusterStore
			.filter(c => c.isUserList)
			.map(c => ({
				"name": cidToName[c.id],
				"images": c.images.map(i => i.iid)
		}));

		let workingSet = $clusterStore
			.filter(c => !c.isUserList)
			.map(c => c.images.map(i => i.iid))
			.flat()
	
		return {
			"interface": "VlSlice",
			"baseline": baseline,
			"augment": augment,
			"topk": topk,
			"lists": listData,
			"working": workingSet
		}
	}

	function filter(e) {
		enableFilter = false;
		cidToName = {};

		baseline = e.detail.baseline;
		augment = e.detail.augment;
		topk = e.detail.topk;
	
		// Fetch new clustering from the server
		fetch('./filter', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				baseline: baseline,
				augment: augment,
				k: topk,
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
			.then((function() {
				setScale();
			}));

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

		if (e.detail.sortText == null) {
			e.detail.sortText = "";
		}

		if (e.detail.sortKey != "text" && e.detail.sortReverse) {
			sortText = `More "${augment}" → Less "${augment}"`;
		} else if (e.detail.sortKey != "text" && !e.detail.sortReverse) {
			sortText = `Less "${augment}" → More "${augment}"`;
		} else if (e.detail.sortKey == "text" && e.detail.sortReverse) {
			sortText = `More "${e.detail.sortText}" → Less "${e.detail.sortText}"`;
		} else if (e.detail.sortKey == "text" && !e.detail.sortReverse) {
			sortText = `Less "${e.detail.sortText}" → More "${e.detail.sortText}"`;
		}

		return clusters;
	}

	function reverseClusters(e) {
		sortText = sortText.split('→').reverse().join('→');
		clusterStore.update(v => v.reverse());
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

	function setScale() {
			// Setup scaling for summary bars
			let vMax = Math.max(...$clusterStore.map(c => c.variance));
			let cMax = Math.max(...$clusterStore.map(c => c.size));

			let cw = document.getElementsByClassName('cluster-summary')[0].clientWidth;
			let range = [0, cw - 115];
			scaleMean = scaleMean.range(range);
			scaleVariance = scaleVariance.domain([0, vMax]).range(range);
			scaleSize = scaleSize.domain([0, cMax]).range(range);
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

			cidToName[jsonData.id] = newListName;
			$clusterStore = [...$clusterStore, jsonData];
		})
		.then(function() {
			setScale();
			unSelectAll();
			modalOpen = false;
		});
	}

	function remList(cluster) {
		fetch('./remlist', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify(cluster)
		}).then(function() {
			delete cidToName[cluster.id];
			cidToName = cidToName
			$clusterStore = $clusterStore.filter(c => c.id != cluster.id);
			setScale();
		})
	}

	function addSelection(cid) {
		let selectedList = $clusterStore.filter(c => c.id == cid)[0]
		let selectedImagesToAdd = [];
		for (let i = 0; i < $selectedStore.length; i++) {
			let img = $selectedStore[i];

			if (~selectedList.images.includes(img)) {
				selectedImagesToAdd.push(img);
			}
		}
	
		let update = [...new Set([...selectedList.images, ...selectedImagesToAdd])];
		updateSelection(selectedList, update);
	}

	function addImage(list, image) {
		for (let i = 0; i < $clusterStore.length; i++) {
			for (let j = 0; j < $clusterStore[i].images.length; j++) {
				let img = $clusterStore[i].images[j];
				if (img.iid == image.iid) {
					let update = [...new Set([...list.images, img])];
					updateSelection(list, update);
					break;
				}
			}
		}
	}

	function remImage(list, image) {
		for (let i = 0; i < $clusterStore.length; i++) {
			for (let j = 0; j < $clusterStore[i].images.length; j++) {
				let img = $clusterStore[i].images[j];
				if (img.iid == image.iid) {
					remSelection(list, img);
					break;
				}
			}
		}
	}

	function remSelection(list, img) {
		if (list.images.length == 1) {
			remList(list);
		} else {
			updateSelection(list, list.images.filter(i => i != img));
		}
	}

	function updateSelection(selectedList, updatedImages) {
		fetch('./updateuserlist', {
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

			unSelectAll();
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
    <span slot="title">Slices</span>
    <svelte:fragment slot="content">
        {#each $clusterStore as cluster (cluster.id)}
            {#if cluster.isUserList && cluster.isDisplayed}
				<div class="my-14">
					<h2 class="text-xl font-bold">
						<input 
							type="text" 
							class="input input-ghost input-lg w-full max-w-md"
							style="font-weight: bold !important"
							bind:value={cidToName[cluster.id]}
						/>
					</h2>
					<ClusterRow 
						{cluster} {scaleMean} {scaleVariance} {scaleSize} {baseline} {augment}
						name={cidToName[cluster.id]} 
						on:deleteCluster={() => remList(cluster)}
						on:addImage={e => addImage(cluster, e.detail.image)}
						on:deleteImage={e => remImage(cluster, e.detail.image)}
					/>
				</div>
            {/if}
        {/each}
    </svelte:fragment>
</Section>

<!-- GENERATED CLUSTER DISPLAY -->
<Section badge={nClustersDisplayed}>
    <span slot="title">Clusters {#if $clusterStore.length > 0}({sortText}){/if}</span>
    <svelte:fragment slot="content">
        {#each $clusterStore as cluster (cluster.id)}
            {#if !cluster.isUserList && cluster.isDisplayed}
                <ClusterRow {cluster} {scaleMean} {scaleVariance} {scaleSize} />
            {/if}
        {/each}
    </svelte:fragment>
</Section>

<!-- ABSOLUTE POSITION ITEMS -->
<div class="fixed flex items-center bottom-14 left-14 w-1/2 z-10">
	<div 
		class="dropdown dropdown-top"
		class:dropdown-hover={$selectedStore.length > 0}
	>
		<!-- svelte-ignore a11y-label-has-associated-control -->
		<label 
			class="btn m-1"
			class:btn-disabled={$selectedStore.length == 0}
			on:click={() => {modalOpen = true; newListName = ""}}
		>
			Add to List ({$selectedStore.length})
		</label>
		<ul class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 min-w-max">
			<li>
				<button on:click={() => {modalOpen = true; newListName = ""}}>
					<i class="fa-solid fa-plus"></i>
					Create a List
				</button>
			</li>
			{#each Object.entries(cidToName) as [cid, name]}
				<li><button onclick="this.blur();" on:click={() => addSelection(cid)}>{name}</button></li>
			{/each}
		</ul>
	</div>

	<button 
		class="btn" 
		class:btn-disabled={$selectedStore.length == 0}
		on:click="{unSelectAll}"
	>
		Clear Selection
	</button>
</div>

<div class="modal" class:modal-open={modalOpen}>
  <div class="modal-box relative">
    <h3 class="text-lg font-bold">Create a new list</h3>
	<input 
		bind:value={newListName} 
		type="text" 
		placeholder="List name" 
		class="input input-bordered w-full my-4 min-w-full"
	/>
	<div class="flex items-center justify-end">
		<button 
			class="btn m-1" 
			on:click={() => modalOpen = false}
		>
			Cancel
		</button>
		<button 
			class="btn btn-primary" 
			class:btn-disabled={newListName == ""} 
			on:click={addNewList}
		>
			Create List
		</button>
	</div>
  </div>
</div>
