from urllib.parse import urlencode

import httpx
from typing import Any, AsyncGenerator

from loguru import logger


class JenkinsClient:
    def __init__(
        self, jenkins_base_url: str, jenkins_user: str, jenkins_password: str
    ) -> None:
        self.jenkins_base_url = jenkins_base_url
        self.jenkins_user = jenkins_user
        self.jenkins_password = jenkins_password

        auth = (self.jenkins_user, self.jenkins_password)
        self.client = httpx.AsyncClient(auth=auth)

    async def get_jobs(self) -> AsyncGenerator[list[dict[str, Any]], None]:
        per_page = 100
        page = 0
        logger.info("Getting jobs from Jenkins")

        while True:
            # Parameters for pagination
            params = {
                'tree': f'jobs[name,url,description,displayName,fullDisplayName,fullName]'
            }
            encoded_params = urlencode(params)

            job_response = await self.client.get(f"{self.jenkins_base_url}/api/json?{encoded_params}")
            job_response.raise_for_status()
            jobs = job_response.json()['jobs']

            # If there are no more jobs, exit the loop
            if not jobs:
                break

            logger.info(f"Got {len(jobs)} jobs from Jenkins")

            transformed = [
                {
                    "type": "item.updated",
                    "data": job,
                    "url": job.get("url"),
                    # "time": job.get("time")
                }
                for job in jobs
            ]

            yield transformed
            page += 1

            if len(jobs) < per_page:
                break

    async def get_builds(self, job_slug: str) -> list[dict[str, Any]]:
        logger.info(f"Getting builds from Jenkins for job {job_slug}")

        params = {
            'tree': f'builds[id,number,url,result,duration,timestamp,displayName,fullDisplayName]'
        }
        encoded_params = urlencode(params)

        build_response = await self.client.get(
            f"{self.jenkins_base_url}/job/{job_slug}/api/json?{encoded_params}"
        )
        build_response.raise_for_status()
        builds = build_response.json()
        logger.info(f"Got {len(builds)} builds from Jenkins for job {job_slug}")

        transformed_builds = [
            {
                "type": "build.finalize",
                "source": job_slug,
                "url": build.get("url", None),
                "data": build
            }
            for build in builds if isinstance(build, dict)
        ]
        print(f"Builds: {transformed_builds}")

        return transformed_builds
