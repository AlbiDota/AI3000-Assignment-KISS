// we'll only ever run this thing locally, so dont care about security or alternate urls whatever
const chatUrl = "http://localhost:5000/chat"

// parameters and such
const chatBox = document.getElementById("chatbox");
const qInput = document.getElementById("question");
const sendBtn = document.getElementById("sendBtn");

const chatHistory = [];

function getSelectedType() {
    const selected = document.querySelector('input[name="type"]:checked');
    return selected ? selected.value : "faq";
}

function renderChat() {
    chatBox.innerHTML = chatHistory.map(e => {
        const tag = e.role == "bot" ? "bot" : "user";
        return `<div class="${tag}"><strong>${e.role}:</strong> ${e.content}</div>`;
    }).join("");
}

async function sendQuestion() {
    const question = qInput.value.trim();
    const type = getSelectedType();
    if (!question)
        return;

    chatHistory.push({role: "user", content: question});
    renderChat();
    qInput.value = "";

    const payload = {
        type: type,
        question: question,
        history: chatHistory
    };
    console.log(payload);

    try {
        const res = await fetch(chatUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const resData = await res.json();

        if (res.ok) {
            const botText = resData.response;
            chatHistory.push({role: "bot", content: botText});
        } else {
            chatHistory.push({role: "bot", content: `Error: ${resData.error}`});
        }

    } catch(err) {
        chatHistory.push({role: "bot", content: `api error: ${err.message}`});
    }

    renderChat();

}


sendBtn.addEventListener("click", sendQuestion);
qInput.addEventListener("keydown", e => { if (e.key === "Enter") sendQuestion(); });