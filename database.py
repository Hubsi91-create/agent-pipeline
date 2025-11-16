"""
Database Module - SQLite Helpers for Dashboard

Handles all database operations for the Music Agents Production Dashboard.
Stores metrics, events, training sessions, and system health data.

Tables:
- metrics: Agent quality scores, speed, errors over time
- events: Training events, errors, alerts
- training_sessions: Historical training runs
- system_health: CPU, memory, disk usage over time

Author: Music Video Production System
Version: 1.0.0
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite Database Manager for Dashboard.

    Provides thread-safe database operations with automatic
    initialization, error handling, and connection pooling.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize Database Manager.

        Args:
            db_path: Path to SQLite database file (defaults to DATABASE_PATH env var or './dashboard.db')
        """
        # Get database path from environment or use default
        if db_path is None:
            import os
            db_path = os.getenv('DATABASE_PATH', './dashboard.db')

        self.db_path = db_path
        self.logger = logging.getLogger("DatabaseManager")

        # Initialize database (creates all tables)
        self.init_db()

        self.logger.info(f"Database initialized at {db_path}")

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Ensures connections are properly closed even if errors occur.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()

    def init_db(self):
        """
        Initialize database tables.

        Creates all required tables if they don't exist:
        - metrics
        - events
        - training_sessions
        - system_health
        - api_keys (for encrypted API key storage)
        - storyboard_videos
        - storyboard_thumbnails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Table: metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent_id TEXT,
                    metric_type TEXT,
                    value REAL,
                    notes TEXT
                )
            """)

            # Table: events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    agent_id TEXT,
                    message TEXT,
                    severity TEXT,
                    metadata TEXT
                )
            """)

            # Table: training_sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME,
                    end_time DATETIME,
                    duration_seconds REAL,
                    agents_trained INTEGER,
                    overall_improvement REAL,
                    status TEXT,
                    phase_times TEXT,
                    metadata TEXT
                )
            """)

            # Table: system_health
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    uptime_seconds INTEGER,
                    active_connections INTEGER
                )
            """)

            # Table: api_keys (encrypted storage for API keys)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    service TEXT NOT NULL,
                    encrypted_key TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, service)
                )
            """)

            # Table: storyboard_videos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storyboard_videos (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    project_name TEXT,
                    song_title TEXT,
                    music_file TEXT,
                    genre TEXT,
                    bpm INTEGER,
                    engine TEXT,
                    prompt TEXT,
                    video_url TEXT,
                    status TEXT,
                    youtube_title TEXT,
                    youtube_description TEXT,
                    youtube_tags TEXT,
                    cost REAL,
                    credits_used INTEGER,
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)

            # Table: storyboard_thumbnails
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storyboard_thumbnails (
                    id TEXT PRIMARY KEY,
                    video_id TEXT,
                    variant TEXT,
                    image_url TEXT,
                    click_prediction REAL,
                    is_selected BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES storyboard_videos(id)
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_agent
                ON metrics(agent_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp
                ON events(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type
                ON events(event_type)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_keys_user
                ON api_keys(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_storyboard_videos_user
                ON storyboard_videos(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_storyboard_videos_status
                ON storyboard_videos(status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_storyboard_thumbnails_video
                ON storyboard_thumbnails(video_id)
            """)

            # ============================================================
            # SCREENPLAY STORYBOARD TABLES
            # ============================================================

            # Table: screenplays (uploaded screenplay files)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenplays (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT,
                    file_type TEXT,
                    scene_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'parsed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)

            # Table: screenplay_scenes (individual scenes from screenplay)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenplay_scenes (
                    id TEXT PRIMARY KEY,
                    screenplay_id TEXT NOT NULL,
                    scene_number INTEGER NOT NULL,
                    heading TEXT,
                    description TEXT,
                    prompt TEXT,
                    generated_image_id TEXT,
                    settings TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (screenplay_id) REFERENCES screenplays(id) ON DELETE CASCADE
                )
            """)

            # Table: visual_references (uploaded reference images)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visual_references (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    screenplay_id TEXT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    file_path TEXT,
                    base64_data TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (screenplay_id) REFERENCES screenplays(id) ON DELETE SET NULL
                )
            """)

            # Table: generated_images (AI-generated scene images)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_images (
                    id TEXT PRIMARY KEY,
                    scene_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    image_url TEXT,
                    base64_data TEXT,
                    format TEXT,
                    quality TEXT,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    generation_time_ms INTEGER,
                    cost REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scene_id) REFERENCES screenplay_scenes(id) ON DELETE CASCADE
                )
            """)

            # Table: storyboard_exports (exported PDF/video files)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storyboard_exports (
                    id TEXT PRIMARY KEY,
                    screenplay_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    export_type TEXT NOT NULL,
                    file_path TEXT,
                    layout TEXT,
                    codec TEXT,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (screenplay_id) REFERENCES screenplays(id) ON DELETE CASCADE
                )
            """)

            # Create indexes for screenplay tables
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_screenplays_user
                ON screenplays(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_screenplay_scenes_screenplay
                ON screenplay_scenes(screenplay_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_visual_references_user
                ON visual_references(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_visual_references_screenplay
                ON visual_references(screenplay_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_generated_images_scene
                ON generated_images(scene_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_generated_images_status
                ON generated_images(status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_storyboard_exports_screenplay
                ON storyboard_exports(screenplay_id)
            """)

            self.logger.info("Database tables initialized successfully")

    # ============================================================
    # METRICS OPERATIONS
    # ============================================================

    def save_metric(
        self,
        agent_id: str,
        metric_type: str,
        value: float,
        notes: Optional[str] = None
    ) -> int:
        """
        Save a single metric to database.

        Args:
            agent_id: Agent identifier (e.g., 'agent_1', 'system')
            metric_type: Type of metric (quality, speed, errors)
            value: Metric value
            notes: Optional notes

        Returns:
            int: ID of inserted metric
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metrics (agent_id, metric_type, value, notes)
                VALUES (?, ?, ?, ?)
            """, (agent_id, metric_type, value, notes))

            return cursor.lastrowid

    def get_metrics(
        self,
        agent_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Retrieve metrics from database.

        Args:
            agent_id: Filter by agent (None = all agents)
            metric_type: Filter by metric type (None = all types)
            hours: Number of hours to look back
            limit: Maximum number of results

        Returns:
            List of metrics as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT * FROM metrics
                WHERE timestamp >= datetime('now', '-{} hours')
            """.format(hours)

            params = []

            if agent_id:
                query += " AND agent_id = ?"
                params.append(agent_id)

            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_latest_metric(
        self,
        agent_id: str,
        metric_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent metric for an agent.

        Args:
            agent_id: Agent identifier
            metric_type: Type of metric

        Returns:
            Latest metric or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM metrics
                WHERE agent_id = ? AND metric_type = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (agent_id, metric_type))

            row = cursor.fetchone()
            return dict(row) if row else None

    # ============================================================
    # EVENTS OPERATIONS
    # ============================================================

    def save_event(
        self,
        event_type: str,
        message: str,
        agent_id: Optional[str] = None,
        severity: str = 'info',
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save an event to database.

        Args:
            event_type: Type of event (training, error, alert, etc.)
            message: Event message
            agent_id: Related agent (optional)
            severity: Event severity (info, warning, error, critical)
            metadata: Additional metadata as dictionary

        Returns:
            int: ID of inserted event
        """
        metadata_json = json.dumps(metadata) if metadata else None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (event_type, agent_id, message, severity, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (event_type, agent_id, message, severity, metadata_json))

            return cursor.lastrowid

    def get_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events from database.

        Args:
            event_type: Filter by event type (None = all)
            severity: Filter by severity (None = all)
            hours: Number of hours to look back
            limit: Maximum number of results

        Returns:
            List of events as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT * FROM events
                WHERE timestamp >= datetime('now', '-{} hours')
            """.format(hours)

            params = []

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)

            if severity:
                query += " AND severity = ?"
                params.append(severity)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            rows = cursor.fetchall()
            events = []

            for row in rows:
                event = dict(row)
                # Parse metadata JSON
                if event.get('metadata'):
                    try:
                        event['metadata'] = json.loads(event['metadata'])
                    except json.JSONDecodeError:
                        event['metadata'] = {}
                events.append(event)

            return events

    # ============================================================
    # TRAINING SESSIONS OPERATIONS
    # ============================================================

    def save_training_session(
        self,
        start_time: str,
        end_time: str,
        duration_seconds: float,
        agents_trained: int,
        overall_improvement: float,
        status: str,
        phase_times: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save a training session to database.

        Args:
            start_time: Training start time (ISO format)
            end_time: Training end time (ISO format)
            duration_seconds: Total duration
            agents_trained: Number of agents trained
            overall_improvement: Overall system improvement percentage
            status: Session status (success, failed, partial)
            phase_times: Dictionary of phase durations
            metadata: Additional metadata

        Returns:
            int: ID of inserted training session
        """
        phase_times_json = json.dumps(phase_times)
        metadata_json = json.dumps(metadata) if metadata else None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_sessions
                (start_time, end_time, duration_seconds, agents_trained,
                 overall_improvement, status, phase_times, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (start_time, end_time, duration_seconds, agents_trained,
                  overall_improvement, status, phase_times_json, metadata_json))

            return cursor.lastrowid

    def get_training_sessions(
        self,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve training sessions.

        Args:
            days: Number of days to look back
            limit: Maximum number of results

        Returns:
            List of training sessions as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM training_sessions
                WHERE start_time >= datetime('now', '-{} days')
                ORDER BY start_time DESC
                LIMIT ?
            """.format(days), (limit,))

            rows = cursor.fetchall()
            sessions = []

            for row in rows:
                session = dict(row)
                # Parse JSON fields
                if session.get('phase_times'):
                    try:
                        session['phase_times'] = json.loads(session['phase_times'])
                    except json.JSONDecodeError:
                        session['phase_times'] = {}

                if session.get('metadata'):
                    try:
                        session['metadata'] = json.loads(session['metadata'])
                    except json.JSONDecodeError:
                        session['metadata'] = {}

                sessions.append(session)

            return sessions

    def get_latest_training_session(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent training session.

        Returns:
            Latest training session or None
        """
        sessions = self.get_training_sessions(days=30, limit=1)
        return sessions[0] if sessions else None

    # ============================================================
    # SYSTEM HEALTH OPERATIONS
    # ============================================================

    def save_system_health(
        self,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: float,
        uptime_seconds: int,
        active_connections: int = 0
    ) -> int:
        """
        Save system health snapshot to database.

        Args:
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
            disk_percent: Disk usage percentage
            uptime_seconds: System uptime in seconds
            active_connections: Number of active connections

        Returns:
            int: ID of inserted health record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_health
                (cpu_percent, memory_percent, disk_percent, uptime_seconds, active_connections)
                VALUES (?, ?, ?, ?, ?)
            """, (cpu_percent, memory_percent, disk_percent, uptime_seconds, active_connections))

            return cursor.lastrowid

    def get_system_health_history(
        self,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Retrieve system health history.

        Args:
            hours: Number of hours to look back
            limit: Maximum number of results

        Returns:
            List of system health records
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM system_health
                WHERE timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT ?
            """.format(hours), (limit,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_latest_system_health(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent system health snapshot.

        Returns:
            Latest system health record or None
        """
        health = self.get_system_health_history(hours=1, limit=1)
        return health[0] if health else None

    # ============================================================
    # UTILITY OPERATIONS
    # ============================================================

    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Clean up old data from database.

        Removes records older than specified number of days.

        Args:
            days_to_keep: Number of days to retain
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Cleanup metrics
            cursor.execute("""
                DELETE FROM metrics
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days_to_keep))
            metrics_deleted = cursor.rowcount

            # Cleanup events
            cursor.execute("""
                DELETE FROM events
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days_to_keep))
            events_deleted = cursor.rowcount

            # Cleanup system health
            cursor.execute("""
                DELETE FROM system_health
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days_to_keep))
            health_deleted = cursor.rowcount

            self.logger.info(
                f"Cleanup completed: {metrics_deleted} metrics, "
                f"{events_deleted} events, {health_deleted} health records deleted"
            )

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with table counts and database size
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Count records in each table
            for table in ['metrics', 'events', 'training_sessions', 'system_health']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]

            # Get database size (bytes)
            import os
            if os.path.exists(self.db_path):
                stats['database_size_bytes'] = os.path.getsize(self.db_path)
                stats['database_size_mb'] = round(stats['database_size_bytes'] / 1024 / 1024, 2)

            return stats

    # ============================================================
    # STORYBOARD VIDEO OPERATIONS
    # ============================================================

    def save_video_task(
        self,
        task_id: str,
        user_id: str,
        project_name: str,
        song_title: str,
        music_file: str,
        genre: str,
        bpm: Optional[int] = None,
        engine: str = 'runway_standard',
        prompt: str = '',
        status: str = 'pending',
        youtube_title: Optional[str] = None,
        youtube_description: Optional[str] = None,
        youtube_tags: Optional[str] = None,
        video_url: Optional[str] = None,
        cost: Optional[float] = None,
        credits_used: Optional[int] = None,
        duration: Optional[int] = None
    ) -> int:
        """
        Save a video task to database.

        Args:
            task_id: Unique task identifier
            user_id: User identifier
            project_name: Project name
            song_title: Song title
            music_file: Path/URL to music file
            genre: Music genre
            bpm: Beats per minute (optional)
            engine: Video generation engine
            prompt: Generation prompt
            status: Task status (pending, processing, completed, failed)
            youtube_title: YouTube optimized title
            youtube_description: YouTube description
            youtube_tags: YouTube tags (JSON array)
            video_url: Generated video URL
            cost: Generation cost
            credits_used: Credits consumed
            duration: Video duration in seconds

        Returns:
            int: Number of rows inserted (1 on success)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO storyboard_videos
                (id, user_id, project_name, song_title, music_file, genre, bpm,
                 engine, prompt, status, youtube_title, youtube_description,
                 youtube_tags, video_url, cost, credits_used, duration, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                task_id, user_id, project_name, song_title, music_file, genre, bpm,
                engine, prompt, status, youtube_title, youtube_description,
                youtube_tags, video_url, cost, credits_used, duration
            ))

            self.logger.info(f"Saved video task: {task_id} for user: {user_id}")
            return cursor.rowcount

    def get_video_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single video task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Video task dictionary or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM storyboard_videos
                WHERE id = ?
            """, (task_id,))

            row = cursor.fetchone()
            if row:
                task = dict(row)
                # Parse JSON fields
                if task.get('youtube_tags'):
                    try:
                        task['youtube_tags'] = json.loads(task['youtube_tags'])
                    except json.JSONDecodeError:
                        task['youtube_tags'] = []
                return task
            return None

    def get_video_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get video tasks with optional filtering.

        Args:
            user_id: Filter by user (None = all users)
            status: Filter by status (None = all statuses)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of video tasks
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM storyboard_videos WHERE 1=1"
            params = []

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)

            rows = cursor.fetchall()
            tasks = []

            for row in rows:
                task = dict(row)
                # Parse JSON fields
                if task.get('youtube_tags'):
                    try:
                        task['youtube_tags'] = json.loads(task['youtube_tags'])
                    except json.JSONDecodeError:
                        task['youtube_tags'] = []
                tasks.append(task)

            return tasks

    def update_video_task_status(
        self,
        task_id: str,
        status: str,
        video_url: Optional[str] = None,
        error_message: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> int:
        """
        Update video task status.

        Args:
            task_id: Task identifier
            status: New status
            video_url: Video URL (optional)
            error_message: Error message if failed
            completed_at: Completion timestamp (ISO format)

        Returns:
            Number of rows updated
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic update query
            updates = ["status = ?"]
            params = [status]

            if video_url:
                updates.append("video_url = ?")
                params.append(video_url)

            if error_message:
                updates.append("error_message = ?")
                params.append(error_message)

            if completed_at:
                updates.append("completed_at = ?")
                params.append(completed_at)

            params.append(task_id)

            query = f"""
                UPDATE storyboard_videos
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, params)

            self.logger.info(f"Updated video task {task_id} to status: {status}")
            return cursor.rowcount

    def update_video_task(
        self,
        task_id: str,
        **kwargs
    ) -> int:
        """
        Update video task with arbitrary fields.

        Args:
            task_id: Task identifier
            **kwargs: Fields to update (status, video_url, cost, etc.)

        Returns:
            Number of rows updated
        """
        if not kwargs:
            return 0

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic update query
            updates = []
            params = []

            allowed_fields = {
                'status', 'video_url', 'youtube_title', 'youtube_description',
                'youtube_tags', 'cost', 'credits_used', 'duration',
                'error_message', 'completed_at', 'prompt', 'engine'
            }

            for key, value in kwargs.items():
                if key in allowed_fields:
                    updates.append(f"{key} = ?")
                    params.append(value)

            if not updates:
                return 0

            params.append(task_id)

            query = f"""
                UPDATE storyboard_videos
                SET {', '.join(updates)}
                WHERE id = ?
            """

            cursor.execute(query, params)

            self.logger.info(f"Updated video task {task_id} with {len(updates)} fields")
            return cursor.rowcount

    def delete_video_task(self, task_id: str) -> int:
        """
        Delete a video task and its associated thumbnails.

        Args:
            task_id: Task identifier

        Returns:
            Number of rows deleted
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Delete thumbnails first (foreign key constraint)
            cursor.execute("""
                DELETE FROM storyboard_thumbnails
                WHERE video_id = ?
            """, (task_id,))

            # Delete video task
            cursor.execute("""
                DELETE FROM storyboard_videos
                WHERE id = ?
            """, (task_id,))

            self.logger.info(f"Deleted video task: {task_id}")
            return cursor.rowcount

    # ============================================================
    # STORYBOARD THUMBNAILS OPERATIONS
    # ============================================================

    def save_thumbnail(
        self,
        thumbnail_id: str,
        video_id: str,
        variant: str,
        image_url: str,
        click_prediction: Optional[float] = None,
        is_selected: bool = False
    ) -> int:
        """
        Save a thumbnail variant.

        Args:
            thumbnail_id: Unique thumbnail identifier
            video_id: Associated video task ID
            variant: Variant type (bold_text, emotional_face, etc.)
            image_url: Thumbnail image URL
            click_prediction: Predicted click-through rate (0-1)
            is_selected: Whether this thumbnail is selected

        Returns:
            Number of rows inserted
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO storyboard_thumbnails
                (id, video_id, variant, image_url, click_prediction, is_selected, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (thumbnail_id, video_id, variant, image_url, click_prediction, is_selected))

            self.logger.info(f"Saved thumbnail: {thumbnail_id} for video: {video_id}")
            return cursor.rowcount

    def get_thumbnails(
        self,
        video_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all thumbnails for a video.

        Args:
            video_id: Video task identifier

        Returns:
            List of thumbnail dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM storyboard_thumbnails
                WHERE video_id = ?
                ORDER BY click_prediction DESC, created_at DESC
            """, (video_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_thumbnail_selection(
        self,
        video_id: str,
        selected_thumbnail_id: str
    ) -> int:
        """
        Update thumbnail selection for a video.

        Marks one thumbnail as selected and all others as not selected.

        Args:
            video_id: Video task identifier
            selected_thumbnail_id: Thumbnail to mark as selected

        Returns:
            Number of rows updated
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Deselect all thumbnails for this video
            cursor.execute("""
                UPDATE storyboard_thumbnails
                SET is_selected = 0
                WHERE video_id = ?
            """, (video_id,))

            # Select the specified thumbnail
            cursor.execute("""
                UPDATE storyboard_thumbnails
                SET is_selected = 1
                WHERE id = ? AND video_id = ?
            """, (selected_thumbnail_id, video_id))

            self.logger.info(f"Updated thumbnail selection for video {video_id}: {selected_thumbnail_id}")
            return cursor.rowcount

    def get_selected_thumbnail(
        self,
        video_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the selected thumbnail for a video.

        Args:
            video_id: Video task identifier

        Returns:
            Selected thumbnail or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM storyboard_thumbnails
                WHERE video_id = ? AND is_selected = 1
                LIMIT 1
            """, (video_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

    # ============================================================
    # STORYBOARD STATISTICS
    # ============================================================

    def get_storyboard_stats(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get storyboard statistics.

        Args:
            user_id: Filter by user (None = all users)

        Returns:
            Statistics dictionary
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Video tasks count
            query = "SELECT COUNT(*) FROM storyboard_videos"
            params = []

            if user_id:
                query += " WHERE user_id = ?"
                params.append(user_id)

            cursor.execute(query, params)
            stats['total_tasks'] = cursor.fetchone()[0]

            # Tasks by status
            query = "SELECT status, COUNT(*) FROM storyboard_videos"
            if user_id:
                query += " WHERE user_id = ?"

            query += " GROUP BY status"

            cursor.execute(query, params)
            stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}

            # Total cost
            query = "SELECT SUM(cost) FROM storyboard_videos WHERE cost IS NOT NULL"
            if user_id:
                query += " AND user_id = ?"

            cursor.execute(query, params)
            total_cost = cursor.fetchone()[0]
            stats['total_cost'] = total_cost if total_cost else 0.0

            # Total credits used
            query = "SELECT SUM(credits_used) FROM storyboard_videos WHERE credits_used IS NOT NULL"
            if user_id:
                query += " AND user_id = ?"

            cursor.execute(query, params)
            total_credits = cursor.fetchone()[0]
            stats['total_credits_used'] = total_credits if total_credits else 0

            # Thumbnails count
            query = "SELECT COUNT(*) FROM storyboard_thumbnails"
            if user_id:
                query += " WHERE video_id IN (SELECT id FROM storyboard_videos WHERE user_id = ?)"

            cursor.execute(query, params)
            stats['total_thumbnails'] = cursor.fetchone()[0]

            return stats


# ============================================================
# GLOBAL DATABASE INSTANCE
# ============================================================

# Singleton instance for application-wide use
_db_instance = None


def get_db() -> DatabaseManager:
    """
    Get global database instance.

    Returns:
        DatabaseManager: Singleton database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance