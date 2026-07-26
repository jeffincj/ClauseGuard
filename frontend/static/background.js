// ClauseGuard ambient background — a slowly rotating wireframe "document
// facet" (icosahedron) plus a drifting particle network with proximity
// lines, in the gold/ink theme. Subtle parallax follows the cursor.
(function () {
  const container = document.getElementById("bg-canvas-container");
  if (!container || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.z = 30;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const GOLD = 0xc9973f;

  // Rotating wireframe icosahedron — a faceted "document under scrutiny"
  const icoGeo = new THREE.IcosahedronGeometry(9, 0);
  const icoMat = new THREE.MeshBasicMaterial({
    color: GOLD,
    wireframe: true,
    transparent: true,
    opacity: 0.32,
  });
  const ico = new THREE.Mesh(icoGeo, icoMat);
  ico.position.set(11, 4, -6);
  scene.add(ico);

  // Drifting particle field
  const PARTICLE_COUNT = 90;
  const particles = [];
  const particleGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(PARTICLE_COUNT * 3);

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const x = (Math.random() - 0.5) * 60;
    const y = (Math.random() - 0.5) * 40;
    const z = (Math.random() - 0.5) * 30 - 10;
    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;
    particles.push({
      x,
      y,
      z,
      vx: (Math.random() - 0.5) * 0.012,
      vy: (Math.random() - 0.5) * 0.012,
      vz: (Math.random() - 0.5) * 0.012,
    });
  }
  particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: GOLD,
    size: 0.35,
    transparent: true,
    opacity: 0.6,
  });
  const points = new THREE.Points(particleGeo, particleMat);
  scene.add(points);

  // Proximity lines connecting nearby particles (clause-network feel)
  const lineMat = new THREE.LineBasicMaterial({
    color: GOLD,
    transparent: true,
    opacity: 0.12,
  });
  let lineSegments = new THREE.LineSegments(new THREE.BufferGeometry(), lineMat);
  scene.add(lineSegments);

  const PROXIMITY_THRESHOLD = 9;

  function updateLines() {
    const linePositions = [];
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dz = particles[i].z - particles[j].z;
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (dist < PROXIMITY_THRESHOLD) {
          linePositions.push(particles[i].x, particles[i].y, particles[i].z);
          linePositions.push(particles[j].x, particles[j].y, particles[j].z);
        }
      }
    }
    lineSegments.geometry.dispose();
    lineSegments.geometry = new THREE.BufferGeometry();
    lineSegments.geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(linePositions, 3)
    );
  }

  let mouseX = 0;
  let mouseY = 0;
  document.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX / window.innerWidth) * 2 - 1;
    mouseY = (e.clientY / window.innerHeight) * 2 - 1;
  });

  let frame = 0;
  function animate() {
    requestAnimationFrame(animate);
    frame++;

    ico.rotation.x += 0.0015;
    ico.rotation.y += 0.002;

    const posAttr = particleGeo.attributes.position;
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.z += p.vz;
      if (Math.abs(p.x) > 30) p.vx *= -1;
      if (Math.abs(p.y) > 20) p.vy *= -1;
      if (Math.abs(p.z) > 20) p.vz *= -1;
      posAttr.array[i * 3] = p.x;
      posAttr.array[i * 3 + 1] = p.y;
      posAttr.array[i * 3 + 2] = p.z;
    }
    posAttr.needsUpdate = true;

    // Recompute proximity lines every few frames only (perf)
    if (frame % 4 === 0) updateLines();

    // Subtle camera parallax following the cursor
    camera.position.x += (mouseX * 4 - camera.position.x) * 0.02;
    camera.position.y += (-mouseY * 3 - camera.position.y) * 0.02;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();