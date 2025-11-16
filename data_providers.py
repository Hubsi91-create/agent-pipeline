"""
Data Provider Abstraction Layer
================================
Enables seamless switching between local file-based and cloud API-based data sources.

Architecture:
- Local Development: Reads REAL data from orchestrator output files
- Cloud Production: Fetches data from REST APIs
- Frontend: Completely transparent - no changes needed

NO DUMMY DATA - Only real implementations!
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime
from pathlib import Path


class DataProvider(ABC):
    """
    Abstract base class for data providers.
    Enables: Local (File-based) → Cloud (API-based) switch
    """

    @abstractmethod
    def get_training_status(self) -> Dict[str, Any]:
        """Get training status - works local or cloud"""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get quality metrics - works local or cloud"""
        pass

    @abstractmethod
    def get_agents_status(self) -> Dict[str, Any]:
        """Get agent status - works local or cloud"""
        pass

    @abstractmethod
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health - works local or cloud"""
        pass


class LocalDataProvider(DataProvider):
    """
    LOCAL: Reads data from local orchestrator files
    For: Development & Local Testing

    IMPORTANT: Uses REAL orchestrator output files!
    NOT: Hardcoded/Mock data!
    """

    def __init__(self, base_path: str = None):
        """
        Initialize with orchestrator base path

        Args:
            base_path: Root path to orchestrator files (defaults to project root)
        """
        if base_path is None:
            # Auto-detect project root
            current_dir = Path(__file__).resolve().parent
            base_path = current_dir.parent.parent

        self.base_path = Path(base_path)
        self.config_path = self.base_path / 'orchestrator' / 'training' / 'config.json'
        self.report_path = self.base_path / 'orchestrator' / 'orchestration_report.json'
        self.logs_path = self.base_path / 'orchestrator' / 'logs'
        self.agents_path = self.base_path / 'orchestrator' / 'agents'

    def get_training_status(self) -> Dict[str, Any]:
        """
        Reads REAL training status from:
        - orchestrator/training/config.json (Training Config)
        - orchestrator/orchestration_report.json (Real Status)
        - orchestrator/logs/ (Progress)

        IMPORTANT: These are REAL output files from the orchestrator!
        """
        try:
            training_data = {
                'status': 'idle',
                'phase': 'initialization',
                'current_iteration': 0,
                'total_iterations': 100,
                'completed_iterations': 0,
                'progress_percentage': 0,
                'start_time': None,
                'elapsed_seconds': 0,
                'estimated_completion': None,
                'source': 'local'
            }

            # 1. Read Config (if exists)
            if self.config_path.exists():
                try:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        training_data['phase'] = config.get('phase', 'initialization')
                        training_data['total_iterations'] = config.get('total_iterations', 100)
                except json.JSONDecodeError:
                    pass  # Use defaults

            # 2. Read Report (REAL orchestrator output!)
            if self.report_path.exists():
                try:
                    with open(self.report_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        training_data['current_iteration'] = report.get('iteration', 0)
                        training_data['status'] = report.get('status', 'idle')
                        training_data['start_time'] = report.get('start_time')
                        training_data['elapsed_seconds'] = report.get('elapsed_time', 0)

                        # Extract additional metadata if available
                        if 'metadata' in report:
                            training_data.update(report['metadata'])
                except json.JSONDecodeError:
                    pass

            # 3. Count completed logs
            if self.logs_path.exists():
                log_files = list(self.logs_path.glob('*.log'))
                training_data['completed_iterations'] = len(log_files)

            # 4. Calculate progress
            total = training_data['total_iterations']
            current = training_data['current_iteration']
            if total > 0:
                training_data['progress_percentage'] = int((current / total) * 100)

            # 5. Estimate completion time
            if training_data['elapsed_seconds'] > 0 and current > 0:
                avg_time_per_iteration = training_data['elapsed_seconds'] / current
                remaining_iterations = total - current
                estimated_seconds = avg_time_per_iteration * remaining_iterations
                training_data['estimated_completion'] = estimated_seconds

            return training_data

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to read training status: {str(e)}',
                'phase': 'error_state',
                'source': 'local'
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Reads REAL metrics from orchestrator report
        NOT: Hardcoded values!
        """
        try:
            metrics = {
                'quality_score': None,
                'performance': None,
                'efficiency': None,
                'reliability': None,
                'timestamp': None,
                'source': 'local'
            }

            if self.report_path.exists():
                with open(self.report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)

                    # Extract metrics from report
                    metrics['quality_score'] = report.get('quality_score')
                    metrics['performance'] = report.get('performance_index')
                    metrics['efficiency'] = report.get('efficiency_score')
                    metrics['reliability'] = report.get('reliability_rating')
                    metrics['timestamp'] = report.get('timestamp')

                    # Extract detailed metrics if available
                    if 'metrics' in report:
                        metrics.update(report['metrics'])

            return metrics

        except Exception as e:
            return {
                'error': str(e),
                'status': 'metrics_unavailable',
                'source': 'local'
            }

    def get_agents_status(self) -> Dict[str, Any]:
        """
        Reads REAL agent status from orchestrator files
        """
        try:
            agents = []

            # Read agent files from orchestrator/agents/
            if self.agents_path.exists():
                for agent_file in self.agents_path.glob('*.py'):
                    agent_name = agent_file.stem

                    # Try to read agent status from report
                    agent_info = {
                        'name': agent_name,
                        'status': 'available',
                        'health': 'operational',
                        'type': self._detect_agent_type(agent_name)
                    }

                    # Check if there's a status file for this agent
                    status_file = self.agents_path / f'{agent_name}_status.json'
                    if status_file.exists():
                        try:
                            with open(status_file, 'r', encoding='utf-8') as f:
                                status_data = json.load(f)
                                agent_info.update(status_data)
                        except json.JSONDecodeError:
                            pass

                    agents.append(agent_info)

            # Read from orchestration report if available
            if self.report_path.exists():
                try:
                    with open(self.report_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        if 'agents' in report:
                            # Merge with report data
                            report_agents = report['agents']
                            for agent in agents:
                                if agent['name'] in report_agents:
                                    agent.update(report_agents[agent['name']])
                except json.JSONDecodeError:
                    pass

            return {
                'agents': agents,
                'total': len(agents),
                'online': len([a for a in agents if a.get('status') == 'online' or a.get('status') == 'available']),
                'offline': len([a for a in agents if a.get('status') == 'offline']),
                'source': 'local'
            }

        except Exception as e:
            return {
                'error': str(e),
                'agents': [],
                'total': 0,
                'source': 'local'
            }

    def get_system_health(self) -> Dict[str, Any]:
        """
        Calculate REAL system health from orchestrator files
        """
        try:
            health = {
                'status': 'operational',
                'components': {},
                'overall_health': 100,
                'timestamp': datetime.now().isoformat(),
                'source': 'local'
            }

            # Check orchestrator availability
            health['components']['orchestrator'] = {
                'status': 'online' if self.report_path.exists() else 'offline',
                'health': 100 if self.report_path.exists() else 0
            }

            # Check agents
            agents_status = self.get_agents_status()
            if 'error' not in agents_status:
                total_agents = agents_status.get('total', 0)
                online_agents = agents_status.get('online', 0)

                if total_agents > 0:
                    agent_health = int((online_agents / total_agents) * 100)
                else:
                    agent_health = 0

                health['components']['agents'] = {
                    'status': 'online' if online_agents > 0 else 'offline',
                    'health': agent_health,
                    'online': online_agents,
                    'total': total_agents
                }

            # Check training system
            training_status = self.get_training_status()
            if 'error' not in training_status:
                training_health = 100 if training_status.get('status') != 'error' else 0
                health['components']['training'] = {
                    'status': training_status.get('status', 'unknown'),
                    'health': training_health
                }

            # Calculate overall health
            component_healths = [c['health'] for c in health['components'].values()]
            if component_healths:
                health['overall_health'] = int(sum(component_healths) / len(component_healths))

            # Determine overall status
            if health['overall_health'] >= 80:
                health['status'] = 'operational'
            elif health['overall_health'] >= 50:
                health['status'] = 'degraded'
            else:
                health['status'] = 'critical'

            return health

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'overall_health': 0,
                'source': 'local'
            }

    def _detect_agent_type(self, agent_name: str) -> str:
        """Detect agent type from name"""
        agent_name_lower = agent_name.lower()

        if 'orchestrat' in agent_name_lower:
            return 'orchestrator'
        elif 'train' in agent_name_lower:
            return 'training'
        elif 'music' in agent_name_lower or 'audio' in agent_name_lower:
            return 'music'
        elif 'backend' in agent_name_lower:
            return 'backend'
        elif 'frontend' in agent_name_lower:
            return 'frontend'
        else:
            return 'utility'


