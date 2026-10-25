const form = document.querySelector("#analysis-form");
const submitButton = document.querySelector("#submit-button");
const result = document.querySelector("#result");
const resultTitle = document.querySelector("#result-title");
const resultEngine = document.querySelector("#result-engine");
const resultError = document.querySelector("#result-error");
const resultAnswer = document.querySelector("#result-answer");

document.querySelector("#year").textContent = new Date().getFullYear();

function displayAnswer(text) {
  resultAnswer.replaceChildren();
  for (const paragraph of text.split(/\n{2,}/)) {
    const [heading, ...body] = paragraph.split("\n");
    const element = document.createElement("p");
    const label = document.createElement("strong");
    label.textContent = heading;
    element.append(label, document.createTextNode(body.join(" ")));
    resultAnswer.append(element);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.hidden = true;
  resultError.hidden = true;
  submitButton.disabled = true;
  submitButton.querySelector(".button-label").textContent = "Menganalisis…";

  const values = new FormData(form);
  const payload = Object.fromEntries(values.entries());

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    result.hidden = false;
    resultTitle.textContent = data.ticker || payload.ticker.trim().toUpperCase();
    if (!response.ok) {
      resultEngine.hidden = true;
      resultAnswer.replaceChildren();
      resultError.textContent = data.error || "Analysis failed. Please try again.";
      resultError.hidden = false;
      return;
    }
    resultEngine.textContent = data.engine;
    resultEngine.hidden = false;
    displayAnswer(data.answer);
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch {
    result.hidden = false;
    resultTitle.textContent = payload.ticker.trim().toUpperCase();
    resultEngine.hidden = true;
    resultAnswer.replaceChildren();
    resultError.textContent = "Could not connect to NusaWall. Reload the page and try again.";
    resultError.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.querySelector(".button-label").textContent = "Jalankan analisis";
  }
});
