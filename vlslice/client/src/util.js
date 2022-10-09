export function clickOutside(node) {
	const handleClick = (event) => {
		if (!node.contains(event.target)) {
      if (
        !event.srcElement.classList.contains("btn") &&
        !event.srcElement.nodeName == "IMG"
      ) {
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