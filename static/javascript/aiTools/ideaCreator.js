const aiMarkdown = document.getElementById("aiMarkdown")
let session



var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try{
      var capabilities = await ai.languageModel.availability();
      taskSummaryText.textContent = "AI Unavailable"
  }catch{
      console.error("No AI")
  }
  if (!(capabilities == "available"))console.error("No AI")
    taskSummaryText.textContent = "Loading AI"
  available_ai = true;
  session = await ai.languageModel.create({
    temperature: 1.5,
    topK:10,
    initialPrompts: [
      { "role": "system", "content": "Create 1 simple and easy idea for a user to code in Python. There is only a console output. It **cannot** use external libraries (numpy, hashlib, etc.) but can use the included ones (math, random, etc.). The user does **not** have access to the file system. Do not include code examples/snippets in the idea. Make the idea summary short and simple and easy make sure there is only **one** idea. If there is complicated words explain them" },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Create a simple text-based calculator that can perform basic arithmetic operations (+, -, *, /) based on user input." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Develop a number guessing game where the program randomly selects a number between 1 and 100, and the user has to guess it with hints of 'higher' or 'lower' after each incorrect guess." },
      { "role": "user", "content": "Create an idea that uses data types" },
      { "role": "assistant", "content": "Design a program that takes user input for name, age, and height, then displays a formatted sentence using different data types like strings, integers, and floats." },
      { "role": "user", "content": "Create an idea that uses variables" },
      { "role": "assistant", "content": "Build a simple temperature converter that allows the user to input a temperature in Celsius and converts it to Fahrenheit using a stored formula in a variable." }
    ]
  });
  taskSummaryText.textContent = "AI Loaded"
  create_idea()
    
  })




  const create_idea = async () => {
    console.log("Generating result");
    if (available_ai){
      taskSummaryText.textContent = "Creating Idea"
      var totalOutput = "";
      taskSummaryContainerTaskList.classList.add('animated-gradient');
      const seed = Math.random().toString(36).substring(2, 7);
      console.log(session)
      const stream = await session.promptStreaming(`Create a simple idea (${seed})`);
      for await (const chunk of stream) {
          aiMarkdown.style.display = "block";
          totalOutput += chunk;
          aiText.textContent = totalOutput;
      } 
        taskSummaryContainerTaskList.classList.remove('animated-gradient');
        taskSummaryText.textContent = "Idea Created"
    }
  }

  const create_idea_weak_topic = async (topic,topic2) => {
    console.log(available_ai)
    if (available_ai){
      console.log("Generating result");


      const result = await session.prompt("Create an idea that uses " + topic);
      console.log(topic+" "+result);
      session.destroy();
      await create_session_idea();

      const result2 = await session.prompt("Create an idea that uses " + topic2);
      console.log(topic2+" "+result2);

    }
  }
