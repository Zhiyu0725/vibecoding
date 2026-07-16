// Simple JS-driven vertical bounce for #js-box using requestAnimationFrame
(() => {
	const box = document.getElementById('js-box');
	if (!box) return;

	let start = null;
	const amplitude = 18; // px
	const period = 1200; // ms

	function step(timestamp){
		if (!start) start = timestamp;
		const elapsed = timestamp - start;
		const t = (elapsed % period) / period; // 0..1
		const y = Math.sin(t * Math.PI * 2) * amplitude;
		box.style.transform = `translateY(${y}px)`;
		requestAnimationFrame(step);
	}

	requestAnimationFrame(step);
})();
