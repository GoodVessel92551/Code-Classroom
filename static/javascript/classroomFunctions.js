const addMessageToUI = (data) => {
    console.log(data);
    let container = document.createElement('span');
    container.id = 'messageContainer_' + data.messageId;
    let messageTitleContainer = document.createElement('div');
    let messageTitle = document.createElement('strong');
    let messageDate = document.createElement('p');
    let messageText = document.createElement('p');
    let deleteIcon = document.createElement('span');
    let deleteCover = document.createElement('div');
    let deleteText = document.createElement('span');
    let deleteButton = document.createElement('button');
    let cancelButton = document.createElement('button');
    let deleteButtonContainer = document.createElement('div');
    if (messageImportant) {
        container.classList.add('importantMessage');
    }
    deleteText.innerText = 'Are you sure?';
    deleteButton.innerText = 'Delete';
    cancelButton.innerText = 'Cancel';
    cancelButton.addEventListener('click', () => {
        deleteCover.style.display = 'none';
    });
    deleteButtonContainer.appendChild(deleteButton);
    deleteButtonContainer.appendChild(cancelButton);
    deleteCover.appendChild(deleteText);
    deleteCover.appendChild(deleteButtonContainer);
    deleteCover.classList.add('deleteCover');
    deleteButtonContainer.classList.add('deleteButtonContainer');
    deleteButton.classList.add('dangerButton');
    cancelButton.classList.add('whiteButton');
    messageTitleContainer.appendChild(deleteCover);

    // Create message bubble SVG
    let messageBubbleSvg = document.createElement('span');
    messageBubbleSvg.innerHTML = '<svg class=svg_' + classInfo.coverImage + ' width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10a9.96 9.96 0 0 1-4.587-1.112l-3.826 1.067a1.25 1.25 0 0 1-1.54-1.54l1.068-3.823A9.96 9.96 0 0 1 2 12C2 6.477 6.477 2 12 2Zm0 1.5A8.5 8.5 0 0 0 3.5 12c0 1.47.373 2.883 1.073 4.137l.15.27-1.112 3.984 3.987-1.112.27.15A8.5 8.5 0 1 0 12 3.5ZM8.75 13h4.498a.75.75 0 0 1 .102 1.493l-.102.007H8.75a.75.75 0 0 1-.102-1.493L8.75 13h4.498H8.75Zm0-3.5h6.505a.75.75 0 0 1 .101 1.493l-.101.007H8.75a.75.75 0 0 1-.102-1.493L8.75 9.5h6.505H8.75Z" fill="#ffffff"/></svg>';

    // Create delete SVG
    deleteIcon.classList.add('deleteMessage');
    deleteIcon.addEventListener('click', () => {
        deleteCover.style.display = 'flex';
    });
    deleteIcon.innerHTML = '<svg class="deleteMessageSVG" width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 1.75a3.25 3.25 0 0 1 3.245 3.066L15.25 5h5.25a.75.75 0 0 1 .102 1.493L20.5 6.5h-.796l-1.28 13.02a2.75 2.75 0 0 1-2.561 2.474l-.176.006H8.313a2.75 2.75 0 0 1-2.714-2.307l-.023-.174L4.295 6.5H3.5a.75.75 0 0 1-.743-.648L2.75 5.75a.75.75 0 0 1 .648-.743L3.5 5h5.25A3.25 3.25 0 0 1 12 1.75Zm6.197 4.75H5.802l1.267 12.872a1.25 1.25 0 0 0 1.117 1.122l.127.006h7.374c.6 0 1.109-.425 1.225-1.002l.02-.126L18.196 6.5ZM13.75 9.25a.75.75 0 0 1 .743.648L14.5 10v7a.75.75 0 0 1-1.493.102L13 17v-7a.75.75 0 0 1 .75-.75Zm-3.5 0a.75.75 0 0 1 .743.648L11 10v7a.75.75 0 0 1-1.493.102L9.5 17v-7a.75.75 0 0 1 .75-.75Zm1.75-6a1.75 1.75 0 0 0-1.744 1.606L10.25 5h3.5A1.75 1.75 0 0 0 12 3.25Z" fill="#ffffff"/></svg>';
    deleteButton.addEventListener('click', () => {
        fetch("/endpoint/class/message/delete", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                classid: classInfo.id,
                messageid: data.messageId
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'complete') {
                    console.log('Message deleted successfully');
                }
            })
    });
    // Build the message container structure
    container.appendChild(messageTitleContainer);
    messageTitleContainer.appendChild(messageBubbleSvg);
    messageTitleContainer.appendChild(messageTitle);
    messageTitleContainer.appendChild(messageDate);
    messageTitleContainer.appendChild(deleteIcon);
    container.appendChild(messageText);


    // Set text content for message elements
    messageTitle.textContent = data.userName;
    messageDate.textContent = data.date;
    messageText.textContent = data.message;

    // Add classes
    messageTitleContainer.classList.add('messageTitleContainer');

    // Insert the new message at the top
    messageContainer.insertBefore(container, messageContainer.firstChild);
}

