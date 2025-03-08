from collections import defaultdict, deque
import heapq

class StudyPlanner:
    def __init__(self):
        # Concept dependency graph: concept -> list of prerequisites
        self.concept_dependencies = defaultdict(list)
        
        # Reverse dependencies: concept -> list of concepts that depend on it
        self.reverse_dependencies = defaultdict(list)
        
        # Track difficulty of each concept (1-10)
        self.concept_difficulty = {}
        
        # Dictionary to store problems for each concept
        self.concept_problems = defaultdict(list)
        
        # Track user progress
        self.completed_problems = set()
        self.completed_concepts = set()
        self.concept_proficiency = defaultdict(float)  # 0.0 to 1.0
    
    def add_concept(self, concept, difficulty, prerequisites=None):
        """Add a concept with its difficulty and prerequisites."""
        if prerequisites is None:
            prerequisites = []
        
        self.concept_difficulty[concept] = difficulty
        self.concept_dependencies[concept] = prerequisites
        
        # Update reverse dependencies
        for prereq in prerequisites:
            self.reverse_dependencies[prereq].append(concept)
    
    def add_problem(self, problem_id, concept, difficulty, name=None):
        """Add a problem for a specific concept."""
        self.concept_problems[concept].append({
            'id': problem_id,
            'difficulty': difficulty,
            'concept': concept,
            'name': name or problem_id
        })
    
    def mark_problem_completed(self, problem_id):
        """Mark a problem as completed and update concept proficiency."""
        self.completed_problems.add(problem_id)
        
        # Find the problem and its concept
        for concept, problems in self.concept_problems.items():
            for problem in problems:
                if problem['id'] == problem_id:
                    # Update proficiency for this concept
                    completed_count = sum(1 for p in problems if p['id'] in self.completed_problems)
                    self.concept_proficiency[concept] = completed_count / len(problems)
                    
                    # If proficiency is high enough, mark concept as completed
                    if self.concept_proficiency[concept] >= 0.8:
                        self.completed_concepts.add(concept)
                    return
    
    def get_available_concepts(self):
        """Get concepts that can be studied now (all prerequisites satisfied)."""
        available = []
        
        for concept in self.concept_dependencies:
            if concept not in self.completed_concepts:
                prerequisites_met = all(
                    prereq in self.completed_concepts 
                    for prereq in self.concept_dependencies[concept]
                )
                if prerequisites_met:
                    available.append(concept)
        
        return available
    
    def get_next_recommended_concepts(self, limit=3):
        """Get recommended concepts to study next."""
        available = self.get_available_concepts()
        
        # Calculate a score for each available concept
        concept_scores = []
        for concept in available:
            # Base score is inverse of difficulty (easier concepts get higher score)
            base_score = 1.0 / self.concept_difficulty[concept]
            
            # Boost score if concept unlocks many other concepts
            unlock_boost = len(self.reverse_dependencies[concept]) * 0.2
            
            # Priority to concepts that have in-progress proficiency
            progress_boost = self.concept_proficiency[concept] * 0.5
            
            total_score = base_score + unlock_boost + progress_boost
            concept_scores.append((-total_score, concept))  # Negative for max-heap
        
        # Get top concepts
        heapq.heapify(concept_scores)
        return [heapq.heappop(concept_scores)[1] for _ in range(min(limit, len(concept_scores)))]
    
    def get_recommended_problems(self, limit=5):
        """Get recommended problems to solve next."""
        recommended_concepts = self.get_next_recommended_concepts(limit=3)
        recommended_problems = []
        
        for concept in recommended_concepts:
            # Get uncompleted problems for this concept
            uncompleted = [
                p for p in self.concept_problems[concept] 
                if p['id'] not in self.completed_problems
            ]
            
            # Sort by difficulty (easier first if proficiency is low)
            proficiency = self.concept_proficiency[concept]
            if proficiency < 0.3:
                # Sort by increasing difficulty if beginner
                sorted_problems = sorted(uncompleted, key=lambda p: p['difficulty'])
            else:
                # Sort by decreasing difficulty if more proficient
                sorted_problems = sorted(uncompleted, key=lambda p: -p['difficulty'])
            
            # Add top problems from this concept
            recommended_problems.extend(sorted_problems[:2])
            
            if len(recommended_problems) >= limit:
                break
        
        return recommended_problems[:limit]
    
    def get_learning_path(self):
        """Generate a complete learning path through all concepts."""
        # Use topological sort to find a valid learning order
        visited = set()
        temp_visited = set()
        order = []
        
        def dfs(concept):
            if concept in temp_visited:
                raise ValueError("Cycle detected in concept dependencies")
            if concept in visited:
                return
            
            temp_visited.add(concept)
            
            for prereq in self.concept_dependencies[concept]:
                dfs(prereq)
            
            temp_visited.remove(concept)
            visited.add(concept)
            order.append(concept)
        
        # Run DFS for each concept
        for concept in self.concept_dependencies:
            if concept not in visited:
                dfs(concept)
        
        # Reverse to get correct order (prerequisites first)
        return order[::-1]
    
    def generate_study_plan(self, days):
        """Generate a day-by-day study plan."""
        learning_path = [c for c in self.get_learning_path() if c not in self.completed_concepts]
        study_plan = []
        
        # Distribute concepts and problems across days
        concepts_per_day = max(1, len(learning_path) // days)
        
        for day in range(1, days + 1):
            day_concepts = learning_path[:concepts_per_day]
            learning_path = learning_path[concepts_per_day:]
            
            day_plan = {
                'day': day,
                'concepts': day_concepts,
                'problems': []
            }
            
            # Add 2-3 problems for each concept
            for concept in day_concepts:
                concept_problems = [
                    p for p in self.concept_problems[concept]
                    if p['id'] not in self.completed_problems
                ]
                day_plan['problems'].extend(concept_problems[:2])
            
            study_plan.append(day_plan)
            
            if not learning_path:
                break
        
        return study_plan
