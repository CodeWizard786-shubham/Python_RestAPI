from fastapi import FastAPI, File, UploadFile ,Response

app = FastAPI()

# upload the file 
@app.post('/uploadfile/')
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    with open(file.filename, 'wb') as f:
        f.write(contents)
    return {'filename': file.filename} 


# read file from folder
@app.get('/getfile/')
async def get_file(filename: str):
    with open(filename, 'rb') as f:
        contents = f.read()
    return Response(content=contents, media_type='image/jpeg')
