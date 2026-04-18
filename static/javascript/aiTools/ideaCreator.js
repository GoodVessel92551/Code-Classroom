// Generates simple Python project ideas with a local AI model, streams them to the UI, and lets users save an idea as a new project.

const aiMarkdown = document.getElementById("aiMarkdown") // Container to show streamed AI output.
let session // AI session handle used for prompting.
const params = new URLSearchParams(window.location.search);
const topic = params.get("query"); // Optional topic hint from URL to guide idea generation.
const startCreating = document.getElementById("startCreating"); // Button shown after idea is ready.
const enableAIButton = document.getElementById("enableAIButton"); // Shown if AI is unavailable.

var available_ai = false; // Tracks if the AI session is initialized and ready.

document.addEventListener("DOMContentLoaded", async () => {
  // On load: check model availability and create a session if possible.
  const {available, defaultTemperature, defaultTopK, maxTopK } = await LanguageModel.params(); // Availability + defaults (not all used).
  if ((available !== "no")) {
    taskSummaryText.textContent = "AI Unavailable" // Update status when AI is disabled.
    enableAIButton.style.display = "flex"; // Offer user a way to enable AI.
    return
  }
  taskSummaryText.textContent = "Loading AI" // UI feedback while initializing.
  available_ai = true;
  session = await ai.languageModel.create({
    temperature: 1.5, // Encourage creative variety in ideas.
    topK: 10,         // Sample from top-k tokens for more diverse outputs.
    initialPrompts: [
      { "role": "system", "content": `Action: Create a simple small project in python. \ 
        Rules: Be concise. Make sure the project does not use any modules. The project can't access the file system.The project must be completed in python in the terminal.` }, // Guardrails: no modules, no filesystem, terminal-only, concise.
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Create a simple text-based calculator that can perform basic arithmetic operations (+, -, *, /) based on user input." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Develop a number guessing game where the program randomly selects a number between 1 and 100, and the user has to guess it with hints of 'higher' or 'lower' after each incorrect guess." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Design a program that takes user input for name, age, and height, then displays a formatted sentence using different data types like strings, integers, and floats." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Build a simple temperature converter that allows the user to input a temperature in Celsius and converts it to Fahrenheit using a stored formula in a variable." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": 'Create a game called "guess the number". The computer thinks of a secret number randomly within its range (like 0 - 5). The program asks the user to input a guess until they get the number right. It provides feedback (e.g., "Higher", "Lower", exact guess) to guide the user.' }
    ]
  });
  taskSummaryText.textContent = "AI Loaded" // Ready to generate.
  create_idea() // Kick off idea generation immediately.
})

const create_idea = async () => {
  // Streams an idea from the model and updates the UI incrementally.
  console.log("Generating result");
  if (available_ai) {
    taskSummaryText.textContent = "Creating Idea" // Status text while generating.
    var totalOutput = "";
    taskSummaryContainerTaskList.classList.add('animated-gradient'); // Visual feedback during streaming.

    const seed = Math.random().toString(36).substring(2, 9); // Adds noise to reduce repetition between generations.
    let stream
    if (topic) {
      // Topic-aware prompt if a query parameter is provided.
      stream = await session.promptStreaming(`Create a simple idea that users ${topic} (Ignore Seed: ${seed})`);
    } else {
      // Generic idea prompt.
      stream = await session.promptStreaming(`Create a simple idea (Ignore Seed: ${seed})`);
    }

    // Incrementally render the response as it streams in.
    for await (const chunk of stream) {
      aiMarkdown.style.display = "block"; // Ensure output container is visible once chunks arrive.
      totalOutput += chunk;
      aiText.textContent = totalOutput; // Progressive UI updates.
    }

    taskSummaryContainerTaskList.classList.remove('animated-gradient'); // Stop animation when done.
    taskSummaryText.textContent = "Idea Created" // Final status.
    startCreating.style.display = "flex"; // Reveal next-step button.
  }
}

const newProjectInstructions = (instructions) => {
  // Saves the generated idea into a localStorage-backed project and navigates to the editor.
  let projects = localStorage.getItem('codeProjects'); // Project store.
  let num_projects = localStorage.getItem('num_projects'); // Incremental idea count.
  if (num_projects) {
    num_projects = parseInt(num_projects);
  } else {
    num_projects = 1; // Initialize counter if missing.
  }
  projects = JSON.parse(projects);
  let projectKeys = Object.keys(projects);
  if (projectKeys.length > 10) {
    alert('You can only have 10 projects'); // Simple quota guard.
  } else {
    const randomString = Math.random().toString(36).substring(2, 8); // New project ID.
    let newProject = {
      "name": "Idea #" + num_projects, // Human-friendly name.
      "code": '"""\n' + aiText.textContent + '"""', // Store idea as a Python docstring in the code field.
    }
    projects[randomString] = newProject; // Persist project.
    localStorage.setItem('codeProjects', JSON.stringify(projects));
    localStorage.setItem('num_projects', num_projects + 1); // Increment the counter.
    window.location.href = `/quickCode?project=${randomString}`; // Navigate to editor with project loaded.
  }
}