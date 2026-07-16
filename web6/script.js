(function() {
  var box = document.getElementById('js-box');
  if (!box) return;
  var start = null;
  var amplitude = 18;
  var period = 1200;
  function step(timestamp) {
    if (!start) start = timestamp;
    var elapsed = timestamp - start;
    var t = (elapsed % period) / period;
    var y = Math.sin(t * Math.PI * 2) * amplitude;
    box.style.transform = 'translateY(' + y + 'px)';
    requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
})();
