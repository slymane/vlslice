<script>
    import { slide } from 'svelte/transition';
    import SummaryBars from './SummaryBars.svelte';
    import ImgB64 from './atomic/ImgB64.svelte';

    const imgsNPreview = 12;
    const imgDispSize = 128;

    export let cluster;
    export let scaleMean;
    export let scaleVariance;
    export let scaleSize;
</script>

<div class="grid grid-cols-8 mb-20">
    <!-- Summary -->
    <div class="col-span-2 cluster-summary">

        <!-- Bars -->
        <SummaryBars {cluster} {scaleMean} {scaleVariance} {scaleSize}/>

        <!-- Selector Buttons -->
        <div class="flex flex-wrap justify-center">
            <button class="btn btn-xs w-1/3 mx-2 my-1" on:click="{() => cluster.userList = true}">Add to List</button>
            <button class="btn btn-xs w-1/3 mx-2 my-1" on:click="{() => cluster.userList = false}">Add to Last</button>
            <button class="btn btn-xs btn-outline btn-success w-1/3 mx-2 my-1">Select All</button>
            <button class="btn btn-xs btn-outline btn-error w-1/3 mx-2 my-1">Deselect All</button>
        </div>
    </div>

    <!-- Images -->
    <div class="col-span-5">
        <div class="grid grid-cols-12 gap-px mb-px">
            {#each cluster.images.slice(0, imgsNPreview) as img (img.id)}
                <ImgB64 id={img.id} b64={img.b64} bind:selected={img.selected} size={imgDispSize}/>
            {/each}
        </div>

        {#if cluster.showMore}
            <div class="grid grid-cols-12 gap-px" transition:slide>
                {#each cluster.images.slice(imgsNPreview + 1, cluster.images.length) as img (img.id)}
                    <ImgB64 class="m-0" id={img.id} b64={img.b64} bind:selected={img.selected} size={imgDispSize}/>
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
            <input type="checkbox" class="toggle mr-1" bind:checked={cluster.showSimilar} />
            <span class="label-text">Show Similar</span> 
        </label>
        <label class="label cursor-pointer justify-start">
            <input type="checkbox" class="toggle mr-1" bind:checked={cluster.showCounter} />
            <span class="label-text">Show Counterfactual</span> 
        </label>
    </div>
</div>

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
