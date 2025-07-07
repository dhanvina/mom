import pytest
from unittest.mock import MagicMock, patch
from app.utils.ollama_utils import OllamaManager, OllamaRunningError, ModelNotFoundError


@pytest.fixture
def ollama_manager():
    return OllamaManager(model_name="mistral")


def test_is_server_running_true(ollama_manager):
    with patch.object(ollama_manager.client, "list", return_value={"models": []}):
        assert ollama_manager.is_server_running() is True


def test_is_server_running_false(ollama_manager):
    with patch.object(ollama_manager.client, "list", side_effect=Exception("Connection error")):
        assert ollama_manager.is_server_running() is False


def test_list_models_success():
    fake_models = MagicMock()
    fake_models.models = [MagicMock(model="mistral"), MagicMock(model="llama3")]
    with patch("app.utils.ollama_utils.ollama.list", return_value=fake_models):
        manager = OllamaManager("mistral")
        models = manager.list_models()
        assert "mistral" in models
        assert "llama3" in models


def test_list_models_failure():
    with patch("app.utils.ollama_utils.ollama.list", side_effect=Exception("Server down")):
        manager = OllamaManager("mistral")
        assert manager.list_models() == []


def test_is_model_available_true():
    with patch("app.utils.ollama_utils.OllamaManager.list_models", return_value=["mistral"]):
        manager = OllamaManager("mistral")
        assert manager.is_model_available() is True


def test_is_model_available_false():
    with patch("app.utils.ollama_utils.OllamaManager.list_models", return_value=["llama2"]):
        manager = OllamaManager("mistral")
        assert manager.is_model_available() is False


def test_pull_model_success():
    with patch("app.utils.ollama_utils.ollama.pull", return_value=True):
        manager = OllamaManager("mistral")
        assert manager.pull_model() is True


def test_pull_model_failure():
    with patch("app.utils.ollama_utils.ollama.pull", side_effect=Exception("pull failed")):
        manager = OllamaManager("mistral")
        assert manager.pull_model() is False


def test_get_model_info_found():
    mock_model = MagicMock(
        name="Mistral",
        model="mistral",
        size="2GB",
        modified_at="2024-07-01",
        digest="xyz123"
    )
    mock_list = MagicMock()
    mock_list.models = [mock_model]

    with patch("app.utils.ollama_utils.ollama.list", return_value=mock_list):
        manager = OllamaManager("mistral")
        manager.model = "mistral"
        info = manager.get_model_info("mistral")
        assert info["model"] == "mistral"
        assert info["size"] == "2GB"


def test_get_model_info_not_found():
    mock_list = MagicMock()
    mock_list.models = []

    with patch("app.utils.ollama_utils.ollama.list", return_value=mock_list):
        manager = OllamaManager("mistral")
        manager.model = "mistral"
        assert manager.get_model_info("mistral") == {}
