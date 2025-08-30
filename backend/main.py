import os
import uuid
import sqlite3
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings


app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库初始化
conn = sqlite3.connect('knowledge-base.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT, is_admin BOOLEAN)''')
c.execute('''CREATE TABLE IF NOT EXISTS knowledge_bases
             (id TEXT PRIMARY KEY, name TEXT, owner_id INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS documents
             (id TEXT PRIMARY KEY, kb_id TEXT, filename TEXT, status TEXT)''')
conn.commit()

# 用户系统
users = {
    "admin": {"username": "admin", "password": "admin123", "is_admin": True},
    "user1": {"username": "user1", "password": "user123", "is_admin": False}
}

# jwt 认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class UserLogin(BaseModel):
    username: str
    password: str
class DocumentUpload(BaseModel):
    kb_id: str

# 文件解析工具函数
def pase_document(file_path: str, file_type: str) -> str:
    if file_type == 'pdf':
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_type == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_type == "docx":
        import docx2txt
        return docx2txt.process(file_path)
    else:
        raise ValueError("暂时支持上传pdf, txt, docx格式的文件")
    
# 文本chunk
def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "。", "！", "？", "，"]
    )
    return splitter.split_text(text)

# 登录接口
@app.post("/login")
def login(user: UserLogin):
    if user.username in users and users[user.username]["password"] == user.password:
        # 在实际应用中应生成JWT token令牌
        token = f"fake_token_for_{user.username}"
        return {
            "token": token, 
            "user": {
                "username": user.username, 
                "is_admin": users[user.username]["is_admin"]
            },
            
            }
    raise HTTPException(status_code=400, detail="用户名或密码错误")

# 文件上传接口
@app.post("/upload")
async def upload_file(
    kb_id: str = Depends(DocumentUpload), 
    # kb_id: str = Form(...),
    file: UploadFile = File(...), 
    token: str = Depends(oauth2_scheme)
    ): 
    # 在实际中验证token
    
    # 保存文件
    file_type = file.filename.split('.')[-1].lower()
    if file_type not in ['pdf', 'txt', 'docx']:
        raise HTTPException(status_code=400, detail="仅支持上传pdf, txt, docx格式的文件")
    
    os.makedirs('uploads', exist_ok=True)
    filename = f"{uuid.uuid4()}.{file_type}"
    file_path = os.path.join('uploads', filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 解析文件
    try:
        text = pase_document(file_path, file_type)
        chunks = chunk_text(text)
        
        # 生成向量，存储到FAISS
        embeddings = OllamaEmbeddings(model="bag-m3")
        if os.path.exists(f"vectorstores/{kb_id}"):
            vector_store = FAISS.load_local(f"vectorstores/{kb_id}", embeddings)
            vector_store.add_texts(chunks)
        else:
            vector_store = FAISS.from_texts(chunks, embeddings)
        
        vector_store.save_local(f"vectorstores/{kb_id}")

        # 更新数据库
        return {"status": "文件上传并处理成功", "filename": file.filename}
    
    # 抛异常
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
    
# 知识库管理
@app.post("/knowledge/create")
def create_kb(name: str, token: str = Depends(oauth2_scheme)):
    kb_id = str(uuid.uuid4())
    os.makedirs(f"vectorstores/{kb_id}", exist_ok=True)
    return {"kb_id": kb_id, "name": name}

# 知识库列表
@app.get("/knowledge/list")
def list_kbs(token: str = Depends(oauth2_scheme)):
    # 简化的知识库列表
    return [{"id": "default", "name": "默认知识库"}]

# 管理员接口
@app.get("/admin/users")
def list_users(token: str = Depends(oauth2_scheme)):
    # 验证管理员权限
    return[
        {"id": 1, "username": "admin", "is_admin": True},
        {"id": 2, "username": "user1", "is_admin": False}
    ]


if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="127.0.0.1", port=8001) 