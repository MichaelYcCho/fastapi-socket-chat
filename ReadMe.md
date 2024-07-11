# FastAPI Chat Application


### 관련된 모델정보및 다이어그램은 /docs/fast-api-chat.drawio.pdf 파일을 참조해주세요.


## 개요
이 프로젝트는 FastAPI를 사용하여 구축된 간단한 채팅 애플리케이션입니다. 사용자는 1:1 채팅 및 그룹 채팅을 할 수 있으며, 메시지는 SQLite 데이터베이스에 저장됩니다. 이 프로젝트는 Docker와 Docker Compose를 사용하여 배포하고 테스트할 수 있습니다.



## 기능
- 1:1 채팅 및 그룹 채팅
- 사용자 접속 상태 확인
- 채팅 로그 저장
- 그룹 생성 및 사용자 추가



## 실행방법 
1. Docker로 실행
- docker-compose up --build

2. 수동실행(poetry)
- poetry install
- uvicorn main:app --reload



## POSTMAN 테스트시 Sample Request

```
// 그룹 생성
{
    "type": "GROUP_CREATE",
    "group_name": "group1"
}
```

```
// 그룹원 추가
{
    "type": "GROUP_ADD_USER",
    "group_name": "group1"

}
```

```
//그룹 메세지
{
    "type": "GROUP_MESSAGE",
    "group_name": "group1",
    "message": "Group message!"
}
```



```
// 개인메세지
{
     "type": "PERSONAL_MESSAGE",
     "to": "2",
     "message": "Hello, this is a personal message!"
 }
```
