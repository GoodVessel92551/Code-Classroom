const aiText = document.getElementById("aiText");
const aiMarkdown = document.getElementById("aiMarkdown")
const taskMarkdown1 = document.getElementById("taskMarkdown1")
const taskTitle1 = document.getElementById("taskTitle1")
const taskText1 = document.getElementById("taskText1")
const taskMarkdown2 = document.getElementById("taskMarkdown2")
const taskTitle2 = document.getElementById("taskTitle2")
const taskText2 = document.getElementById("taskText2")
const taskMarkdown3 = document.getElementById("taskMarkdown3")
const taskTitle3 = document.getElementById("taskTitle3")
const taskText3 = document.getElementById("taskText3")
const taskMarkdown4 = document.getElementById("taskMarkdown4")
const taskTitle4 = document.getElementById("taskTitle4")
const taskText4 = document.getElementById("taskText4")
const taskMarkdown5 = document.getElementById("taskMarkdown5")
const taskTitle5 = document.getElementById("taskTitle5")
const taskText5 = document.getElementById("taskText5")
const createText = document.getElementById("createText")
const tasksLearningPath = document.getElementById("tasksLearningPath")
const learningPathText = document.getElementById("learningPathText")
const learningPathButton = document.getElementById("learningPathButton")
const learningPathThininking = document.getElementById("learningPathThininking")
const learningPathButtonStart = document.getElementById("learningPathButtonStart")
let learningPathLocal = JSON.parse(localStorage.getItem('learningPath'));

if (learningPathLocal == null) {

} else {
    let learningPathInfo = learningPathLocal.info;
    if (learningPathInfo.completed == false) {
        window.location.href = "/learningPathTask";
    }
}
// ... (Your existing DOM variable declarations remain the same)

let masterData = {};
let taskNumCount = 0;

// Data processing logic remains the same
Object.keys(usersClasses).forEach(key => {
    usersClasses[key].members.forEach(member => {
        if (member.id == userID) {
            classRole = (member.role == "teacher") ? "teacher" : "student";
        }
    });
    if (classRole == "teacher") return;

    Object.keys(usersClasses[key].tasks).forEach(task => {
        let taskInfo = usersClasses[key].tasks[task];
        if (taskInfo.type == "resource" || taskInfo.type == "poll") return;
        
        let taskInfoSimple = { ...taskInfo };
        let studentData = taskInfoSimple.student_data[Object.keys(taskInfo.student_data)[0]];
        
        if (studentData == undefined) {
            taskInfoSimple.taskStatus = "Not Started";
        } else {
            taskInfoSimple.feedback = studentData.feedback;
            taskInfoSimple.taskStatus = studentData.status;
        }
        
        // Cleanup unnecessary data for the AI context window
        delete taskInfoSimple.student_data;
        delete taskInfoSimple.taskPoints;
        delete taskInfoSimple.taskId;
        delete taskInfoSimple.taskDue;
        delete taskInfoSimple.id;
        
        masterData[taskNumCount] = taskInfoSimple;
        taskNumCount++;
    });
});

var available_ai = false;
let session;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Updated Availability Check
    const availability = await LanguageModel.availability();
    
    if (availability === "unavailable") {
        const taskSummaryText = document.getElementById("taskSummaryText");
        if (taskSummaryText) taskSummaryText.textContent = "AI Unavailable";
        return;
    }
    
    available_ai = true;
    
    // 2. Initialize first session for summarization
    session = await LanguageModel.create({
        // In the new API, 'system' is often passed within initialPrompts 
        // but 'systemPrompt' is supported in some versions as a shorthand.
        initialPrompts: [
            { 
                role: "system", 
                content: "You will have to summarize what topics in python the user is currently doing. Try to keep it concise and to the point. Do NOT name tasks, only comment on the topics/skills. Output like you are thinking about this." 
            }
        ]
    });
});

const create_result = async () => {
    createText.textContent = "Creating";
    
    if (available_ai && session) {
        let totalOutput = "";
        // 3. Prompting for summary
        const promptString = `Tasks: ${JSON.stringify(masterData)}\n\n Weak Topics: ${JSON.stringify(weakTopics[0][0])}, ${JSON.stringify(weakTopics[0][1])}`;
        
        const stream = session.promptStreaming(promptString);
        
        for await (const chunk of stream) {
            aiMarkdown.style.display = "block";
            totalOutput = chunk; // New API chunks are typically cumulative
            aiText.textContent = totalOutput;
        }

        // 4. Destroy and recreate session for task title generation (Task 2)
        session.destroy();
        session = await LanguageModel.create({
            initialPrompts: [
                { role: "system", content: "You will receive details about a student's coding strengths and weaknesses. Generate 5 relevant task titles in a JSON list format [\"Title 1\", \"Title 2\"]. No libraries except random/math. No file access." },
                // ... (Include your few-shot examples here as seen in your original code)
                { role: "user", content: "The student understands basic Python functions... (example)" },
                { role: "assistant", content: '["Practice with While Loops: Counting Down","Understanding Nested Loops: Multiplication Table"]' }
            ]
        });

        let attempts = 0;
        let result = [];
        const maxAttempts = 3;

        while (attempts < maxAttempts) {
            // Passing the summary (totalOutput) as the user prompt
            const rawResult = await session.prompt(totalOutput);
            try {
                const parsedResult = JSON.parse(rawResult);
                if (Array.isArray(parsedResult)) {
                    result = parsedResult;
                    break;
                }
            } catch (e) {
                console.error("Invalid JSON format, retrying...");
            }
            attempts++;
        }

        if (result.length > 0) {
            // Update UI Titles
            const titles = [taskTitle1, taskTitle2, taskTitle3, taskTitle4, taskTitle5];
            result.forEach((title, idx) => {
                if (titles[idx]) titles[idx].textContent = title;
            });

            tasksLearningPath.style.display = "flex";
            learningPathText.style.display = "none";
            learningPathButton.style.display = "none";
            learningPathThininking.style.display = "none";

            // 5. Recreate session for instruction generation (Task 3)
            session.destroy();
            session = await LanguageModel.create({
                initialPrompts: [
                    { role: "system", content: "Write clear, concise instructions for a Python task. No code. No extra libraries. Keep it short." }
                ]
            });

            var learningPath = {
                "info": { "started": false, "completed": false, "currentTask": 0 },
                "tasks": {}
            };

            for (let i = 0; i < result.length; i++) {
                const task = result[i];
                const instructionStream = session.promptStreaming("Task Title: " + task);
                
                // Map index to your specific UI elements
                const displayTargets = [
                    { text: taskText1, md: taskMarkdown1 },
                    { text: taskText2, md: taskMarkdown2 },
                    { text: taskText3, md: taskMarkdown3 },
                    { text: taskText4, md: taskMarkdown4 },
                    { text: taskText5, md: taskMarkdown5 }
                ];

                let finalInstruction = "";
                for await (const chunk of instructionStream) {
                    // Set the output to the chunk (don't use +=)
                    finalInstruction = chunk; 
                    
                    if (displayTargets[i]) {
                        displayTargets[i].md.style.display = "block";
                        displayTargets[i].text.textContent = finalInstruction;
                        // Keep the view scrolled to the bottom as it types
                        displayTargets[i].md.scrollTop = displayTargets[i].md.scrollHeight;
                    }
                }
                // Save the final result to your object
                learningPath["tasks"][task].instructions = finalInstruction;
            }

            createText.textContent = "";
            session.destroy();
            learningPathButtonStart.style.display = "flex";
            localStorage.setItem("learningPath", JSON.stringify(learningPath));
        }
    }
};