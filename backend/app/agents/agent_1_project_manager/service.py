"""
Agent 1: Project Manager
Creates and manages video production projects
"""

from typing import Optional
from app.models.data_models import Project, ProjectCreate, ProjectStatus
from app.infrastructure.database.google_sheet_service import google_sheet_service, SHEET_A1_PROJECTS
from app.utils.logger import setup_logger

logger = setup_logger("Agent1_ProjectManager")


class Agent1ProjectManager:
    """Singleton service for project management"""

    _instance: Optional['Agent1ProjectManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Create a new music video project

        Args:
            project_data: Project creation data

        Returns:
            Created project
        """
        logger.info(f"Creating new project: {project_data.name}")

        # Create project
        project = Project(
            name=project_data.name,
            artist=project_data.artist,
            song_title=project_data.song_title,
            status=ProjectStatus(status="INIT", progress_percentage=0.0)
        )

        # Save to Google Sheets
        await self._save_to_sheets(project)

        logger.info(f"Project created: {project.id}")
        return project

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        record = await google_sheet_service.find_record(
            SHEET_A1_PROJECTS,
            "id",
            project_id
        )

        if record:
            return Project(**record)
        return None

    async def update_project_status(
        self,
        project_id: str,
        status: str,
        current_agent: Optional[str] = None,
        progress: Optional[float] = None
    ) -> bool:
        """Update project status"""
        updates = {"status": status}
        if current_agent:
            updates["current_agent"] = current_agent
        if progress is not None:
            updates["progress_percentage"] = progress

        return await google_sheet_service.update_record(
            SHEET_A1_PROJECTS,
            "id",
            project_id,
            updates
        )

    async def _save_to_sheets(self, project: Project) -> bool:
        """Save project to Google Sheets"""
        data = [
            project.id,
            project.name,
            project.artist,
            project.song_title,
            project.audio_file_path or "",
            project.status.status,
            project.status.current_agent or "",
            project.status.progress_percentage,
            project.created_at.isoformat(),
            project.updated_at.isoformat()
        ]

        return await google_sheet_service.append_row(SHEET_A1_PROJECTS, data)


# Singleton instance
agent1_service = Agent1ProjectManager()
