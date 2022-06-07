<script>
    export let badge;
</script>

<div class="collapse">
    <input type="checkbox"/> 
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
