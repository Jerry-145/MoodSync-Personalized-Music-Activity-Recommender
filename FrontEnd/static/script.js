let selectedEmoji = "";

/* ---------------- EMOJI SELECTION ---------------- */
document.querySelectorAll(".emoji-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".emoji-btn")
            .forEach(b => b.classList.remove("selected"));

        btn.classList.add("selected");
        selectedEmoji = btn.dataset.emoji;

        document.getElementById("selectedText").innerText =
            `Selected Mood: ${btn.dataset.emoji} ${btn.dataset.name}`;

        document.getElementById("emojiSubmit").disabled = false;
    });
});

/* ---------------- EMOJI SUBMIT ---------------- */
document.getElementById("emojiSubmit").addEventListener("click", async () => {
    const res = await fetch("/emoji", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({emoji: selectedEmoji})
    });

    const data = await res.json();
    updateUI(data);
});

/* ---------------- CAMERA DETECTION ---------------- */
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

/* ---------------- UPDATE UI ---------------- */
function updateUI(data) {
    document.querySelector(".result").style.display = "block";
    document.getElementById("emotionTitle").innerText =
        `Detected Emotion: ${data.emotion}`;

    const list = document.querySelector(".track-list");
    list.innerHTML = "";

    data.tracks.forEach(t => {
        list.innerHTML += `
            <div class="track-card">
                <div class="track-info">
                    <strong>${t.name}</strong>
                    <p>${t.artist}</p>
                </div>
                ${t.preview_url ? `
                    <audio controls
                        src="${t.preview_url}"
                        onplay="saveHistory('${t.name}', '${t.artist}', '${data.emotion}')">
                    </audio>
                ` : `<p>No preview available</p>`}
            </div>
        `;
    });
}

/* ---------------- SAVE HISTORY ---------------- */
async function saveHistory(songName, artist, emotion) {
    try {
        await fetch("/save_history", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                song_name: songName,
                artist: artist,
                emotion: emotion
            })
        });
    } catch (error) {
        console.error("Error saving history:", error);
    }
}

/* ---------------- SEARCH ---------------- */
document.getElementById("searchBtn").addEventListener("click", async () => {
    const query = document.getElementById("searchInput").value;
    if (!query) return;

    const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    updateUI({
        emotion: "Search Results",
        tracks: data
    });
});

/* ---------------- POPULAR ---------------- */
document.getElementById("popularBtn").addEventListener("click", async () => {
    const res = await fetch("/popular");
    const data = await res.json();

    updateUI({
        emotion: "🔥 Popular Songs",
        tracks: data
    });
});
