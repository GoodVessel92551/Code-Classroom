


var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try{
      var capabilities = await ai.languageModel.capabilities();
  }catch{
      console.error("No AI")
  }
  if (capabilities.available == "no" || capabilities.available == "after-download")console.error("No AI")
  available_ai = true;
  session = await ai.languageModel.create({
    temperature: 1.5,
    topK:10,
    initialPrompts: [
        { role: "system", content: "Create 1 simple a easy idea for a user to code in Python there is only a console output. It cannot use external libraries (numpy, hashlib, ect) but can use the included ones (math,random,ect). The user does not have access to the file system. Do not include Code Example/snippets in the idea. Make the idea summery short and simple" },
        { role: "user", content: "Create an idea" },
        { role: "assistant", content: "Create a simple text-based calculator that can perform basic arithmetic operations (+, -, *, /) based on user input." },
        { role: "user", content: "Create an idea" },
        { role: "assistant", content: "Develop a number guessing game where the program randomly selects a number between 1 and 100, and the user has to guess it with hints of 'higher' or 'lower' after each incorrect guess." }
      ]
    
    });
  })


  const create_idea = async () => {
    console.log("Generating result");
    if (available_ai){
      const result = await session.prompt("Create an idea (seffse)"); 
      localStorage.setItem("codeIdea", result);
      window.location.href = "/code";
    }
  }