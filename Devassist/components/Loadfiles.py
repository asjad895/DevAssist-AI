from pydantic import BaseModel, HttpUrl, ValidationError
import os
from git import Repo
import asyncio
from Devassist.config import fileconfig

class GitHubRepoInput(BaseModel):
    repo_url: HttpUrl
    destination_path: str = fileconfig.CODEBASE_DIR


async def download_github_repo(input_data: GitHubRepoInput):
    """
    Download a GitHub repository to the local system.

    Args:
        input_data (GitHubRepoInput): Validated input data for repository URL and destination path.
    """
    try:
        if (not os.path.exists(input_data.destination_path)) or (len(os.listdir(input_data.destination_path)))<0:
            Repo.clone_from(input_data.repo_url, input_data.destination_path) # type: ignore
            print(f"Repository downloaded to: {input_data.destination_path}")
        else:
            print(f"{input_data.destination_path} already exists. ")
    except Exception as e:
        print(f"Error downloading repository: {e}")

# try:
#     input_data = GitHubRepoInput(
#         repo_url='https://github.com/asjad895/GENAI_CHATBOT', # type: ignore
#         destination_path = fileconfig.CODEBASE_DIR
#     )
#     await asyncio.run(download_github_repo(input_data))
# except ValidationError as ve:
#     print(f"Input validation error: {ve}")
