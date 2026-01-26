document.addEventListener("DOMContentLoaded", () => {

    const emojiButtons = document.querySelectorAll(".emoji-btn");
    const submitBtn = document.getElementById("emojiSubmit");
    const selectedText = document.getElementById("selectedText");

    emojiButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            emojiButtons.forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
            selectedText.innerText = `Selected Mood: ${btn.dataset.emoji} ${btn.dataset.name}`;
            submitBtn.disabled = false;
        });
    });

    document.addEventListener("click", e => {

        if (e.target.classList.contains("play-btn")) {
            const track = e.target.closest(".track");
            const audio = track.querySelector("audio");
            const isPlaying = !audio.paused;

            document.querySelectorAll("audio").forEach(a => {
                a.pause();
                a.currentTime = 0;
            });

            document.querySelectorAll(".play-btn").forEach(b => b.innerText = "▶");

            if (!isPlaying) {
                audio.play();
                e.target.innerText = "⏸";
            }
        }

        if (e.target.classList.contains("like-btn")) {
            e.target.classList.toggle("liked");
        }

        if (e.target.classList.contains("add-playlist")) {
            const track = e.target.closest(".track");
            track.classList.add("added");
            setTimeout(() => track.classList.remove("added"), 1000);
        }
    });

});
