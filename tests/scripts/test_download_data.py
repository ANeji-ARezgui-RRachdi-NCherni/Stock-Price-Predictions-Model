import pytest
from datetime import datetime, timedelta
from unittest import mock

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.download_data import get_dates, update_dates, download

# -------------- Fixtures ----------------
@pytest.fixture
def today_date():
    return datetime.today().date()

@pytest.fixture
def session_mock():
    return mock.Mock()

@pytest.fixture
def dummy_response():
    mock_resp = mock.Mock()
    mock_resp.status_code = 200
    mock_resp.content = b"symbole;date;ouverture;haut;bas;cloture;volume\r\nSYM1;01-01-2024;100;110;90;105;1000"
    return mock_resp

# -------------- Tests for get_dates ----------------
class TestGetDates:

    def test_get_dates_today(self, today_date):
        """Test when start date is today's date."""
        start_str = today_date.strftime("%d-%m-%Y")
        start, end = get_dates(start_str)
        assert start == today_date
        assert end == today_date

    @pytest.mark.parametrize("input_date", ["01-01-2024", "15-08-2023"])
    def test_get_dates_past_dates(self, input_date):
        """Test normal case with past dates."""
        expected_start = datetime.strptime(input_date, "%d-%m-%Y").date()
        expected_end = expected_start + timedelta(days=83)
        start, end = get_dates(input_date)
        assert start == expected_start
        assert end == expected_end

# -------------- Tests for update_dates ----------------
class TestUpdateDates:

    def test_update_dates_normal(self):
        """Test that update_dates shifts by +1 and +84 days."""
        original_date = datetime(2024, 1, 1).date()
        start, end = update_dates(original_date)
        assert start == original_date + timedelta(days=1)
        assert end == original_date + timedelta(days=84)

# -------------- Tests for download_data ----------------
class TestDownloadData:

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.stat")  # <--- Mock os.stat too
    def test_download_successful(self, mock_stat, mock_exists, mock_makedirs, mock_open_file, session_mock, dummy_response):
        """Test successful download and file creation."""
        session_mock.post.return_value = dummy_response
        # Mock st_size attribute to simulate empty file (size 0)
        mock_stat.return_value.st_size = 0

        download(
            "2024-01-01",
            "2024-03-24",
            cookies={},
            token="dummy_token",
            session=session_mock,
            link="https://www.ilboursa.com/marches/download/DUMMY",
            fileName="DUMMY.csv"
        )

    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=True)
    def test_download_failure(self, mock_exists, mock_makedirs, session_mock):
        """Test failed download raises Exception."""
        failed_response = mock.Mock()
        failed_response.status_code = 500
        session_mock.post.return_value = failed_response

        with pytest.raises(Exception, match="❌ Failed to download file. Status code: 500"):
            download(
                "2024-01-01",
                "2024-03-24",
                cookies={},
                token="dummy_token",
                session=session_mock,
                link="https://www.ilboursa.com/marches/download/DUMMY",
                fileName="DUMMY.csv"
            )

