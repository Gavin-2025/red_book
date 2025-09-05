# GitHub Actions 配置说明

## 🎯 项目已成功推送到 GitHub！

仓库地址：https://github.com/Gavin-2025/red_book

## 🔧 添加自动构建功能

### 方法一：更新 Token 权限
1. 访问 GitHub → Settings → Developer settings → Personal access tokens
2. 编辑你的 token
3. 添加 `workflow` 权限
4. 运行以下命令：

```bash
cd "/Users/chengang/work/code/red book"
git add .github/workflows/build-windows.yml
git commit -m "添加GitHub Actions自动构建工作流"
git push https://你的新token@github.com/Gavin-2025/red_book.git main
```

### 方法二：网页创建（推荐）
1. 访问 https://github.com/Gavin-2025/red_book/actions
2. 点击 "New workflow"
3. 点击 "set up a workflow yourself"
4. 将以下内容复制到编辑器中：

```yaml
name: Build Windows Executable

on:
  workflow_dispatch:  # 允许手动触发

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --console --name="小红书达人评估系统_v2.0" --add-data="示例数据模板.csv;." --hidden-import=streamlit --hidden-import=streamlit.web.cli advanced_evaluator.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: windows-executable
        path: dist/小红书达人评估系统_v2.0.exe
```

5. 保存文件名为 `build-windows.yml`
6. 提交更改

## 🚀 使用自动构建

配置完成后：
1. 访问 Actions 页面
2. 选择 "Build Windows Executable"
3. 点击 "Run workflow"
4. 等待构建完成
5. 下载生成的 exe 文件

## 📁 当前项目结构

- ✅ 核心代码已推送
- ✅ 文档已完善
- ⏳ 等待添加自动构建功能

祝你使用愉快！🎉