class CloudDataProvider(DataProvider):
    """
    CLOUD: Fetches data via REST APIs
    For: Production on Google Cloud/AWS/Azure

    IMPORTANT: This class is used when system is deployed to cloud!
    Response format matches LocalDataProvider exactly - transparent for frontend!
    """

    def __init__(self, cloud_api_url: str, api_key: str):
        """
        Initialize cloud provider

        Args:
            cloud_api_url: Base URL for cloud API (e.g., https://api.music-agents.com)
            api_key: API authentication key
        """
        self.cloud_api_url = cloud_api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def get_training_status(self) -> Dict[str, Any]:
        """
        Fetch training status from cloud API
        EXACT same response format as LocalDataProvider!
        """
        import requests
        try:
            response = requests.get(
                f'{self.cloud_api_url}/api/training/status',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            data['source'] = 'cloud'
            return data
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'source': 'cloud_api',
                'status': 'unavailable'
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Fetch metrics from cloud API"""
        import requests
        try:
            response = requests.get(
                f'{self.cloud_api_url}/api/metrics/quality',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            data['source'] = 'cloud'
            return data
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'source': 'cloud_api'
            }

    def get_agents_status(self) -> Dict[str, Any]:
        """Fetch agent status from cloud API"""
        import requests
        try:
            response = requests.get(
                f'{self.cloud_api_url}/api/agents/status',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            data['source'] = 'cloud'
            return data
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'source': 'cloud_api',
                'agents': [],
                'total': 0
            }

    def get_system_health(self) -> Dict[str, Any]:
        """Fetch system health from cloud API"""
        import requests
        try:
            response = requests.get(
                f'{self.cloud_api_url}/api/system/health',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            data['source'] = 'cloud'
            return data
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'source': 'cloud_api',
                'status': 'unavailable',
                'overall_health': 0
            }


class DataProviderFactory:
    """Factory for data provider selection based on environment"""

    @staticmethod
    def get_provider(environment: str = 'local', **kwargs) -> DataProvider:
        """
        Select data provider based on environment

        Args:
            environment: 'local', 'staging', or 'cloud'
            **kwargs: Additional provider-specific arguments

        Usage in app.py:
            provider = DataProviderFactory.get_provider(
                os.getenv('ENVIRONMENT', 'local')
            )

        Returns:
            DataProvider: Appropriate provider for the environment
        """
        environment = environment.lower()

        if environment == 'cloud':
            # Cloud production - use REST APIs
            cloud_api_url = kwargs.get('cloud_api_url') or os.getenv('CLOUD_API_URL')
            api_key = kwargs.get('api_key') or os.getenv('CLOUD_API_KEY')

            if not cloud_api_url or not api_key:
                raise ValueError(
                    "Cloud environment requires CLOUD_API_URL and CLOUD_API_KEY"
                )

            return CloudDataProvider(
                cloud_api_url=cloud_api_url,
                api_key=api_key
            )

        elif environment == 'staging':
            # Staging - could be hybrid (for now use local)
            base_path = kwargs.get('base_path')
            return LocalDataProvider(base_path=base_path)

        else:  # local (default)
            # Local development - use file-based provider
            base_path = kwargs.get('base_path')
            return LocalDataProvider(base_path=base_path)


# Singleton instance (initialized in app.py)
_provider_instance: Optional[DataProvider] = None


def get_data_provider() -> DataProvider:
    """
    Get the configured data provider instance

    Returns:
        DataProvider: The active data provider

    Raises:
        RuntimeError: If provider not initialized
    """
    global _provider_instance

    if _provider_instance is None:
        # Auto-initialize with local provider
        _provider_instance = DataProviderFactory.get_provider('local')

    return _provider_instance


def initialize_provider(environment: str = None, **kwargs) -> DataProvider:
    """
    Initialize the global data provider

    Args:
        environment: Environment name ('local', 'staging', 'cloud')
        **kwargs: Additional provider-specific arguments

    Returns:
        DataProvider: The initialized provider
    """
    global _provider_instance

    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'local')

    _provider_instance = DataProviderFactory.get_provider(environment, **kwargs)
    return _provider_instance
