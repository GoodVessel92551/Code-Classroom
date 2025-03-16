let projects = localStorage.getItem('codeProjects');
const codeProjectTemplate = document.getElementById('codeProjectTemplate');
const container = document.getElementById('codeProjectsContainer');
const loadProjects = () => {
    if (projects) {
        projects = JSON.parse(projects);
        let projectKeys = Object.keys(projects);
        projectKeys.forEach(key => {
            const project = projects[key];
            const clone = codeProjectTemplate.content.cloneNode(true);
            clone.querySelector('.projectName').textContent = project.name;
            clone.querySelector('.projectLink').href = `/quickCode?project=${key}`;
            codeProjectsContainer.appendChild(clone);
        });
    }else{
        let projectJSON = {
            "firstProject":{"name":"First Project","code":"print('Hello World')"}
        }
        localStorage.setItem('codeProjects', JSON.stringify(projectJSON));
        projects = localStorage.getItem('codeProjects');
        loadProjects();
    }
}
loadProjects();

const newProject = () =>{
    let projects = localStorage.getItem('codeProjects');
    let num_projects = localStorage.getItem('num_projects');
    if (num_projects){
        num_projects = parseInt(num_projects);
    }else{
        num_projects = 1;
    }
    projects = JSON.parse(projects);
    let projectKeys = Object.keys(projects);
    if (projectKeys.length > 10){
        alert('You can only have 10 projects');
    }else{
        const randomString = Math.random().toString(36).substring(2, 8);
        let newProject = {
            "name": "New Project #" + num_projects,
            "code": "print('Hello World')"
        }
        projects[randomString] = newProject;
        localStorage.setItem('codeProjects', JSON.stringify(projects));
        localStorage.setItem('num_projects', num_projects+1);
        window.location.href = `/quickCode?project=${randomString}`;
    }
}

const newProjectInstructions = (instructions) => {
    let projects = localStorage.getItem('codeProjects');
    let num_projects = localStorage.getItem('num_projects');
    if (num_projects){
        num_projects = parseInt(num_projects);
    }else{
        num_projects = 1;
    }
    projects = JSON.parse(projects);
    let projectKeys = Object.keys(projects);
    if (projectKeys.length > 10){
        alert('You can only have 10 projects');
    }else{
        const randomString = Math.random().toString(36).substring(2, 8);
        let newProject = {
            "name": "Idea #" + num_projects,
            "code": "#"+instructions
        }
        projects[randomString] = newProject;
        localStorage.setItem('codeProjects', JSON.stringify(projects));
        localStorage.setItem('num_projects', num_projects+1);
        window.location.href = `/quickCode?project=${randomString}`;
    }
}