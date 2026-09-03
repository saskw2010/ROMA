import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents import SecurityAuditorAgent


async def run() -> None:
    agent = SecurityAuditorAgent()
    report = await agent.audit("https://github.com/example/repo", branch="main")
    print(json.dumps(report.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(run())
