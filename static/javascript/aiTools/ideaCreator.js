const aiMarkdown = document.getElementById("aiMarkdown")
let session
const params = new URLSearchParams(window.location.search);
const topic = params.get("query");
const startCreating = document.getElementById("startCreating");
const enableAIButton = document.getElementById("enableAIButton");



var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try {
    var capabilities = await ai.languageModel.availability();
  } catch {
    console.error("No AI")
    taskSummaryText.textContent = "AI Unavailable"
    enableAIButton.style.display = "flex";
    return
  }
  if (!(capabilities == "available")) {
    taskSummaryText.textContent = "AI Unavailable"
    enableAIButton.style.display = "flex";
    return
  }
  taskSummaryText.textContent = "Loading AI"
  available_ai = true;
  session = await ai.languageModel.create({
    temperature: 1.5,
    topK: 10,
    initialPrompts: [
      { "role": "system", "content": `Action: Create a simple small project in python. \ 
        Rules: Be concise. Make sure the project does not use any modules. The project can't access the file system.The project must be completed in python in the terminal.` },
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
  taskSummaryText.textContent = "AI Loaded"
  create_idea()
  
})




const create_idea = async () => {
  console.log("Generating result");
  if (available_ai) {
    taskSummaryText.textContent = "Creating Idea"
    var totalOutput = "";
    taskSummaryContainerTaskList.classList.add('animated-gradient');
    const seed = Math.random().toString(36).substring(2, 9);
    console.log(session)
    let stream
    console.log(seed)
    if (topic) {
      stream = await session.promptStreaming(`Create a simple idea that users ${topic} (Ignore Seed: ${seed})`);
    } else {
      stream = await session.promptStreaming(`Create a simple idea (Ignore Seed: ${seed})`);
    }
    for await (const chunk of stream) {
      aiMarkdown.style.display = "block";
      totalOutput += chunk;
      aiText.textContent = totalOutput;
    }
    taskSummaryContainerTaskList.classList.remove('animated-gradient');
    taskSummaryText.textContent = "Idea Created"
    startCreating.style.display = "flex";
  }
}


const newProjectInstructions = (instructions) => {
  let projects = localStorage.getItem('codeProjects');
  let num_projects = localStorage.getItem('num_projects');
  if (num_projects) {
    num_projects = parseInt(num_projects);
  } else {
    num_projects = 1;
  }
  projects = JSON.parse(projects);
  let projectKeys = Object.keys(projects);
  if (projectKeys.length > 10) {
    alert('You can only have 10 projects');
  } else {
    const randomString = Math.random().toString(36).substring(2, 8);
    let newProject = {
      "name": "Idea #" + num_projects,
      "code": '"""\n' + aiText.textContent + '"""',
    }
    projects[randomString] = newProject;
    localStorage.setItem('codeProjects', JSON.stringify(projects));
    localStorage.setItem('num_projects', num_projects + 1);
    window.location.href = `/quickCode?project=${randomString}`;
  }
}