"""
Advanced Study Plan Generator
Generates personalized, adaptive study plans with intelligent scheduling
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import math


class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class StudyGoal(Enum):
    EXAM_PREP = "exam_prep"
    SKILL_BUILDING = "skill_building"
    QUICK_REVIEW = "quick_review"
    DEEP_MASTERY = "deep_mastery"


class TimePreference(Enum):
    MORNING = "morning"  # 6-12
    AFTERNOON = "afternoon"  # 12-18
    EVENING = "evening"  # 18-22
    NIGHT = "night"  # 22-6
    FLEXIBLE = "flexible"


@dataclass
class StudySession:
    """Represents a single study session"""
    date: str
    time_slot: str
    duration_minutes: int
    topic: str
    subtopics: List[str]
    difficulty: str
    study_techniques: List[str]
    breaks: List[Dict[str, int]]
    resources: List[str]
    goals: List[str]
    pre_session_prep: str
    post_session_review: str
    estimated_focus_level: str
    completed: bool = False
    notes: str = ""
    completed_at: Optional[str] = None


@dataclass
class StudyPlan:
    """Complete study plan with all sessions and metadata"""
    plan_id: str
    created_at: str
    subject: str
    goal: str
    exam_date: Optional[str]
    total_days: int
    daily_hours: float
    difficulty_level: str
    sessions: List[StudySession]
    milestones: List[Dict]
    weekly_reviews: List[str]
    adaptive_recommendations: List[str]
    motivational_tips: List[str]


class StudyPlanGenerator:
    """
    Advanced Study Plan Generator with:
    - Spaced repetition algorithm
    - Cognitive load balancing
    - Pomodoro technique integration
    - Adaptive difficulty progression
    - Personalized scheduling
    """

    def __init__(self):
        self.study_techniques = {
            "beginner": ["Active Reading", "Note Taking", "Flashcards", "Summary Writing"],
            "intermediate": ["Feynman Technique", "Mind Mapping", "Practice Problems", "Peer Discussion"],
            "advanced": ["Deep Work Sessions", "Research Papers", "Project-Based Learning", "Teaching Others"],
            "expert": ["Original Research", "Advanced Problem Solving", "Critical Analysis", "Innovation Projects"]
        }

        self.focus_patterns = {
            "morning": {"high": (6, 10), "medium": (10, 12)},
            "afternoon": {"medium": (12, 15), "high": (15, 18)},
            "evening": {"high": (18, 20), "low": (20, 22)},
            "night": {"low": (22, 24), "very_low": (0, 6)}
        }

    def _plan_to_dict(self, plan: StudyPlan) -> Dict:
        """Convert StudyPlan object to dictionary format"""
        return asdict(plan)

    def _plan_sessions_to_list(self, plan: StudyPlan) -> List[Dict]:
        """Convert plan sessions to a simplified list format"""
        output = []
        for session in plan.sessions:
            output.append({
                "date": session.date,
                "topic": session.topic,
                "duration_hours": round(session.duration_minutes / 60, 2),
                "time_slot": session.time_slot,
                "difficulty": session.difficulty,
                "focus_level": session.estimated_focus_level
            })
        return output

    def generate_plan(
        self,
        subject: str,
        topics: List[str],
        goal: StudyGoal,
        difficulty: DifficultyLevel,
        total_days: int,
        daily_hours: float,
        exam_date: Optional[str] = None,
        time_preference: TimePreference = TimePreference.FLEXIBLE,
        learning_style: str = "visual",
        current_knowledge: Dict[str, int] = None,
        weak_areas: List[str] = None,
        breaks_enabled: bool = True
    ) -> StudyPlan:
        """
        Generate a comprehensive, personalized study plan

        Args:
            subject: Main subject to study
            topics: List of topics to cover
            goal: Study goal type
            difficulty: Current difficulty level
            total_days: Number of days for the plan
            daily_hours: Hours available per day
            exam_date: Optional exam date for deadline-based planning
            time_preference: Preferred time of day for studying
            learning_style: visual/auditory/kinesthetic/reading
            current_knowledge: Dict of topic -> knowledge_level (0-100)
            weak_areas: Topics that need more focus
            breaks_enabled: Whether to include Pomodoro breaks
        """
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize knowledge tracking
        if current_knowledge is None:
            current_knowledge = {topic: 0 for topic in topics}

        if weak_areas is None:
            weak_areas = []

        # Calculate topic allocation with intelligent weighting
        topic_allocation = self._calculate_topic_allocation(
            topics, total_days, daily_hours, current_knowledge, weak_areas
        )

        # Generate sessions with spaced repetition
        sessions = self._generate_sessions(
            topics, topic_allocation, total_days, daily_hours,
            difficulty, time_preference, learning_style,
            breaks_enabled, goal
        )

        # Create milestones
        milestones = self._create_milestones(topics, total_days, goal)

        # Generate weekly review dates
        weekly_reviews = self._generate_weekly_reviews(total_days)

        # Adaptive recommendations
        recommendations = self._generate_recommendations(
            difficulty, goal, daily_hours, learning_style
        )

        # Motivational tips
        motivational_tips = self._generate_motivational_tips(total_days, goal)

        return StudyPlan(
            plan_id=plan_id,
            created_at=datetime.now().isoformat(),
            subject=subject,
            goal=goal.value,
            exam_date=exam_date,
            total_days=total_days,
            daily_hours=daily_hours,
            difficulty_level=difficulty.value,
            sessions=sessions,
            milestones=milestones,
            weekly_reviews=weekly_reviews,
            adaptive_recommendations=recommendations,
            motivational_tips=motivational_tips
        )

    def _calculate_topic_allocation(
        self,
        topics: List[str],
        total_days: int,
        daily_hours: float,
        current_knowledge: Dict[str, int],
        weak_areas: List[str]
    ) -> Dict[str, float]:
        """
        Intelligently allocate time to topics based on:
        - Current knowledge level (less time for known topics)
        - Weak areas (more time for difficult topics)
        - Spaced repetition (review schedule)
        """
        total_hours = total_days * daily_hours
        allocation = {}

        # Calculate weights for each topic
        weights = {}
        for topic in topics:
            knowledge = current_knowledge.get(topic, 0)

            # Base weight (inverse of knowledge)
            base_weight = 100 - knowledge

            # Boost for weak areas
            weak_boost = 1.5 if topic in weak_areas else 1.0

            # Spaced repetition boost (more review for partially learned topics)
            spaced_boost = 1.0
            if 30 <= knowledge <= 70:
                spaced_boost = 1.3  # These need most repetition

            weights[topic] = base_weight * weak_boost * spaced_boost

        # Normalize weights to hours
        total_weight = sum(weights.values())
        for topic, weight in weights.items():
            allocation[topic] = (weight / total_weight) * total_hours

        return allocation

    def _generate_sessions(
        self,
        topics: List[str],
        topic_allocation: Dict[str, float],
        total_days: int,
        daily_hours: float,
        difficulty: DifficultyLevel,
        time_preference: TimePreference,
        learning_style: str,
        breaks_enabled: bool,
        goal: StudyGoal
    ) -> List[StudySession]:
        """Generate daily study sessions with intelligent scheduling"""
        sessions = []
        start_date = datetime.now()

        # Track topic coverage for spaced repetition
        topic_last_studied = {topic: -999 for topic in topics}
        topic_study_count = {topic: 0 for topic in topics}

        for day in range(total_days):
            current_date = start_date + timedelta(days=day)
            day_number = day + 1

            # Determine which topic to study (spaced repetition logic)
            topic = self._select_topic_for_day(
                topics, topic_allocation, day_number,
                topic_last_studied, topic_study_count
            )

            # Get time slot based on preference and focus patterns
            time_slot = self._get_optimal_time_slot(
                time_preference, day_number, daily_hours
            )

            # Calculate session duration with breaks
            duration = int(daily_hours * 60)
            breaks = self._calculate_breaks(duration) if breaks_enabled else []

            # Determine difficulty progression (start easier, build up)
            session_difficulty = self._get_session_difficulty(
                difficulty, day_number, total_days
            )

            # Select study techniques
            techniques = self._select_study_techniques(
                session_difficulty, learning_style, day_number
            )

            # Generate subtopics and goals
            subtopics = self._generate_subtopics(topic, day_number, goal)
            goals = self._generate_session_goals(topic, subtopics, goal)

            # Get resources based on learning style
            resources = self._get_learning_resources(topic, learning_style)

            # Determine focus level based on time and day
            focus_level = self._estimate_focus_level(time_slot, day_number)

            # Pre and post session activities
            pre_prep = self._get_pre_session_prep(day_number, topic)
            post_review = self._get_post_session_review(day_number, topic)

            session = StudySession(
                date=current_date.strftime("%Y-%m-%d"),
                time_slot=time_slot,
                duration_minutes=duration,
                topic=topic,
                subtopics=subtopics,
                difficulty=session_difficulty,
                study_techniques=techniques,
                breaks=breaks,
                resources=resources,
                goals=goals,
                pre_session_prep=pre_prep,
                post_session_review=post_review,
                estimated_focus_level=focus_level
            )

            sessions.append(session)

            # Update tracking
            topic_last_studied[topic] = day_number
            topic_study_count[topic] += 1

        return sessions

    def _select_topic_for_day(
        self,
        topics: List[str],
        allocation: Dict[str, float],
        day: int,
        last_studied: Dict[str, int],
        study_count: Dict[str, int]
    ) -> str:
        """Select topic using spaced repetition algorithm"""
        scores = {}

        for topic in topics:
            # Days since last study (higher is better for repetition)
            days_since = day - last_studied[topic]

            # Remaining allocation (prioritize under-studied topics)
            remaining = allocation[topic] - (study_count[topic] * 1.5)

            # Spaced repetition score (exponential curve)
            if study_count[topic] == 0:
                spaced_score = 1000  # Always prioritize unstudied topics
            else:
                # Optimal review intervals: 1, 3, 7, 14 days
                optimal_intervals = [1, 3, 7, 14, 30]
                spaced_score = min([abs(days_since - interval) for interval in optimal_intervals])
                spaced_score = 100 - spaced_score  # Invert (closer to optimal = higher score)

            # Combined score
            scores[topic] = (remaining * 0.4) + (spaced_score * 0.4) + (days_since * 0.2)

        return max(scores, key=scores.get)

    def _get_optimal_time_slot(
        self,
        preference: TimePreference,
        day: int,
        hours: float
    ) -> str:
        """Get optimal time slot based on preference and circadian rhythm"""
        if preference == TimePreference.MORNING:
            return f"06:00 - {6 + int(hours):02d}:00"
        elif preference == TimePreference.AFTERNOON:
            return f"14:00 - {14 + int(hours):02d}:00"
        elif preference == TimePreference.EVENING:
            return f"18:00 - {18 + int(hours):02d}:00"
        elif preference == TimePreference.NIGHT:
            return f"21:00 - {21 + int(hours):02d}:00"
        else:  # FLEXIBLE
            # Alternate between optimal times
            slots = ["07:00", "14:00", "18:00"]
            start = slots[day % len(slots)]
            end_hour = int(start.split(":")[0]) + int(hours)
            return f"{start} - {end_hour:02d}:00"

    def _calculate_breaks(self, duration_minutes: int) -> List[Dict[str, int]]:
        """Calculate Pomodoro breaks (25 min work + 5 min break)"""
        breaks = []
        pomodoro_cycle = 25  # minutes of work
        short_break = 5
        long_break = 15
        completed_pomodoros = 0
        elapsed = 0

        while elapsed < duration_minutes:
            work_time = min(pomodoro_cycle, duration_minutes - elapsed)
            elapsed += work_time
            completed_pomodoros += 1

            if elapsed < duration_minutes:
                # Long break after 4 pomodoros
                break_time = long_break if completed_pomodoros % 4 == 0 else short_break
                breaks.append({
                    "after_minutes": elapsed,
                    "duration_minutes": break_time,
                    "type": "long" if break_time == long_break else "short"
                })
                elapsed += break_time

        return breaks

    def _get_session_difficulty(
        self,
        base_difficulty: DifficultyLevel,
        day: int,
        total_days: int
    ) -> str:
        """Progressive difficulty increase throughout the plan"""
        progress_ratio = day / total_days
        difficulties = ["beginner", "intermediate", "advanced", "expert"]
        base_idx = difficulties.index(base_difficulty.value)

        # Gradually increase difficulty
        if progress_ratio < 0.3:
            return difficulties[max(0, base_idx - 1)]
        elif progress_ratio < 0.6:
            return difficulties[base_idx]
        elif progress_ratio < 0.85:
            return difficulties[min(len(difficulties) - 1, base_idx + 1)]
        else:
            return difficulties[min(len(difficulties) - 1, base_idx + 1)]

    def _select_study_techniques(
        self,
        difficulty: str,
        learning_style: str,
        day: int
    ) -> List[str]:
        """Select appropriate study techniques"""
        base_techniques = self.study_techniques.get(difficulty, self.study_techniques["intermediate"])

        # Add learning-style specific techniques
        style_techniques = {
            "visual": ["Diagrams", "Color Coding", "Video Tutorials"],
            "auditory": ["Podcasts", "Discussions", "Read Aloud"],
            "kinesthetic": ["Hands-on Practice", "Real Projects", "Lab Work"],
            "reading": ["Textbooks", "Articles", "Documentation"]
        }

        selected = base_techniques[:2]
        selected.extend(style_techniques.get(learning_style, [])[:1])

        return selected

    def _generate_subtopics(self, topic: str, day: int, goal: StudyGoal) -> List[str]:
        """Generate relevant subtopics for the session"""
        # This would typically use AI or a knowledge graph
        # For now, generate structured subtopics
        if goal == StudyGoal.EXAM_PREP:
            return [
                f"{topic} - Core Concepts",
                f"{topic} - Practice Problems",
                f"{topic} - Common Mistakes"
            ]
        elif goal == StudyGoal.DEEP_MASTERY:
            return [
                f"{topic} - Theoretical Foundation",
                f"{topic} - Advanced Applications",
                f"{topic} - Research & Innovation"
            ]
        elif goal == StudyGoal.QUICK_REVIEW:
            return [
                f"{topic} - Key Points Review",
                f"{topic} - Quick Quiz"
            ]
        else:
            return [
                f"{topic} - Introduction",
                f"{topic} - Practice",
                f"{topic} - Application"
            ]

    def _generate_session_goals(
        self,
        topic: str,
        subtopics: List[str],
        goal: StudyGoal
    ) -> List[str]:
        """Generate specific, measurable goals for the session"""
        goals = [
            f"Understand core concepts of {topic}",
            f"Complete exercises on {subtopics[0]}",
            f"Achieve 80%+ on practice quiz"
        ]
        return goals

    def _get_learning_resources(self, topic: str, learning_style: str) -> List[str]:
        """Suggest appropriate learning resources"""
        resources = {
            "visual": [
                "YouTube tutorials",
                "Infographics",
                "Interactive simulations"
            ],
            "auditory": [
                "Podcasts",
                "Audio lectures",
                "Study group discussions"
            ],
            "kinesthetic": [
                "Hands-on projects",
                "Lab exercises",
                "Real-world applications"
            ],
            "reading": [
                "Textbook chapters",
                "Research papers",
                "Online documentation"
            ]
        }
        return resources.get(learning_style, resources["visual"])

    def _estimate_focus_level(self, time_slot: str, day: int) -> str:
        """Estimate focus level based on time and fatigue"""
        hour = int(time_slot.split(":")[0])

        # Circadian rhythm peaks
        if 9 <= hour <= 11 or 15 <= hour <= 17:
            focus = "High"
        elif 6 <= hour <= 9 or 11 <= hour <= 15 or 17 <= hour <= 20:
            focus = "Medium"
        else:
            focus = "Low"

        # Adjust for study fatigue (later days = slightly lower focus)
        if day > 20 and focus == "High":
            focus = "Medium-High"

        return focus

    def _get_pre_session_prep(self, day: int, topic: str) -> str:
        """Pre-session preparation suggestions"""
        preps = [
            f"Review notes from previous {topic} session",
            "Set up study environment (minimize distractions)",
            "Gather all materials and resources",
            "Do a 5-minute breathing exercise to focus",
            "Set specific goals for this session"
        ]
        return preps[day % len(preps)]

    def _get_post_session_review(self, day: int, topic: str) -> str:
        """Post-session review suggestions"""
        reviews = [
            "Summarize key learnings in your own words",
            "Create flashcards for important concepts",
            "Teach the concept to someone else (Feynman Technique)",
            "Identify 3 things you learned and 1 question you still have",
            "Update your study notes with new insights"
        ]
        return reviews[day % len(reviews)]

    def _create_milestones(
        self,
        topics: List[str],
        total_days: int,
        goal: StudyGoal
    ) -> List[Dict]:
        """Create achievement milestones throughout the plan"""
        milestones = []

        # Calculate milestone days
        milestone_days = [
            int(total_days * 0.25),
            int(total_days * 0.5),
            int(total_days * 0.75),
            total_days
        ]

        milestone_names = [
            "Foundation Complete",
            "Halfway Champion",
            "Advanced Mastery",
            "Goal Achieved"
        ]

        for i, day in enumerate(milestone_days):
            milestones.append({
                "day": day,
                "name": milestone_names[i],
                "description": f"Complete {int((i + 1) * 25)}% of study plan",
                "celebration": "Take a day to review and celebrate your progress!"
            })

        return milestones

    def _generate_weekly_reviews(self, total_days: int) -> List[str]:
        """Generate weekly review dates"""
        reviews = []
        week = 7
        while week <= total_days:
            date = (datetime.now() + timedelta(days=week)).strftime("%Y-%m-%d")
            reviews.append(f"Week {week // 7} Review - {date}")
            week += 7
        return reviews

    def _generate_recommendations(
        self,
        difficulty: DifficultyLevel,
        goal: StudyGoal,
        daily_hours: float,
        learning_style: str
    ) -> List[str]:
        """Generate personalized adaptive recommendations"""
        recommendations = []

        if daily_hours < 2:
            recommendations.append("💡 Consider increasing study time to 2-3 hours for better retention")

        if difficulty == DifficultyLevel.BEGINNER:
            recommendations.append("🎯 Start with foundational concepts before moving to complex topics")

        if goal == StudyGoal.EXAM_PREP:
            recommendations.append("📝 Focus on practice tests in the last 20% of your study plan")

        recommendations.append(f"🎨 Your {learning_style} learning style works best with interactive resources")
        recommendations.append("🔄 Use spaced repetition: review topics after 1, 3, 7, and 14 days")
        recommendations.append("🧠 Take breaks every 25-30 minutes to maintain peak focus")

        return recommendations

    def _generate_motivational_tips(self, total_days: int, goal: StudyGoal) -> List[str]:
        """Generate motivational tips throughout the journey"""
        tips = [
            "🌟 Every expert was once a beginner. Keep going!",
            "💪 Consistency beats intensity. Show up every day.",
            "🎯 Focus on progress, not perfection.",
            "🚀 Your future self will thank you for starting today.",
            "🔥 Difficult roads often lead to beautiful destinations.",
            "📚 Learning is a journey, not a destination.",
            "⭐ Small daily improvements lead to stunning results.",
            "🎓 You're investing in the best asset - yourself!"
        ]
        return tips

    def save_plan(self, plan: StudyPlan, filepath: str = "state.json"):
        """Save study plan to JSON file"""
        try:
            # Load existing data
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"study_plans": []}

            # Convert plan to dict
            plan_dict = asdict(plan)

            # Add or update plan
            existing_idx = None
            for i, p in enumerate(data.get("study_plans", [])):
                if p["plan_id"] == plan.plan_id:
                    existing_idx = i
                    break

            if existing_idx is not None:
                data["study_plans"][existing_idx] = plan_dict
            else:
                if "study_plans" not in data:
                    data["study_plans"] = []
                data["study_plans"].append(plan_dict)

            # Save
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving plan: {e}")
            return False

    def load_plan(self, plan_id: str, filepath: str = "state.json") -> Optional[StudyPlan]:
        """Load a study plan from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            for plan_dict in data.get("study_plans", []):
                if plan_dict["plan_id"] == plan_id:
                    # Reconstruct StudySession objects
                    sessions = [StudySession(**s) for s in plan_dict["sessions"]]
                    plan_dict["sessions"] = sessions
                    return StudyPlan(**plan_dict)

            return None
        except Exception as e:
            print(f"Error loading plan: {e}")
            return None

    def get_todays_session(self, plan: StudyPlan) -> Optional[StudySession]:
        """Get today's study session from the plan"""
        today = datetime.now().strftime("%Y-%m-%d")
        for session in plan.sessions:
            if session.date == today:
                return session
        return None

    def update_session_progress(
        self,
        plan_id: str,
        session_date: str,
        completed: bool,
        notes: str = "",
        filepath: str = "state.json"
    ) -> bool:
        """Update progress for a specific session"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            for plan in data.get("study_plans", []):
                if plan["plan_id"] == plan_id:
                    for session in plan["sessions"]:
                        if session["date"] == session_date:
                            session["completed"] = completed
                            session["notes"] = notes
                            session["completed_at"] = datetime.now().isoformat()
                            break
                    break

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error updating session: {e}")
            return False


# Example usage
if __name__ == "__main__":
    generator = StudyPlanGenerator()

    # Create a comprehensive study plan
    plan = generator.generate_plan(
        subject="Machine Learning",
        topics=[
            "Linear Regression",
            "Logistic Regression",
            "Neural Networks",
            "Decision Trees",
            "Deep Learning"
        ],
        goal=StudyGoal.EXAM_PREP,
        difficulty=DifficultyLevel.INTERMEDIATE,
        total_days=30,
        daily_hours=2.5,
        exam_date="2025-01-20",
        time_preference=TimePreference.EVENING,
        learning_style="visual",
        current_knowledge={
            "Linear Regression": 40,
            "Logistic Regression": 20,
            "Neural Networks": 0,
            "Decision Trees": 30,
            "Deep Learning": 0
        },
        weak_areas=["Neural Networks", "Deep Learning"],
        breaks_enabled=True
    )

    # Save the plan
    generator.save_plan(plan)

    # Print today's session
    today_session = generator.get_todays_session(plan)
    if today_session:
        print(f"\n🎯 Today's Study Session ({today_session.date})")
        print(f"⏰ Time: {today_session.time_slot}")
        print(f"📚 Topic: {today_session.topic}")
        print(f"🎓 Difficulty: {today_session.difficulty}")
        print(f"⚡ Focus Level: {today_session.estimated_focus_level}")
        print(f"\n📝 Goals:")
        for goal in today_session.goals:
            print(f"   • {goal}")

    print(f"\n✅ Study plan generated successfully!")
    print(f"📊 Total sessions: {len(plan.sessions)}")
    print(f"🎯 Milestones: {len(plan.milestones)}")
    print(f"💡 Recommendations: {len(plan.adaptive_recommendations)}")