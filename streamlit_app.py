import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components
from study_planner import StudyPlanner
import random
import base64
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Interview Study Planner",
    page_icon="🎓",
    layout="wide"
)

# Initialize our planner with example data (in a real app, you'd load from a database)
@st.cache_resource
def get_planner():
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
    
    return planner

planner = get_planner()

# Initialize session state for storing study plan
if 'study_plan' not in st.session_state:
    st.session_state.study_plan = []

# Helper functions
def get_difficulty_color(difficulty):
    if difficulty <= 2:
        return "green"
    elif difficulty <= 4:
        return "blue"
    elif difficulty <= 6:
        return "orange"
    else:
        return "red"

def generate_concept_graph():
    # Create a graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    for concept, difficulty in planner.concept_difficulty.items():
        G.add_node(concept, 
                 difficulty=difficulty, 
                 completed=concept in planner.completed_concepts,
                 proficiency=planner.concept_proficiency[concept])
        
        for prereq in planner.concept_dependencies[concept]:
            G.add_edge(prereq, concept)
    
    # Create interactive graph with pyvis
    nt = Network(height="400px", width="100%", directed=True)
    
    # Set physics layout
    nt.barnes_hut(spring_length=150)
    
    # Add nodes with custom styling
    for node in G.nodes():
        difficulty = G.nodes[node]['difficulty']
        completed = G.nodes[node]['completed']
        proficiency = G.nodes[node]['proficiency']
        
        # Set node color based on difficulty and completion
        if completed:
            color = "#28a745"  # Green for completed
        else:
            # Color based on difficulty
            colors = ["#28a745", "#17a2b8", "#ffc107", "#fd7e14", "#dc3545"]
            color_index = min(int((difficulty - 1) / 2), len(colors) - 1)
            color = colors[color_index]
        
        # Size based on number of connections
        size = 25 + 5 * (len(list(G.predecessors(node))) + len(list(G.successors(node))))
        
        nt.add_node(node, label=node, title=f"{node}\nDifficulty: {difficulty}\nProgress: {int(proficiency*100)}%",
                   color=color, size=size)
    
    # Add edges
    for edge in G.edges():
        nt.add_edge(edge[0], edge[1])
    
    # Return HTML
    return nt.generate_html()

# Header
st.title("🎓 Interview Study Planner")
st.markdown("---")

# Main layout with 3 columns
left_col, center_col, right_col = st.columns([1, 2, 1])

# Left sidebar: Recommendations
with left_col:
    # Recommended Concepts
    st.subheader("📋 Recommended Concepts")
    recommended_concepts = planner.get_next_recommended_concepts(limit=3)
    
    if not recommended_concepts:
        st.info("No recommendations available")
    else:
        for concept_name in recommended_concepts:
            concept = {
                'name': concept_name,
                'difficulty': planner.concept_difficulty[concept_name],
                'prerequisites': planner.concept_dependencies[concept_name],
                'proficiency': planner.concept_proficiency[concept_name]
            }
            
            # Create expandable card for each concept
            with st.expander(f"{concept['name']} (Level {concept['difficulty']})", expanded=True):
                if concept['prerequisites']:
                    st.caption(f"Prerequisites: {', '.join(concept['prerequisites'])}")
                else:
                    st.caption("No prerequisites")
                
                # Progress bar
                st.progress(concept['proficiency'])
                st.caption(f"Proficiency: {int(concept['proficiency'] * 100)}%")
    
    # Recommended Problems
    st.subheader("💻 Recommended Problems")
    recommended_problems = planner.get_recommended_problems(limit=5)
    
    if not recommended_problems:
        st.info("No problems recommended")
    else:
        for problem in recommended_problems:
            # Create a container for the problem
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{problem['name']}**")
                    st.caption(f"Concept: {problem['concept']}")
                with col2:
                    difficulty_color = get_difficulty_color(problem['difficulty'])
                    st.markdown(f"<span style='color:{difficulty_color};'>Level {problem['difficulty']}</span>", unsafe_allow_html=True)
                    if st.button("Complete", key=f"rec_{problem['id']}"):
                        planner.mark_problem_completed(problem['id'])
                        st.experimental_rerun()
                st.markdown("---")

