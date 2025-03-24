


var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try {
    var capabilities = await ai.languageModel.availability()
  } catch {
    console.error("No AI")
  }
  if (!(capabilities == "available")) console.error("No AI")
  available_ai = true;
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
      { role: "user", content: "SyntaxError: EOF in multi-line string on line 1" },
      { role: "assistant", content: "Syntax" }
    ]

  });
})



const create_result = async (error) => {
  console.log("Generating result");
  if (available_ai) {
    const result = await session.prompt(error);
    console.log(result);
    fetch("/endpoint/ai/weaktopics", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        result: result,
      }),
    });
  }
}