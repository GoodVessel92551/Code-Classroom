let classesContainer = document.getElementById("classesContainer");
const template = document.getElementById("classroomTemplate");
const noClasses = document.getElementById("noClasses");
let classesNum = 0;

Object.keys(classes).forEach(key => {
    classesNum++;
    let classInfo = classes[key].classInfo;


    const clone = template.content.cloneNode(true);

    
    const link = clone.querySelector("a");

    link.addEventListener("click", function() {
        link.classList.add("openClassroom");

        // This ensures that if the user navigates back to this page, the "openClassroom" 
        // class is removed, resetting the link's state.
        // A flag is used to ensure the event listener is only added once.
        if (!window.homePageShowListenerAdded) {
            window.addEventListener("pageshow", (event) => {
            if (event.persisted) {
                document.querySelectorAll(".openClassroom").forEach(el => {
                el.classList.remove("openClassroom");
                });
            }
            });
            window.homePageShowListenerAdded = true;
        }
    });
    
        

    const img = clone.querySelector("img");
    const title = clone.querySelector("h3");
    const description = clone.querySelector("p");


    img.src = "/static/coverImages/classroomCovers/" + classInfo.coverImage + "Gradient.webp";
    title.textContent = classInfo.name;
    description.textContent = classInfo.description;
    link.href = "/classroom/" + key;

    classesContainer.prepend(clone);
});

console.log(classesNum);

if (classesNum == 0) {
    noClasses.style.display = "flex";
}