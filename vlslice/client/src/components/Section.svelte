<script>
    export let badge;
</script>

<div tabindex="0" class="collapse collapse-arrow">
    <input type="checkbox" checked/> 
    <div class="collapse-title text-2xl font-medium">
        <div class="indicator" on:click="{(e) => e.target.parentElement.previousElementSibling.click()}">
            <span class="indicator-item badge badge-primary">{badge}</span> 
            <slot name="title"/>
        </div>
        <div class="divider"></div>
    </div>
    <div class="collapse-content"> 
        <slot name="content"/>
    </div>
</div>
