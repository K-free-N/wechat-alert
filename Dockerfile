FROM python:3.10.2
COPY ./app /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
# 指定了一下国内镜像,由于requirement.txt中有要安装的包,下载又很慢,所以选择国内镜像;
RUN pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 原本是CMD的,这样我们在K8s中部署不好传参,所以改了entrypoint;
ENTRYPOINT ["python", "/app/main.py"]
