# 🧠 Smart Task Analyzer

A full-stack Django application that intelligently scores and prioritizes tasks based on urgency, importance, effort, and dependency chains.

## 🛠️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd smart_task_analyzer
Create and Activate Virtual Environment

Bash

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
Install Dependencies

Bash

pip install -r requirements.txt
Run the Application

Bash

python manage.py runserver
Open your browser to http://127.0.0.1:8000/.

Run Unit Tests

Bash

python manage.py test
Algorithm Explanation
The core of this application is the Priority Scoring Engine located in analyzer/services.py. The algorithm assigns a numerical score to each task, where a higher score indicates higher priority. The scoring logic is derived from a Weighted Sum Model (WSM) that balances four competing factors.

1. Urgency (Date Intelligence)
We calculate urgency by comparing the due_date to the current date.

Past Due: Critical priority. We apply a base score of 100 plus a penalty for every day overdue (100 + days_late * 2). This ensures overdue tasks always top the list.

Business Days: To prevent false security over weekends, the algorithm uses a count_business_days helper that calculates strict working days remaining, ignoring Saturdays and Sundays.

Linear Decay: For future tasks, urgency decays linearly as the deadline approaches.

2. Dependencies (Graph Theory)
This is the most critical factor for unblocking teams.

Blocking Bonus: We inspect the dependency graph to see how many other tasks are waiting on the current task. Each downstream dependent adds significant points (+10 per blocked task).

Cycle Detection: Before scoring, we run a Depth First Search (DFS) algorithm to detect circular dependencies (e.g., A → B → A). If a cycle is detected, involved tasks are flagged with a score of -1 and a warning message, preventing the system from recommending impossible workflows.

3. Importance & Effort
Importance: User-defined rating (1-10) is multiplied by a weight factor (1.2x) to distinguish high-value work from busy work.

Effort: We apply an inverted effort score (10 - hours), rewarding "Quick Wins" (low effort tasks) with a small point boost to encourage clearing the queue.

4. Configurable Strategies
The algorithm is dynamic. Depending on the user's selected strategy, the weights shift:

Smart Balance: The default weighted formula described above.

Fastest Wins: Prioritizes 1 / effort.

High Impact: Prioritizes Importance * 15.

Deadline Driven: Prioritizes Urgency * 2.

Design Decisions & Trade-offs
1. Stateless vs. Stateful
Decision: I chose to make the API primarily stateless (receiving JSON input rather than saving to a DB for every analysis). Why: This allows for instant "what-if" scenarios. A user can paste a potential schedule, see the scoring, and tweak it without polluting the permanent database. It also simplifies the testing of the algorithm.

2. Dependency Cycle Handling
Decision: I chose to flag cycles with a negative score rather than throwing a server error. Why: In a real-world scenario, crashing the app helps no one. By returning a -1 score and an explanation ("Critical: Circular Dependency"), the user can identify exactly which tasks are causing the deadlock and fix them.

3. Frontend Architecture
Decision: I separated the Frontend logic (script.js) and Styling (style.css) into the static/ folder rather than keeping them inline. Why: This adheres to the Separation of Concerns principle, making the code cleaner, maintainable, and easier to debug.

Time Breakdown
Backend Logic (TaskAnalyzer): 2.5 hours

Focus on cycle detection and business day calculation.

API Integration: 0.5 hours

Frontend (HTML/CSS/JS): 2 hours

Implemented Glassmorphism UI and dynamic Eisenhower Matrix.

Unit Testing: 45 mins

Verified edge cases like circular dependencies.

Documentation & Cleanup: 30 mins

Total Time: ~6 hours

Bonus Challenges Attempted
I successfully implemented the following bonus features:

Dependency Graph Visualization (Cycle Detection): Implemented a DFS algorithm to detect and flag circular dependencies.

Date Intelligence: The algorithm calculates "Business Days," ignoring weekends when determining urgency.

Eisenhower Matrix View: Added a dynamic frontend view to toggle between a list and a 2x2 Urgent/Important grid.

Unit Tests: Wrote comprehensive TestCase coverage for urgency, importance, and cycle detection logic.

Future Improvements
With more time, I would add:

Database Persistence: Save task lists to Django models so users don't have to re-paste JSON.

Drag-and-Drop UI: Allow users to drag tasks between Eisenhower quadrants to update their importance/urgency automatically.

User Accounts: Use Django Auth to let different users manage their own task lists.
