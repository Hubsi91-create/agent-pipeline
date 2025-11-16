"""
Test Video Database Layer
==========================
Tests for save/load video task operations in database.py

Run this file to verify all database methods work correctly.
"""

import os
import json
from datetime import datetime
from database import DatabaseManager

# Test database path (will be deleted after tests)
TEST_DB_PATH = './test_video_tasks.db'


def cleanup_test_db():
    """Remove test database if it exists"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"[OK] Cleaned up test database: {TEST_DB_PATH}")


def test_save_video_task():
    """Test saving a video task"""
    print("\n=== Test: save_video_task() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Save a video task
    result = db.save_video_task(
        task_id='task_001',
        user_id='user_1',
        project_name='Summer Vibes 2025',
        song_title='Electric Dreams',
        music_file='https://drive.google.com/file/123',
        genre='Electronic',
        bpm=128,
        engine='runway_gen3',
        prompt='Cinematic neon city at night with pulsing lights',
        status='pending',
        youtube_title='Electric Dreams - Official Music Video',
        youtube_description='New electronic track with stunning visuals',
        youtube_tags=json.dumps(['electronic', 'music video', 'edm']),
        duration=180
    )

    assert result == 1, "Should insert 1 row"
    print("[OK] Video task saved successfully")


def test_get_video_task():
    """Test retrieving a single video task"""
    print("\n=== Test: get_video_task() ===")

    db = DatabaseManager(TEST_DB_PATH)

    task = db.get_video_task('task_001')

    assert task is not None, "Task should exist"
    assert task['id'] == 'task_001', "Task ID should match"
    assert task['song_title'] == 'Electric Dreams', "Song title should match"
    assert task['bpm'] == 128, "BPM should match"
    assert isinstance(task['youtube_tags'], list), "YouTube tags should be parsed as list"

    print(f"[OK] Video task retrieved: {task['song_title']}")
    print(f"  - Status: {task['status']}")
    print(f"  - Genre: {task['genre']}")
    print(f"  - BPM: {task['bpm']}")
    print(f"  - Tags: {task['youtube_tags']}")


def test_get_video_tasks():
    """Test listing video tasks"""
    print("\n=== Test: get_video_tasks() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Add more tasks
    db.save_video_task(
        task_id='task_002',
        user_id='user_1',
        project_name='Rock Anthem',
        song_title='Thunder Road',
        music_file='https://drive.google.com/file/456',
        genre='Rock',
        bpm=140,
        engine='runway_standard',
        prompt='Desert highway with storm clouds',
        status='processing'
    )

    db.save_video_task(
        task_id='task_003',
        user_id='user_2',
        project_name='Jazz Night',
        song_title='Moonlight Serenade',
        music_file='https://drive.google.com/file/789',
        genre='Jazz',
        bpm=90,
        engine='runway_gen3',
        prompt='Smoky jazz club with dim lighting',
        status='completed'
    )

    # Get all tasks
    all_tasks = db.get_video_tasks()
    assert len(all_tasks) == 3, "Should have 3 tasks"
    print(f"[OK] Retrieved all tasks: {len(all_tasks)}")

    # Get tasks by user
    user1_tasks = db.get_video_tasks(user_id='user_1')
    assert len(user1_tasks) == 2, "User 1 should have 2 tasks"
    print(f"[OK] Retrieved user_1 tasks: {len(user1_tasks)}")

    # Get tasks by status
    pending_tasks = db.get_video_tasks(status='pending')
    assert len(pending_tasks) == 1, "Should have 1 pending task"
    print(f"[OK] Retrieved pending tasks: {len(pending_tasks)}")

    # Get tasks with limit
    limited_tasks = db.get_video_tasks(limit=2)
    assert len(limited_tasks) == 2, "Should return 2 tasks"
    print(f"[OK] Retrieved with limit: {len(limited_tasks)}")


def test_update_video_task_status():
    """Test updating video task status"""
    print("\n=== Test: update_video_task_status() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Update status
    result = db.update_video_task_status(
        task_id='task_001',
        status='completed',
        video_url='https://storage.runway.com/video_001.mp4',
        completed_at=datetime.now().isoformat()
    )

    assert result == 1, "Should update 1 row"

    # Verify update
    task = db.get_video_task('task_001')
    assert task['status'] == 'completed', "Status should be updated"
    assert task['video_url'] == 'https://storage.runway.com/video_001.mp4', "Video URL should be set"

    print(f"[OK] Video task status updated to: {task['status']}")
    print(f"  - Video URL: {task['video_url']}")


def test_update_video_task():
    """Test updating video task with arbitrary fields"""
    print("\n=== Test: update_video_task() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Update multiple fields
    result = db.update_video_task(
        task_id='task_001',
        cost=12.50,
        credits_used=250,
        youtube_description='Updated description with more details'
    )

    assert result == 1, "Should update 1 row"

    # Verify update
    task = db.get_video_task('task_001')
    assert task['cost'] == 12.50, "Cost should be updated"
    assert task['credits_used'] == 250, "Credits should be updated"

    print(f"[OK] Video task updated successfully")
    print(f"  - Cost: ${task['cost']}")
    print(f"  - Credits used: {task['credits_used']}")


def test_save_thumbnail():
    """Test saving thumbnails"""
    print("\n=== Test: save_thumbnail() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Save thumbnails
    thumbnails = [
        {
            'id': 'thumb_001',
            'variant': 'bold_text',
            'url': 'https://storage.recraft.com/thumb_001.jpg',
            'prediction': 0.85
        },
        {
            'id': 'thumb_002',
            'variant': 'emotional_face',
            'url': 'https://storage.recraft.com/thumb_002.jpg',
            'prediction': 0.92
        },
        {
            'id': 'thumb_003',
            'variant': 'action_shot',
            'url': 'https://storage.recraft.com/thumb_003.jpg',
            'prediction': 0.78
        }
    ]

    for thumb in thumbnails:
        result = db.save_thumbnail(
            thumbnail_id=thumb['id'],
            video_id='task_001',
            variant=thumb['variant'],
            image_url=thumb['url'],
            click_prediction=thumb['prediction']
        )
        assert result == 1, f"Should insert thumbnail {thumb['id']}"

    print(f"[OK] Saved {len(thumbnails)} thumbnails")


def test_get_thumbnails():
    """Test retrieving thumbnails"""
    print("\n=== Test: get_thumbnails() ===")

    db = DatabaseManager(TEST_DB_PATH)

    thumbnails = db.get_thumbnails('task_001')

    assert len(thumbnails) == 3, "Should have 3 thumbnails"

    # Check ordering (highest prediction first)
    assert thumbnails[0]['click_prediction'] == 0.92, "Should be ordered by prediction"

    print(f"[OK] Retrieved {len(thumbnails)} thumbnails")
    for thumb in thumbnails:
        print(f"  - {thumb['variant']}: {thumb['click_prediction']:.0%} CTR prediction")


def test_update_thumbnail_selection():
    """Test updating thumbnail selection"""
    print("\n=== Test: update_thumbnail_selection() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Select a thumbnail
    result = db.update_thumbnail_selection('task_001', 'thumb_002')

    assert result > 0, "Should update at least 1 row"

    # Verify selection
    selected = db.get_selected_thumbnail('task_001')
    assert selected is not None, "Should have a selected thumbnail"
    assert selected['id'] == 'thumb_002', "Selected thumbnail should match"
    assert selected['is_selected'] == 1, "Should be marked as selected"

    print(f"[OK] Thumbnail selection updated")
    print(f"  - Selected: {selected['variant']}")
    print(f"  - Prediction: {selected['click_prediction']:.0%}")


def test_get_storyboard_stats():
    """Test getting storyboard statistics"""
    print("\n=== Test: get_storyboard_stats() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Get overall stats
    stats = db.get_storyboard_stats()

    assert stats['total_tasks'] == 3, "Should have 3 total tasks"
    assert stats['total_thumbnails'] == 3, "Should have 3 thumbnails"
    assert stats['total_cost'] > 0, "Should have cost data"

    print(f"[OK] Overall Statistics:")
    print(f"  - Total tasks: {stats['total_tasks']}")
    print(f"  - Total thumbnails: {stats['total_thumbnails']}")
    print(f"  - Total cost: ${stats['total_cost']:.2f}")
    print(f"  - Total credits: {stats['total_credits_used']}")
    print(f"  - By status: {stats['by_status']}")

    # Get user-specific stats
    user_stats = db.get_storyboard_stats(user_id='user_1')
    assert user_stats['total_tasks'] == 2, "User 1 should have 2 tasks"

    print(f"\n[OK] User 1 Statistics:")
    print(f"  - Total tasks: {user_stats['total_tasks']}")
    print(f"  - By status: {user_stats['by_status']}")


def test_delete_video_task():
    """Test deleting video tasks"""
    print("\n=== Test: delete_video_task() ===")

    db = DatabaseManager(TEST_DB_PATH)

    # Delete a task
    result = db.delete_video_task('task_002')

    assert result == 1, "Should delete 1 row"

    # Verify deletion
    task = db.get_video_task('task_002')
    assert task is None, "Task should be deleted"

    # Check remaining tasks
    remaining_tasks = db.get_video_tasks()
    assert len(remaining_tasks) == 2, "Should have 2 remaining tasks"

    print(f"[OK] Video task deleted successfully")
    print(f"  - Remaining tasks: {len(remaining_tasks)}")


def run_all_tests():
    """Run all database tests"""
    print("\n" + "="*60)
    print("VIDEO DATABASE LAYER TESTS")
    print("="*60)

    # Clean up before tests
    cleanup_test_db()

    try:
        # Run tests in order
        test_save_video_task()
        test_get_video_task()
        test_get_video_tasks()
        test_update_video_task_status()
        test_update_video_task()
        test_save_thumbnail()
        test_get_thumbnails()
        test_update_thumbnail_selection()
        test_get_storyboard_stats()
        test_delete_video_task()

        print("\n" + "="*60)
        print("[OK] ALL TESTS PASSED!")
        print("="*60)

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        raise

    except Exception as e:
        print(f"\n[FAIL] ERROR: {str(e)}")
        raise

    finally:
        # Clean up after tests
        print("\n")
        cleanup_test_db()


if __name__ == '__main__':
    run_all_tests()
