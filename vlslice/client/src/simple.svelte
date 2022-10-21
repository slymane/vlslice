<script>
    import ImgB64 from './components/atomic/ImgB64.svelte'
    import Section from './components/Section.svelte';
    import { clusterStore } from './store'
    import { exportData } from './util';

    let baseline = null;
    let augment = null;
    let topk = null;
    let enableFilter = true;

    let lists = [];
    let images = [];
    let lid = 0;

	let modalOpen = false;
	let newListName = "";
	let lidToName = {};

    clusterStore.subscribe(e => {
        lists = lists;
        images = images;
    })

    $: selected = images.filter(i => i.selected)

    export function snapshot() {
        let listData = lists
			.map(l => ({
				"name": lidToName[l.id],
				"images": l.images.map(i => i.iid)
		}));
    
		return {
            "interface": "Simple",
			"baseline": baseline,
			"augment": augment,
			"topk": topk,
            "lists": listData,
            "working": images.map(i => i.iid)
		}
    }

    function addNewList() {
        lists = [...lists, {"id": lid, "images": selected}];
        lidToName[lid] = newListName;
        unSelectAll();
        modalOpen = false;
        lid++;
    }

    function addSelection(id) {
        let selectedList = lists.filter(l => l.id == id)[0];
        let selectedImagesToAdd = [];
		for (let i = 0; i < selected.length; i++) {
			let img = selected[i];

			if (~selectedList.images.includes(img)) {
				selectedImagesToAdd.push(img);
			}
		}
    
        for (let i = 0; i < lists.length; i++) {
            if (lists[i].id == selectedList.id) {
                lists[i].images = [...lists[i].images, ...selectedImagesToAdd];
            }
        }
        unSelectAll();
    }

    function remSelection(list, img) {
        for (let i = 0; i < lists.length; i++) {
            if (lists[i].id == list.id) {
                lists[i].images = lists[i].images.filter(i => i != img);

                if (lists[i].images.length == 0) {
                    deleteList(list);
                }
            }
        }
        lists = lists;
        images = images;
    }

    function deleteList(list) {
        lists = lists.filter(l => l.id != list.id);
        delete lidToName[list.id];
        lidToName = lidToName;
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
        lists = [];
        images = [];
        lidToName = {};
	
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
            <input class="input input-bordered w-full" type="number" placeholder="1000" min="2" bind:value={topk}/>
            <button class="btn" disabled="{enableFilter ? null : 'disabled'}" type="submit" on:click={filter}>
                Filter
                <i class="fa-solid fa-cog ml-1" class:fa-spin={!enableFilter}></i>
            </button>
        </div>
    </div>
</div>

<!-- USER CLUSTER DISPLAY -->
<Section badge={lists.length}>
    <span slot="title">Saved Lists</span>
    <svelte:fragment slot="content">
        {#each lists as list (list.id)}
            <div class="my-14">
                <h2 class="text-xl font-bold mb-1">
                    <input 
                        type="text" 
                        class="input input-ghost input-lg w-full max-w-md"
                        style="font-weight: bold !important"
                        bind:value={lidToName[list.id]}
                    />
                </h2>
                <div class="flex w-1/4">
                    <button 
                        class="btn btn-xs btn-outline w-1/3 mx-2 my-1" 
                        on:click={() => exportData(list, lidToName[list.id])}
                    >
                        Export List
                    </button>
                    <button 
                        class="btn btn-xs btn-outline w-1/3 mx-2 my-1" 
                        on:click={() => deleteList(list)}
                    >
                        Delete List
                    </button>
                </div>
                <div class="flex flex-wrap justify-left p-2">
                    {#each list.images as img (img.idx)}
                        <div class="m-1">
                            <ImgB64 
                                id={img.idx} 
                                path={img.iid} 
                                bind:selected={img.selected} 
                                size={128} 
                                deleteable
                                on:delete={() => remSelection(list, img)}
                            />
                        </div>
                    {/each}
                </div>
            </div>
        {/each}
    </svelte:fragment>
</Section>

<Section badge={images.length}>
    <span slot="title">Images {#if images.length > 0}(More "{augment}" → Less "{augment}"){/if}</span>
    <svelte:fragment slot="content">
        <div class="flex flex-wrap justify-center">
            {#each images as img (img.idx)}
                <div class="m-1">
                    <ImgB64 id={img.idx} path={img.iid} bind:selected={img.selected} size={128}/>
                </div>
            {/each}
        </div>
    </svelte:fragment>
</Section>

<!-- ABSOLUTE POSITION ITEMS -->
<div class="fixed flex items-center bottom-14 left-14 w-1/2 z-10">
	<div 
		class="dropdown dropdown-top"
		class:dropdown-hover={selected.length > 0}
	>
		<!-- svelte-ignore a11y-label-has-associated-control -->
		<label 
			class="btn m-1"
			class:btn-disabled={selected.length == 0}
            on:click={() => {modalOpen = true; newListName = ""}}
		>
			Add to List ({selected.length})
		</label>
		<ul class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 min-w-max">
			<li>
				<button on:click={() => {modalOpen = true; newListName = ""}}>
					<i class="fa-solid fa-plus"></i>
					Create a List
				</button>
			</li>
			{#each Object.entries(lidToName) as [id, name]}
				<li><button onclick="this.blur();" on:click={() => addSelection(id)}>{name}</button></li>
			{/each}
		</ul>
	</div>

	<button 
		class="btn" 
		class:btn-disabled={selected.length == 0}
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