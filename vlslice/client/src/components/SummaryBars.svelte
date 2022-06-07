<script>
    import Bar from './atomic/Bar.svelte';

    export let cluster;
    export let scaleMean;
    export let scaleVariance;
    export let scaleSize;
</script>

<svg id="summary-{cluster.id}" width="100%" height="60">
    <Bar offsetY={0} scale={scaleMean} value={cluster.mean} signed>Mean</Bar>
    <Bar offsetY={20} scale={scaleVariance} value={cluster.variance}>Variance</Bar>
    <Bar offsetY={40} scale={scaleSize} value={cluster.size}>Size</Bar>
</svg>
