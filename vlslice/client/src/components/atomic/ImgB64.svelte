<script>
    import { clusterStore } from '../../store.js';

    export let id;
    export let path;
    export let size;
    export let selected;

    function select() {
        selected = !selected;
        $clusterStore = $clusterStore;
    }
</script>

<img 
    id="img-{id}" 
    alt="Filtered dataset sample" 
    on:click|stopPropagation="{select}" 
    class="expand m-0" class:selected
    src="openimages/{path}" 
    width="{size}" 
    height="{size}"
    style="cursor: pointer;"
    loading="lazy"
/>

<style>
    .selected {
        outline: 3px solid hsl(var(--su));
        outline-offset: -3px;
    }

    .expand {
        transition: transform 100ms;
        transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }

    .expand:hover {
        transform: scale(2.0);
    }
</style>
