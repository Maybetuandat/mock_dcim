uvicorn main:app --host 0.0.0.0 --port 9999 --reload
docker run -d -p 9999:9999 --name mock-dcim --restart unless-stopped mock-dcim:latest