"""
Unit tests for Smart Skill Gap Recommender Engine.
"""

import pytest

from app import create_app
from app.services.skill_recommender_service import (
    TIER_PROFILES,
    analyze_skill_gap,
    analyze_student_skill_gap,
    get_target_skills_for_company,
)
from app.services.student_service import get_all_students_simple


def test_tier_profiles_structure():
    """Verify standard hiring tier profiles exist and have proper weighting."""
    assert "Super Dream" in TIER_PROFILES
    assert "Dream" in TIER_PROFILES
    assert "Core Engineering" in TIER_PROFILES
    assert "Mass / IT Services" in TIER_PROFILES

    for tier_key, profile in TIER_PROFILES.items():
        assert "title" in profile
        assert "benchmark_ctc" in profile
        assert len(profile["core_skills"]) >= 4
        total_weight = sum(s.get("weight", 0) for s in profile["core_skills"])
        assert total_weight == 100


def test_analyze_skill_gap_full_match():
    """Verify that a candidate possessing all target competencies scores 100%."""
    target_skills = [s["skill_name"] for s in TIER_PROFILES["Super Dream"]["core_skills"]]
    result = analyze_skill_gap(target_skills, target_type="tier", target_value="Super Dream")

    assert result["match_score"] == 100.0
    assert len(result["missing_skills"]) == 0
    assert len(result["acquired_skills"]) == len(target_skills)
    assert "Drive Ready" in result["readiness"]
    assert len(result["roadmap"]) == 3


def test_analyze_skill_gap_partial_and_empty():
    """Verify weighted score calculation for partial skills inventory."""
    empty_res = analyze_skill_gap([], target_type="tier", target_value="Dream")
    assert empty_res["match_score"] == 0.0
    assert len(empty_res["acquired_skills"]) == 0
    assert len(empty_res["missing_skills"]) > 0

    partial_res = analyze_skill_gap(["SQL", "Python"], target_type="tier", target_value="Dream")
    assert 0.0 < partial_res["match_score"] < 100.0
    assert len(partial_res["acquired_skills"]) == 2
    assert "roadmap" in partial_res


def test_analyze_student_skill_gap_db():
    """Verify student gap analysis using active database records."""
    students = get_all_students_simple()
    if students:
        st_id = students[0]["student_id"]
        res = analyze_student_skill_gap(st_id, target_type="tier", target_value="Dream")
        assert res is not None
        assert "match_score" in res
        assert 0.0 <= res["match_score"] <= 100.0
        assert "student" in res
        assert res["student"]["student_id"] == st_id


def test_recommender_routes(student_client):
    """Verify GET and POST requests to the /skills/recommender UI route (accessible by student)."""
    response = student_client.get("/skills/recommender")
    assert response.status_code == 200
    assert b"Target Recruiter Competency &amp; Skill Gap Recommender" in response.data or b"Skill Gap" in response.data

    post_resp = student_client.post(
        "/skills/recommender", data={"target_type": "tier", "target_value": "Super Dream", "skills": ["Python", "SQL"]}
    )
    assert post_resp.status_code == 200
    assert b"Competency Match Affinity" in post_resp.data


def test_api_recommender(client):
    """Verify JSON API endpoint for interactive reactivity."""
    payload = {"target_type": "tier", "target_value": "Dream", "skills": ["Python", "SQL", "Communication Skills"]}
    response = client.post("/skills/api/recommender", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "analysis" in data
    assert data["analysis"]["match_score"] > 0.0


def test_skills_crud_routes(officer_client):
    """Verify CRUD endpoints for skills management."""
    import time

    skill_title = f"TestSkill_{int(time.time() * 1000) % 100000}"

    # 1. View Skills directory
    list_resp = officer_client.get("/skills/")
    assert list_resp.status_code == 200

    # 2. Add Skill
    add_resp = officer_client.post(
        "/skills/add", data={"skill_name": skill_title, "skill_category": "Cloud & DevOps"}, follow_redirects=True
    )
    assert add_resp.status_code == 200
    assert skill_title.encode() in add_resp.data

    # Fetch created skill_id
    from app.services.skill_service import get_all_skills

    all_s = get_all_skills()
    created_s = next((s for s in all_s if s["skill_name"] == skill_title), None)
    assert created_s is not None
    sid = created_s["skill_id"]

    # 3. Edit Skill
    edit_resp = officer_client.post(
        f"/skills/{sid}/edit",
        data={"skill_name": f"{skill_title}_Updated", "skill_category": "Software Engineering"},
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200
    assert b"updated successfully" in edit_resp.data

    # 4. Delete Skill
    del_resp = officer_client.post(f"/skills/{sid}/delete", follow_redirects=True)
    assert del_resp.status_code == 200
    assert b"deleted" in del_resp.data.lower()
