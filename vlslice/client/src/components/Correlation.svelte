<script>
    export let cluster;
    export let augment;
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)

    export function getCorrelation() {
        fetch('./correlation', {
                method: 'POST',
                headers: {'Content-Type': 'Application/json'},
                body: JSON.stringify({
                    "cluster": cluster
                })
        })
        .then(r => (r.json()))
        .then(function(jsonData) {
            console.log(jsonData);

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
                        axis: {title: "List Similarity"},
                        field: "sim", 
                        type: "quantitative", 
                        scale: {
                            domain: [Math.min(...x), Math.max(...x)]
                        }
                    },
                    y: {
                        axis: {title: `\"${augment}\" Affinity`},
                        field: "dcs", 
                        type: "quantitative",
                        scale: {
                            domain: [-1, 1]
                        }
                    },
                    color: {
                        axis: {title: "List Member"},
                        field: "is_member", 
                        type: "nominal"
                    },
                    tooltip: [{"field": "image"}]
                }
            }
            vegaEmbed('#correlation', spec, {'actions': false});
        });
    }

</script>

<div id='correlation'></div>

<style>

</style>