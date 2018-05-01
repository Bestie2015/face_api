## Face API

### Run
```
export AZURE_FACE_API_KEY=your_azure_face_api_key
docker-compose up
```

### Endpoints
* `127.0.0.1:5002/healthcheck` 	[GET] - return 200
* `127.0.0.1:5002/` 			         [POST] - return metadata on the best image  
  * body: `["main001.jpg","main003.jpg"]`
  * return `{
    "main001.jpg": {
        "faceId": "12d51e2f-6bf9-46d7-b4ff-b8db399c924a",
        "faceRectangle": {
            "height": 221,
            "left": 114,
            "top": 315,
            "width": 221
        }
    }
}`


### Tests
in order to run tests while docker is running- `docker exec -it face_api pytest`
