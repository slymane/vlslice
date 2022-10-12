<script>
    import ImgB64 from './components/atomic/ImgB64.svelte'
    import { clickOutside, exportSelection } from './util.js'
    import { fade } from 'svelte/transition';
    import Section from './components/Section.svelte';
    import { clusterStore } from './store'

    let baseline = null;
    let augment = null;
    let topk = null;
    let enableFilter = true;

    let hoveredList = null;
    let selectedList = null;
    let lists = [];
    let images = [];
    let lid = 0;

    clusterStore.subscribe(e => {
        lists = lists;
        images = images;
    })

    let selectedImagesToAdd = [];
    let selectedImagesToRem = [];
    $: {
		selectedImagesToAdd = []; 
		selectedImagesToRem = [];

		for (let i = 0; i < selected.length; i++) {
			let img = selected[i];

			if (selectedList != null && selectedList.images.includes(img)) {
				selectedImagesToRem.push(img);
			} else {
				selectedImagesToAdd.push(img);
			}
		}
	}

    $: selected = images.filter(i => i.selected)

    function addNewList() {
        lists = [...lists, {"id": lid, "images": selected}];
        lists = lists;
        images = images;
        lid++;
    }

    function addSelection() {
        console.log(lists);
        console.log(selectedList);
        for (let i = 0; i < lists.length; i++) {
            if (lists[i].id == selectedList.id) {
                console.log("Adding");
                lists[i].images = [...lists[i].images, ...selectedImagesToAdd];
            }
        }
        lists = lists;
        images = images;
    }

    function remSelection() {
        for (let i = 0; i < lists.length; i++) {
            if (lists[i].id == selectedList.id) {
                lists[i].images = lists[i].images.filter(img => !selectedImagesToRem.includes(img));
            }
        }
        lists = lists;
        images = images;
    }

    function unSelectAll() {
        for (let i = 0; i < images.length; i++) {
            images[i].selected = false;
        }
        lists = lists;
        images = images;
    }

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

<!-- USER CLUSTER DISPLAY -->
<Section badge={lists.length}>
    <span slot="title">Lists</span>
    <svelte:fragment slot="content">
        {#each lists as list (list.id)}
            <div
                use:clickOutside
                on:mouseenter={() => hoveredList = list}
                on:mouseleave={() => hoveredList = null}
                on:click={() => selectedList = list}
                on:outclick={() => selectedList = null}
                class="my-14"
                class:opacity-50={selectedList != null && selectedList != list}
                class:opacity-75={selectedList == null && hoveredList != null && hoveredList != list}
                class:shadow-lg={selectedList == list || hoveredList == list}
                style="transition: opacity 500ms;"
            >
                <div class="flex flex-wrap justify-left p-2">
                    {#each list.images as img (img.idx)}
                        <div class="m-1">
                            <ImgB64 id={img.idx} b64={img.b64} bind:selected={img.selected} size={128}/>
                        </div>
                    {/each}
                </div>
            </div>
        {/each}
    </svelte:fragment>
</Section>

<Section badge={images.length}>
    <span slot="title">Images</span>
    <svelte:fragment slot="content">
        <div class="flex flex-wrap justify-center">
            {#each images as img (img.idx)}
                <div class="m-1">
                    <ImgB64 id={img.idx} b64={img.b64} bind:selected={img.selected} size={128}/>
                </div>
            {/each}
        </div>
    </svelte:fragment>
</Section>

{#if selectedList != null || selected.length > 0}
    <div transition:fade class="fixed bottom-10 left-10 w-1/2">
        {#if selectedList != null}
            <button 
                class="btn w-3/8"
                class:btn-disabled={selectedImagesToAdd.length == 0}
                on:click="{addSelection}"
            >
                    Add to list ({selectedImagesToAdd.length})
            </button>

            <button 
                class="btn w-3/8"
                class:btn-disabled={selectedImagesToRem.length == 0}
                on:click="{remSelection}"
            >
                    Remove from list ({selectedImagesToRem.length})
            </button>
        {:else if selected.length > 0}
            <button 
                class="btn w-3/8" 
                on:click={addNewList}
            >
                Add new list ({selected.length})
            </button>
        {/if}

		<button 
			class="btn w-1/8" 
			class:btn-disabled={selected.length == 0}
			on:click={() => exportSelection(selected)}
		>
			Export Selection ({selected.length})
		</button>

        <button 
            class="btn btn-error w-2/8" 
            class:btn-disabled={selected.length == 0}
            on:click="{unSelectAll}"
        >
            Clear
        </button>
    </div>
{/if}

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