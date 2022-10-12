<script>
    import ImgB64 from './components/atomic/ImgB64.svelte'
    import { exportSelection } from './util'

    let baseline = null;
    let augment = null;
    let topk = null;
    let enableFilter = true;
    let images = []

    $: selected = images.filter(i => i.selected)

	function filter() {
		enableFilter = false;
	
		// Fetch new clustering from the server
		fetch('./simple', {
			method: 'POST',
			headers: {'Content-Type': 'Application/json'},
			body: JSON.stringify({
				baseline: baseline,
				augment: augment,
				k: topk,
			})
		})
		.then(r => (r.json()))
		.then(function(jsonData) {
            images = jsonData;
            enableFilter = true;
		});
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
            <span class="label-text">TopK</span>
        </label>
        <div id="filter-topk" class="input-group">
            <input class="input input-bordered w-full" type="number" placeholder="1000" bind:value={topk}/>
            <button class="btn" disabled="{enableFilter ? null : 'disabled'}" type="submit" on:click={filter}>
                Filter
                <i class="fa-solid fa-cog ml-1" class:fa-spin={!enableFilter}></i>
            </button>
        </div>
    </div>
</div>

<div class="flex flex-wrap justify-center">
    {#each images as img (img.idx)}
        <div class="m-1">
            <ImgB64 id={img.idx} b64={img.b64} bind:selected={img.selected} size={128}/>
        </div>
    {/each}
</div>

<div class="fixed bottom-10 left-10 w-1/2">
    <button 
        class="btn w-1/8" 
        class:btn-disabled={selected.length == 0}
        on:click={() => exportSelection(selected)}
    >
        Export Selection ({selected.length})
    </button>
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