<script>
    import { createEventDispatcher } from 'svelte';
    import { hSlide } from '../transitions/hslide'

    const dispatch = createEventDispatcher();

    export let enableFilter;
    let baseline = null;
    let augment = null;
    let topk = null;
    let sortKey = 'mean';
    let sortText = null;
    let sortReverse = true;

    function filter() {
        if (baseline == null || augment == null || topk == null) {
            console.log('Null values...');
            return;
        }
        dispatch('filter', {
            baseline: baseline,
            augment: augment,
            topk: topk,
            sortKey: sortKey,
            sortReverse: sortReverse
        });
    }

    function sortClusters() {
        dispatch('sort', {
            sortKey: sortKey,
            sortText: sortText,
            sortReverse: sortReverse
        });
    }

    function reverseClusters() {
        sortReverse = !sortReverse;
        dispatch('reverse')
    }
</script>

<div id='controls' class="form-control w-full">

    <!-- Baseline text Input -->
    <div class="w-full max-w-xs">
        <label class="label" for="filter-baseline" >
            <span class="label-text">Baseline Text</span>
        </label>
        <input id="filter-baseline" class="input input-bordered w-full" 
            type="text" placeholder="A photo of a person" bind:value={baseline}/>
    </div>

    <!-- Augmented Text Input -->
    <div class="w-full max-w-xs">
        <label class="label" for="filter-augment" >
            <span class="label-text">Augmented Text</span>
        </label>
        <input id="filter-augment" class="input input-bordered w-full" 
            type="text" placeholder="A photo of a ceo" bind:value={augment}/>
    </div>

    <!-- Filter to TopK -->
    <div class="w-full max-w-xs">
        <label class="label" for="filter-topk" >
            <span class="label-text">Number Images</span>
        </label>
        <div id="filter-topk" class="input-group">
            <input class="input input-bordered w-full" type="number" placeholder="2000" min="2" bind:value={topk}/>
            <button class="btn" disabled="{enableFilter ? null : 'disabled'}" type="submit" on:click={filter}>
                Query
                <i class="fa-solid fa-sync ml-1" class:fa-spin={!enableFilter}></i>
            </button>
        </div>
    </div>

    <!-- Sorting -->
    <div class="w-full">
        <label class="label" for="sort" >
            <span class="label-text">Sort Clusters By...</span>
        </label>
        <div id="sort" class="input-group">
            <select class="select select-bordered" bind:value={sortKey} on:change={sortClusters}>
                <option value="mean" selected>Augmented text similarity</option>
                <!--<option value="variance">DC Variance</option>-->
                <!--<option value="size">Cluster Size</option>-->
                <option value="text">Custom text similarity</option>
            </select>

            {#if sortKey == "text"}
                <input 
                    transition:hSlide={{ axis: 'x' }}
                    class="input input-bordered w-full max-w-xs" 
                    type="text" 
                    placeholder="Search text..."
                    bind:value={sortText}
                    on:keydown={(e) => {if (e.key == 'Enter') {sortClusters()}}}
                />
            {/if}

            <button class="btn" on:click={reverseClusters}>
                {#if sortReverse}
                    <i class="fa-solid fa-arrow-down"></i>
                {:else}
                    <i class="fa-solid fa-arrow-up"></i>
                {/if}
            </button>
        </div>
    </div>
</div>

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