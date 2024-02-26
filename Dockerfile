
#pull official base image 도커에 기본으로 있는 파이썬 설치되어있는 이미지 불러오기
FROM python:3.8.0-slim-buster

#set work directory 작업 폴더 지정
WORKDIR /usr/src/app

# set environment variables  확장자가 .pyc인 파일 생성하지않기 + 파이썬 로그가 버퍼링 없이 즉각적으로 출력
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

#현재의 작업물을 작업폴더로 이전
COPY . /usr/src/app/
# install dependencies requirements파일에 나열된 라이브러리들 설치하기
RUN pip install --upgrade pip
RUN pip install -r requirements.txt