"""Unit tests related to FastAPI app."""

from src.quote_consumer.main import app


class TestFastapiApp:
    def test_app_attributes(self) -> None:
        assert app.title == "Quote Consumer"
        assert app.description == "This app fetches data from Exchange and stores it."
        assert app.version == "1.0.0"
        assert app.contact == {
            "url": "https://github.com/denisborisov",
            "name": "Denis Borisov",
            "email": "denis.borisov@hotmail.com",
        }
        assert app.docs_url == "/api/docs"
        assert app.redoc_url == "/api/redoc"
