

var available_ai = false; // Tracks whether the AI model is available after initialization.

document.addEventListener("DOMContentLoaded", async () => {
  // On page load: check model availability and establish a session.
  try {
    var capabilities = await ai.languageModel.availability() // Query runtime availability.
  } catch {
    console.error("No AI") // Availability check failed.
  }
  if (!(capabilities == "available")) console.error("No AI") // Non-available state logged.
  available_ai = true; // Mark AI usable (assumes success if no exception).
  // Create session with few-shot examples to map Python errors to categories.
  session = await ai.languageModel.create({
    initialPrompts: [
      { role: "system", content: "You will be given a python error respond with the area which the error falls under use the falling only ['Syntax','Data Types','Loops','Indentation','Math','Variables','Imports']" },
      { role: "user", content: "SyntaxError: invalid syntax in line 3" },
      { role: "assistant", content: "Syntax" }, // Syntax classification example.
      { role: "user", content: "ValueError: invalid literal for int() with base 10: 'abc'" },
      { role: "assistant", content: "Data Types" }, // Type conversion error.
      { role: "user", content: "IndexError: list index out of range" },
      { role: "assistant", content: "Loops" }, // Chosen category (indexing/iteration context).
      { role: "user", content: "IndentationError: unexpected indent" },
      { role: "assistant", content: "Indentation" }, // Indentation structure issue.
      { role: "user", content: "NameError: name 'printt' is not defined. Did you mean: 'print'?" },
      { role: "assistant", content: "Variables" }, // Undefined variable/name.
      { role: "user", content: "SyntaxError: EOF in multi-line string on line 1" },
      { role: "assistant", content: "Syntax" } // Unterminated string = syntax.
    ]

  });
})

const create_result = async (error) => {
  // Given a Python error string: classify and POST result to server.
  console.log("Generating result");
  if (available_ai) {
    const result = await session.prompt(error); // Ask model for category.
    console.log(result); // Log classification for debugging.
    fetch("/endpoint/ai/weaktopics", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        result: result, // Send classification to backend.
      }),
    });
  }
}