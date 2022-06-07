<script>
    export let id;
    export let b64;
    export let size;
    export let selected;

    function select() {
        selected = !selected;
        console.log(id + ' - ' + selected);
    }
</script>

<img 
    id="img-{id}" 
    alt="Filtered dataset sample" 
    on:click="{select}"
    class="m-0" class:selected
    src="data:image/png;base64,{b64}" 
    width="{size}" 
    height="{size}"
/>

<style>
    .selected {
        outline: 3px solid hsl(var(--su));
        outline-offset: -3px;
    }
</style>