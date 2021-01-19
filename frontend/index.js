(function() {
  function loadImage(filepath, position) {
    const map = new THREE.TextureLoader().load("path/" + filepath);
    const material = new THREE.SpriteMaterial({ map: map, color: 0xffffff });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(position[0], position[1], position[2]);
    return sprite;
  }

  function createVisual(data) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth / 2, window.innerHeight / 2);
    document.body.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);

    for (let idx in data["filepaths"]) {
      const sprite = loadImage(data["filepaths"][idx], data["3d_projections"][idx]);
      scene.add(sprite);
    }

    const cameraStart = data["3d_projections"][0];
    controls.target.set(cameraStart[0], cameraStart[1], cameraStart[2]);
    controls.update();

    const animate = function() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };

    var raycaster = new THREE.Raycaster(); // create once
    var mouse = new THREE.Vector2(); // create once

    const onDocumentMouseDown = event => {
      event.preventDefault();
      mouse.set(
        (event.clientX / window.innerWidth) * 2 * 2 - 1,
        -((event.clientY / window.innerHeight) * 2) * 2 + 1
      );

      raycaster.setFromCamera(mouse, camera);

      const intersects = raycaster.intersectObjects(scene.children);
      console.log(scene.children);
      console.log(intersects);
      if (intersects.length > 0) {
        controls.target.set(
          intersects[intersects.length - 1].object.position.x,
          intersects[intersects.length - 1].object.position.y,
          intersects[intersects.length - 1].object.position.z
        );
        controls.update();
      }
      scene.add(
        new THREE.ArrowHelper(raycaster.ray.direction, raycaster.ray.origin, 300, 0xff0000)
      );

      renderer.render(scene, camera);
    };
    document.addEventListener("click", onDocumentMouseDown, false);

    animate();
  }

  const handleZipUpload = event => {
    const files = event.target.files;
    const formData = new FormData();
    formData.append("zip", files[0]);

    fetch("/upload_cache", {
      method: "POST",
      body: formData
    })
      .then(response => response.json())
      .then(json_path => {
        console.log("Successful upload. JSON Graph lives at: ", json_path);

        $.getJSON("/path/" + json_path, function(data) {
          console.log("Passed data: ", data);
          createVisual(data);
        });
      })
      .catch(error => {
        console.error(error);
      });
  };

  document.querySelector("#zip-file").addEventListener("change", event => {
    handleZipUpload(event);
  });
})();
