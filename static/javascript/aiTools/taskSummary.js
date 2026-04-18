// Builds a concise AI-generated summary of a student's tasks using normalized class/task data.

let masterData = {} // Aggregated simplified task records keyed by incremental index.
const aiText = document.getElementById("aiText");
let taskNumCount = 0
const taskSummaryContainerTaskList = document.getElementById("taskSummaryContainerTaskList");
const aiMarkdown = document.getElementById("aiMarkdown");
const taskSummaryText = document.getElementById("taskSummaryText");
const {available, defaultTemperature, defaultTopK, maxTopK } = await LanguageModel.params(); // Fetch model/runtime parameters (availability flag used below).

let classRole = "student"; // Default role; affects whether tasks are processed.
Object.keys(usersClasses).forEach(key => {
    // Determine current user's role within this class.
    usersClasses[key].members.forEach(member => {
        if (member.id == userID) {
            classRole = member.role == "teacher" ? "teacher" : "student";
        }
    })
    if (classRole == "teacher") {
        return // Teachers do not need student task summary generation.
    }
    // Flatten tasks: extract student-specific status/feedback, remove extraneous fields.
    Object.keys(usersClasses[key].tasks).forEach(task => {
        let taskInfo = usersClasses[key].tasks[task];
        let taskInfoSimple = taskInfo // Work on same reference (mutating original object).
        let studentData = taskInfoSimple.student_data[Object.keys(taskInfo.student_data)[0]]; // First (and assumed only) student record.
        console.log(studentData)
        if (studentData == undefined) {
            taskInfoSimple.status = "Not Started"; // Fallback when no data.
        } else {
            taskInfoSimple.feedback = studentData.feedback; // Include teacher feedback if present.
            taskInfoSimple.taskStatus = studentData.status; // Preserve completion status.
        }
        // Remove fields not needed for summarization to reduce prompt size.
        delete taskInfoSimple.student_data;
        delete taskInfoSimple.taskPoints;
        delete taskInfoSimple.taskDescription;
        delete taskInfoSimple.taskId;
        masterData[taskNumCount] = taskInfoSimple; // Store simplified task snapshot.
        taskNumCount++;
    })
});

var available_ai = false; // Flag toggled once model session is created.
document.addEventListener("DOMContentLoaded", async () => {
    // If model not available, show UI to enable and abort initialization.
    if ((available !== "no")) {
        taskSummaryText.textContent = "AI Unavailable"
        enableAIButton.style.display = "flex";
        return
      }
    taskSummaryText.textContent = "Loading AI"
    available_ai = true;
    // systemPrompt instructs model to produce a single concise paragraph; date injected for temporal context.
    session = await ai.languageModel.create({
        systemPrompt: "You will be given a JSON dictionary containing a list of tasks that a student has due. Your job is to generate a concise, one-short-paragraph summary of these tasks for the student, using direct language with words like 'you.' Avoid bullet points and keep the summary brief while still conveying key details. If feedback is provided, make sure to incorporate it naturally into the summary.Check the status for the task to see if it has been completed. The current date is:" + new Date().toISOString().split('T')[0],
    });
    taskSummaryText.textContent = "AI Loaded"
    create_result() // Trigger summary generation immediately after load.
})

const create_result = async () => {
    console.log(available_ai);
    if (available_ai) {
        console.log("Generating result");
        taskSummaryText.textContent = "Creating Summary"
        var totalOutput = "";

        // Visual cue: animate container while streaming tokens.
        taskSummaryContainerTaskList.classList.add('animated-gradient');

        // Stream response for incremental UI updates; reduces perceived latency.
        const stream = await session.promptStreaming("Json Data:" + JSON.stringify(masterData, null, 2));
        for await (const chunk of stream) {
            aiMarkdown.style.display = "block"; // Ensure output container visible once first chunk arrives.
            console.log(chunk);
            totalOutput += chunk; // Accumulate partial output.
            aiText.textContent = totalOutput; // Update text node progressively.
        }

        // Cleanup UI state post-generation.
        taskSummaryContainerTaskList.classList.remove('animated-gradient');
        taskSummaryText.textContent = "Summary Created"
    }
}
