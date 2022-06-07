<script>
    import { clusterStore } from '../store';

    export let fieldName;
    export let bounds = null;
    export let scaleY = 'linear'

    function cssToHSL(varId) {
		let hsl = getComputedStyle(document.querySelector(':root')).getPropertyValue(varId);
		return `hsl(${hsl})`;
	}

    clusterStore.subscribe(data => {
        let spec = {
            $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
            description: `Histogram for ${fieldName}`,
            data: {values: data},
            params: [{
                    name: 'select',
                    select: {type: 'interval', encoding: ['x']}
                }],
            mark: {
                type: 'bar',
                fill: cssToHSL('--n'),
                stroke: cssToHSL('--s')
            },
            encoding: {
                x: {
                    title : fieldName,
                    bin: {maxbins: 50},
                    field: fieldName,
                },
                y: {
                    title: 'count',
                    aggregate: 'count',
                    scale: {type: scaleY}
                },
                strokeWidth: {
                    condition: [{
                        param: 'select',
                        empty: false,
                        value: 1
                    }],
                    value: 0
                }
            }
        }

        vegaEmbed(`#filter-${fieldName}`, spec, {'actions': false}).then(function(result) {
            result.view.addSignalListener('select', function(signalName, e) {
                bounds = fieldName in e ? e[fieldName] : null;
            })
        });
    })
</script>

<div id='filter-{fieldName}'></div>
