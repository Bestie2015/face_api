## Face API

### Run
```
export AZURE_FACE_API_KEY=12345678
docker-compose up
```

### Endpoints
* /healthcheck 	[GET] - return 200
* / 			[POST] - return metadata on the best image  
* * body: ["main001.jpg","main003.jpg"]


### Tests
in order to run tests while docker is running- `docker exec -it face_api pytest`
