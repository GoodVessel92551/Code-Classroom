
session = null;
let error_element = document.getElementById("error");

document.addEventListener("DOMContentLoaded", async () => {
    try{
        var capabilities = await ai.languageModel.capabilities();
    }catch{
        console.error("No AI")
    }
    if (capabilities.available == "no" || capabilities.available == "after-download")console.error("No AI")
      session = await ai.languageModel.create({
        initialPrompts: [
          { role: "system", content: "You will be given a python error respond with the area which the error falls under use the falling only ['Syntax','Data Types','Loops','Indentation','Math','Variables','Imports']" },
          { role: "user", content: "SyntaxError: invalid syntax in line 3" },
          { role: "assistant", content: "Syntax" },
          { role: "user", content: "ValueError: invalid literal for int() with base 10: 'abc'" },
          { role: "assistant", content: "Data Types" },
          { role: "user", content: "IndexError: list index out of range" },
          { role: "assistant", content: "Loops" },
          { role: "user", content: "IndentationError: unexpected indent" },
          { role: "assistant", content: "Indentation" },
          { role: "user", content: "NameError: name 'printt' is not defined. Did you mean: 'print'?" },
          { role: "assistant", content: "Variables" },
        ]
        
        });
    })


    const create_result = async () => {
      console.log("Generating result");
      const result = await session.prompt(error_element.value);
      console.log(result);
    }




