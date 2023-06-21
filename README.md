# ChatGPT-chatbot

# Setup enviroment
Follow and download:
* Server Ngrok: https://ngrok.com/docs/getting-started/
* MongoDb Compass: https://www.mongodb.com/products/compass
* Python 3.11+

## Guide
* open terminal cd to platform need to use :```cd messenger``` 
* run ```make init```
* add necessary parameter(openai apikey, facebook token, etc.)
* run ```make run```

# Facebook
* open terminal cd to platform need to use :```cd server-api-facebook```
1. Create file ``.gpt_api_key``, `.messenger_token` for gpt api key, messenger token
2. Create app in https://developers.facebook.com to get messenger token
3. Follow Makefile
* requirements: ```pip install -r requirements.txt```

# Zalo
* open terminal cd to platform need to use :```cd server-api-zalo```
1. Create file ``config.json`` for api gpt key 
2. Create app in https://developers.zalo.me to setup
3. Follow Makefile 
* requirements: ```pip install -r requirements.txt```
