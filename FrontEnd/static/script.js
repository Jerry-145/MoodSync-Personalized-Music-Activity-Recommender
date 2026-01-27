let selectedEmoji = "";

document.querySelectorAll(".emoji-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".emoji-btn").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        selectedEmoji = btn.dataset.emoji;
        document.getElementById("selectedText").innerText =
            `Selected Mood: ${btn.dataset.emoji} ${btn.dataset.name}`;
        document.getElementById("emojiSubmit").disabled = false;
    });
});

document.getElementById("emojiSubmit").addEventListener("click", async () => {
    const res = await fetch("/emoji", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({emoji: selectedEmoji})
    });
    const data = await res.json();
    updateUI(data);
});

document.getElementById("cameraBtn").addEventListener("click", async () => {
    const btn = document.getElementById("cameraBtn");
    btn.innerText = "Detecting...";
    btn.disabled = true;

    const res = await fetch("/detect", {method: "POST"});
    const data = await res.json();
    updateUI(data);

    btn.innerText = "📷 Detect Emotion";
    btn.disabled = false;
});

function updateUI(data) {
    document.querySelector(".result").style.display = "block";
    document.getElementById("emotionTitle").innerText =
        `Detected Emotion: ${data.emotion}`;

    const list = document.querySelector(".track-list");
    list.innerHTML = "";

    data.tracks.forEach(t => {
        list.innerHTML += `
            <div>
                <strong>${t.name}</strong> - ${t.artist}
                ${t.preview_url ? `<audio controls src="${t.preview_url}"></audio>` : ""}
                <br><a href="${t.spotify_url}" target="_blank">Open in Spotify</a>
            </div><hr>
        `;
    });
}
