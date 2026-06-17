"""Test fixtures for zeroeye API tests."""
import pytest
import subprocess
import time
import requests

@pytest.fixture(scope="session")
def server_url():
    """Start the backend server and return its URL."""
    proc = subprocess.Popen(
        ["cargo", "run", "--release"],
        cwd="backend",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    url = "http://localhost:8080"
    # Wait for server
    for _ in range(30):
        try:
            requests.get(url + "/health")
            break
        except requests.ConnectionError:
            time.sleep(1)
    yield url
    proc.terminate()
    proc.wait()

@pytest.fixture
def client():
    """Return a requests session for testing."""
    import requests
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
