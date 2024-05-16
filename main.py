from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from fastapi.responses import Response
from Functions.login import login as lg
import pandas as pd
import io 

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static") 
template = Jinja2Templates(directory="templates")



@app.post("/uploaded")
async def create_upload_files(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    try:
        print("Recibiendo archivos...")
        dfs = []  
        for file in files:
            print(f"Procesando archivo: {file.filename}")
            contents = await file.read() 
            df = pd.read_excel(io.BytesIO(contents))  
            dfs.append(df)


        combined_df = pd.concat(dfs)

        print("Generando archivo de salida...")

        output_excel = io.BytesIO()
        combined_df.to_excel(output_excel, index=False)
        output_excel.seek(0)

        print("Leyendo contenido del archivo generado en memoria...")

        file_content = output_excel.getvalue()

        print("Devolviendo el contenido del archivo como respuesta HTTP...")
        return Response(content=file_content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment;filename=output.xlsx"})

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/uploadfiles")
def upload_files(req: Request):
    return template.TemplateResponse(
        name = "uploadfiles.html",
        context= {"request":req}
    )

@app.get("/main")
async def read_root(req: Request):

    return template.TemplateResponse(
        name = "component.html",
        context = {"request": req}
    )
@app.get("/")
async def login(request: Request):
    return template.TemplateResponse("login.html", {"request": request})
                                      

@app.post("/Login")
async def handle_login(request: Request):
    body = await request.body()
    decoded_body = body.decode("utf-8")
    form_data = {}
    for item in decoded_body.split("&"):
        key, value = item.split("=")
        form_data[key] = value
    username = form_data.get("username", "")
    password = form_data.get("password", "")
    
    username = username.replace('+'," ")
    login = await lg(username, password)
    if(login):
        if(login == "Admin"):
            return RedirectResponse(url="/uploadfiles", status_code=303)
        return RedirectResponse(url="/main", status_code=303)
    return RedirectResponse(url="/", status_code=303)

