import os
import shutil
from unittest.mock import patch
from worker_service.processors.ocr_client import AutoOcrClient

def test_autooocr_client_uses_provided_cmd():
    client = AutoOcrClient(tesseract_cmd="/custom/tesseract")
    with patch("shutil.which") as mock_which:
        # We don't want it to even call shutil.which if cmd is provided,
        # but let's see how it's implemented.
        # Current implementation: tesseract_path = self._tesseract_cmd or shutil.which("tesseract")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "some text"

            client.extract_text("dummy.jpg")

            mock_run.assert_called()
            args, _ = mock_run.call_args
            assert args[0][0] == "/custom/tesseract"

def test_autooocr_client_falls_back_to_which():
    client = AutoOcrClient(tesseract_cmd=None)
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/tesseract"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "some text"

            client.extract_text("dummy.jpg")

            mock_which.assert_called_with("tesseract")
            args, _ = mock_run.call_args
            assert args[0][0] == "/usr/bin/tesseract"

def test_autooocr_client_windows_fallback():
    client = AutoOcrClient(tesseract_cmd=None)
    with patch("os.name", "nt"):
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            with patch("os.path.exists") as mock_exists:
                # Mock it so it finds it in the first common path
                mock_exists.side_effect = lambda p: p == r"C:\Program Files\Tesseract-OCR\tesseract.exe"

                with patch("subprocess.run") as mock_run:
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stdout = "some text"

                    client.extract_text("dummy.jpg")

                    args, _ = mock_run.call_args
                    assert args[0][0] == r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def test_autooocr_client_fallback_to_filename():
    client = AutoOcrClient(tesseract_cmd=None)
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None
        # Ensure we are not on windows for this test to avoid those fallbacks
        with patch("os.name", "posix"):
            text = client.extract_text("my-receipt_image.jpg")
            assert text == "my receipt image"
