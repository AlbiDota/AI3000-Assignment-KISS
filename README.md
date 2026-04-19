# AI3000-Assignment-KISS
## Contributors
- [Oscar](https://github.com/OscarGamst)
- [Sara](https://github.com/saraechk)
- [Albert](https://github.com/AlbiDota)

---

## How to run
### Dependencies

```
pip install sentence-transformers openai python-dotenv
```

<br/>

---

### API key
Get your api key from [OpenAi](https://platform.openai.com/api-keys),
or contact Albert to borrow one :)

Create a .env file in this folder and place the API key there like so:

```
OPENAI_API_KEY="api_key_here_hehe"
```

<br/>

---

### Start server
In root directory ->
```
python api.py
```

<br/>

---

### Using the "chatbot" function
#### Html+js
Located in the /html folder, you can just launch the html file with the server running, and javascript will do most of the work for you.

You will see a chatbox with an input field and a box to display the chat messages.

![chatbox-example](/html/example.png)

Here you can simply send questions, and both your input and the OpenAI output will be displayed here.

You can also check out the top semantic hits being logged in the server terminal while waiting for your response.

<br/>

#### Postman
You can use postman and send a body like the following example:

Set up a POST-request to 'http://localhost:5000/chat'

The "history" parameter is entirely optional, and is not needed in the post body.

```
{
    "type": "faq",
    "question": "Selger dere figurer og maling til warhammer?",
    "history": [
        {
            "role": "user", 
            "content": "er det åpent på torsdag?"
        },
        {
            "role": "assistant", 
            "content": "Ja. Butikken er åpen på torsdag. Åpningstiden er 08:00–22:00 på alle hverdager (mandag–fredag), så torsdag er åpen.\n\nKilder brukt: faq-021 - Opening Times."
        }
    ]
}
```

<br/>

---

