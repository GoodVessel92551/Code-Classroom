const aiText = document.getElementById("aiText");

const weakTopic1Text = document.getElementById("weakTopic1Text");
const weakTopic2Text = document.getElementById("weakTopic2Text");

const weakTopic1Icon = document.getElementById("weakTopic1Icon");
const weakTopic2Icon = document.getElementById("weakTopic2Icon");

weakTopic1Text.textContent = weakTopics[0][0];
weakTopic2Text.textContent = weakTopics[1][0];

weakTopic1Icon.src = "/static/icons/weakTopicsSVGs/"+weakTopics[0][0].toLowerCase() + ".svg";
weakTopic2Icon.src = "/static/icons/weakTopicsSVGs/"+weakTopics[1][0].toLowerCase() + ".svg";

const create_session_weak_idea = async () => {
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
    });
  }
  
const create_session_summary = async () => {
  taskSummaryText.textContent = "Loading AI"
    session = await ai.languageModel.create({
        systemPrompt: "You will receive two topics representing weak areas in coding for the student you are addressing. bBriefly explain the topics and explain that they are the students weak areas and and suggest ways the student can improve. Your job is to generate a concise, short-single-paragraph summary also have a of these tasks, using direct language with words like 'you.' Avoid bullet points and keep the summary brief while effectively conveying key details.",
      });
      taskSummaryText.textContent = "AI Loaded"
      create_result_summary()
}

const create_result_summary = async () => {
    if (available_ai) {
        console.log("Generating result");
        taskSummaryText.textContent = "Creating Summary"
        var totalOutput = "";
        taskSummaryContainerTaskList.classList.add('animated-gradient');
        const stream = await session.promptStreaming("Weak Topics: "+weakTopics[0][0]+" + "+weakTopics[1][0]);
        for await (const chunk of stream) {
            aiMarkdown.style.display = "block";
            totalOutput += chunk;
            aiText.textContent = totalOutput;
            console.log(totalOutput);
        }
        taskSummaryContainerTaskList.classList.remove('animated-gradient');
        taskSummaryText.textContent = "Summary Created"
        session.destroy();
    
    }
}
  
const enableAIButton = document.getElementById("enableAIButton");



var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try{
      var capabilities = await ai.languageModel.availability();
  }catch{
      console.error("No AI")
      taskSummaryText.textContent = "AI Unavailable"
      enableAIButton.style.display = "flex";
      return
  }
  if (!(capabilities == "available")){
    taskSummaryText.textContent = "AI Unavailable"
    enableAIButton.style.display = "flex";
    return
  }
  taskSummaryText.textContent = "Loading AI"
    available_ai = true;
    await create_session_summary()
    
      
    })

    const create_idea_weak_topic = async (topic,topic2) => {
      console.log(available_ai)
      if (available_ai){
        console.log("Generating result");
  
  
        const result = await session.prompt("Create an idea that uses " + topic);
        console.log(topic+" "+result);
        session.destroy();
        await create_session_weak_idea();
  
        const result2 = await session.prompt("Create an idea that uses " + topic2);
        console.log(topic2+" "+result2);
  
      }
    }
  