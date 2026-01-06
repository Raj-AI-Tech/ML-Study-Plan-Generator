"""
ML Study Companion - Streamlit UI (FIXED)
Beautiful, intuitive interface for the study plan generator
"""

import streamlit as st
import json
from datetime import datetime
import plotly.graph_objects as go

# Import the study plan generator
from study_plan_generator import (
    StudyPlanGenerator,
    StudyGoal,
    DifficultyLevel,
    TimePreference
)

# Page configuration
st.set_page_config(
    page_title="ML Study Companion",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
    }
    .study-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 10px 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .session-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .milestone-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'generator' not in st.session_state:
    st.session_state.generator = StudyPlanGenerator()

if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'create'


def load_all_plans():
    """Load all study plans from state.json"""
    try:
        with open('state.json', 'r') as f:
            data = json.load(f)
            return data.get('study_plans', [])
    except FileNotFoundError:
        return []


def create_progress_chart(plan):
    """Create a progress visualization"""
    today = datetime.now().date()
    plan_start = datetime.fromisoformat(plan['created_at']).date()

    completed_sessions = sum(1 for s in plan['sessions'] if s.get('completed', False))
    total_sessions = len(plan['sessions'])

    fig = go.Figure(data=[
        go.Bar(
            x=['Completed', 'Remaining'],
            y=[completed_sessions, total_sessions - completed_sessions],
            marker_color=['#4CAF50', '#e0e0e0']
        )
    ])

    fig.update_layout(
        title="Study Progress",
        yaxis_title="Sessions",
        height=300,
        showlegend=False
    )

    return fig


def create_topic_distribution_chart(plan):
    """Create topic distribution pie chart"""
    topics = {}
    for session in plan['sessions']:
        topic = session['topic']
        topics[topic] = topics.get(topic, 0) + 1

    fig = go.Figure(data=[
        go.Pie(
            labels=list(topics.keys()),
            values=list(topics.values()),
            hole=0.4
        )
    ])

    fig.update_layout(
        title="Topic Distribution",
        height=400
    )

    return fig


