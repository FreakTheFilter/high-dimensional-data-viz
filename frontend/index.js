(function() {
  console.log("Test");

  const handleZipUpload = event => {
    const files = event.target.files;
    const formData = new FormData();
    formData.append("zip", files[0]);

    fetch("/upload", {
      method: "POST",
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        console.log("Successful upload.");
      })
      .catch(error => {
        console.error(error);
      });
  };

  document.querySelector("#zip-file").addEventListener("change", event => {
    handleZipUpload(event);
  });
})();
