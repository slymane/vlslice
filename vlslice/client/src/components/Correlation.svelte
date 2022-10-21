<script>
    import { createEventDispatcher } from 'svelte';

    export let cluster;
    export let name;
    export let baseline;
    export let augment;

    $: id = name.replace(" ", "-");

    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)
    const dispatch = createEventDispatcher();

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
                layer: [
                    {mark: "point",
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
                    }},
                    {mark: {
                        type: "line",
                        color: "blue"
                    },
                    transform: [{
                        regression: "dcs",
                        on: "sim"
                    }],
                    encoding: {
                        x: {
                            field: "sim",
                            type: "quantitative"
                        },
                        y: {
                            field: "dcs",
                            type: "quantitative"
                        }
                    }}
                ]
            }
            vegaEmbed(`#correlation-${id}`, spec, {'actions': false}).then(function(result) {
                result.view.addEventListener('click', function(event, item) {
                    if (item.hasOwnProperty("datum")) {
                        console.log(item.datum.is_member.slice(0, 2) == "In" ? "delete" : "add");
                        item.datum.is_member.slice(0, 2) == "In" ? dispatch("delete", item.datum) : dispatch("add", item.datum);
                    }
                });
            });
        });
    }

    $: getCorrelation(cluster)

</script>

<div id='correlation-{id}'></div>

<style>

</style>