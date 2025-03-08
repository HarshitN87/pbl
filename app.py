from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from study_planner import StudyPlanner  # Import the StudyPlanner class we created earlier

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # More specific CORS configuration
CORS(app)  # Allow cross-origin requests

# Initialize our planner with some example data
planner = StudyPlanner()

# Add concepts with difficulty and prerequisites
planner.add_concept("Arrays", 2)
planner.add_concept("Strings", 2)
planner.add_concept("Hash Tables", 3, ["Arrays"])
planner.add_concept("Linked Lists", 3)
planner.add_concept("Stacks & Queues", 4, ["Arrays", "Linked Lists"])
planner.add_concept("Trees", 5, ["Linked Lists"])
planner.add_concept("Graphs", 7, ["Trees"])
planner.add_concept("Dynamic Programming", 8, ["Arrays", "Recursion"])
planner.add_concept("Recursion", 5)
planner.add_concept("Sorting", 4, ["Arrays"])
planner.add_concept("Binary Search", 4, ["Arrays", "Sorting"])

# Add problems for each concept
planner.add_problem("p1", "Arrays", 1, "Two Sum")
planner.add_problem("p2", "Arrays", 2, "Container With Most Water")
planner.add_problem("p3", "Arrays", 3, "Merge Intervals")
planner.add_problem("p4", "Strings", 1, "Valid Anagram")
planner.add_problem("p5", "Strings", 2, "Longest Palindromic Substring")
planner.add_problem("p6", "Hash Tables", 2, "Group Anagrams")
planner.add_problem("p7", "Hash Tables", 3, "LRU Cache")
planner.add_problem("p8", "Linked Lists", 2, "Reverse Linked List")
planner.add_problem("p9", "Recursion", 3, "Generate Parentheses")
planner.add_problem("p10", "Dynamic Programming", 4, "Climbing Stairs")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/concepts', methods=['GET'])
def get_concepts():
    concepts = []
    for concept, difficulty in planner.concept_difficulty.items():
        concepts.append({
            'name': concept,
            'difficulty': difficulty,
            'prerequisites': planner.concept_dependencies[concept],
            'proficiency': planner.concept_proficiency[concept],
            'completed': concept in planner.completed_concepts
        })
    return jsonify(concepts)

@app.route('/api/problems', methods=['GET'])
def get_problems():
    problems = []
    for concept, concept_problems in planner.concept_problems.items():
        for problem in concept_problems:
            problems.append({
                'id': problem['id'],
                'name': problem.get('name', problem['id']),
                'concept': problem['concept'],
                'difficulty': problem['difficulty'],
                'completed': problem['id'] in planner.completed_problems
            })
    return jsonify(problems)

@app.route('/api/available-concepts', methods=['GET'])
def get_available_concepts():
    available = planner.get_available_concepts()
    return jsonify(available)

@app.route('/api/recommended-concepts', methods=['GET'])
def get_recommended_concepts():
    limit = request.args.get('limit', 3, type=int)
    recommended = planner.get_next_recommended_concepts(limit=limit)
    return jsonify(recommended)

@app.route('/api/recommended-problems', methods=['GET'])
def get_recommended_problems():
    limit = request.args.get('limit', 5, type=int)
    recommended = planner.get_recommended_problems(limit=limit)
    return jsonify(recommended)

@app.route('/api/learning-path', methods=['GET'])
def get_learning_path():
    path = planner.get_learning_path()
    return jsonify(path)

@app.route('/api/study-plan', methods=['GET'])
def get_study_plan():
    days = request.args.get('days', 10, type=int)
    plan = planner.generate_study_plan(days=days)
    return jsonify(plan)

@app.route('/api/complete-problem', methods=['POST'])
def complete_problem():
    data = request.json
    problem_id = data.get('problemId')
    if not problem_id:
        return jsonify({'error': 'Problem ID is required'}), 400
    
    planner.mark_problem_completed(problem_id)
    return jsonify({'success': True})

@app.route('/api/concept-graph', methods=['GET'])
def get_concept_graph():
    nodes = []
    links = []
    
    for concept, difficulty in planner.concept_difficulty.items():
        nodes.append({
            'id': concept,
            'difficulty': difficulty,
            'completed': concept in planner.completed_concepts,
            'proficiency': planner.concept_proficiency[concept]
        })
        
        for prereq in planner.concept_dependencies[concept]:
            links.append({
                'source': prereq,
                'target': concept
            })
    
    return jsonify({
        'nodes': nodes,
        'links': links
    })

@app.route('/api/add-concept', methods=['POST'])
def add_concept():
    data = request.json
    concept_name = data.get('name')
    difficulty = data.get('difficulty')
    prerequisites = data.get('prerequisites', [])
    
    if not concept_name or not difficulty:
        return jsonify({'error': 'Name and difficulty are required'}), 400
    
    planner.add_concept(concept_name, difficulty, prerequisites)
    return jsonify({'success': True})

@app.route('/api/add-problem', methods=['POST'])
def add_problem():
    data = request.json
    problem_id = data.get('id')
    concept = data.get('concept')
    difficulty = data.get('difficulty')
    name = data.get('name')
    
    if not problem_id or not concept or not difficulty:
        return jsonify({'error': 'ID, concept, and difficulty are required'}), 400
    
    planner.add_problem(problem_id, concept, difficulty, name)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
