import datetime
from datetime import date, timedelta

class TaskAnalyzer:
    def __init__(self, tasks, strategy='smart'):
        self.tasks = tasks
        self.strategy = strategy
        self.today = date.today()
        # Map task IDs to task objects for easier lookup
        self.task_map = {t.get('id', i): t for i, t in enumerate(tasks)}

    def count_business_days(self, start_date, end_date):
        """Counts days excluding weekends (Sat/Sun)"""
        day_diff = (end_date - start_date).days
        work_days = 0
        for i in range(day_diff):
            day = start_date + timedelta(days=i+1)
            if day.weekday() < 5: # 0-4 are Mon-Fri
                work_days += 1
        return work_days

    def detect_cycles(self):
        """
        DFS approach to detect circular dependencies.
        Returns a set of IDs involved in cycles.
        """
        visited = set()
        recursion_stack = set()
        cyclic_nodes = set()

        def dfs(task_id):
            visited.add(task_id)
            recursion_stack.add(task_id)

            task = self.task_map.get(task_id)
            if task and 'dependencies' in task:
                for dep_id in task['dependencies']:
                    if dep_id not in visited:
                        if dfs(dep_id):
                            # CRITICAL FIX: If my child is in a cycle, I am too!
                            cyclic_nodes.add(task_id)
                            return True
                    elif dep_id in recursion_stack:
                        # Found a back edge (cycle detected)
                        cyclic_nodes.add(task_id)
                        return True
            
            recursion_stack.remove(task_id)
            return False

        for task_id in self.task_map:
            if task_id not in visited:
                dfs(task_id)
        
        return cyclic_nodes

    def calculate_urgency(self, due_date_str):
        if not due_date_str:
            return 0
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
            
            
            
            # LOGIC: Business Days
            if due_date < self.today:
                days_left = (due_date - self.today).days # Keep negative for past due
            else:
                days_left = self.count_business_days(self.today, due_date)
            
            # The rest of the scoring logic stays the same...
            if days_left < 0:
                return 100 + (abs(days_left) * 2)
            elif days_left == 0:
                return 80
            elif days_left <= 2: # Tightened threshold since we count work days
                return 60
            else:
                return max(0, 50 - (days_left * 2)) 
        except ValueError:
            return 0

            
    def get_downstream_impact(self, task_id):
        """Calculates how many other tasks are blocked by this one."""
        count = 0
        for t in self.tasks:
            if task_id in t.get('dependencies', []):
                count += 1
        return count

    def analyze(self):
        cyclic_ids = self.detect_cycles()
        analyzed_tasks = []

        for task in self.tasks:
            # 1. Clean Data
            task_id = task.get('id')
            imp = float(task.get('importance', 5))
            hrs = float(task.get('estimated_hours', 5))
            due = task.get('due_date')
            
            # 2. Calculate Factors
            urgency_score = self.calculate_urgency(due)
            impact_score = self.get_downstream_impact(task_id) * 10
            
            # 3. Apply Strategy Weights
            score = 0
            explanation = []

            if task_id in cyclic_ids:
                explanation.append("⚠️ Critical: Circular dependency detected.")
                score = -1 # Push to bottom or flag
            
            elif self.strategy == 'fastest':
                # Prioritize Quick Wins (Low hours = High score)
                score = (1 / (hrs + 1)) * 100
                explanation.append(f"Fast win: Only {hrs} hours.")

            elif self.strategy == 'impact':
                # Prioritize Importance
                score = imp * 15
                explanation.append(f"High Importance rating: {imp}.")

            elif self.strategy == 'deadline':
                # Prioritize Urgency
                score = urgency_score * 2
                explanation.append(f"Urgency score: {urgency_score}.")

            else: # 'smart' (Default Balanced Algorithm)
                # Weighted Formula
                w_urgency = 1.5
                w_importance = 1.2
                w_effort = 0.5 # Negative correlation (lower is better)
                w_dep = 2.0

                effort_score = max(0, (10 - hrs)) * 2 # Invert hours (1hr = 18pts, 10hr = 0pts)
                
                score = (urgency_score * w_urgency) + \
                        (imp * 10 * w_importance) + \
                        (effort_score * w_effort) + \
                        (impact_score * w_dep)
                
                # Dynamic Explanations
                if urgency_score > 60: explanation.append("Due very soon.")
                if imp >= 8: explanation.append("High importance.")
                if hrs <= 2: explanation.append("Quick win.")
                if impact_score > 0: explanation.append(f"Blocks {int(impact_score/10)} other tasks.")

            # Attach results
            task['score'] = round(score, 2)
            task['explanation'] = " ".join(explanation) if explanation else "Standard priority."
            analyzed_tasks.append(task)

        # Sort descending by score
        return sorted(analyzed_tasks, key=lambda x: x['score'], reverse=True)