# Center column: Concept Graph and Study Plan
with center_col:
    # Concept Graph
    st.subheader("🔄 Concept Dependency Graph")
    graph_html = generate_concept_graph()
    components.html(graph_html, height=450)
    
    # Study Plan
    st.subheader("📅 Study Plan")
    
    # Inputs for generating study plan
    plan_col1, plan_col2 = st.columns([3, 1])
    with plan_col1:
        days = st.slider("Number of days", min_value=1, max_value=30, value=10)
    with plan_col2:
        if st.button("Generate Plan"):
            st.session_state.study_plan = planner.generate_study_plan(days=days)
    
    # Display study plan
    if not st.session_state.study_plan:
        st.info("Generate a study plan to get started")
    else:
        for day in st.session_state.study_plan:
            with st.expander(f"Day {day['day']}", expanded=day['day'] == 1):
                # Concepts for the day
                st.markdown("**Concepts:**")
                concept_cols = st.columns(len(day['concepts']))
                for i, concept in enumerate(day['concepts']):
                    with concept_cols[i]:
                        st.markdown(f"<div style='background-color:#f0f2f6;padding:8px;border-radius:5px;text-align:center;'>{concept}</div>", unsafe_allow_html=True)
                
                # Problems for the day
                st.markdown("**Problems:**")
                for problem in day['problems']:
                    completed = problem['id'] in planner.completed_problems
                    
                    problem_container = st.container()
                    with problem_container:
                        p_col1, p_col2, p_col3 = st.columns([3, 1, 1])
                        with p_col1:
                            if completed:
                                st.markdown(f"~~{problem['name']}~~")
                                st.caption(f"~~{problem['concept']}~~")
                            else:
                                st.markdown(f"{problem['name']}")
                                st.caption(f"{problem['concept']}")
                        with p_col2:
                            difficulty_color = get_difficulty_color(problem['difficulty'])
                            st.markdown(f"<span style='color:{difficulty_color};'>Level {problem['difficulty']}</span>", unsafe_allow_html=True)
                        with p_col3:
                            if not completed:
                                if st.button("Complete", key=f"plan_{problem['id']}"):
                                    planner.mark_problem_completed(problem['id'])
                                    st.experimental_rerun()
                            else:
                                st.markdown("✅")
                    st.markdown("---")

# Right sidebar: Progress & Problems
with right_col:
    # Progress tracking
    st.subheader("📈 Your Progress")
    
    # Overall progress
    total_problems = len([p for concept_probs in planner.concept_problems.values() for p in concept_probs])
    completed_problems = len(planner.completed_problems)
    overall_percentage = completed_problems / total_problems if total_problems > 0 else 0
    
    st.markdown("**Overall Progress**")
    st.progress(overall_percentage)
    st.caption(f"{completed_problems}/{total_problems} problems completed ({int(overall_percentage * 100)}%)")
    
    # Concept progress
    st.markdown("**Concept Progress**")
    for concept, difficulty in planner.concept_difficulty.items():
        concept_problems = [p for p in planner.concept_problems[concept]]
        completed_concept_problems = [p for p in concept_problems if p['id'] in planner.completed_problems]
        percentage = len(completed_concept_problems) / len(concept_problems) if concept_problems else 0
        
        concept_col1, concept_col2 = st.columns([3, 1])
        with concept_col1:
            st.caption(concept)
            st.progress(percentage)
        with concept_col2:
            st.caption(f"{len(completed_concept_problems)}/{len(concept_problems)}")
    
    # Problems list with filter
    st.subheader("📝 Problems")
    
    # Concept filter
    all_concepts = list(planner.concept_difficulty.keys())
    selected_concept = st.selectbox("Filter by concept", ["All Concepts"] + all_concepts)
    
    # Get filtered problems
    filtered_problems = []
    for concept, concept_problems in planner.concept_problems.items():
        if selected_concept == "All Concepts" or selected_concept == concept:
            filtered_problems.extend(concept_problems)
    
    # Display problems
    if not filtered_problems:
        st.info("No problems found")
    else:
        # Group problems by concept if "All Concepts" is selected
        if selected_concept == "All Concepts":
            concepts_to_display = all_concepts
        else:
            concepts_to_display = [selected_concept]
        
        for concept in concepts_to_display:
            # Get problems for this concept
            concept_problems = [p for p in filtered_problems if p['concept'] == concept]
            if not concept_problems:
                continue
            
            # Display concept header if showing all concepts
            if selected_concept == "All Concepts":
                st.markdown(f"**{concept}**")
            
            # Display problems
            for problem in concept_problems:
                completed = problem['id'] in planner.completed_problems
                
                with st.container():
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        if completed:
                            st.markdown(f"~~{problem['name']}~~")
                        else:
                            st.markdown(f"{problem['name']}")
                    with cols[1]:
                        difficulty_color = get_difficulty_color(problem['difficulty'])
                        st.markdown(f"<span style='color:{difficulty_color};'>Level {problem['difficulty']}</span>", unsafe_allow_html=True)
                    with cols[2]:
                        if not completed:
                            if st.button("Complete", key=f"list_{problem['id']}"):
                                planner.mark_problem_completed(problem['id'])
                                st.experimental_rerun()
                        else:
                            st.markdown("✅")
                st.markdown("---")

# Add a bit of custom CSS to improve the look
st.markdown("""
<style>
    .stProgress .st-bo {
        background-color: #17a2b8;
    }
    .stProgress .st-bp {
        background-color: #28a745;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True) 