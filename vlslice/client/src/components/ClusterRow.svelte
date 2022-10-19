<script>
    import { slide } from 'svelte/transition';
    import SummaryBars from './SummaryBars.svelte';
    import ImgB64 from './atomic/ImgB64.svelte';
    import { createEventDispatcher } from 'svelte';

    import { clusterStore } from '../store.js'
    import { exportData } from '../util.js';
    import Correlation from './Correlation.svelte'

    const imgsNPreview = 12;
    const imgDispSize = 128;
    const dispatch = createEventDispatcher();

    export let name = "";
    export let cluster;
    export let scaleMean;
    export let scaleVariance;
    export let scaleSize;
    export let disableShow = false;

    export let baseline = "";
    export let augment = "";

    let showSimilar = false;
    let showCounter = false;
    let showCorrelation = false;

    let correlation;

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

    function getSimilar(cluster) {
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

    function getCounter(cluster) {
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


    $: getSimilar(cluster);
    $: getCounter(cluster);

</script>

<div class="bbottom">
<div class="grid grid-cols-8 p-2">
    <!-- Summary -->
    <div class="col-span-2 cluster-summary">

        <!-- Bars -->
        <SummaryBars {cluster} {scaleMean} {scaleVariance} {scaleSize}/>

        <!-- Selector Buttons -->
        <div class="flex flex-wrap justify-center">
            <button class="btn btn-xs btn-outline w-1/3 mx-2 my-1" on:click={selectAll}>Select All</button>
            <button class="btn btn-xs btn-outline w-1/3 mx-2 my-1" on:click={unselectAll}>Unselect All</button>
            {#if cluster.isUserList}
                <button 
                    class="btn btn-xs btn-outline w-1/3 mx-2 my-1" 
                    on:click={() => exportData(cluster, name)}
                >
                    Export List
                </button>
                <button 
                    class="btn btn-xs btn-outline w-1/3 mx-2 my-1" 
                    on:click={() => dispatch("deleteCluster")}
                >
                    Delete List
                </button>
            {/if}
        </div>
    </div>

    <!-- Images -->
    <div class="col-span-5">
        <div class="grid grid-cols-12 gap-0.5 mb-px">
            {#each cluster.images.slice(0, imgsNPreview) as img (img.idx)}
                <ImgB64 
                    id={img.idx} 
                    path={img.iid} 
                    bind:selected={img.selected} 
                    size={imgDispSize}
                    deleteable={cluster.isUserList}
                    on:delete={() => dispatch("deleteImage", {"image": img})}
                />
            {/each}
        </div>

        {#if cluster.showMore}
            <div class="grid grid-cols-12 gap-0.5" transition:slide>
                {#each cluster.images.slice(imgsNPreview, cluster.images.length) as img (img.idx)}
                    <ImgB64 
                        class="m-0" 
                        id={img.idx} 
                        path={img.iid} 
                        bind:selected={img.selected} 
                        size={imgDispSize}
                        deleteable={cluster.isUserList}
                        on:delete={() => dispatch("deleteImage", {"image": img})}
                    />
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

        {#if !disableShow}
            <label disabled class="label cursor-pointer justify-start">
                <input
                    type="checkbox"
                    class="toggle mr-1"
                    bind:checked={showSimilar}
                    on:change={() => getSimilar(cluster)}
                />
                <span class="label-text">Show Similar</span>
            </label>
            <label class="label cursor-pointer justify-start">
                <input 
                    type="checkbox"
                    class="toggle mr-1"
                    bind:checked={showCounter}
                    on:change={() => getCounter(cluster)}
                />
                <span class="label-text">Show Counterfactual</span>
            </label>
            {#if cluster.isUserList}
                <label class="label cursor-pointer justify-start">
                    <input 
                        type="checkbox"
                        class="toggle mr-1"
                        bind:checked={showCorrelation}
                        on:change={correlation.getCorrelation(cluster)}
                    />
                    <span class="label-text">Show Correlation</span> 
                </label>
            {/if}
        {/if}
    </div>
</div>

{#if showSimilar}
    <div class="shadow-lg shadow-info w-9/10 p-8 mb-8" transition:slide>
        <h3 class="text-lg text-info mb-2">Similar clusters...</h3>

        <div style="max-height: 500px;" class="overflow-y-scroll">
            {#each similarClusters as cid}
                {@const similarCluster = $clusterStore.filter(c => c.id == cid)[0]}
                {#if cluster.id != cid}
                    <svelte:self cluster={similarCluster} {scaleMean} {scaleVariance} {scaleSize} disableShow></svelte:self>
                {/if}
            {/each}
        </div>
    </div>
{/if}

{#if showCounter}
    <div class="shadow-lg shadow-info w-9/10 p-8 mb-8" transition:slide>
        <h3 class="text-lg text-info mb-2">Counterfactual clusters...</h3>

        <div style="max-height: 500px;" class="overflow-y-scroll">
            {#each counterClusters as cid}
                {@const counterCluster = $clusterStore.filter(c => c.id == cid)[0]}
                <svelte:self cluster={counterCluster} {scaleMean} {scaleVariance} {scaleSize} disableShow></svelte:self>
            {/each}
        </div>
    </div>
{/if}

<!-- Dataset level correlation -->
{#if showCorrelation}
    <div class="shadow-lg w-9/10 p-8 mb-8" transition:slide>
        <h3 class="text-lg">Correlation with {augment}...</h3>
            <Correlation 
                bind:this={correlation} 
                {cluster} {name} {baseline} {augment}
                on:add={(e) => dispatch("addImage", {"image": e.detail})}
                on:delete={(e) => dispatch("deleteImage", {"image": e.detail})}
            />
    </div>
{/if}

</div>

<style>

    .bbottom {
        border-bottom-width: 1px;
        border-color: hsl(var(--b3))
    }

	.cluster-summary {
		display: flex;
		flex-direction: column;
	}

	.disable-span {
		color: hsl(var(--b3));
		cursor: not-allowed;
	}
</style>
