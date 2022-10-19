<script>
    export let cluster;
    export let name;
    export let baseline;
    export let augment;
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)

    export function getCorrelation(cluster) {
        fetch('./correlation', {
                method: 'POST',
                headers: {'Content-Type': 'Application/json'},
                body: JSON.stringify({
                    "cluster": cluster
                })
        })
        .then(r => (r.json()))
        .then(function(jsonData) {
            for (let i = 0; i < jsonData.length; i++) {
                jsonData[i].is_member = jsonData[i].is_member ? `In "${name}"` : `Not In "${name}"`;
            }
            let x = jsonData.map(sample => sample["sim"]);

            let spec = {
                $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
                description: "Correlation between cluster centroid similarity and DC",
                width: 0.8 * vw,
                height: 250,
                data: {values: jsonData},
                mark: "point",
                encoding: {
                    x: {
                        axis: {title: `Less "${name}" → More "${name}"`},
                        field: "sim", 
                        type: "quantitative", 
                        scale: {
                            domain: [Math.min(...x), Math.max(...x)]
                        }
                    },
                    y: {
                        axis: {title: `"${baseline}" → "${augment}"`},
                        field: "dcs", 
                        type: "quantitative",
                        scale: {
                            domain: [-1, 1]
                        }
                    },
                    color: {
                        axis: {title: "List Membership"},
                        field: "is_member", 
                        type: "nominal",
                        scale: {range: ["green", "gray"]}
                    },
                    tooltip: [{"field": "image"}]
                }
            }
            vegaEmbed('#correlation', spec, {'actions': false});
        });
    }

    $: getCorrelation(cluster)

</script>

<div id='correlation'></div>

<style>

</style>