import { writable, derived } from 'svelte/store';

export const clusterStore = writable([]);

export const selectedStore = derived(
    clusterStore,
    $clusterStore => {
        let selected = [];
        for (let i = 0; i < $clusterStore.length; i++) {
            selected.push(...$clusterStore[i].images.filter(img => img.selected))
        }

        return [...new Set(selected)];
    }
)
