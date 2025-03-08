// API endpoints
const API_BASE = '/api';
const API = {
    CONCEPTS: `${API_BASE}/concepts`,
    PROBLEMS: `${API_BASE}/problems`,
    AVAILABLE_CONCEPTS: `${API_BASE}/available-concepts`,
    RECOMMENDED_CONCEPTS: `${API_BASE}/recommended-concepts`,
    RECOMMENDED_PROBLEMS: `${API_BASE}/recommended-problems`,
    LEARNING_PATH: `${API_BASE}/learning-path`,
    STUDY_PLAN: `${API_BASE}/study-plan`,
    COMPLETE_PROBLEM: `${API_BASE}/complete-problem`,
    CONCEPT_GRAPH: `${API_BASE}/concept-graph`
};

// State management
let concepts = [];
let problems = [];
let studyPlan = [];

// DOM Elements
const $recommendedConcepts = document.getElementById('recommended-concepts');
const $recommendedProblems = document.getElementById('recommended-problems');
const $conceptProgress = document.getElementById('concept-progress');
const $overallProgress = document.getElementById('overall-progress');
const $problemsList = document.getElementById('problems-list');
const $conceptFilter = document.getElementById('concept-filter');
const $studyPlan = document.getElementById('study-plan');
const $generatePlanBtn = document.getElementById('generate-plan-btn');
const $createPlanBtn = document.getElementById('create-plan-btn');
const $daysInput = document.getElementById('days-input');
const $conceptGraph = document.getElementById('concept-graph');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing app...");
    initialize();
});

async function initialize() {
    try {
        console.log("Fetching concepts...");
        // Load initial data
        await Promise.all([
            fetchConcepts(),
            fetchProblems()
        ]);
        
        console.log("Data loaded. Concepts:", concepts.length, "Problems:", problems.length);
        
        // Render UI components
        populateConceptFilter();
        renderRecommendedConcepts();
        renderRecommendedProblems();
        renderProgress();
        renderProblems();
        renderConceptGraph();
        
        // Add event listeners
        $conceptFilter.addEventListener('change', renderProblems);
        $generatePlanBtn.addEventListener('click', showPlanModal);
        $createPlanBtn.addEventListener('click', generateStudyPlan);
        
        // Bootstrap modal initialization
        const planModal = new bootstrap.Modal(document.getElementById('plan-modal'));
        window.planModal = planModal;
        
        console.log("Initialization complete");
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Failed to initialize app. See console for details.');
    }
}

// API functions
async function fetchConcepts() {
    const response = await fetch(API.CONCEPTS);
    concepts = await response.json();
    return concepts;
}

async function fetchProblems() {
    const response = await fetch(API.PROBLEMS);
    problems = await response.json();
    return problems;
}

async function fetchRecommendedConcepts() {
    const response = await fetch(API.RECOMMENDED_CONCEPTS);
    return await response.json();
}

async function fetchRecommendedProblems() {
    const response = await fetch(API.RECOMMENDED_PROBLEMS);
    return await response.json();
}

async function fetchStudyPlan(days) {
    const response = await fetch(`${API.STUDY_PLAN}?days=${days}`);
    studyPlan = await response.json();
    return studyPlan;
}

async function fetchConceptGraph() {
    const response = await fetch(API.CONCEPT_GRAPH);
    return await response.json();
}

async function markProblemCompleted(problemId) {
    await fetch(API.COMPLETE_PROBLEM, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ problemId })
    });
    
    // Refresh data
    await Promise.all([
        fetchConcepts(),
        fetchProblems()
    ]);
    
    // Update UI
    renderRecommendedConcepts();
    renderRecommendedProblems();
    renderProgress();
    renderProblems();
    renderConceptGraph();
}

// UI Rendering functions
function populateConceptFilter() {
    $conceptFilter.innerHTML = '<option value="all">All Concepts</option>';
    
    concepts.forEach(concept => {
        const option = document.createElement('option');
        option.value = concept.name;
        option.textContent = concept.name;
        $conceptFilter.appendChild(option);
    });
}

