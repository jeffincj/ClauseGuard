// 3D tilt effect on the upload card — tracks cursor position within the
// tilt-wrapper and rotates the card accordingly, resetting smoothly on
// mouse leave.
(function () {
  const wrapper = document.getElementById("tiltWrapper");
  if (!wrapper) return;

  const card = wrapper.querySelector(".folder-body");
  if (!card) return;

  const MAX_TILT_DEGREES = 8;

  wrapper.addEventListener("mousemove", (e) => {
    const rect = wrapper.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateY = ((x - centerX) / centerX) * MAX_TILT_DEGREES;
    const rotateX = -((y - centerY) / centerY) * MAX_TILT_DEGREES;

    card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.01)`;
  });

  wrapper.addEventListener("mouseleave", () => {
    card.style.transform = "rotateX(0deg) rotateY(0deg) scale(1)";
  });
})();