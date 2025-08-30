## 项目架构：
knowledge-base/
├── backend/                  # FastAPI 后端
│   ├── main.py               # 主应用
│   ├── requirements.txt      # 依赖
│   ├── uploads/              # 上传文件存储
│   └── vectorstores/         # FAISS向量存储
├──frontend/                  # vue前端
├── src/
│   ├── store/
│   │   └── index.js
│   ├── router/
│   │   └── index.js          # 路由管理
│   ├── views/
│   │   ├── Login.vue         # 登录页面
│   │   ├── KnowledgeBase.vue # 知识库页面
│   │   └── Admin.vue         # 用户管理页面
│   ├── components/
│   │   ├── FileUpload.vue    # 文件上传组件
│   │   └── ChatBox.vue       # 聊天组件
│   ├── App.vue               # 主程序
│   └── main.js               # 配置文件
├── babel.config.js
├── vue.config.js
├── .eslintrc.js
├── .env
└── package.json

## 项目部署步骤，按照以下执行：
### 1.创建虚拟环境
#### 用python创建：
#### python -m venv venv  or  python3 -m venv venv      
#### 激活环境（Windows）：.\venv\Scripts\activate  
#### 激活环境（Linux）：source venv/bin/activate  

#### 用conda创建：
#### conda create knowledge-base
#### conda activate knowledge-base

### 2.安装依赖：
#### cd knowledge-base
#### pip install -r .\requirements.txt (不行就挂阿里云或者腾讯云)

### 4.启动后端服务：
#### cd backend
#### python main.js 


### 3.前端依赖：
#### cd frontend
#### npm install 
#### 启动服务： npm run serve

