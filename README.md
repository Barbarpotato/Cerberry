# Development Environment

## Continous Integration
By Integrating the code to main branch, ensure that we have passed several unit test before merging to the main branch. in this project we used nosetest package to test all functional unit and make sure it works. there are several configuration like installing some packages : `nose`, `pinocchio`, `coverage` then create the automate script in `setup.cfg`

I am also included github action for supporting the CI pipeline and add some event whenever me or someone else push the code to the main branch it will catch the specific event (git push, etc) that triggering the task and jobs.
## Continous Delivery
Launching to production is just using a `vercel` platform. By pushing the code to the main branch the Vercel platform will execute the trigger and launching application to a production.

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

