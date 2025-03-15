

const create_session = async () => {
  session = await ai.languageModel.create({
    temperature: 1.5,
    topK:10,
    initialPrompts: [
      { "role": "system", "content": "Create 1 simple and easy idea for a user to code in Python. There is only a console output. It **cannot** use external libraries (numpy, hashlib, etc.) but can use the included ones (math, random, etc.). The user does **not** have access to the file system. Do not include code examples/snippets in the idea. Make the idea summary short and simple." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Create a simple text-based calculator that can perform basic arithmetic operations (+, -, *, /) based on user input." },
      { "role": "user", "content": "Create an idea" },
      { "role": "assistant", "content": "Develop a number guessing game where the program randomly selects a number between 1 and 100, and the user has to guess it with hints of 'higher' or 'lower' after each incorrect guess." },
      { "role": "user", "content": "Create an idea that uses data types" },
      { "role": "assistant", "content": "Design a program that takes user input for name, age, and height, then displays a formatted sentence using different data types like strings, integers, and floats." },
      { "role": "user", "content": "Create an idea that uses variables" },
      { "role": "assistant", "content": "Build a simple temperature converter that allows the user to input a temperature in Celsius and converts it to Fahrenheit using a stored formula in a variable." }
  ]
})}


var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try{
      var capabilities = await ai.languageModel.availability();
  }catch{
      console.error("No AI")
  }
  
  if (!(capabilities == "available"))console.error("No AI")
  available_ai = true;
  create_session();
  
    
  })




  const create_idea = async () => {
    console.log("Generating result");
    if (available_ai){
      const randomStr = Math.random().toString(36).substring(2, 7);
      const result = await session.prompt(`Create a simple idea (${randomStr})`);    console.log(result);
      localStorage.setItem("codeIdea", result);
      window.location.href = "/code";
    }
  }

  const create_idea_weak_topic = async (topic,topic2) => {
    const weakTopicTaskOneTitle = document.getElementById("weakTopicTaskOneTitle");
    const weakTopicTaskOneDescription = document.getElementById("weakTopicTaskOneDescription");
    const weakTopicTaskTwoTitle = document.getElementById("weakTopicTaskTwoTitle");
    const weakTopicTaskTwoDescription = document.getElementById("weakTopicTaskTwoDescription");
    console.log("Generating result");
    if (available_ai){
      weakTopicTaskOneTitle.textContent = "Task with " + topic;
      weakTopicTaskTwoTitle.textContent = "Task with " + topic2;

      const result = await session.prompt("Create an idea that uses " + topic);
      weakTopicTaskOneDescription.textContent = result;
      console.log(topic+" "+result);
      session.destroy();
      await create_session();

      const result2 = await session.prompt("Create an idea that uses " + topic2);
      weakTopicTaskTwoDescription.textContent = result2;
      console.log(topic2+" "+result2);

    }
  }
