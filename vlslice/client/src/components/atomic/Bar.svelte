<script>
    export let offsetX = 0;
    export let offsetY = 0;
    export let signed = false;
    export let scale;
    export let value;
</script>

<g transform="translate({offsetX}, {offsetY})">
    <!-- Text describing bar -->
    <text 
        x="65" 
        y="10" 
        dominant-baseline="middle" 
        text-anchor="end" 
        fill="hsl(var(--bc))"
    >
        <slot></slot>
    </text>

    <!-- Bar encoding value -->
    <rect 
        x="70" 
        y="5" 
        width="{scale(Math.abs(value))}" 
        height="10" 
        fill={!signed ? "hsl(var(--n))" : value > 0 ? "hsl(var(--su))" : "hsl(var(--er))"}
    />

    <!-- Text encoding value -->
    <text 
        x="{75 + scale(Math.abs(value))}" 
        y="10" dominant-baseline="middle" 
        fill="hsl(var(--b3))"
    >
        ({signed && (value > 0) ? '+' : ''}{value % 1 === 0 ? value : value.toFixed(2)})
    </text>
</g>