async function renderRecommendedConcepts() {
    const recommendedConcepts = await fetchRecommendedConcepts();
    
    $recommendedConcepts.innerHTML = '';
    
    if (recommendedConcepts.length === 0) {
        $recommendedConcepts.innerHTML = '<li class="list-group-item">No recommendations available</li>';
        return;
    }
    
    recommendedConcepts.forEach(conceptName => {
        const concept = concepts.find(c => c.name === conceptName);
        if (!concept) return;
        
        const li = document.createElement('li');
        li.className = 'list-group-item concept-card';
        
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${concept.name}</h6>
                    <div class="text-muted small">
                        ${concept.prerequisites.length > 0 ? 
                          `Prerequisites: ${concept.prerequisites.join(', ')}` : 
                          'No prerequisites'}
                    </div>
                </div>
                <span class="badge bg-secondary difficulty-${concept.difficulty}">
                    Level ${concept.difficulty}
                </span>
            </div>
            <div class="progress concept-progress-bar mt-2">
                <div class="progress-bar" role="progressbar" 
                     style="width: ${concept.proficiency * 100}%" 
                     aria-valuenow="${concept.proficiency * 100}" 
                     aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
        `;
        
        $recommendedConcepts.appendChild(li);
    });
}

async function renderRecommendedProblems() {
    const recommendedProblems = await fetchRecommendedProblems();
    
    $recommendedProblems.innerHTML = '';
    
    if (recommendedProblems.length === 0) {
        $recommendedProblems.innerHTML = '<li class="list-group-item">No problems recommended</li>';
        return;
    }
    
    recommendedProblems.forEach(problem => {
        const li = document.createElement('li');
        li.className = 'list-group-item problem-card d-flex justify-content-between align-items-center';
        
        li.innerHTML = `
            <div>
                <div><b>${problem.name || problem.id}</b></div>
                <small class="text-muted">${problem.concept}</small>
            </div>
            <div>
                <span class="badge bg-secondary difficulty-${problem.difficulty}">
                    Level ${problem.difficulty}
                </span>
                <button class="btn btn-sm btn-outline-success ms-2 complete-btn" 
                        data-problem-id="${problem.id}">
                    <i class="fas fa-check"></i>
                </button>
            </div>
        `;
        
        $recommendedProblems.appendChild(li);
    });
    
    // Add event listeners for complete buttons
    document.querySelectorAll('.complete-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const problemId = e.currentTarget.dataset.problemId;
            await markProblemCompleted(problemId);
        });
    });
}

function renderProgress() {
    // Calculate overall progress
    const completedProblems = problems.filter(p => p.completed).length;
    const totalProblems = problems.length;
    const overallPercentage = (completedProblems / totalProblems) * 100;
    
    $overallProgress.style.width = `${overallPercentage}%`;
    $overallProgress.setAttribute('aria-valuenow', overallPercentage);
    $overallProgress.textContent = `${Math.round(overallPercentage)}%`;
    
    // Render progress for each concept
    $conceptProgress.innerHTML = '';
    
    concepts.forEach(concept => {
        const conceptProblems = problems.filter(p => p.concept === concept.name);
        const completedConceptProblems = conceptProblems.filter(p => p.completed).length;
        const percentage = conceptProblems.length > 0 ? 
            (completedConceptProblems / conceptProblems.length) * 100 : 0;
        
        const div = document.createElement('div');
        div.className = 'mb-2';
        
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <small>${concept.name}</small>
                <small>${completedConceptProblems}/${conceptProblems.length}</small>
            </div>
            <div class="progress" style="height: 5px;">
                <div class="progress-bar ${percentage === 100 ? 'bg-success' : 'bg-info'}" 
                     role="progressbar" style="width: ${percentage}%" 
                     aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
        `;
        
        $conceptProgress.appendChild(div);
    });
}

function renderProblems() {
    const selectedConcept = $conceptFilter.value;
    
    let filteredProblems = problems;
    if (selectedConcept !== 'all') {
        filteredProblems = problems.filter(p => p.concept === selectedConcept);
    }
    
    $problemsList.innerHTML = '';
    
    if (filteredProblems.length === 0) {
        $problemsList.innerHTML = '<div class="alert alert-info">No problems found</div>';
        return;
    }
    
    // Group problems by concept
    const problemsByConceptMap = filteredProblems.reduce((acc, problem) => {
        if (!acc[problem.concept]) {
            acc[problem.concept] = [];
        }
        acc[problem.concept].push(problem);
        return acc;
    }, {});
    
    // Sort by concept name and render
    Object.keys(problemsByConceptMap).sort().forEach(conceptName => {
        const conceptProblems = problemsByConceptMap[conceptName];
        
        if (selectedConcept === 'all') {
            const conceptHeader = document.createElement('h6');
            conceptHeader.className = 'mt-3 mb-2';
            conceptHeader.textContent = conceptName;
            $problemsList.appendChild(conceptHeader);
        }
        
        conceptProblems.forEach(problem => {
            const div = document.createElement('div');
            div.className = `card problem-card mb-2 ${problem.completed ? 'completed' : ''}`;
            
            div.innerHTML = `
                <div class="card-body py-2 px-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div>${problem.name || problem.id}</div>
                            <small class="text-muted">Difficulty: ${problem.difficulty}</small>
                        </div>
                        <div>
                            ${problem.completed ? 
                              '<span class="badge bg-success"><i class="fas fa-check"></i> Completed</span>' : 
                              `<button class="btn btn-sm btn-outline-primary complete-btn" 
                                       data-problem-id="${problem.id}">
                                   Mark Complete
                               </button>`
                            }
                        </div>
                    </div>
                </div>
            `;
            
            $problemsList.appendChild(div);
        });
    });
    
    // Add event listeners for complete buttons
    document.querySelectorAll('.complete-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const problemId = e.currentTarget.dataset.problemId;
            await markProblemCompleted(problemId);
        });
    });
}

