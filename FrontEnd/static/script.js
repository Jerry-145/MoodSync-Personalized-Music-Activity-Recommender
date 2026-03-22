let selectedEmoji = "";
let currentEmotion = "Search";   // ⭐ IMPORTANT FIX


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

    currentEmotion = data.emotion || currentEmotion;

    document.querySelector(".result").style.display = "block";

    document.getElementById("emotionTitle").innerText =
        `Detected Emotion: ${currentEmotion}`;

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
    <button onclick="playSong('${t.preview_url}', '${escapeQuotes(t.name)}', '${escapeQuotes(t.artist)}')">
        ▶ Play Preview
    </button>
` : ""}

<a href="${t.spotify_url}" target="_blank"
   onclick="saveHistory('${escapeQuotes(t.name)}', '${escapeQuotes(t.artist)}', '${escapeQuotes(currentEmotion)}')">
    <button>🎧 Open in Spotify</button>
</a>

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

        console.log("✅ History saved:", songName);

    } catch (error) {
        console.error("❌ Error saving history:", error);
    }
}


/* ---------------- SEARCH ---------------- */
document.getElementById("searchBtn").addEventListener("click", async () => {

    const query = document.getElementById("searchInput").value.trim();
    if (!query) return;

    const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (!data || data.length === 0) {
        document.querySelector(".result").style.display = "block";

        document.getElementById("emotionTitle").innerText = "No Results Found";

        document.querySelector(".track-list").innerHTML =
            `<p style="text-align:center; color:gray;">No songs found</p>`;
        return;
    }

    updateUI({
        emotion: currentEmotion,
        tracks: data
    });
});


/* ---------------- POPULAR ---------------- */
document.getElementById("popularBtn").addEventListener("click", async () => {

    const res = await fetch("/popular");
    const data = await res.json();

    updateUI({
        emotion: currentEmotion || "Popular",
        tracks: data
    });
});


/* ---------------- HELPER ---------------- */
function escapeQuotes(text) {
    if (!text) return "";
    return text.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

let currentAudio = null;

function playSong(url, name, artist) {

    // Stop previous song
    if (currentAudio) {
        currentAudio.pause();
    }

    currentAudio = new Audio(url);
    currentAudio.play();

    // Save history when played
    saveHistory(name, artist, currentEmotion);

    console.log("▶ Playing:", name);
}