def create_timeline_chart(plan):
    """Create study timeline"""
    dates = []
    topics = []
    durations = []

    for session in plan['sessions']:
        dates.append(session['date'])
        topics.append(session['topic'])
        durations.append(session['duration_minutes'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=durations,
        mode='lines+markers',
        name='Study Duration',
        line=dict(color='#667eea', width=2),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="Study Timeline",
        xaxis_title="Date",
        yaxis_title="Duration (minutes)",
        height=300
    )

    return fig


def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.image("1000062984.png", width=150)
        st.title("🎓 LearnZy")
        st.markdown("---")

        # Navigation
        if st.button("📝 Create New Plan", use_container_width=True):
            st.session_state.view_mode = 'create'
            st.rerun()

        if st.button("📚 My Study Plans", use_container_width=True):
            st.session_state.view_mode = 'view'
            st.rerun()

        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.view_mode = 'dashboard'
            st.rerun()

        st.markdown("---")

        # Quick stats
        plans = load_all_plans()
        st.metric("Total Plans", len(plans))

        if plans:
            total_sessions = sum(len(p['sessions']) for p in plans)
            completed = sum(sum(1 for s in p['sessions'] if s.get('completed', False)) for p in plans)
            st.metric("Total Sessions", total_sessions)
            st.metric("Completed", completed)

        st.markdown("---")
        st.caption("Your Vision Is Our Destiny❤️")


def render_create_plan_page():
    """Render the create study plan page"""
    st.title("🎯 Create Your Study Plan")
    st.markdown("Let's build a personalized study plan that works for you!")

    with st.form("study_plan_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📚 Basic Information")
            subject = st.text_input(
                "Subject/Course",
                placeholder="e.g., Machine Learning, Data Structures",
                help="What do you want to study?"
            )

            topics_input = st.text_area(
                "Topics (one per line)",
                placeholder="Linear Regression\nNeural Networks\nDecision Trees",
                height=150,
                help="List all topics you need to cover"
            )

            goal = st.selectbox(
                "Study Goal",
                options=[g.value for g in StudyGoal],
                format_func=lambda x: x.replace('_', ' ').title(),
                help="What's your main objective?"
            )

            difficulty = st.selectbox(
                "Current Level",
                options=[d.value for d in DifficultyLevel],
                format_func=lambda x: x.title(),
                help="Your current knowledge level"
            )

        with col2:
            st.subheader("⏰ Schedule Settings")
            total_days = st.slider(
                "Study Duration (days)",
                min_value=7,
                max_value=180,
                value=30,
                help="How many days do you have?"
            )

            daily_hours = st.slider(
                "Daily Study Hours",
                min_value=0.5,
                max_value=8.0,
                value=2.0,
                step=0.5,
                help="How many hours per day?"
            )

            exam_date = st.date_input(
                "Exam/Target Date (optional)",
                value=None,
                help="When is your deadline?"
            )

            time_pref = st.selectbox(
                "Preferred Study Time",
                options=[t.value for t in TimePreference],
                format_func=lambda x: x.title(),
                help="When do you study best?"
            )

            learning_style = st.selectbox(
                "Learning Style",
                options=["visual", "auditory", "kinesthetic", "reading"],
                format_func=lambda x: x.title(),
                help="How do you learn best?"
            )

        st.markdown("---")

        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col3, col4 = st.columns(2)

            with col3:
                weak_areas_input = st.text_area(
                    "Weak Areas (optional)",
                    placeholder="Topics you struggle with",
                    help="These will get extra focus"
                )

                breaks_enabled = st.checkbox(
                    "Enable Pomodoro Breaks",
                    value=True,
                    help="25-min work + 5-min break cycles"
                )

            with col4:
                st.info("💡 **Knowledge Levels**: Rate your current knowledge of each topic (0-100)")
                knowledge_input = st.text_area(
                    "Current Knowledge (optional)",
                    placeholder="Linear Regression: 40\nNeural Networks: 0",
                    help="Format: Topic: Score"
                )

        # Submit button
        submitted = st.form_submit_button("🚀 Generate Study Plan", use_container_width=True)

    # MOVED OUTSIDE THE FORM
    if submitted:
        if not subject or not topics_input:
            st.error("⚠️ Please fill in the subject and topics!")
            return

        # Parse topics
        topics = [t.strip() for t in topics_input.split('\n') if t.strip()]

        # Parse weak areas
        weak_areas = []
        if weak_areas_input:
            weak_areas = [w.strip() for w in weak_areas_input.split('\n') if w.strip()]

        # Parse knowledge levels
        current_knowledge = {}
        if knowledge_input:
            for line in knowledge_input.split('\n'):
                if ':' in line:
                    topic, score = line.split(':', 1)
                    try:
                        current_knowledge[topic.strip()] = int(score.strip())
                    except ValueError:
                        pass

        # Create progress bar
        with st.spinner('🔮 Generating your personalized study plan...'):
            try:
                # Generate the plan
                plan = st.session_state.generator.generate_plan(
                    subject=subject,
                    topics=topics,
                    goal=StudyGoal(goal),
                    difficulty=DifficultyLevel(difficulty),
                    total_days=total_days,
                    daily_hours=daily_hours,
                    exam_date=exam_date.isoformat() if exam_date else None,
                    time_preference=TimePreference(time_pref),
                    learning_style=learning_style,
                    current_knowledge=current_knowledge if current_knowledge else None,
                    weak_areas=weak_areas if weak_areas else None,
                    breaks_enabled=breaks_enabled
                )

                # Save the plan
                st.session_state.generator.save_plan(plan)

                # Convert to dict for storage in session state
                plan_dict = st.session_state.generator._plan_to_dict(plan)
                st.session_state.current_plan = plan_dict

                # Success message
                st.balloons()
                st.success("✅ Study plan generated successfully!")

                # Show summary
                st.markdown(f"""
                    <div class="success-box">
                        <h3>🎉 Your Plan is Ready!</h3>
                        <p><strong>Subject:</strong> {subject}</p>
                        <p><strong>Duration:</strong> {total_days} days</p>
                        <p><strong>Total Sessions:</strong> {len(plan_dict['sessions'])}</p>
                        <p><strong>Total Study Hours:</strong> {total_days * daily_hours:.1f} hours</p>
                    </div>
                """, unsafe_allow_html=True)

                # Show first session
                if plan_dict['sessions']:
                    st.markdown("### 📅 Your First Session")
                    first_session = plan_dict['sessions'][0]
                    render_session_card(first_session, plan_dict['plan_id'], show_actions=False, session_index=0, key_prefix="create_")

                # Navigation buttons
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📊 View Full Plan", use_container_width=True, key="view_plan_btn"):
                        st.session_state.view_mode = 'dashboard'
                        st.rerun()
                with col_b:
                    if st.button("📝 Create Another Plan", use_container_width=True, key="create_another_btn"):
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating plan: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


def render_session_card(session, plan_id, show_actions=True, session_index=None, key_prefix=""):
    """Render a session card with unique keys"""
    # Handle both dict and dataclass
    if hasattr(session, '__dict__'):
        session_data = session.__dict__
    else:
        session_data = session

    completed = session_data.get('completed', False)
    border_color = "#4CAF50" if completed else "#667eea"

    st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; 
             box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 10px 0; 
             border-left: 4px solid {border_color};">
            <h4 style="color: #2c3e50; margin: 0; font-weight: 600;">
                <span style="margin-right: 8px;">{"✅" if completed else "📚"}</span>
                <span style="color: #2c3e50;">{session_data['topic']}</span>
            </h4>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"📅 **Date:** {session_data['date']}")
        st.write(f"⏰ **Time:** {session_data['time_slot']}")

    with col2:
        st.write(f"⏱️ **Duration:** {session_data['duration_minutes']} min")
        st.write(f"🎯 **Difficulty:** {session_data['difficulty'].title()}")

    with col3:
        st.write(f"⚡ **Focus:** {session_data['estimated_focus_level']}")
        st.write(f"🛠️ **Techniques:** {len(session_data['study_techniques'])}")

    # Expanders don't need unique keys in most cases
    with st.expander("📖 Session Details", expanded=False):
        st.markdown("**📝 Subtopics:**")
        for subtopic in session_data['subtopics']:
            st.write(f"  • {subtopic}")

        st.markdown("**🎯 Goals:**")
        for goal in session_data['goals']:
            st.write(f"  • {goal}")

        st.markdown("**🛠️ Study Techniques:**")
        for technique in session_data['study_techniques']:
            st.write(f"  • {technique}")

        if session_data['breaks']:
            st.markdown("**☕ Breaks:**")
            for brk in session_data['breaks']:
                st.write(f"  • {brk['type'].title()} break after {brk['after_minutes']} min ({brk['duration_minutes']} min)")

        st.markdown(f"**📚 Resources:** {', '.join(session_data['resources'])}")

        st.info(f"**🔍 Pre-Session:** {session_data['pre_session_prep']}")
        st.success(f"**✨ Post-Session:** {session_data['post_session_review']}")

    # FIXED: Use session_index and key_prefix for truly unique keys
    if show_actions and not completed:
        # Use index if provided, otherwise create a unique hash
        if session_index is not None:
            unique_key = f"{key_prefix}complete_{plan_id}_{session_index}"
        else:
            # Fallback: use date and topic
            unique_key = f"{key_prefix}complete_{plan_id}_{session_data['date']}_{abs(hash(session_data['topic']))}"

        if st.button(f"✅ Mark Complete", key=unique_key):
            st.session_state.generator.update_session_progress(
                plan_id, session_data['date'], True, ""
            )
            st.success("Session marked as complete! 🎉")
            st.rerun()


