import uvicorn
from app.application import create_application

app = create_application()


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
