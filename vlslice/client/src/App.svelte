<script>
	import VLSlice from './vlslice.svelte';
	let helpModalOpen = true;
</script>

<main class="max-w-none relative">

	<!-- TITLE/NAV BAR -->
	<div class="navbar bg-neutral text-neutral-content flex justify-between">
		<h1 class="normal-case text-4xl p-4">VLSlice</h1>
		<label 
			class="btn m-1"
			on:click={() => {helpModalOpen = true}}
		>
			Help
		</label>
	</div>

	<!-- MAIN CONTENT -->
	<div id="content" class="p-4">
		<VLSlice />
	</div>

	<div class="modal" class:modal-open={helpModalOpen}>
		<div class="modal-box relative">
			<h3 class="text-lg font-bold">Getting Started</h3>
	
			<br>
			<b><h4>Step 1: Query subjects and bias domain</h4></b>
			<p style="width: 100%">
				Enter baseline (A subject, e.g., "A photo of a person") 
				and augmented texts (A bias, e.g., "A photo of a CEO") 
				to study, and the number of images
				for top-k filtering (recommend 2000). 
				Click "Query" to run clustering, calculate ΔC, and output candidate slices.
			</p>
	
			<br>
			<b><h4>Step 2: Explore visiolinguistic clusters</h4></b>
			<p style="width: 100%">
	
				Clusters are default sorted by most positive affinity with the bias (large green bar) to most
				negative affinity (large red bar). Clusters can be cross filtered by click-dragging regions in the cluster
				statistic histograms. Changing "Sort clusters by" on the top right allows search by arbitrary text. Click images
				to select them and mouse over "Add to slice" then click "Create a new slice" to create a new slice from them.
			</p>
	
			<br>
			<b><h4>Step 3: Refine clusters by gathering supporting examples</h4></b>
			<p style="width: 100%">
				Click "Show Similar" and "Show counterfactual" on the right to display lists of similar and counterfactual clusters to your slice. 
				If many samples have been added, optionally click "Show More" to un/hide additional samples. With images selected, 
				mouse over "Add to slice" then select "[YOUR_SLICE_NAME]" to add them to a slice.
			</p>
	
			<br>
			<b><h4>Step 4: Validate model behavior</h4></b>
			<p style="width: 100%">
				Select "Show Correlation" to show a scatter plot displaying image similarity with slice centroids against affinity. A positive/negative slope
				is indicitive of positive/negative bias association. Clicking individual points in this plot will add/remove them from the slice.
			</p>
			<div class="flex items-center justify-end">
				<button 
					class="btn m-1" 
					on:click={() => helpModalOpen = false}
				>
					Close
				</button>
			</div>
		</div>
	</div>
</main>
