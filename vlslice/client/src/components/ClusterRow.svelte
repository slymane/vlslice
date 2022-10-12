<script>
    import { slide } from 'svelte/transition';
    import SummaryBars from './SummaryBars.svelte';
    import ImgB64 from './atomic/ImgB64.svelte';

    import { clusterStore } from '../store.js'

    const imgsNPreview = 12;
    const imgDispSize = 128;

    export let cluster;
    export let scaleMean;
    export let scaleVariance;
    export let scaleSize;

    let showSimilar = false;
    let showCounter = false;

    let similarClusters = [];
    let counterClusters = [];

    function selectAll() {
        for (let i = 0; i < cluster.images.length; i++) {
            cluster.images[i].selected = true;
        }

        $clusterStore = $clusterStore;
    }

    function unselectAll() {
        for (let i = 0; i < cluster.images.length; i++) {
            cluster.images[i].selected = false;
        }

        $clusterStore = $clusterStore;
    }

    function getSimilar() {
        if (showSimilar) {
            fetch('./similar', {
                method: 'POST',
                headers: {'Content-Type': 'Application/json'},
                body: JSON.stringify({
                   "cluster": cluster
                })
            })
            .then(r => (r.json()))
            .then(function(jsonData) {
                similarClusters = jsonData['neighbors'];
            })
        }
    }

    function getCounter() {
        if (showCounter) {
            fetch('./counter', {
                method: 'POST',
                headers: {'Content-Type': 'Application/json'},
                body: JSON.stringify({
                    "cluster": cluster
                })
            })
            .then(r => (r.json()))
            .then(function(jsonData) {
                counterClusters = jsonData['counters'];
            })
        }
    }

</script>

<div class="grid grid-cols-8 p-2">
    <!-- Summary -->
    <div class="col-span-2 cluster-summary">

        <!-- Bars -->
        <SummaryBars {cluster} {scaleMean} {scaleVariance} {scaleSize}/>

        <!-- Selector Buttons -->
        <div class="flex flex-wrap justify-center">
            <button class="btn btn-xs btn-outline w-1/3 mx-2 my-1" on:click={selectAll}>Select All</button>
            <button class="btn btn-xs btn-outline w-1/3 mx-2 my-1" on:click={unselectAll}>Unselect All</button>
        </div>
    </div>

    <!-- Images -->
    <div class="col-span-5">
        <div class="grid grid-cols-12 gap-0.5 mb-px">
            {#each cluster.images.slice(0, imgsNPreview) as img (img.idx)}
                <ImgB64 id={img.idx} b64={img.b64} bind:selected={img.selected} size={imgDispSize}/>
            {/each}
        </div>

        {#if cluster.showMore}
            <div class="grid grid-cols-12 gap-0.5" transition:slide>
                {#each cluster.images.slice(imgsNPreview, cluster.images.length) as img (img.idx)}
                    <ImgB64 class="m-0" id={img.idx} b64={img.b64} bind:selected={img.selected} size={imgDispSize}/>
                {/each}
            </div>
        {/if}
    </div>

    <!-- Drop Downs -->
    <div class="form-control justify-start">
        <label class="label cursor-pointer justify-start">
            <input type="checkbox" class="toggle mr-1" bind:checked={cluster.showMore} 
                disabled={cluster.images.length <= 12}/>
            <span class="label-text" class:disable-span="{cluster.images.length <= 12 ? 'hsl(var(--b3))' : ''}">
                Show More</span> 
        </label>
        <label disabled class="label cursor-pointer justify-start">
            <input 
                type="checkbox" 
                class="toggle mr-1" 
                bind:checked={showSimilar} 
                on:change={getSimilar}    
            />
            <span class="label-text">Show Similar</span> 
        </label>
        <label class="label cursor-pointer justify-start">
            <input 
                type="checkbox" 
                class="toggle mr-1" 
                bind:checked={showCounter} 
                on:change={getCounter}
            />
            <span class="label-text">Show Counterfactual</span> 
        </label>
    </div>
</div>

{#if showSimilar}
    <div class="shadow-lg shadow-success w-9/10 p-8 mb-8" transition:slide>
        {#each similarClusters as cid}
            {@const similarCluster = $clusterStore.filter(c => c.id == cid)[0]}
            {#if cluster.id != cid}
                <svelte:self cluster={similarCluster} {scaleMean} {scaleVariance} {scaleSize}></svelte:self>
            {/if}
        {/each}
    </div>
{/if}

{#if showCounter}
    <div class="shadow-lg shadow-error w-9/10 p-8 mb-8" transition:slide>
        {#each counterClusters as cid}
            {@const counterCluster = $clusterStore.filter(c => c.id == cid)[0]}
            <svelte:self cluster={counterCluster} {scaleMean} {scaleVariance} {scaleSize}></svelte:self>
        {/each}
    </div>
{/if}

<style>
	.cluster-summary {
		display: flex;
		flex-direction: column;
	}

	.disable-span {
		color: hsl(var(--b3));
		cursor: not-allowed;
	}
</style>
