import logging
import os
import glob
import sys
sys.path.append(os.getcwd()) 
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from google.cloud import storage
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from agent import root_agent as root_app


FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket name (without gs:// prefix).")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_string("agent_name", None, "The name of the agent, identifying the wheel file")

flags.DEFINE_bool("create", False, "Create a new agent.")
flags.DEFINE_bool("delete", False, "Delete an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_staging_bucket(project_id: str, location: str, bucket_name: str) -> str:
    storage_client = storage.Client(project=project_id)
    try:
        bucket = storage_client.lookup_bucket(bucket_name)
        if bucket:
            logger.info("Staging bucket gs://%s already exists.", bucket_name)
        else:
            logger.info("Staging bucket gs://%s not found. Creating...", bucket_name)
            new_bucket = storage_client.create_bucket(
                bucket_name, project=project_id, location=location
            )
            logger.info("Successfully created staging bucket gs://%s in %s.", new_bucket.name, location)
            new_bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            new_bucket.patch()
            logger.info("Enabled uniform bucket-level access for gs://%s.", new_bucket.name)

    except google_exceptions.Forbidden as e:
        logger.error("Permission denied for bucket gs://%s. Error: %s", bucket_name, e)
        raise
    except google_exceptions.Conflict as e:
        logger.warning("Bucket gs://%s likely already exists. Error: %s", bucket_name, e)
    except google_exceptions.ClientError as e:
        logger.error("Failed to create or access bucket gs://%s. Error: %s", bucket_name, e)
        raise

    return f"gs://{bucket_name}"


def create(env_vars: dict[str, str], agent_whl_file: str) -> None:
    """Creates and deploys the agent."""
    adk_app = AdkApp(
        agent=root_app,
        enable_tracing=True,
    )

    if not os.path.exists(agent_whl_file):
        logger.error("Agent wheel file not found at: %s", agent_whl_file)
        raise FileNotFoundError(f"Agent wheel file not found: {agent_whl_file}")

    logger.info("Using agent wheel file: %s", agent_whl_file)

    from datetime import datetime
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    deps = [
        agent_whl_file,
        "google-adk==1.23.0",
        "google-cloud-bigquery>=3.11.0",
        "google-cloud-bigquery-storage>=2.24.0",
        "deprecated>=1.2.14",
        "fpdf2>=2.7.0",
        "pydantic>=2.0.0",
        "cloudpickle==3.1.2",
        "python-dateutil>=2.8.2",
        "google-cloud-storage>=2.0.0",
        "google-cloud-firestore>=2.0.0",
        "google-api-python-client>=2.0.0"
    ]

    remote_agent = agent_engines.create(
        adk_app,
        requirements=deps,
        extra_packages=[agent_whl_file],
        env_vars=env_vars,
        display_name=f"HR Onboarding Agent - {formatted_datetime}"
    )

    logger.info("Created remote agent: %s", remote_agent.resource_name)


def delete(resource_id: str) -> None:
    logger.info("Attempting to delete agent: %s", resource_id)
    try:
        remote_agent = agent_engines.get(resource_id)
        remote_agent.delete(force=True)
        logger.info("Successfully deleted remote agent: %s", resource_id)
        print(f"\nSuccessfully deleted agent: {resource_id}")
    except google_exceptions.NotFound:
        logger.error("Agent with resource ID %s not found.", resource_id)
        print(f"\nAgent not found: {resource_id}")
    except Exception as e:
        logger.error("An error occurred while deleting agent %s: %s", resource_id, e)
        print(f"\nError deleting agent {resource_id}: {e}")


def main(argv: list[str]) -> None:
    """Main execution function."""
    load_dotenv()
    env_vars = {}
    agent_name = FLAGS.agent_name
    try:
        agent_whl_file = glob.glob(f"dist/{agent_name}-*-py3-none-any.whl")[0]
    except IndexError:
        print(f"\nError: Wheel file for agent '{agent_name}' not found. Have you run 'poetry build'?")
        return

    project_id = FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    default_bucket_name = f"{project_id}-adk-staging" if project_id else None
    bucket_name = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", default_bucket_name)

    env_var_keys = [
        "BUCKET_NAME",
        "CALENDAR_ID",
        "GOOGLE_GENAI_USE_VERTEXAI",
    ]
    for key in env_var_keys:
        value = os.getenv(key)
        if value:
            env_vars[key] = value

    logger.info("Using PROJECT: %s", project_id)
    logger.info("Using LOCATION: %s", location)
    logger.info("Using BUCKET NAME: %s", bucket_name)

    if not FLAGS.agent_name:
        print("\nError: Missing required --agent_name flag.")
        return
    if not project_id:
        print("\nError: Missing required GCP Project ID.")
        return
    if not location:
        print("\nError: Missing required GCP Location.")
        return
    if not bucket_name:
        print("\nError: Missing required GCS Bucket Name.")
        return
    if not FLAGS.create and not FLAGS.delete:
        print("\nError: You must specify either --create or --delete flag.")
        return
    if FLAGS.delete and not FLAGS.resource_id:
        print("\nError: --resource_id is required when using the --delete flag.")
        return

    try:
        staging_bucket_uri = None
        if FLAGS.create:
            staging_bucket_uri = setup_staging_bucket(project_id, location, bucket_name)

        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket_uri,
        )

        if FLAGS.create:
            create(env_vars, agent_whl_file)
        elif FLAGS.delete:
            delete(FLAGS.resource_id)

    except google_exceptions.Forbidden as e:
        print(f"Permission Error: {e}")
    except FileNotFoundError as e:
        print(f"\nFile Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        logger.exception("Unhandled exception in main:")


if __name__ == "__main__":
    app.run(main)