def render_view_plans_page():
    """Render the view all plans page"""
    st.title("📚 My Study Plans")

    plans = load_all_plans()

    if not plans:
        st.info("📝 You haven't created any study plans yet. Let's create one!")
        if st.button("➕ Create Your First Plan", use_container_width=True):
            st.session_state.view_mode = 'create'
            st.rerun()
        return

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_subject = st.selectbox(
            "Filter by Subject",
            ["All"] + list(set(p['subject'] for p in plans))
        )
    with col2:
        filter_goal = st.selectbox(
            "Filter by Goal",
            ["All"] + list(set(p['goal'] for p in plans))
        )
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest", "Oldest", "Most Progress"]
        )

    # Apply filters
    filtered_plans = plans
    if filter_subject != "All":
        filtered_plans = [p for p in filtered_plans if p['subject'] == filter_subject]
    if filter_goal != "All":
        filtered_plans = [p for p in filtered_plans if p['goal'] == filter_goal]

    # Sort
    if sort_by == "Newest":
        filtered_plans = sorted(filtered_plans, key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Oldest":
        filtered_plans = sorted(filtered_plans, key=lambda x: x['created_at'])
    else:  # Most Progress
        filtered_plans = sorted(
            filtered_plans,
            key=lambda x: sum(1 for s in x['sessions'] if s.get('completed', False)),
            reverse=True
        )

    st.markdown("---")

    # Display plans
    for plan in filtered_plans:
        completed = sum(1 for s in plan['sessions'] if s.get('completed', False))
        total = len(plan['sessions'])
        progress = (completed / total * 100) if total > 0 else 0

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.markdown(f"### 📚 {plan['subject']}")
                st.caption(f"Created: {datetime.fromisoformat(plan['created_at']).strftime('%B %d, %Y')}")

            with col2:
                st.metric("Progress", f"{progress:.0f}%")

            with col3:
                st.metric("Sessions", f"{completed}/{total}")

            with col4:
                if st.button("👁️ View", key=f"view_{plan['plan_id']}"):
                    st.session_state.current_plan = plan
                    st.session_state.view_mode = 'dashboard'
                    st.rerun()

            # Progress bar
            st.progress(progress / 100)

            # Plan details
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.write(f"🎯 **Goal:** {plan['goal'].replace('_', ' ').title()}")
            col_b.write(f"📅 **Duration:** {plan['total_days']} days")
            col_c.write(f"⏰ **Daily Hours:** {plan['daily_hours']}")
            col_d.write(f"📊 **Level:** {plan['difficulty_level'].title()}")

            st.markdown("---")


def render_dashboard_page():
    """Render the main dashboard"""
    plan = st.session_state.current_plan

    if not plan:
        plans = load_all_plans()
        if plans:
            plan = plans[0]  # Load most recent
            st.session_state.current_plan = plan
        else:
            st.info("📝 No study plans found. Create one to get started!")
            if st.button("➕ Create Study Plan", use_container_width=True):
                st.session_state.view_mode = 'create'
                st.rerun()
            return

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"📚 {plan['subject']}")
        st.caption(f"Created {datetime.fromisoformat(plan['created_at']).strftime('%B %d, %Y')}")
    with col2:
        if st.button("⬅️ Back to Plans"):
            st.session_state.view_mode = 'view'
            st.rerun()

    # Metrics
    completed = sum(1 for s in plan['sessions'] if s.get('completed', False))
    total = len(plan['sessions'])
    progress = (completed / total * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Progress", f"{progress:.0f}%", f"{completed}/{total} sessions")
    col2.metric("🎯 Goal", plan['goal'].replace('_', ' ').title())
    col3.metric("⏰ Daily Hours", f"{plan['daily_hours']} hrs")
    col4.metric("📈 Level", plan['difficulty_level'].title())

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Today's Session",
        "📚 All Sessions",
        "📊 Analytics",
        "🎯 Milestones",
        "💡 Recommendations"
    ])

    # Tab 1: Today's Session
    with tab1:
        today_session = None
        today = datetime.now().strftime("%Y-%m-%d")

        for idx, session in enumerate(plan['sessions']):
            if session['date'] == today:
                today_session = session
                st.markdown("### 🌟 Today's Study Session")
                render_session_card(today_session, plan['plan_id'], session_index=idx, key_prefix="tab1_")
                break

        if today_session:
            # Motivational quote
            import random
            quotes = plan['motivational_tips']
            st.info(random.choice(quotes))
        else:
            st.info("🎉 No session scheduled for today! Take a well-deserved break or review previous topics.")

            # Show upcoming session
            upcoming = None
            upcoming_idx = None
            for idx, session in enumerate(plan['sessions']):
                if session['date'] > today and not session.get('completed', False):
                    upcoming = session
                    upcoming_idx = idx
                    break

            if upcoming:
                st.markdown("### 📅 Next Session")
                render_session_card(upcoming, plan['plan_id'], show_actions=False, session_index=upcoming_idx, key_prefix="tab1_upcoming_")

    # Tab 2: All Sessions
    with tab2:
        st.markdown("### 📚 Complete Study Schedule")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Completed", "Pending"],
                key="filter_status_tab2"
            )
        with col2:
            filter_topic = st.selectbox(
                "Filter by Topic",
                ["All"] + list(set(s['topic'] for s in plan['sessions'])),
                key="filter_topic_tab2"
            )

        # Apply filters
        filtered_sessions = []
        for idx, s in enumerate(plan['sessions']):
            # Status filter
            if filter_status == "Completed" and not s.get('completed', False):
                continue
            if filter_status == "Pending" and s.get('completed', False):
                continue

            # Topic filter
            if filter_topic != "All" and s['topic'] != filter_topic:
                continue

            filtered_sessions.append((idx, s))

        st.write(f"Showing {len(filtered_sessions)} sessions")

        # Render filtered sessions with their original indices
        for idx, session in filtered_sessions:
            render_session_card(session, plan['plan_id'], session_index=idx, key_prefix="tab2_")

    # Tab 3: Analytics
    with tab3:
        st.markdown("### 📊 Study Analytics")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_progress_chart(plan), use_container_width=True)
            st.plotly_chart(create_timeline_chart(plan), use_container_width=True)

        with col2:
            st.plotly_chart(create_topic_distribution_chart(plan), use_container_width=True)

            # Study streak
            st.markdown("### 🔥 Study Streak")
            streak = 0
            for session in reversed(plan['sessions']):
                if session.get('completed', False):
                    streak += 1
                else:
                    break
            st.metric("Current Streak", f"{streak} days")

    # Tab 4: Milestones
    with tab4:
        st.markdown("### 🎯 Milestones & Achievements")

        for milestone in plan['milestones']:
            completed = sum(1 for s in plan['sessions'] if s.get('completed', False))
            is_achieved = completed >= milestone['day']

            icon = "🏆" if is_achieved else "🎯"
            st.markdown(f"""
                <div style="background: {'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' if is_achieved else '#f8f9fa'}; 
                     color: {'white' if is_achieved else 'black'}; padding: 15px; 
                     border-radius: 10px; margin: 10px 0;">
                    <h4>{icon} {milestone['name']}</h4>
                    <p>{milestone['description']}</p>
                    <p><em>{milestone['celebration']}</em></p>
                </div>
            """, unsafe_allow_html=True)

        # Weekly reviews
        st.markdown("### 📅 Weekly Review Schedule")
        for review in plan['weekly_reviews']:
            st.write(f"• {review}")

    # Tab 5: Recommendations
    with tab5:
        st.markdown("### 💡 Personalized Recommendations")

        for rec in plan['adaptive_recommendations']:
            st.info(rec)

        st.markdown("### 🌟 Motivational Tips")
        for tip in plan['motivational_tips']:
            st.success(tip)


def main():
    """Main application function"""
    render_sidebar()

    # Route to appropriate page
    if st.session_state.view_mode == 'create':
        render_create_plan_page()
    elif st.session_state.view_mode == 'view':
        render_view_plans_page()
    elif st.session_state.view_mode == 'dashboard':
        render_dashboard_page()


if __name__ == "__main__":

    main()