const removeMessageFromUI = (messageId) => {
    console.log("Delete "+messageId);
    const messageContainer = document.getElementById('messageContainer_' + messageId);
    if (messageContainer) {
        messageContainer.remove();
    }
}

const addPersonToUI = (person) => {
    let container = document.createElement('div');
    let personName = document.createElement('strong');
    let personRole = document.createElement('p');
    let personAvatar = document.createElement('span');
    personName.innerText = person.username;
    if (person.role == "teacher") {
        personRole.innerText = "Teacher"
        personRole.classList.add('personRoleTeacher');
    } else {
        personRole.innerText = "Student"
    }
    personRole.classList.add('personRole');
    // Create SVG avatar instead of using an image
    personAvatar.innerHTML = `<svg class=svg_` + classInfo.coverImage + ` width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M17.754 14a2.249 2.249 0 0 1 2.25 2.249v.575c0 .894-.32 1.76-.902 2.438-1.57 1.834-3.957 2.739-7.102 2.739-3.146 0-5.532-.905-7.098-2.74a3.75 3.75 0 0 1-.898-2.435v-.577a2.249 2.249 0 0 1 2.249-2.25h11.501Zm0 1.5H6.253a.749.749 0 0 0-.75.749v.577c0 .536.192 1.054.54 1.461 1.253 1.468 3.219 2.214 5.957 2.214s4.706-.746 5.962-2.214a2.25 2.25 0 0 0 .541-1.463v-.575a.749.749 0 0 0-.749-.75ZM12 2.004a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 1.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" fill="#fff"/></svg>`;

    container.appendChild(personAvatar);
    container.appendChild(personName);
    container.appendChild(personRole);
    document.getElementById('peopleContainer').appendChild(container);
}

