// Function to open tab
function openTab(evt, tabName) {
    // Get all tab content elements
    var tabcontent = document.getElementsByClassName("tabcontent");
    for (var i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all tab buttons
    var tablinks = document.getElementsByClassName("tablinks");
    for (var i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the selected tab and mark its button as active
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Function to safely get nested object properties
function getNestedValue(obj, path, defaultValue = null) {
    return path.split('.').reduce((current, key) => 
        (current && current[key] !== undefined) ? current[key] : defaultValue, obj);
}

// Function to populate project information
function populateProjectInfo() {
    // Get project data - first try saphire_data.project, then data.project
    let project = getNestedValue(saphireData, 'saphire_data.project', {});
    if (!project || Object.keys(project).length === 0) {
        project = getNestedValue(saphireData, 'data.project', {});
    }
    
    // Get job ID from either location
    let jobId = getNestedValue(saphireData, 'job_id', null);
    if (!jobId) {
        jobId = getNestedValue(saphireData, 'data.job_id', 'Unknown');
    }

    // Update project information
    document.getElementById('projectName').textContent = project.name || 'Not specified';
    document.getElementById('projectDesc').textContent = project.description || 'Not provided';
    document.getElementById('jobId').textContent = jobId;
}

// Function to get SAPHIRE data from either location
function getSaphireData() {
    let data = getNestedValue(saphireData, 'saphire_data', null);
    if (!data) {
        data = getNestedValue(saphireData, 'data', {});
    }
    return data;
}

// Function to update summary counts
function updateSummaryCounts() {
    const data = getSaphireData();
    document.getElementById('faultTreeCount').textContent = (data.fault_trees || []).length;
    document.getElementById('eventTreeCount').textContent = (data.event_trees || []).length;
    document.getElementById('basicEventCount').textContent = (data.basic_events || []).length;
    document.getElementById('endStateCount').textContent = (data.end_states || []).length;
}

// Function to populate basic events list
function populateBasicEvents() {
    const basicEventsList = document.getElementById('basicEventsList');
    const data = getSaphireData();
    const basicEvents = data.basic_events || [];

    if (basicEvents.length === 0) {
        basicEventsList.innerHTML = '<p>No basic events found in the model.</p>';
        return;
    }

    basicEvents.forEach(event => {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'list-item';
        eventDiv.innerHTML = `
            <strong>${event.id || 'Unknown'}</strong>
            ${event.probability ? `<br>Probability: ${event.probability}` : ''}
            ${event.description ? `<br>Description: ${event.description}` : ''}
            ${event.type ? `<br>Type: ${event.type}` : ''}
        `;
        basicEventsList.appendChild(eventDiv);
    });
}

// Function to populate fault trees list
function populateFaultTrees() {
    const faultTreesList = document.getElementById('faultTreesList');
    const data = getSaphireData();
    const faultTrees = data.fault_trees || [];

    if (faultTrees.length === 0) {
        faultTreesList.innerHTML = '<p>No fault trees found in the model.</p>';
        return;
    }

    faultTrees.forEach(tree => {
        const treeDiv = document.createElement('div');
        treeDiv.className = 'list-item';
        treeDiv.innerHTML = `
            <strong>${tree.id || 'Unnamed'}</strong>
            ${tree.description ? `<br>Description: ${tree.description}` : ''}
            ${tree.top_gate ? `<br>Top Gate: ${tree.top_gate}` : ''}
            ${tree.gates ? `<br>Number of Gates: ${tree.gates.length}` : ''}
        `;
        faultTreesList.appendChild(treeDiv);
    });
}

// Function to populate event trees list
function populateEventTrees() {
    const eventTreesList = document.getElementById('eventTreesList');
    const data = getSaphireData();
    const eventTrees = data.event_trees || [];

    if (eventTrees.length === 0) {
        eventTreesList.innerHTML = '<p>No event trees found in the model.</p>';
        return;
    }

    eventTrees.forEach(tree => {
        const treeDiv = document.createElement('div');
        treeDiv.className = 'list-item';
        treeDiv.innerHTML = `
            <strong>${tree.id || 'Unnamed'}</strong>
            ${tree.description ? `<br>Description: ${tree.description}` : ''}
            ${tree.initiating_event ? `<br>Initiating Event: ${tree.initiating_event}` : ''}
            ${tree.branches ? `<br>Number of Branches: ${tree.branches.length}` : ''}
        `;
        eventTreesList.appendChild(treeDiv);
    });
}

// Function to populate raw JSON viewer
function populateRawJSON() {
    const jsonViewer = document.getElementById('jsonViewer');
    jsonViewer.textContent = JSON.stringify(saphireData, null, 2);
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Make sure saphireData is defined
        if (typeof saphireData === 'undefined') {
            throw new Error('SAPHIRE data not found');
        }

        // Populate all sections
        populateProjectInfo();
        updateSummaryCounts();
        populateBasicEvents();
        populateFaultTrees();
        populateEventTrees();
        populateRawJSON();

    } catch (error) {
        console.error('Error initializing visualization:', error);
        // Show error message in the UI
        document.getElementById('app').innerHTML = `
            <div class="error">
                <h2>Error Loading Visualization</h2>
                <p>${error.message}</p>
            </div>
        `;
    }
}); 