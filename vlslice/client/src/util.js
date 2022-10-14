export function clickOutside(node) {
	const handleClick = (event) => {
		console.log(event);
		if (!node.contains(event.target)) {
			if (!(event.srcElement.classList.contains("btn") || event.srcElement.nodeName == "IMG")) {
				node.dispatchEvent(new CustomEvent("outclick"));
			}
		}
	};

	document.addEventListener("click", handleClick, true);

	return {
		destroy() {
			document.removeEventListener("click", handleClick, true);
		}
	};
}

export function exportData(data, name) {
	var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
	var downloadAnchorNode = document.createElement('a');
	downloadAnchorNode.setAttribute("href", dataStr);
	downloadAnchorNode.setAttribute("download", name + ".json");
	downloadAnchorNode.click();
	downloadAnchorNode.remove();
}
