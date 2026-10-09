const form = document.querySelector("#imageForm");
const imageInput = document.querySelector("#imageInput");
const processButton = document.querySelector("#processButton");
const downloadButton = document.querySelector("#downloadButton");
const originalPreview = document.querySelector("#originalPreview");
const processedPreview = document.querySelector("#processedPreview");
const fileName = document.querySelector("#fileName");
const statusLabel = document.querySelector("#statusLabel");
const message = document.querySelector("#message");

const sliders = ["brightness", "contrast", "sharpness", "saturation", "blur"];

function setMessage(text, type = "") {
  message.textContent = text;
  message.className = `message ${type}`.trim();
}

function setImage(img, url) {
  img.src = url;
  img.parentElement.classList.add("has-image");
}

sliders.forEach((id) => {
  const slider = document.querySelector(`#${id}`);
  const label = document.querySelector(`#${id}Value`);
  slider.addEventListener("input", () => {
    label.textContent = Number(slider.value).toFixed(2);
  });
});

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  downloadButton.classList.add("hidden");
  processedPreview.removeAttribute("src");
  processedPreview.parentElement.classList.remove("has-image");
  statusLabel.textContent = "Waiting";

  if (!file) {
    fileName.textContent = "No file selected";
    originalPreview.parentElement.classList.remove("has-image");
    return;
  }

  fileName.textContent = file.name;
  setImage(originalPreview, URL.createObjectURL(file));
  setMessage("Ready to process.");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!imageInput.files[0]) {
    setMessage("Please upload an image first.", "error");
    return;
  }

  processButton.disabled = true;
  processButton.textContent = "Processing...";
  statusLabel.textContent = "Processing";
  setMessage("Applying image enhancements...");

  try {
    const response = await fetch("/process", {
      method: "POST",
      body: new FormData(form),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Processing failed.");
    }

    setImage(originalPreview, data.original_url);
    setImage(processedPreview, `${data.processed_url}?t=${Date.now()}`);
    downloadButton.href = data.download_url;
    downloadButton.classList.remove("hidden");
    statusLabel.textContent = "Complete";
    setMessage("Image processed successfully.", "success");
  } catch (error) {
    statusLabel.textContent = "Failed";
    setMessage(error.message, "error");
  } finally {
    processButton.disabled = false;
    processButton.textContent = "Process Image";
  }
});
