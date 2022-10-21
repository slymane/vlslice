<script>
    import { slide } from 'svelte/transition';
    export let badge;
    let checked = true;;
</script>

<div tabindex="0" class="collapse collapse-arrow">
    <input bind:checked type="checkbox"/> 
    <div class="collapse-title text-2xl font-medium">
        <div class="indicator" on:click="{(e) => e.target.parentElement.previousElementSibling.click()}">
            <span class="indicator-item badge badge-primary">{badge}</span> 
            <slot name="title"/>
        </div>
        <div class="divider"></div>
    </div>
    <div class="collapse-content" class:no-max-height={checked}> 
        <slot name="content"/>
    </div>
</div>

<style>
    .no-max-height {
        max-height: none !important;
    }
</style>