function showPlanModal() {
    window.planModal.show();
}

async function generateStudyPlan() {
    const days = parseInt($daysInput.value) || 10;
    
    await fetchStudyPlan(days);
    renderStudyPlan();
    
    window.planModal.hide();
}

function renderStudyPlan() {
    $studyPlan.innerHTML = '';
    
    if (!studyPlan || studyPlan.length === 0) {
        $studyPlan.innerHTML = '<div class="alert alert-info">No study plan available</div>';
        return;
    }
    
    studyPlan.forEach(day => {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'day-card';
        
        const dayProblems = day.problems.map(p => {
            const problem = typeof p === 'string' ? 
                problems.find(prob => prob.id === p) : p;
            
            if (!problem) return '';
            
            return `
                <div class="problem-card p-2 ${problem.completed ? 'completed' : ''}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div>${problem.name || problem.id}</div>
                            <small class="text-muted">${problem.concept}</small>
                        </div>
                        <span class="badge bg-secondary difficulty-${problem.difficulty}">
                            Level ${problem.difficulty}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
        
        const conceptTags = day.concepts.map(c => 
            `<span class="concept-tag">${c}</span>`
        ).join('');
        
        dayDiv.innerHTML = `
            <div class="day-header">
                Day ${day.day}
            </div>
            <div class="mb-2">
                <strong>Concepts:</strong> 
                <div class="mt-1">${conceptTags}</div>
            </div>
            <div>
                <strong>Problems:</strong>
                <div class="mt-2">${dayProblems}</div>
            </div>
        `;
        
        $studyPlan.appendChild(dayDiv);
    });
}

function renderConceptGraph() {
    // Clear any existing graph
    d3.select("#concept-graph").html("");
    
    // Fetch graph data and render
    fetchConceptGraph().then(graphData => {
        const width = document.getElementById('concept-graph').clientWidth;
        const height = 400;
        
        const svg = d3.select("#concept-graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
            
        // Create a force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(50));
            
        // Draw the links
        const link = svg.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter()
            .append("line")
            .attr("class", "concept-link")
            .attr("stroke-width", 2);
            
        // Draw the nodes
        const node = svg.append("g")
            .selectAll("g")
            .data(graphData.nodes)
            .enter()
            .append("g")
            .attr("class", "concept-node")
            .on("mouseover", function() {
                d3.select(this).select("circle").transition()
                    .duration(300)
                    .attr("r", 30);
            })
            .on("mouseout", function() {
                d3.select(this).select("circle").transition()
                    .duration(300)
                    .attr("r", d => getNodeRadius(d));
            })
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
                
        // Add circles to the nodes
        node.append("circle")
            .attr("r", d => getNodeRadius(d))
            .attr("fill", d => getNodeColor(d))
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);
            
        // Add labels to the nodes
        node.append("text")
            .text(d => d.id)
            .attr("text-anchor", "middle")
            .attr("dy", 4)
            .attr("font-size", "10px")
            .attr("fill", "#fff");
            
        // Update positions during simulation
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
                
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
        
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        function getNodeRadius(d) {
            return d.completed ? 25 : 20;
        }
        
        function getNodeColor(d) {
            if (d.completed) return "#28a745";
            
            // Color based on difficulty
            const colors = [
                "#28a745", // 1-2: Green
                "#17a2b8", // 3-4: Blue
                "#ffc107", // 5-6: Yellow
                "#fd7e14", // 7-8: Orange
                "#dc3545"  // 9-10: Red
            ];
            
            const colorIndex = Math.min(Math.floor((d.difficulty - 1) / 2), colors.length - 1);
            return colors[colorIndex];
        }
    });
}
