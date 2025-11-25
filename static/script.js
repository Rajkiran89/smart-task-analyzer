let currentTasks = []; // 1. Global variable to store tasks

document.addEventListener('DOMContentLoaded', () => {
    // Optional init code
});

async function analyzeTasks() {
    const inputField = document.getElementById('jsonInput');
    const strategyField = document.getElementById('strategy');
    const resultsDiv = document.getElementById('results');
    const btn = document.querySelector('.analyze-btn');

    // 2. Validate Input
    let tasks;
    try {
        tasks = JSON.parse(inputField.value);
    } catch (e) {
        showError("Invalid JSON format. Please check for missing commas or quotes.");
        return;
    }

    // 3. Loading State
    btn.textContent = "Analyzing...";
    btn.disabled = true;
    resultsDiv.innerHTML = `
        <div style="text-align:center; padding: 40px; color: #6b7280;">
            <div class="loader"></div>
            Processing Algorithm...
        </div>
    `;

    try {
        // 4. API Call
        const response = await fetch('/api/tasks/analyze/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategyField.value
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // 5. SUCCESS! Save data and render BOTH views
            currentTasks = data.data; 
            renderList(currentTasks);   // Render the standard list
            renderMatrix(currentTasks); // Render the new Matrix grid
        } else {
            showError(data.message);
        }

    } catch (error) {
        console.error(error);
        showError("Connection failed. Is the Django server running?");
    } finally {
        // Reset Button
        btn.textContent = "Analyze Tasks";
        btn.disabled = false;
    }
}

// --- VIEW SWITCHER ---
function switchView(view) {
    const listDiv = document.getElementById('results');
    const matrixDiv = document.getElementById('matrix-view');
    const listBtn = document.getElementById('listViewBtn');
    const matrixBtn = document.getElementById('matrixViewBtn');

    if (view === 'list') {
        listDiv.style.display = 'block';
        matrixDiv.style.display = 'none';
        listBtn.classList.add('active');
        matrixBtn.classList.remove('active');
    } else {
        listDiv.style.display = 'none';
        matrixDiv.style.display = 'grid'; // CSS Grid
        listBtn.classList.remove('active');
        matrixBtn.classList.add('active');
        
        // Safety check: ensure matrix is rendered if switching views
        if(currentTasks.length > 0) renderMatrix(currentTasks);
    }
}

// --- RENDERERS ---

function renderList(tasks) {
    const container = document.getElementById('results');
    
    if (tasks.length === 0) {
        container.innerHTML = "<p>No tasks found.</p>";
        return;
    }

    const html = tasks.map((task, index) => {
        let priClass = 'priority-low';
        if (index === 0) priClass = 'priority-high';
        else if (index < 3) priClass = 'priority-med';

        return `
            <div class="task-item ${priClass}">
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <span class="score-badge">Score: ${task.score}</span>
                </div>
                
                <div class="meta-info">
                    <span class="meta-tag">📅 ${task.due_date || 'N/A'}</span>
                    <span class="meta-tag">⏱️ ${task.estimated_hours}h</span>
                    <span class="meta-tag">⭐ ${task.importance}/10</span>
                </div>

                <div class="explanation-box">
                    💡 ${task.explanation}
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

function renderMatrix(tasks) {
    // 1. Reset the quadrants
    ['q1', 'q2', 'q3', 'q4'].forEach(id => {
        const title = getQuadTitle(id);
        const el = document.getElementById(id + '-list');
        if(el) el.innerHTML = `<h4>${title}</h4>`;
    });

    // 2. Sort tasks into boxes
    tasks.forEach(task => {
        const imp = parseFloat(task.importance);
        const score = parseFloat(task.score);

        // LOGIC: 
        // Important = Importance >= 7
        // Urgent = Score > 50 (Since score calculates urgency)
        
        const isImportant = imp >= 7;
        const isUrgent = score > 50;

        let targetId = 'q4-list'; // Default to Delete
        
        if (isImportant && isUrgent) targetId = 'q1-list';      // Do First
        else if (isImportant && !isUrgent) targetId = 'q2-list'; // Schedule
        else if (!isImportant && isUrgent) targetId = 'q3-list'; // Delegate
        
        // 3. Create the mini-card HTML
        const item = `
            <div class="mini-task">
                <div style="font-weight:600; margin-bottom:4px;">${task.title}</div>
                <div style="font-size:0.75em; color:#666;">Score: ${task.score}</div>
            </div>
        `;

        // 4. Append to the correct box
        const container = document.getElementById(targetId);
        if(container) container.innerHTML += item;
    });
}

function getQuadTitle(id) {
    if(id==='q1') return "Do First (Urgent & Imp)";
    if(id==='q2') return "Schedule (Imp, Not Urgent)";
    if(id==='q3') return "Delegate (Urgent, Not Imp)";
    return "Eliminate (Neither)";
}

function showError(msg) {
    document.getElementById('results').innerHTML = `
        <div style="background:#fee2e2; color:#991b1b; padding:15px; border-radius:8px;">
            <strong>Error:</strong> ${msg}
        </div>
    `;
}