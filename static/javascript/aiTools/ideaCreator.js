// Generates simple Python project ideas with a local AI model
const aiMarkdown = document.getElementById("aiMarkdown"); 
let session; 
const params = new URLSearchParams(window.location.search);
const topic = params.get("query"); 
const startCreating = document.getElementById("startCreating"); 
const enableAIButton = document.getElementById("enableAIButton");
const taskSummaryText = document.getElementById("taskSummaryText"); // Assumed ID based on your code

let available_ai = false; 

document.addEventListener("DOMContentLoaded", async () => {
  // 1. Check availability correctly using the new API
  const availability = await LanguageModel.availability();
  
  if (availability === "unavailable") {
    taskSummaryText.textContent = "AI Unavailable";
    enableAIButton.style.display = "flex";
    return;
  }

  taskSummaryText.textContent = "Loading AI";

  try {
    // 2. Create session using LanguageModel.create()
    session = await LanguageModel.create({
      temperature: 1.5,
      topK: 10,
      initialPrompts: [
        { role: "system", content: "Action: Create a simple small project in python. Rules: Be concise. Make sure the project does not use any modules. The project can't access the file system. The project must be completed in python in the terminal." },
      ]
    });

    available_ai = true;
    taskSummaryText.textContent = "AI Loaded";
    create_idea(); 
  } catch (err) {
    console.error("Failed to create AI session:", err);
    taskSummaryText.textContent = "Error Loading AI";
  }
});

const create_idea = async () => {
  console.log("Generating result");
  if (available_ai && session) {
    taskSummaryText.textContent = "Creating Idea";
    let totalOutput = "";
    
    // Visual feedback (ensure taskSummaryContainerTaskList is defined in your HTML)
    const container = document.getElementById("taskSummaryContainerTaskList");
    if (container) container.classList.add('animated-gradient');

    const seed = Math.random().toString(36).substring(2, 9);
    const promptText = topic 
      ? `Create a simple idea that uses ${topic} (Ignore Seed: ${seed})` 
      : `Create a simple idea (Ignore Seed: ${seed})`;

    try {
      // 3. Use promptStreaming directly from the session
      const stream = session.promptStreaming(promptText);

      for await (const chunk of stream) {
        aiMarkdown.style.display = "block";
        totalOutput = chunk; // In the new API, chunks are often cumulative or replaced
        // Use aiMarkdown or aiText (ensure these exist in your HTML)
        const aiDisplay = document.getElementById("aiText");
        if (aiDisplay) aiDisplay.textContent += totalOutput;
      }

      if (container) container.classList.remove('animated-gradient');
      taskSummaryText.textContent = "Idea Created";
      startCreating.style.display = "flex";
    } catch (err) {
      console.error("Streaming error:", err);
      taskSummaryText.textContent = "Generation Failed";
    }
  }
};