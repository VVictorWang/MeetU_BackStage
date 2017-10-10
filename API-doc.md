# `MeetU`后台接口
## 全局参数:
- 数据形式为`application/json`
- 需要`token`的接口用`@token_require`标注

## 用户信息(`userinfo`):
```json
{
    "_id": "No006", //the user's id
    "nickname": "第一个", //the user's nickname
    "phone": "15824578911", //the user's phone number
    "qq": "643708967", //the user's qq
    "age": 18, //the user's age
    "love_level": 0, //the user's love level, between 0 and 100
    "needs": [] //the orders that the user participates
}
```
## 订单信息(`needinfo`)
```json
{
    "creator_id": "No002", //the creator's id
    "desc": "带我把", //the description of the order
    "continue_time": 10, //the time that the order will continue
    "sex": "男", //the creator's sex
    "longitude": 121.2, //the creator's longitude
    "latitude": 134.3, //the creator's latitude
    "location": "华中科技大学", //the creator's location
    "destination": "东一食堂", //the creator's destination
    "create_time": 1507636528, //the time when the order was created
    "status": 0, //the status of the order(0 represents waiting for someone to help; 1 represents the order is undergo; 2 represents the order was finished)
    "helper_id": -1, //the helper's id
    "_id": "59dcb53079aef322f174e467" //the order id
}
```

## 接口描述
### 用户注册
`URL`: `api/v1/user`, `method`=**`POST`**

`Request Body`:
```json
{
	"id": string,
	"phone":string,
	"qq": string,
	"password": string,
	"nickname": string,
	"age":int
}
```
