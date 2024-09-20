# Development Environment

## Activating the virtual environment
Creating the virtual env (if never applied to this repo)
```bash
python -m venv venv
```
Go to Root Dircetory and activate the virtual environment using the script below:
```bash
source venv/Scripts/activate
```
Install the requirement package
```bash
pip install -r requirements.txt
```
Running the development app using
```bash
flask run
```

## Docker Image
The Docker Image is available in this site: <a target="_blank" href="https://hub.docker.com/repository/docker/darmajr94/backend-blog/general">backend-blog:development</a> the docker image is automatically update when this repository is pushed and merged to the main branch