const addTaskToUI = (task) => {
    var taskType = task.type
    let container = document.createElement('a');
    container.id = task.id;
    let taskTitle = document.createElement('strong');
    let taskDate = document.createElement('p');
    let taskIndercater = document.createElement('div');
    let svg
    if (taskType == "resource") {
        svg = '<svg class=svg_' + classInfo.coverImage + ' xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 16 16"><!-- Icon from Fluent UI System Icons by Microsoft Corporation - https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE --><path fill="currentColor" d="M6 3a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1zm0 1h4v1H6zm5-3H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h7.5a.5.5 0 0 0 0-1H5a1 1 0 0 1-1-1v-.003h8.5a.5.5 0 0 0 .5-.5V3a2 2 0 0 0-2-2M4 11.997V3a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v8.997z"/></svg>'
        container.innerHTML = svg;
        container.appendChild(taskTitle);
        container.addEventListener('click', () => {
            openResource(task.taskDescription, task.taskName, task.id)
        })
    } else if (taskType == "poll") {
        const voters = task.voters;
        console.log(voters)
        svg = `<svg class=svg_` + classInfo.coverImage + ` xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 16 16"><!-- Icon from Fluent UI System Icons by Microsoft Corporation - https://github.com/microsoft/fluentui-system-icons/blob/main/LICENSE --><path fill="currentColor" d="M15 8a2 2 0 0 0-2-2H3a2 2 0 1 0 0 4h10a2 2 0 0 0 2-2m-2 1H3a1 1 0 1 1 0-2h10a1 1 0 1 1 0 2M9 3a2 2 0 0 0-2-2H3a2 2 0 1 0 0 4h4a2 2 0 0 0 2-2M3 4a1 1 0 0 1 0-2h4a1 1 0 0 1 0 2zm6 7a2 2 0 1 1 0 4H3a2 2 0 1 1 0-4zm0 3a1 1 0 1 0 0-2H3a1 1 0 1 0 0 2z"/></svg>`
        taskTopBar = document.createElement('div');
        taskTopBar.classList.add('pollTopBar');
    
        // Create title container to hold both the SVG and title
        let titleContainer = document.createElement('div');
        titleContainer.classList.add('pollTitleContainer');
        titleContainer.innerHTML = svg;
        titleContainer.appendChild(taskTitle);
    
        // Create delete icon and confirmation dialog
        if (teacher) {
            let deleteIcon = document.createElement('span');
            let deleteCover = document.createElement('div');
            let deleteText = document.createElement('span');
            let deleteButton = document.createElement('button');
            let cancelButton = document.createElement('button');
            let deleteButtonContainer = document.createElement('div');
    
            deleteText.innerText = 'Are you sure?';
            deleteButton.innerText = 'Delete';
            cancelButton.innerText = 'Cancel';
            cancelButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                deleteCover.style.display = 'none';
            });
    
            deleteButtonContainer.appendChild(deleteButton);
            deleteButtonContainer.appendChild(cancelButton);
            deleteCover.appendChild(deleteText);
            deleteCover.appendChild(deleteButtonContainer);
            deleteCover.classList.add('deleteCover');
            deleteButtonContainer.classList.add('deleteButtonContainer');
            deleteButton.classList.add('dangerButton');
            cancelButton.classList.add('whiteButton');
    
            deleteIcon.classList.add('deleteMessage');
            deleteIcon.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                deleteCover.style.display = 'flex';
            });
            deleteIcon.innerHTML = '<svg class="deleteMessageSVG" width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 1.75a3.25 3.25 0 0 1 3.245 3.066L15.25 5h5.25a.75.75 0 0 1 .102 1.493L20.5 6.5h-.796l-1.28 13.02a2.75 2.75 0 0 1-2.561 2.474l-.176.006H8.313a2.75 2.75 0 0 1-2.714-2.307l-.023-.174L4.295 6.5H3.5a.75.75 0 0 1-.743-.648L2.75 5.75a.75.75 0 0 1 .648-.743L3.5 5h5.25A3.25 3.25 0 0 1 12 1.75Zm6.197 4.75H5.802l1.267 12.872a1.25 1.25 0 0 0 1.117 1.122l.127.006h7.374c.6 0 1.109-.425 1.225-1.002l.02-.126L18.196 6.5ZM13.75 9.25a.75.75 0 0 1 .743.648L14.5 10v7a.75.75 0 0 1-1.493.102L13 17v-7a.75.75 0 0 1 .75-.75Zm-3.5 0a.75.75 0 0 1 .743.648L11 10v7a.75.75 0 0 1-1.493.102L9.5 17v-7a.75.75 0 0 1 .75-.75Zm1.75-6a1.75 1.75 0 0 0-1.744 1.606L10.25 5h3.5A1.75 1.75 0 0 0 12 3.25Z" fill="#ffffff"/></svg>';
    
            deleteButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                fetch("/endpoint/task/delete", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        classid: classInfo.id,
                        taskid: task.id
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'complete') {
                            container.remove();
                        }
                    })
            });
    
            taskTopBar.appendChild(titleContainer);
            taskTopBar.appendChild(deleteIcon);
            taskTopBar.appendChild(deleteCover);
        } else {
            taskTopBar.appendChild(titleContainer);
        }
        taskTitle.innerText = task.taskName;
        container.appendChild(taskTopBar);
        container.classList.add('pollTask');
        const pollOptions = task.options;
        const pollOptionsKeys = Object.keys(pollOptions);
        pollOptionsKeys.forEach(option => {
            let totalVotes = voters.length;
            let pollOption = document.createElement('div');
            let pollOptionText = document.createElement('p');
            let pollOptionCount = document.createElement('p');
            pollOption.classList.add('pollOption');
            pollOptionText.innerText = pollOptions[option]["option"];
            let votePercentage = totalVotes > 0 ? (pollOptions[option]["votes"] / totalVotes * 100).toFixed(0) : 0;
            pollOptionCount.innerText = votePercentage + "%";
    
            pollOption.style.backgroundImage = `linear-gradient(to right, #30384E ${votePercentage}%, #242B3E ${votePercentage}%)`;
            pollOption.appendChild(pollOptionText);
            pollOption.appendChild(pollOptionCount);
            container.appendChild(pollOption);
            if (!voters.includes(userID)) {
                pollOption.addEventListener('click', () => {
                    fetch("/endpoint/poll/vote", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            classid: classInfo.id,
                            pollid: task.id,
                            option: pollOptions[option]["option"]
                        })
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'complete') {
                                const new_poll_data = data.poll_data;
                                // Update the poll UI with new data
                                pollOptionsKeys.forEach((option, index) => {
                                    const newTotalVotes = new_poll_data.voters.length;
                                    const newVoteCount = new_poll_data.options[option].votes;
                                    const newVotePercentage = newTotalVotes > 0 ? (newVoteCount / newTotalVotes * 100).toFixed(0) : 0;
    
                                    // Find all poll options and update them
                                    const pollOptions = container.querySelectorAll('.pollOption');
                                    if (pollOptions[index]) {
                                        // Update the text and percentage
                                        const percentageEl = pollOptions[index].querySelector('p:last-child');
                                        percentageEl.innerText = newVotePercentage + "%";
    
                                        // Update the gradient background
                                        pollOptions[index].style.backgroundImage = `linear-gradient(to right, #30384E ${newVotePercentage}%, #242B3E ${newVotePercentage}%)`;
                                    }
                                });
    
                                // Disable further voting
                                const pollOptions = container.querySelectorAll('.pollOption');
                                pollOptions.forEach(option => {
                                    option.style.pointerEvents = 'none';
                                    option.classList.add('voted');
                                });
                            }
                        })
                });
            };
        })
    }


    else {
        svg = '<svg class=svg_' + classInfo.coverImage + ' width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M7 12.25a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0Zm.75 2.25a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5ZM7 18.25a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0Zm3.75-6.75a.75.75 0 0 0 0 1.5h5.5a.75.75 0 0 0 0-1.5h-5.5ZM10 15.25a.75.75 0 0 1 .75-.75h5.5a.75.75 0 0 1 0 1.5h-5.5a.75.75 0 0 1-.75-.75Zm.75 2.25a.75.75 0 0 0 0 1.5h5.5a.75.75 0 0 0 0-1.5h-5.5Zm8.664-9.086-5.829-5.828a.493.493 0 0 0-.049-.04.626.626 0 0 1-.036-.03 2.072 2.072 0 0 0-.219-.18.652.652 0 0 0-.08-.044l-.048-.024-.05-.029c-.054-.031-.109-.063-.166-.087a1.977 1.977 0 0 0-.624-.138c-.02-.001-.04-.004-.059-.007A.605.605 0 0 0 12.172 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9.828a2 2 0 0 0-.586-1.414ZM18.5 20a.5.5 0 0 1-.5.5H6a.5.5 0 0 1-.5-.5V4a.5.5 0 0 1 .5-.5h6V8a2 2 0 0 0 2 2h4.5v10Zm-5-15.379L17.378 8.5H14a.5.5 0 0 1-.5-.5V4.621Z" fill="#ffffff"/></svg>'
        container.innerHTML = svg;
        container.appendChild(taskTitle);
        container.appendChild(taskDate);
        container.appendChild(taskIndercater);
        container.href = '/task/' + classInfo.id + '/' + task.id;
        const dueDate = new Date(task.taskDue);
        const currentDate = new Date();

        currentDate.setHours(0, 0, 0, 0);
        dueDate.setHours(0, 0, 0, 0);
        if (teacher) {
            taskIndercater.classList.add('taskIndercater', 'complete');
        } else {
            console.log(task.student_data)
            if (!Object.keys(task.student_data).includes(userID)) {
                taskIndercater.classList.add('taskIndercater', 'notstarted');
            } else if (dueDate < currentDate && task.student_data[userID].status !== 'completed') {
                taskIndercater.classList.add('taskIndercater', 'missing');
            } else {
                taskIndercater.classList.add('taskIndercater', task.student_data[userID].status);
            }
        }
    }

    taskTitle.innerText = task.taskName;
    taskDate.innerText = task.taskDue;
    taskContainer.insertBefore(container, taskContainer.firstChild);
}

const sendMessage = () => {
    const message = messageInput.value;
    fetch("/endpoint/class/message", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            classid: classInfo.id,
            message: message,
            messageImportant: messageImportant
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'complete') {

                // Reset and close the input container
                messageInput.value = '';
                messageButton.classList.toggle('createTaskButtonSVGRotate');
                messageInputContainer.classList.remove('messageInputContainerExpand');
            }
        })
}
