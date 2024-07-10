# Home Security System 
__________________________________________________________________

## How to start

### Clone project
```bash
git clone https://github.com/VitaliiFedin/Home-Security-System.git
```
### Start project
To start application you need to create .env file inside root directory (where manage.py located) with variables (examples in .env.sample).Then by using docker run in terminal
```bash
docker-compose up -d --build
```
- -d detach mode, so you can still use terminal
- --build build image
## Access application
__________________________________________________________________

To access application via browser go to [Application](http://localhost:8000/)  
To access API go to [API](http://localhost:8000/api)

