<script>
    import { clusterStore } from '../../store.js';
    import { useLazyImage as lazyImage } from 'svelte-lazy-image';
    import { createEventDispatcher } from 'svelte';

    export let id;
    export let path;
    export let size;
    export let selected;
    export let deletable = false;

    const dispatch = createEventDispatcher()

    function select() {
        selected = !selected;
        $clusterStore = $clusterStore;
    }
</script>

<div class="relative expand overflow-visible m-0">
    <img 
        id="img-{id}" 
        alt="Filtered dataset sample" 
        on:click|stopPropagation="{select}" 
        class="relative"
        class:selected
        data-src="{path}" 
        width="{size}" 
        height="{size}"
        style="cursor: pointer;"
        use:lazyImage
    />

    {#if deletable}
        <div class="absolute top-1 left-1">
            <button class="btn btn-circle btn-outline btn-xs " on:click={() => dispatch("delete")}>
                <i class="fa-solid fa-close"></i>
            </button>
        </div>
    {/if}

</div>

<style>
    .selected {
        outline: 3px solid hsl(var(--su));
        outline-offset: -3px;
    }

    .expand {
        transition: transform 100ms;
        transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 0;
    }

    .expand:hover {
        transform: scale(2.0);
        z-index: 1;
    }
</style>
